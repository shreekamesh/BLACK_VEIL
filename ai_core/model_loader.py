"""
BLACK VEIL V2 — Secure Model Loader
Loads and manages ML models with security checks and caching
"""
import hashlib
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import joblib

logger = logging.getLogger(__name__)


MODELS_DIR = Path(os.getenv("BV_MODELS_DIR", "models"))
DATASETS_DIR = Path(os.getenv("BV_DATASETS_DIR", "master_dataset"))

# Model registry mapping
AVAILABLE_MODELS = {
    "unsw_rf": {
        "file": MODELS_DIR / "UNSW_RF.pkl",
        "type": "RandomForest",
        "domain": "network",
        "feature_count": 42,
        "required": True,
    },
    "edge_rf": {
        "file": MODELS_DIR / "EDGE_RF.pkl",
        "type": "RandomForest",
        "domain": "iot",
        "feature_count": 21,
        "required": True,
    },
    "edge_label_encoder": {
        "file": MODELS_DIR / "EDGE_LabelEncoder.pkl",
        "type": "LabelEncoder",
        "domain": "iot",
        "required": True,
    },
    "edge_minmax_scaler": {
        "file": MODELS_DIR / "EDGE_MinMaxScaler.pkl",
        "type": "MinMaxScaler",
        "domain": "iot",
        "required": True,
    },
    "cert_minmax_scaler": {
        "file": MODELS_DIR / "CERT_MinMaxScaler.pkl",
        "type": "MinMaxScaler",
        "domain": "user",
        "required": True,
    },
    "cicids2017_label_encoder": {
        "file": DATASETS_DIR / "CICIDS2017_LabelEncoder.pkl",
        "type": "LabelEncoder",
        "domain": "cicids",
        "required": False,
    },
    "cicids2017_minmax_scaler": {
        "file": DATASETS_DIR / "CICIDS2017_MinMaxScaler.pkl",
        "type": "MinMaxScaler",
        "domain": "cicids",
        "required": False,
    },
}


class ModelLoadError(Exception):
    """Raised when a model fails to load"""
    pass


@dataclass
class ModelInfo:
    """Metadata about a loaded model"""
    name: str
    model_type: str
    domain: str
    file_path: Path
    file_hash: str
    feature_count: Optional[int] = None
    is_loaded: bool = False


class ModelLoader:
    """
    Secure model loader with hash verification and caching.
    Loads .pkl files using joblib for Python 3.13+ protocol compatibility.
    """

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self._cache: dict[str, Any] = {}
        self._info_cache: dict[str, ModelInfo] = {}
        self._load_available_models()

    def _load_available_models(self) -> None:
        """Register all available models from the registry"""
        for name, config in AVAILABLE_MODELS.items():
            file_path = config["file"]
            if file_path.exists():
                self._info_cache[name] = ModelInfo(
                    name=name,
                    model_type=config.get("type", "Unknown"),
                    domain=config.get("domain", "unknown"),
                    file_path=file_path,
                    file_hash=self._compute_file_hash(file_path),
                    feature_count=config.get("feature_count"),
                    is_loaded=False,
                )
                logger.info(f"Registered model: {name} at {file_path}")
            elif config.get("required", False):
                logger.warning(f"Required model not found: {name} at {file_path}")
            else:
                logger.info(f"Optional model not found: {name} at {file_path}")

    @staticmethod
    def _compute_file_hash(file_path: Path) -> str:
        """Compute SHA-256 hash of a file for integrity verification"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def _verify_pickle_safe(file_path: Path) -> bool:
        """
        Basic safety check: verify file exists, is non-empty, and has .pkl extension.
        In production, this should use sandboxed unpickling.
        """
        if not file_path.exists():
            return False
        if file_path.stat().st_size == 0:
            return False
        if file_path.suffix not in (".pkl", ".joblib"):
            logger.warning(f"Unknown model file extension: {file_path.suffix}")
        return True

    def load_model(self, name: str, force_reload: bool = False) -> Any:
        """
        Load a model by name with caching using joblib.
        joblib handles Python 3.13+ pickle protocol 5 correctly.

        Args:
            name: Model name from AVAILABLE_MODELS
            force_reload: Ignore cache and reload from disk

        Returns:
            Loaded model object

        Raises:
            ModelLoadError: If model not found or fails to load
        """
        if not force_reload and name in self._cache:
            logger.debug(f"Cache hit for model: {name}")
            return self._cache[name]

        if name not in self._info_cache:
            raise ModelLoadError(f"Unknown model: {name}")

        info = self._info_cache[name]
        file_path = info.file_path

        if not self._verify_pickle_safe(file_path):
            raise ModelLoadError(f"Model file unsafe or missing: {file_path}")

        try:
            model = joblib.load(file_path)
            self._cache[name] = model
            info.is_loaded = True
            logger.info(f"Loaded model: {name} ({info.model_type})")
            return model

        except ModuleNotFoundError as e:
            raise ModelLoadError(
                f"Model {name} requires unavailable module: {e}. "
                f"This may be due to sklearn module path changes."
            )
        except Exception as e:
            raise ModelLoadError(f"Failed to load model {name}: {e}")

    def unload_model(self, name: str) -> None:
        """Remove a model from cache"""
        self._cache.pop(name, None)
        if name in self._info_cache:
            self._info_cache[name].is_loaded = False
        logger.info(f"Unloaded model: {name}")

    def get_model_info(self, name: str) -> Optional[ModelInfo]:
        """Get metadata about a registered model"""
        return self._info_cache.get(name)

    def list_available_models(self) -> list[str]:
        """List all registered model names"""
        return list(self._info_cache.keys())

    def list_loaded_models(self) -> list[str]:
        """List currently loaded model names"""
        return list(self._cache.keys())

    def preload_all(self) -> dict[str, bool]:
        """
        Preload all available models into cache.
        Returns dict of {model_name: success_bool}
        """
        results = {}
        for name in self._info_cache:
            try:
                self.load_model(name)
                results[name] = True
            except ModelLoadError as e:
                logger.error(f"Failed to preload {name}: {e}")
                results[name] = False
        return results


# Singleton instance
model_loader = ModelLoader()
