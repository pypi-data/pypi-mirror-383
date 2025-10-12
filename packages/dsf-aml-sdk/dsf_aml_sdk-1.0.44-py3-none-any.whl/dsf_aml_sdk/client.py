# ============================================
# dsf_aml_sdk/client.py
# ============================================
from . import __version__
from .models import Config, EvaluationResult, DistillationResult
from .exceptions import APIError, LicenseError, ValidationError

import requests
from typing import Dict, List, Optional, Union, Any, Iterable, Tuple, Callable
from urllib.parse import urljoin
import time
from functools import wraps
import logging
import os
import math
import statistics

logger = logging.getLogger(__name__)

# Límites (overridables por env)
MAX_N_SYNTHETIC = int(os.getenv("DSF_MAX_N_SYNTHETIC", "10000"))
MAX_PARTIAL_VARIANTS = int(os.getenv("DSF_MAX_PARTIAL_VARIANTS", "5000"))
MAX_DATASET_ITEMS = int(os.getenv("DSF_MAX_DATASET_ITEMS", "10000"))
MAX_BATCH_EVAL = int(os.getenv("DSF_MAX_BATCH_EVAL", "1000"))
MAX_BATCH_PREDICT = int(os.getenv("DSF_MAX_BATCH_PREDICT", "2000"))

# Cap “seguro” para evitar 413 por bytes aunque estés en 10K filas
DEFAULT_TARGET_CAP = int(os.getenv("DSF_TARGET_CAP", "9500"))

def _ensure_len(name: str, seq, max_len: int):
    if isinstance(seq, list) and len(seq) > max_len:
        raise ValidationError(f"{name} too large — max {max_len}")

def _normalize_config_for_wire(cfg: Dict[str, Any]) -> Dict[str, Any]:
    # Orden determinístico shallow; el backend igual hace canonicalización.
    if not isinstance(cfg, dict):
        return {}
    return {k: cfg[k] for k in sorted(cfg.keys())}

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

def _is_primitive(x: Any) -> bool:
    return isinstance(x, (int, float, str, bool)) or x is None

def _to_primitive(x: Any) -> Any:
    # Convierte numpy/pandas y anidados simples a primitivos JSON‐safe
    try:
        import numpy as np  # opcional
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, (np.floating,)):
            xf = float(x)
            # NaN/Inf → None
            if math.isnan(xf) or math.isinf(xf):
                return None
            return xf
        if isinstance(x, (np.bool_,)):
            return bool(x)
        if hasattr(x, "item"):
            try:
                v = x.item()
                return _to_primitive(v)
            except Exception:
                pass
    except Exception:
        pass
    if isinstance(x, (list, tuple)):
        return [_to_primitive(v) for v in x]
    if isinstance(x, dict):
        return {str(k): _to_primitive(v) for k, v in x.items()}
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    if _is_primitive(x):
        return x
    # Fallback segura
    return str(x)

def _sanitize_record(rec: Dict[str, Any], allowed_fields: Iterable[str]) -> Dict[str, Any]:
    out = {}
    for k in allowed_fields:
        v = rec.get(k, None)
        v = _to_primitive(v)
        out[k] = v
    return out

def _safe_median(values: List[float]) -> float:
    if not values:
        return 0.0
    try:
        return float(statistics.median(values))
    except Exception:
        # Fallback simple
        vs = sorted(values)
        n = len(vs)
        mid = n // 2
        if n % 2:
            return float(vs[mid])
        return float((vs[mid - 1] + vs[mid]) / 2.0)

def _argsort_abs_distance(values: List[float], target: float) -> List[int]:
    # Devuelve índices ordenados por |value - target|
    return sorted(range(len(values)), key=lambda i: abs(values[i] - target))

