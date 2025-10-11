# ============================================
# dsf_aml_sdk/client.py
# ============================================
from . import __version__
from .models import Config, EvaluationResult, DistillationResult
from .exceptions import APIError, LicenseError, ValidationError

import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin
import time
from functools import wraps
import logging
import os

logger = logging.getLogger(__name__)

MAX_N_SYNTHETIC = int(os.getenv("DSF_MAX_N_SYNTHETIC", "10000"))
MAX_PARTIAL_VARIANTS = int(os.getenv("DSF_MAX_PARTIAL_VARIANTS", "5000"))
MAX_DATASET_ITEMS = int(os.getenv("DSF_MAX_DATASET_ITEMS", "10000"))
MAX_BATCH_EVAL = int(os.getenv("DSF_MAX_BATCH_EVAL", "1000"))
MAX_BATCH_PREDICT = int(os.getenv("DSF_MAX_BATCH_PREDICT", "2000"))

def _ensure_len(name: str, seq, max_len: int):
    if isinstance(seq, list) and len(seq) > max_len:
        raise ValidationError(f"{name} too large — max {max_len}")

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
        "https://dsf-jn5hw8jbt-api-dsfuptech.vercel.app/"
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

        # <-- MODIFICADO: La validación ahora depende del nuevo flag 'validate_on_init'
        if validate_on_init and self.tier != "community" and self.license_key:
            self._validate_license()

    def _validate_license(self):
        req = {
            # disparador mínimo válido para handle_evaluate
            "data": {},
            "config": {"__probe__": {"default": 0, "weight": 1.0, "criticality": 1.0}},
            "license_key": self.license_key,
        # no enviar 'action'
        }
        resp = self._make_request("", req)
        if not isinstance(resp, dict):
            raise LicenseError("License validation failed (unexpected response)")
        
    def _ensure_license_if_needed(self):
        if self.tier != "community" and self.license_key:
            try:
                self._validate_license()
            except Exception:
                # No bloquees; el backend ya hará enforcement y devolverá 403 si aplica
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

            # <-- INICIO DEL BLOQUE REEMPLAZADO
            # Nuevo tratamiento homogéneo para errores 4xx/5xx con o sin cuerpo JSON
            try:
                j = response.json()
            except Exception:
                # Si el parseo JSON falla, se crea un diccionario de error por defecto
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
            # <-- FIN DEL BLOQUE REEMPLAZADO

        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    # ------------------- Core -------------------

    def get_version_info(self) -> Dict:
        """
        Obtiene la información de la versión y los handlers disponibles del backend.
        """
        req = {"action": "__version__"}
        return self._make_request("", req)

    def evaluate(self, data: Dict[str, Any], config: Optional[Union[Dict, Config]] = None) -> EvaluationResult:
        """Evaluación estándar (community+)."""
        if isinstance(config, Config):
            config = config.to_dict()
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")

        self._last_config = (config or {})

        request_data = {"data": data, "config": config or {}, "tier": self.tier}
        if self.license_key:
            request_data["license_key"] = self.license_key

        response = self._make_request("", request_data)
        return EvaluationResult.from_response(response)

    def batch_evaluate(self, data_points: List[Dict], config: Optional[Union[Dict, Config]] = None) -> List[EvaluationResult]:
        if self.tier == "community":
            raise LicenseError("Batch evaluation requires premium tier")
        _ensure_len("data_points", data_points, MAX_BATCH_EVAL)

        if config:
            self._last_config = config.to_dict() if isinstance(config, Config) else config
        use_config = self._last_config or {}
        if isinstance(use_config, Config):
            use_config = use_config.to_dict()

        request = {
            "action": "evaluate_batch",
            "tier": self.tier,
            "license_key": self.license_key,
            "config": use_config,
            "data_points": data_points,
        }

        try:
            resp = self._make_request("", request)
            # Normaliza formatos
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
        

    def bootstrap_config(self, config: Union[Dict, Config]) -> Dict:
        """Bootstrap/validate config (now public for all tiers)"""
        if isinstance(config, Config):
            config = config.to_dict()
        req = {
            'action': 'bootstrap_config',
            'config': config,
            'license_key': self.license_key,
        }
        return self._make_request('', req)


    # ------------------- Pipeline -------------------

    def pipeline_identify_seeds(self, dataset: List[Dict], config: Union[Dict, Config],
                                top_k_percent: float = 0.1, **kwargs) -> Dict:
        request_data = {
            "action": "pipeline_identify_seeds",
            "dataset": dataset,
            "config": config,
            "top_k_percent": top_k_percent,
            "license_key": self.license_key,
            **kwargs
        }
        return self._make_request("", request_data)

    def pipeline_generate_critical(self, config, seeds=None, advanced=None, **kwargs):
        if self.tier == 'community':
            raise LicenseError("Pipeline requires premium tier")

        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        request_data = {
            'action': 'pipeline_generate_critical',
            'config': cfg,
            'license_key': self.license_key,
        }

    # Auto-seeds si no las pasan pero sí hay dataset original
        original_ds = kwargs.get('original_dataset')
        if seeds is None and original_ds:
        # usa top_k_percent opcional si lo pasaron
            tkp = kwargs.get('top_k_percent', 0.1)
            sresp = self.pipeline_identify_seeds(dataset=original_ds, config=cfg, top_k_percent=tkp)
            seeds = [s.get('data', s) for s in (sresp.get('seeds') or [])]

        if seeds:
            request_data['seeds'] = seeds

    # Hyperparámetros prudentes por defecto (anti-timeout)
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
        
        self._ensure_license_if_needed() # <-- AÑADIDO
        
        _ensure_len("dataset", dataset, MAX_DATASET_ITEMS)

        if isinstance(config, Config):
            config = config.to_dict()

        request_data = {
            "action": "pipeline_full_cycle",
            "dataset": dataset,
            "config": config,
            "max_iterations": max_iterations,
            "license_key": self.license_key,
            **kwargs
        }
        return self._make_request("", request_data)

    # ------------------- Curriculum (Enterprise) -------------------

    def curriculum_init(self, dataset: List[Dict], config: Union[Dict, Config], **params) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Curriculum requires enterprise tier")
        if isinstance(config, Config):
            config = config.to_dict()
        request_data = {
            "action": "curriculum_init",
            "dataset": dataset,
            "config": config,
            "license_key": self.license_key,
            **params
        }
        return self._make_request("", request_data)

    def curriculum_step(self, dataset: List[Dict], config: Union[Dict, Config],
                        precomputed_metrics: Optional[Dict] = None) -> Dict:
        if self.tier != "enterprise":
            raise LicenseError("Curriculum requires enterprise tier")
        if isinstance(config, Config):
            config = config.to_dict()
        request_data = {
            "action": "curriculum_step",
            "dataset": dataset,
            "config": config,
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
        """Evalúa con modo no lineal (Professional/Enterprise)."""
        if self.tier == "community":
            raise LicenseError("Nonlinear evaluation requires premium tier")
        if not self.license_key:
            raise LicenseError("license_key required for nonlinear evaluation")

        if isinstance(config, Config):
            config = config.to_dict()

        req = {
            "data": data,
            "config": config,
            "formula_mode": "nonlinear",
            "adjustments": adjustments,
            "tier": self.tier,
            "license_key": self.license_key,  # <-- agregado
        }
        if adjustment_values is not None:
            av = adjustment_values
            if isinstance(av, dict) and av and not any(isinstance(v, dict) for v in av.values()):
                req["data"]["adjustments_values"] = {k: dict(av) for k in config.keys()}
            else:
                req["data"]["adjustments_values"] = av

    # ------------------- Distillation (Professional+) -------------------

    def distill_train(self, config: Union[Dict, Config], samples: int = 1000, seed: int = 42, batch_size: Optional[int] = None, adjustments: Optional[Dict] = None) -> DistillationResult:
        if self.tier == 'community':
            raise LicenseError("Distillation requires premium tier")
        if int(samples) > MAX_N_SYNTHETIC:
            raise ValidationError(f"samples too large — max {MAX_N_SYNTHETIC}")
    
        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        req = {
            'action': 'translate_train',
            'config': cfg,
            'tier': self.tier,
            'license_key': self.license_key,
        # nombres esperados por el handler
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
        """Fast prediction using surrogate model (Premium)"""
        if self.tier == 'community':
            raise LicenseError("Surrogate prediction requires premium tier")
    
        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        req = {
            'action': 'translate_predict',
            'data': data,
            'config': cfg,
            'tier': self.tier,
            'license_key': self.license_key
        }
        resp = self._make_request('', req)
    # el backend devuelve 'score' (no 'score_surrogate')
        return float(resp.get('score', 0.0))

    
    def distill_predict_batch(self, data_batch: List[Dict[str, Any]], config: Union[Dict, Config]) -> List[float]:
        if self.tier == 'community':
            raise LicenseError("Surrogate prediction requires premium tier")
        _ensure_len("data_batch", data_batch, MAX_BATCH_PREDICT)
        
        cfg = config.to_dict() if hasattr(config, "to_dict") else config
        req = {
            'action': 'translate_predict',
            'data_batch': data_batch,
            'config': cfg,
            'tier': self.tier,
            'license_key': self.license_key
        }
        resp = self._make_request('', req)
        return [float(x) for x in resp.get('scores', [])]


    # ------------------- Utilidades -------------------

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

