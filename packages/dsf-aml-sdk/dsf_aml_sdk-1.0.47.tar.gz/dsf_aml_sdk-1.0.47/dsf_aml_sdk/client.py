# ============================================
# dsf_aml_sdk/client.py (DROP-IN)
# ============================================
from . import __version__
from .models import Config, EvaluationResult, DistillationResult
from .exceptions import APIError, LicenseError, ValidationError

import requests
from typing import Dict, List, Optional, Union, Any, Iterable, Tuple
from urllib.parse import urljoin
import time
from functools import wraps
import logging
import os
import math
import random

logger = logging.getLogger(__name__)

# --------- Límites tunables por ENV (con defaults seguros) ----------
MAX_N_SYNTHETIC = int(os.getenv("DSF_MAX_N_SYNTHETIC", "10000"))
MAX_PARTIAL_VARIANTS = int(os.getenv("DSF_MAX_PARTIAL_VARIANTS", "5000"))
MAX_DATASET_ITEMS = int(os.getenv("DSF_MAX_DATASET_ITEMS", "10000"))  # límite duro backend
MAX_BATCH_EVAL = int(os.getenv("DSF_MAX_BATCH_EVAL", "1000"))         # evaluate_batch
MAX_BATCH_PREDICT = int(os.getenv("DSF_MAX_BATCH_PREDICT", "2000"))   # translate_predict
DEFAULT_CHUNK = int(os.getenv("DSF_DEFAULT_CHUNK", "800"))            # tamaño chunk por defecto

# --------- Utilidades internas ----------
def _ensure_len(name: str, seq, max_len: int):
    if isinstance(seq, list) and len(seq) > max_len:
        raise ValidationError(f"{name} too large — max {max_len}")