class AMLSDK:
    BASE_URL = os.environ.get(
        "DSF_AML_BASE_URL",
        "https://dsf-gwx2hvg0t-api-dsfuptech.vercel.app/"
    )
    TIERS = {"community", "professional", "enterprise"}

    def __init__(self, license_key: Optional[str] = None, tier: str = "community",
                 base_url: Optional[str] = None, timeout: int = 30, verify_ssl: bool = True,
                 validate_on_init: bool = False):  # <-- NUEVO
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

        # Validación opcional proactiva
        if validate_on_init and self.tier != "community" and self.license_key:
            self._validate_license()

        # cache de última config usada (para get_metrics, etc.)
        self._last_config: Optional[Dict[str, Any]] = None

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

            # Manejo homogéneo de errores
            try:
                j = response.json()
            except Exception:
                j = {"error": f"Server error {response.status_code}", "detail": response.text[:200]}

            if response.status_code == 403:
                raise LicenseError(j.get("error", "License error"))

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60") or "60")
                raise APIError(f"Rate limited. Retry after {retry_after}s", status_code=429)

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

    # ------------------- Core -------------------

    def get_version_info(self) -> Dict:
        """Obtiene la info de versión/handlers del backend."""
        req = {"action": "__version__"}
        return self._make_request("", req)

    def evaluate(self, data: Dict[str, Any], config: Optional[Union[Dict, Config]] = None) -> EvaluationResult:
        """Evaluación estándar (community+)."""
        if isinstance(config, Config):
            config = config.to_dict()
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")

        config = _normalize_config_for_wire(config or {})
        self._last_config = config

        request_data = {"data": data, "config": config, "tier": self.tier}
        if self.license_key:
            request_data["license_key"] = self.license_key

        response = self._make_request("", request_data)
        return EvaluationResult.from_response(response)

    def batch_evaluate(self, data_points: List[Dict], config: Optional[Union[Dict, Config]] = None) -> List[EvaluationResult]:
        """Evalúa en batch (Professional/Enterprise). Máx 1000 items/call."""
        if self.tier == "community":
            raise LicenseError("Batch evaluation requires premium tier")
        _ensure_len("data_points", data_points, MAX_BATCH_EVAL)

        if config:
            self._last_config = config.to_dict() if isinstance(config, Config) else config
        use_config = self._last_config or {}
        if isinstance(use_config, Config):
            use_config = use_config.to_dict()
        use_config = _normalize_config_for_wire(use_config)

        request = {
            "action": "evaluate_batch",
            "tier": self.tier,
            "license_key": self.license_key,
            "config": use_config,
            "data_points": data_points,
        }

        try:
            resp = self._make_request("", request)
            # Normaliza formatos de respuesta
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
            # Fallback cliente (mantiene contrato)
            return [self.evaluate(dp, use_config) for dp in data_points]

    # ------------------- Utilidades privadas (chunk + selección + saneo) -------------------

    def _chunked_batch_evaluate(
        self,
        data_points: List[Dict[str, Any]],
        config: Union[Dict, Config],
        chunk_size: int = MAX_BATCH_EVAL,
        progress: Optional[Callable[[int, int], None]] = None,
    ) -> List[float]:
        """Evalúa N items en chunks (≤MAX_BATCH_EVAL) y devuelve scores (floats)."""
        cfg = config.to_dict() if isinstance(config, Config) else config
        cfg = _normalize_config_for_wire(cfg)
        all_scores: List[float] = []
        n = len(data_points)
        for i in range(0, n, max(1, min(chunk_size, MAX_BATCH_EVAL))):
            chunk = data_points[i:i+max(1, min(chunk_size, MAX_BATCH_EVAL))]
            results = self.batch_evaluate(chunk, cfg)
            all_scores.extend([r.score for r in results])
            if progress:
                progress(min(i + len(chunk), n), n)
        return all_scores

    def _select_near_threshold(
        self,
        scores: List[float],
        target_cap: int,
        selection_mode: str = "median",
        top_k_percent: Optional[float] = None,
    ) -> List[int]:
        """
        Selección GLOBAL near-threshold:
          - selection_mode="median" → distancia a mediana (default).
          - Si top_k_percent está definido, ignora target_cap y usa ese %.
        Devuelve índices seleccionados.
        """
        if not scores:
            return []
        if top_k_percent is not None:
            k = max(1, int(len(scores) * float(top_k_percent)))
        else:
            k = max(1, min(int(target_cap), len(scores)))

        if selection_mode == "median":
            thr = _safe_median(scores)
        else:
            # futuro: percentil, umbral explícito, etc.
            thr = _safe_median(scores)
        order = _argsort_abs_distance(scores, thr)
        return order[:k]

    def _sanitize_dataset_for_config(self, dataset: List[Dict[str, Any]], config: Union[Dict, Config]) -> List[Dict[str, Any]]:
        cfg = config.to_dict() if isinstance(config, Config) else config
        fields = list(cfg.keys())
        return [_sanitize_record(rec, fields) for rec in dataset]

    # ------------------- Orquestación “auto” (sin tocar API) -------------------

    def full_cycle_auto(
        self,
        dataset: List[Dict[str, Any]],
        config: Union[Dict, Config],
        *,
        target_cap: int = DEFAULT_TARGET_CAP,
        selection_mode: str = "median",
        top_k_percent: Optional[float] = None,
        pre_score_chunk: int = MAX_BATCH_EVAL,
        max_iterations: int = 3,
        # knobs que se pasan directo a pipeline_full_cycle:
        top_k_percent_pipeline: float = 0.50,
        k_variants: int = 12,
        epsilon: float = 0.20,
        diversity_threshold: float = 0.85,
        non_critical_ratio: float = 0.40,
        advanced: Optional[Dict[str, Any]] = None,
        vectors_for_dedup: Optional[List] = None,
        progress: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        retries_on_413: int = 2,
    ) -> Dict:
        """
        Orquesta: pre-scoring chunked → selección global near-threshold → saneo → pipeline_full_cycle.
        Evita 413 (≤10K filas) y conserva la calidad de selección.
        """
        if self.tier != "enterprise":
            raise LicenseError("full_cycle_auto requires enterprise tier")

        if not isinstance(dataset, list) or not dataset:
            raise ValidationError("dataset must be a non-empty list")

        # 1) Pre-scoring con chunking
        if progress: progress("prescoring_start", {"size": len(dataset)})
        scores = self._chunked_batch_evaluate(
            dataset, config, chunk_size=pre_score_chunk,
            progress=(lambda done, total: progress("prescoring_progress", {"done": done, "total": total})) if progress else None
        )
        if progress: progress("prescoring_done", {"size": len(scores)})

        # 2) Selección GLOBAL (near-threshold)
        sel_idx = self._select_near_threshold(
            scores, target_cap=target_cap, selection_mode=selection_mode, top_k_percent=top_k_percent
        )
        subset = [dataset[i] for i in sel_idx]
        if progress: progress("selection", {"selected": len(subset), "of": len(dataset)})

        # 3) Saneo estricto a campos de config
        subset_sanitized = self._sanitize_dataset_for_config(subset, config)

        # 4) Llamada a pipeline_full_cycle (con fallback por 413)
        knobs = {
            "max_iterations": max_iterations,
            "top_k_percent": top_k_percent_pipeline,
            "k_variants": k_variants,
            "epsilon": epsilon,
            "diversity_threshold": diversity_threshold,
            "non_critical_ratio": non_critical_ratio,
            "advanced": dict(advanced or {
                "require_middle": False,
                "max_seeds_to_process": 500,
                "step_scale": 0.50,
                "min_step": 0.01,
                "max_retries": 20,
            }),
            "vectors_for_dedup": vectors_for_dedup or [],
        }

        attempt = 0
        cap = len(subset_sanitized)
        last_err: Optional[Exception] = None
        while attempt <= retries_on_413 and cap > 0:
            try:
                if progress: progress("pipeline_call", {"attempt": attempt + 1, "size": cap})
                return self.pipeline_full_cycle(subset_sanitized[:cap], config, **knobs)
            except APIError as e:
                last_err = e
                msg = str(e).lower()
                # Si es 413 por tamaño, baja cap y reintenta
                if "payload too large" in msg or "413" in msg:
                    cap = int(cap * 0.9)  # reduce 10%
                    attempt += 1
                    if progress: progress("pipeline_retry_413", {"new_cap": cap, "attempt": attempt})
                    continue
                # Si no es 413, propaga
                raise
        # Si agotó reintentos 413:
        raise APIError(f"Pipeline failed with 413 even after retries (last cap={cap}).") from last_err

    # ------------------- Pipeline “raw” -------------------

    def pipeline_identify_seeds(self, dataset: List[Dict], config: Union[Dict, Config],
                                top_k_percent: float = 0.1, **kwargs) -> Dict:
        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        cfg = _normalize_config_for_wire(cfg)
        
        request_data = {
            "action": "pipeline_identify_seeds",
            "dataset": dataset,
            "config": cfg,
            "top_k_percent": top_k_percent,
            "license_key": self.license_key,
            **kwargs
        }
        return self._make_request("", request_data)

    def pipeline_generate_critical(self, config, seeds=None, advanced=None, **kwargs):
        if self.tier == 'community':
            raise LicenseError("Pipeline requires premium tier")

        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        cfg = _normalize_config_for_wire(cfg)
        
        request_data = {
            'action': 'pipeline_generate_critical',
            'config': cfg,
            'license_key': self.license_key,
        }

        # Auto-seeds si no las pasan pero sí hay dataset original
        original_ds = kwargs.get('original_dataset')
        if seeds is None and original_ds:
            tkp = kwargs.get('top_k_percent', 0.1)
            sresp = self.pipeline_identify_seeds(dataset=original_ds, config=cfg, top_k_percent=tkp)
            seeds = [s.get('data', s) for s in (sresp.get('seeds') or [])]

        if seeds:
            request_data['seeds'] = seeds

        # Hyperparámetros prudentes por defecto
        adv = dict(advanced or {})
        adv.setdefault('epsilon', 0.08)
        adv.setdefault('diversity_threshold', 0.92)
        adv.setdefault('non_critical_ratio', 0.15)
        adv.setdefault('max_seeds_to_process', 8)
        adv.setdefault('max_retries', 5)
        adv.setdefault('require_middle', False)
        request_data['advanced'] = adv

        # Pasar original_dataset, etc.
        if original_ds:
            request_data['original_dataset'] = original_ds
        if 'k_variants' in kwargs:
            request_data['k_variants'] = kwargs['k_variants']
        if 'vectors_for_dedup' in kwargs:
            request_data['vectors_for_dedup'] = kwargs['vectors_for_dedup']

        return self._make_request('', request_data)

    def pipeline_full_cycle(self, dataset: List[Dict], config: Union[Dict, Config], max_iterations: int = 5, **kwargs) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Full cycle requires enterprise tier")
        
        self._ensure_license_if_needed()
        _ensure_len("dataset", dataset, MAX_DATASET_ITEMS)

        cfg = config.to_dict() if isinstance(config, Config) else config
        cfg = _normalize_config_for_wire(cfg)

        request_data = {
            "action": "pipeline_full_cycle",
            "dataset": dataset,
            "config": cfg,
            "max_iterations": max_iterations,
            "license_key": self.license_key,
            **kwargs
        }
        return self._make_request("", request_data)

    # ------------------- Curriculum (Enterprise) -------------------

    def curriculum_init(self, dataset: List[Dict], config: Union[Dict, Config], **params) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Curriculum requires enterprise tier")
        
        cfg = config.to_dict() if isinstance(config, Config) else config
        cfg = _normalize_config_for_wire(cfg)
        
        request_data = {
            "action": "curriculum_init",
            "dataset": dataset,
            "config": cfg,
            "license_key": self.license_key,
            **params
        }
        return self._make_request("", request_data)

    def curriculum_step(self, dataset: List[Dict], config: Union[Dict, Config],
                        precomputed_metrics: Optional[Dict] = None) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Curriculum requires enterprise tier")
        
        cfg = config.to_dict() if isinstance(config, Config) else config
        cfg = _normalize_config_for_wire(cfg)
        
        request_data = {
            "action": "curriculum_step",
            "dataset": dataset,
            "config": cfg,
            "license_key": self.license_key
        }
        if precomputed_metrics:
            request_data["precomputed_metrics"] = precomputed_metrics
        return self._make_request("", request_data)

    def curriculum_status(self) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Curriculum requires enterprise tier")
        request_data = {
            "action": "curriculum_status",
            "license_key": self.license_key
        }
        return self._make_request("", request_data)

    # ------------------- Fórmula no lineal -------------------

    def evaluate_nonlinear(self, data: Dict, config: Union[Dict, Config],
                           adjustments: Dict[str, float], adjustment_values: Dict = None) -> EvaluationResult:
        """
        Evalúa con modo no lineal (Professional/Enterprise).
        Nota: el backend espera, si se usan, 'adjustments_values' anidado por campo.
        """
        if self.tier == "community":
            raise LicenseError("Nonlinear evaluation requires premium tier")
        if not self.license_key:
            raise LicenseError("license_key required for nonlinear evaluation")

        cfg = config.to_dict() if isinstance(config, Config) else config
        cfg = _normalize_config_for_wire(cfg)

        payload_data = dict(data or {})
        if adjustment_values is not None:
            av = adjustment_values
            # Si vienen como {campo: valor} (flat), expandir por campos
            flat = isinstance(av, dict) and av and not any(isinstance(v, dict) for v in av.values())
            if flat:
                # replica el mismo dict para cada campo de config
                payload_data["adjustments_values"] = {k: dict(av) for k in cfg.keys()}
            else:
                payload_data["adjustments_values"] = av

        req = {
            "data": payload_data,
            "config": cfg,
            "formula_mode": "nonlinear",
            "adjustments": adjustments,
            "tier": self.tier,
            "license_key": self.license_key,
        }
        resp = self._make_request("", req)
        return EvaluationResult.from_response(resp)

    # ------------------- Distillation (Professional+) -------------------

    def distill_train(self, config: Union[Dict, Config], samples: int = 1000, seed: int = 42, batch_size: Optional[int] = None, adjustments: Optional[Dict] = None) -> DistillationResult:
        if self.tier == 'community':
            raise LicenseError("Distillation requires premium tier")
        if int(samples) > MAX_N_SYNTHETIC:
            raise ValidationError(f"samples too large — max {MAX_N_SYNTHETIC}")
    
        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        cfg = _normalize_config_for_wire(cfg)
        
        req = {
            'action': 'translate_train',
            'config': cfg,
            'tier': self.tier,
            'license_key': self.license_key,
            'n_synthetic': int(samples),
            'seed': int(seed),
        }
        if batch_size is not None:
            req['batch_size'] = int(batch_size)
        if adjustments:
            req['adjustments'] = adjustments

        resp = self._make_request('', req)
        return DistillationResult.from_train_response(resp)

    def distill_export(self) -> Dict:
        """Exporta surrogate (Enterprise)."""
        if self.tier != "enterprise":
            raise LicenseError("Export requires enterprise tier")
        req = {
            "action": "translate_export",
            "tier": self.tier,
            "license_key": self.license_key
        }
        return self._make_request("", req)

    def distill_predict(self, data: Dict[str, Any], config: Union[Dict, Config]) -> float:
        """Predicción rápida con surrogate (Premium)."""
        if self.tier == 'community':
            raise LicenseError("Surrogate prediction requires premium tier")
    
        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        cfg = _normalize_config_for_wire(cfg)
        
        req = {
            'action': 'translate_predict',
            'data': data,
            'config': cfg,
            'tier': self.tier,
            'license_key': self.license_key
        }
        resp = self._make_request('', req)
        return float(resp.get('score', 0.0))

    def distill_predict_batch(self, data_batch: List[Dict[str, Any]], config: Union[Dict, Config]) -> List[float]:
        """Predicción rápida batch con surrogate (≤2000 por llamada)."""
        if self.tier == 'community':
            raise LicenseError("Surrogate prediction requires premium tier")
        _ensure_len("data_batch", data_batch, MAX_BATCH_PREDICT)
        
        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        cfg = _normalize_config_for_wire(cfg)
        
        req = {
            'action': 'translate_predict',
            'data_batch': data_batch,
            'config': cfg,
            'tier': self.tier,
            'license_key': self.license_key
        }
        resp = self._make_request('', req)
        return [float(x) for x in resp.get('scores', [])]

    # ------------------- Utilidades públicas -------------------

    def create_config(self) -> Config:
        return Config()

    def get_metrics(self) -> Optional[Dict]:
        """Obtiene métricas de la fórmula (no disponible en community)."""
        if self.tier == "community":
            return None
        use_config = getattr(self, "_last_config", None)
        if use_config is None or not isinstance(use_config, dict) or not use_config:
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