def _normalize_config_for_wire(cfg: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(cfg, dict):
        return {}
    return {k: cfg[k] for k in sorted(cfg.keys())}

def _chunked(seq: List[Any], chunk: int) -> Iterable[List[Any]]:
    for i in range(0, len(seq), chunk):
        yield seq[i:i + chunk]

def _to_serializable(v: Any) -> Any:
    try:
        import numpy as np
        if isinstance(v, (np.generic,)):
            return v.item()
        if isinstance(v, (np.ndarray,)):
            return v.tolist()
    except Exception:
        pass
    if isinstance(v, (float, int, str, bool)) or v is None:
        return v
    if isinstance(v, (complex,)):
        return float(v)
    # fallback seguro:
    return str(v)  # 👈 antes devolvías v; mejor serializar a str


def _sanitize_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    return {str(k): _to_serializable(v) for k, v in rec.items()}

def _sanitize_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [_sanitize_record(r) for r in records]

def _global_near_threshold(scores: List[float], top_k_percent: float) -> List[int]:
    # Selección por distancia a la mediana global
    if not scores:
        return []
    thr = float(_median(scores))
    distances = [abs(s - thr) for s in scores]
    k = max(1, int(len(scores) * float(top_k_percent)))
    return sorted(range(len(scores)), key=lambda i: distances[i])[:k]

def _median(a: List[float]) -> float:
    b = sorted(a)
    n = len(b)
    if n == 0:
        return 0.0
    mid = n // 2
    if n % 2 == 0:
        return (b[mid - 1] + b[mid]) / 2.0
    return b[mid]

def _cap_list(lst: List[Any], cap: int, seed: int = 42) -> List[Any]:
    if len(lst) <= cap:
        return lst
    random.Random(seed).shuffle(lst)
    return lst[:cap]

# --------- Decorador de reintentos ----------
def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, APIError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
            raise last_exception
        return wrapper
    return decorator

class AMLSDK:
    BASE_URL = os.environ.get(
        "DSF_AML_BASE_URL",
        "https://dsf-gwx2hvg0t-api-dsfuptech.vercel.app/"
    )
    TIERS = {"community", "professional", "enterprise"}

    def __init__(
        self,
        license_key: Optional[str] = None,
        tier: str = "community",
        base_url: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        validate_on_init: bool = False
    ):
        if tier not in self.TIERS:
            raise ValidationError(f"Invalid tier. Allowed: {self.TIERS}")

        self.license_key = license_key
        self.tier = tier
        self.base_url = base_url or os.getenv("DSF_AML_BASE_URL", self.BASE_URL)
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": f"DSF-AML-SDK-Python/{__version__}"
        })

        if validate_on_init and self.tier != "community" and self.license_key:
            self._validate_license()

        # última config usada (para get_metrics())
        self._last_config: Optional[Dict[str, Any]] = None

    # ---------- Helpers de licencia ----------
    def _validate_license(self):
        req = {
            "data": {},
            "config": {"__probe__": {"default": 0, "weight": 1.0, "criticality": 1.0}},
            "license_key": self.license_key,
        }
        resp = self._make_request("", req)
        if not isinstance(resp, dict):
            raise LicenseError("License validation failed (unexpected response)")

    def _ensure_license_if_needed(self):
        if self.tier != "community" and self.license_key:
            try:
                self._validate_license()
            except Exception:
                logger.warning("License pre-check failed; relying on server-side enforcement")

    # ---------- HTTP ----------
    @retry_on_failure(max_retries=3)
    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.post(url, json=data, timeout=self.timeout, verify=self.verify_ssl)

            if response.status_code == 200:
                if not response.content:
                    return {}
                try:
                    return response.json()
                except Exception:
                    raise APIError(f"Malformed JSON (200): {response.text[:200]}", status_code=200)

            # Parseo de errores con/ sin JSON
            try:
                j = response.json()
            except Exception:
                j = {"error": f"Server error {response.status_code}", "detail": response.text[:200]}

            # Casos específicos
            if response.status_code == 403:
                raise LicenseError(j.get("error", "License error"))

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60") or "60")
                raise APIError(f"Rate limited. Retry after {retry_after}s", status_code=429)

            if response.status_code == 413:
                detail = j.get("detail") or "Payload Too Large"
                raise APIError(f"Payload Too Large — {detail}", status_code=413)

            if response.status_code >= 400:
                base = j.get("error", f"Server error {response.status_code}")
                if j.get("detail"):
                    base = f"{base} — {j['detail']}"
                context = {k: j.get(k) for k in ("status","verified_tier","has_license_key","stage","cursor") if k in j}
                if context:
                    base = f"{base} | context={context}"
                raise APIError(base, status_code=response.status_code)

        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    # ---------- Core ----------
    def get_version_info(self) -> Dict:
        return self._make_request("", {"action": "__version__"})

    def evaluate(self, data: Dict[str, Any], config: Optional[Union[Dict, Config]] = None) -> EvaluationResult:
        if isinstance(config, Config):
            config = config.to_dict()
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")

        config = _normalize_config_for_wire(config or {})
        self._last_config = config

        req = {"data": _sanitize_record(data), "config": config, "tier": self.tier}
        if self.license_key:
            req["license_key"] = self.license_key

        resp = self._make_request("", req)
        return EvaluationResult.from_response(resp)

    def batch_evaluate(self, data_points: List[Dict], config: Optional[Union[Dict, Config]] = None) -> List[EvaluationResult]:
        if self.tier == "community":
            raise LicenseError("Batch evaluation requires premium tier")
        _ensure_len("data_points", data_points, MAX_BATCH_EVAL)

        if config:
            self._last_config = config.to_dict() if isinstance(config, Config) else config
        use_config = self._last_config or {}
        if isinstance(use_config, Config):
            use_config = use_config.to_dict()
        use_config = _normalize_config_for_wire(use_config)

        req = {
            "action": "evaluate_batch",
            "tier": self.tier,
            "license_key": self.license_key,
            "config": use_config,
            "data_points": _sanitize_records(data_points),
        }

        try:
            resp = self._make_request("", req)
            # Normalización
            if isinstance(resp, list):
                raw = resp
            elif isinstance(resp, dict):
                raw = resp.get("scores")
                if raw is None:
                    raw = [resp.get(i, resp.get(str(i), 0.0)) for i in range(len(data_points))]
            else:
                raw = []

            if raw and isinstance(raw[0], dict):
                raw = [float(x.get("score", 0.0)) for x in raw]

            return [
                EvaluationResult(score=float(raw[i]) if i < len(raw) else 0.0, tier=self.tier)
                for i in range(len(data_points))
            ]
        except APIError:
            # Fallback: secuencial (mantiene contrato)
            return [self.evaluate(dp, use_config) for dp in data_points]

    def bootstrap_config(self, config: Union[Dict, Config]) -> Dict:
        if isinstance(config, Config):
            config = config.to_dict()
        config = _normalize_config_for_wire(config)
        req = {
            "action": "bootstrap_config",
            "config": config,
            "license_key": self.license_key,
        }
        return self._make_request("", req)

    # ---------- Pipelines ----------
    def pipeline_identify_seeds(self, dataset: List[Dict], config: Union[Dict, Config],
                                top_k_percent: float = 0.1, **kwargs) -> Dict:
        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        cfg = _normalize_config_for_wire(cfg)
        req = {
            "action": "pipeline_identify_seeds",
            "dataset": _sanitize_records(dataset),
            "config": cfg,
            "top_k_percent": top_k_percent,
            "license_key": self.license_key,
            **kwargs
        }
        return self._make_request("", req)

    # ---- NUEVO: selección near-threshold en cliente (sin subir dataset) ----
    def pipeline_identify_seeds_safe(
        self,
        dataset: List[Dict],
        config: Union[Dict, Config],
        top_k_percent: float = 0.3,
        chunk_size: int = DEFAULT_CHUNK
    ) -> Dict:
        """
        Selecciona seeds localmente:
        1) batch_evaluate en chunks (≤MAX_BATCH_EVAL)
        2) near-threshold global por distancia a la mediana
        3) devuelve contrato parecido a pipeline_identify_seeds
        """
        if self.tier == "community":
            raise LicenseError("Seeds selection in batch requires premium tier")

        chunk = max(1, min(int(chunk_size), MAX_BATCH_EVAL))
        ds = _sanitize_records(list(dataset))
        # scoring local
        scores: List[float] = []
        for part in _chunked(ds, chunk):
            part_scores = self.batch_evaluate(part, config)
            scores.extend([r.score for r in part_scores])

        idx = _global_near_threshold(scores, top_k_percent)
        seeds = [{"data": ds[i], "uncertainty": abs(scores[i] - float(_median(scores)))} for i in idx]
        return {
            "pipeline": "client_near_threshold",
            "seeds_count": len(seeds),
            "seeds": seeds,
            "scores_summary": {
                "median": float(_median(scores)),
                "avg": float(sum(scores) / max(1, len(scores))),
                "min": float(min(scores)) if scores else 0.0,
                "max": float(max(scores)) if scores else 0.0,
            }
        }

    def pipeline_generate_critical(self, config, seeds=None, advanced=None, **kwargs):
        if self.tier == 'community':
            raise LicenseError("Pipeline requires premium tier")

        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        cfg = _normalize_config_for_wire(cfg)

        req = {
            'action': 'pipeline_generate_critical',
            'config': cfg,
            'license_key': self.license_key,
        }

        # Auto-seeds si no las pasan pero sí hay dataset original
        original_ds = kwargs.get('original_dataset')
        if seeds is None and original_ds:
            tkp = kwargs.get('top_k_percent', 0.1)
            sresp = self.pipeline_identify_seeds_safe(dataset=original_ds, config=cfg, top_k_percent=tkp)
            seeds = [s.get('data', s) for s in (sresp.get('seeds') or [])]

        # 👇👇 CAP + sanitización AQUÍ
        if seeds:
            # cap dinámico: máx(100, 10% del original_ds) y nunca >300
            max_seeds = min(300, max(100, int(0.1 * len(original_ds or [])) if original_ds else 300))
            # normaliza estructura y hace serializable
            seeds = [_sanitize_record(s.get('data', s) if isinstance(s, dict) else s) for s in seeds][:max_seeds]
            req['seeds'] = seeds

        # Hyperparámetros prudentes por defecto (anti-timeout)
        adv = dict(advanced or {})
        adv.setdefault('epsilon', 0.08)
        adv.setdefault('diversity_threshold', 0.92)
        adv.setdefault('non_critical_ratio', 0.15)
        adv.setdefault('max_seeds_to_process', 8)
        adv.setdefault('max_retries', 5)
        adv.setdefault('require_middle', False)
        req['advanced'] = adv

        # Pasar originales opcionales
        if original_ds:
            req['original_dataset'] = _sanitize_records(original_ds)
        if 'k_variants' in kwargs:
            req['k_variants'] = kwargs['k_variants']
        if 'vectors_for_dedup' in kwargs:
            req['vectors_for_dedup'] = kwargs['vectors_for_dedup']

        return self._make_request('', req)
    
    def pipeline_generate_critical_safe(
        self,
        config,
        original_dataset,
        seeds=None,
        top_k_percent: float = 0.1,
        k_variants: int = 6,
        advanced: Optional[Dict[str, Any]] = None,
        max_chunk: int = 2000,
        max_413_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Versión robusta que evita 413: trocea original_dataset y hace backoff.
        Agrega/concatena resultados preservando métricas básicas.
        """
        if not isinstance(original_dataset, list):
            raise ValidationError("original_dataset must be a list of dicts")

        # Normaliza seeds si vienen
        norm_seeds = []
        if seeds:
            norm_seeds = [_sanitize_record(s.get('data', s) if isinstance(s, dict) else s) for s in seeds]

        # Prepara acumuladores de salida
        total_generated = 0
        critical_samples_acc: List[Dict[str, Any]] = []
        non_critical_acc: int = 0
        near_thr_vals: List[float] = []
        avg_scores: List[float] = []

        # Troceo seguro del original_dataset
        original_dataset = _sanitize_records(list(original_dataset))
        for start in range(0, len(original_dataset), max_chunk):
            ds_chunk = original_dataset[start:start + max_chunk]

            # Backoff 413
            curr_k = int(k_variants)
            curr_seeds = list(norm_seeds) if norm_seeds else None

            for retry in range(max_413_retries):
                try:
                    # Llamada base
                    res = self.pipeline_generate_critical(
                        config=config,
                        seeds=curr_seeds,
                        advanced=advanced,
                        original_dataset=ds_chunk,
                        top_k_percent=float(top_k_percent),
                        k_variants=int(curr_k),
                    )

                    # Manejo de 'partial'
                    partial_acc = []
                    while isinstance(res, dict) and res.get('status') == 'partial':
                        cursor = res.get('cursor')
                        retry_after = int(res.get('retry_after', 2))
                        time.sleep(max(1, retry_after))
                        partial_acc.append(res)
                        # relanza con el cursor
                        res = self.pipeline_generate_critical(
                            config=config,
                            seeds=curr_seeds,
                            advanced=advanced,
                            original_dataset=ds_chunk,
                            top_k_percent=float(top_k_percent),
                            k_variants=int(curr_k),
                            cursor=cursor,
                            partial_results=partial_acc,
                        )

                    # Agrega resultados del chunk
                    if isinstance(res, dict):
                        total_generated += int(res.get('total_generated', 0))
                        critical_samples_acc.extend(res.get('critical_samples', []) or [])
                        non_critical_acc += int(res.get('non_critical_added', 0))
                        q = res.get('quality_metrics') or {}
                        if 'near_threshold' in q:
                            near_thr_vals.append(float(q['near_threshold']))
                        if 'avg_score' in q:
                            avg_scores.append(float(q['avg_score']))

                    break  # chunk OK, pasa al siguiente

                except APIError as e:
                    # Backoff 413: reduce seeds y k_variants, reintenta
                    if getattr(e, 'status_code', None) == 413 and retry < max_413_retries - 1:
                        if curr_seeds:
                            # agresivo: mitad, pero no menos de 50
                            keep = max(50, len(curr_seeds) // 2)
                            curr_seeds = curr_seeds[:keep]
                        curr_k = max(2, curr_k - 1)
                        time.sleep(1 + retry)  # pequeño backoff
                        continue
                    raise  # re-lanza si no es 413 o agotó reintentos

        # Consolidar métricas de calidad (promedios simples)
        quality_metrics = {}
        if near_thr_vals:
            quality_metrics['near_threshold'] = float(sum(near_thr_vals) / len(near_thr_vals))
        if avg_scores:
            quality_metrics['avg_score'] = float(sum(avg_scores) / len(avg_scores))

        return {
            "status": "ok",
            "total_generated": total_generated,
            "critical_samples": critical_samples_acc,
            "non_critical_added": non_critical_acc,
            "quality_metrics": quality_metrics,
        }



    def pipeline_full_cycle(self, dataset: List[Dict], config: Union[Dict, Config], max_iterations: int = 5, **kwargs) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Full cycle requires enterprise tier")

        self._ensure_license_if_needed()
        _ensure_len("dataset", dataset, MAX_DATASET_ITEMS)

        cfg = config.to_dict() if isinstance(config, Config) else config
        cfg = _normalize_config_for_wire(cfg)

        req = {
            "action": "pipeline_full_cycle",
            "dataset": _sanitize_records(dataset),
            "config": cfg,
            "max_iterations": int(max_iterations),
            "license_key": self.license_key,
            **kwargs
        }
        return self._make_request("", req)

    # ---- NUEVO: orquestador seguro para full_cycle ----
    def pipeline_full_cycle_auto(
        self,
        big_dataset: List[Dict],
        config: Union[Dict, Config],
        top_k_percent: float = 0.5,
        target_cap: int = MAX_DATASET_ITEMS,
        chunk_size: int = DEFAULT_CHUNK,
        max_iterations: int = 3,
        **kwargs
    ) -> Dict:
        """
        1) batch_evaluate en chunks sobre big_dataset
        2) selección near-threshold global
        3) cap a ≤ target_cap (≤10K)
        4) llama pipeline_full_cycle con subset
        5) si 413, reduce target_cap y reintenta (e.g., 10K→8K→6K)
        """
        if self.tier != "enterprise":
            raise LicenseError("Full cycle requires enterprise tier")

        ds = _sanitize_records(list(big_dataset))
        chunk = max(1, min(int(chunk_size), MAX_BATCH_EVAL))

        # 1) scoring
        scores: List[float] = []
        for part in _chunked(ds, chunk):
            part_scores = self.batch_evaluate(part, config)
            scores.extend([r.score for r in part_scores])

        # 2) near-threshold indices
        idx = _global_near_threshold(scores, top_k_percent)
        subset = [ds[i] for i in idx]

        # 3) cap duro
        if len(subset) > target_cap:
            subset = _cap_list(subset, cap=target_cap)

        # 4) intento + 5) retroceso si 413
        sizes_try = [target_cap]
        if target_cap >= 10000:
            sizes_try += [8000, 6000]
        for cap in sizes_try:
            sub = subset if len(subset) <= cap else _cap_list(subset, cap=cap)
            try:
                return self.pipeline_full_cycle(sub, config, max_iterations=max_iterations, **kwargs)
            except APIError as e:
                if getattr(e, "status_code", None) == 413 and cap > 2000:
                    logger.warning(f"[SDK] 413 on full_cycle with {len(sub)} rows. Retrying with next smaller cap…")
                    continue
                raise e


        # Si todos fallan (muy raro)
        raise APIError("Unable to run full_cycle without 413 after backoff")

    # ---------- Curriculum (Enterprise) ----------
    def curriculum_init(self, dataset: List[Dict], config: Union[Dict, Config], **params) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Curriculum requires enterprise tier")
        cfg = config.to_dict() if isinstance(config, Config) else config
        cfg = _normalize_config_for_wire(cfg)
        req = {
            "action": "curriculum_init",
            "dataset": _sanitize_records(dataset),
            "config": cfg,
            "license_key": self.license_key,
            **params
        }
        return self._make_request("", req)

    def curriculum_step(self, dataset: List[Dict], config: Union[Dict, Config],
                        precomputed_metrics: Optional[Dict] = None) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Curriculum requires enterprise tier")
        cfg = config.to_dict() if isinstance(config, Config) else config
        cfg = _normalize_config_for_wire(cfg)
        req = {
            "action": "curriculum_step",
            "dataset": _sanitize_records(dataset),
            "config": cfg,
            "license_key": self.license_key
        }
        if precomputed_metrics:
            req["precomputed_metrics"] = precomputed_metrics
        return self._make_request("", req)

    def curriculum_status(self) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Curriculum requires enterprise tier")
        req = {"action": "curriculum_status", "license_key": self.license_key}
        return self._make_request("", req)

    # ---------- Fórmula no lineal ----------
    def evaluate_nonlinear(self, data: Dict, config: Union[Dict, Config],
                           adjustments: Dict[str, float], adjustment_values: Dict = None) -> EvaluationResult:
        if self.tier == "community":
            raise LicenseError("Nonlinear evaluation requires premium tier")
        if not self.license_key:
            raise LicenseError("license_key required for nonlinear evaluation")

        cfg = config.to_dict() if isinstance(config, Config) else config
        cfg = _normalize_config_for_wire(cfg)

        req = {
            "data": _sanitize_record(data),
            "config": cfg,
            "formula_mode": "nonlinear",
            "adjustments": adjustments,
            "tier": self.tier,
            "license_key": self.license_key,
        }
        if adjustment_values is not None:
            req["data"]["adjustments_values"] = adjustment_values

        resp = self._make_request("", req)
        return EvaluationResult.from_response(resp)

    # ---------- Distillation (Professional+) ----------
    def distill_train(self, config: Union[Dict, Config], samples: int = 1000, seed: int = 42,
                      batch_size: Optional[int] = None, adjustments: Optional[Dict] = None) -> DistillationResult:
        if self.tier == 'community':
            raise LicenseError("Distillation requires premium tier")
        if int(samples) > MAX_N_SYNTHETIC:
            raise ValidationError(f"samples too large — max {MAX_N_SYNTHETIC}")

        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        cfg = _normalize_config_for_wire(cfg)
        req = {
            "action": "translate_train",
            "config": cfg,
            "tier": self.tier,
            "license_key": self.license_key,
            "n_synthetic": int(samples),
            "seed": int(seed),
        }
        if batch_size is not None:
            req["batch_size"] = int(batch_size)
        if adjustments:
            req["adjustments"] = adjustments

        resp = self._make_request("", req)
        return DistillationResult.from_train_response(resp)

    def distill_export(self) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Export requires enterprise tier")
        req = {
            "action": "translate_export",
            "tier": self.tier,
            "license_key": self.license_key
        }
        return self._make_request("", req)

    def distill_predict(self, data: Dict[str, Any], config: Union[Dict, Config]) -> float:
        if self.tier == 'community':
            raise LicenseError("Surrogate prediction requires premium tier")

        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        cfg = _normalize_config_for_wire(cfg)
        req = {
            "action": "translate_predict",
            "data": _sanitize_record(data),
            "config": cfg,
            "tier": self.tier,
            "license_key": self.license_key
        }
        resp = self._make_request("", req)
        return float(resp.get("score", 0.0))

    def distill_predict_batch(self, data_batch: List[Dict[str, Any]], config: Union[Dict, Config]) -> List[float]:
        if self.tier == 'community':
            raise LicenseError("Surrogate prediction requires premium tier")
        _ensure_len("data_batch", data_batch, MAX_BATCH_PREDICT)

        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        cfg = _normalize_config_for_wire(cfg)
        req = {
            "action": "translate_predict",
            "data_batch": _sanitize_records(data_batch),
            "config": cfg,
            "tier": self.tier,
            "license_key": self.license_key
        }
        resp = self._make_request("", req)
        return [float(x) for x in resp.get("scores", [])]

    # ---------- Utilidades ----------
    def create_config(self) -> Config:
        return Config()

    def get_metrics(self) -> Optional[Dict]:
        if self.tier == "community":
            return None
        use_config = getattr(self, "_last_config", None)
        if not isinstance(use_config, dict) or not use_config:
            use_config = {"__probe__": {"default": 0, "weight": 1.0, "criticality": 1.0}}

        req = {"data": {}, "config": use_config, "tier": self.tier, "license_key": self.license_key}
        resp = self._make_request("", req)
        return resp.get("metrics")

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

