"""
BLACK VEIL V5 - Model Registry
Centralized registry for all AI models with versioning and metadata
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)


class ModelRegistryEntry:
    """Entry in the model registry."""

    def __init__(
        self,
        name: str,
        version: str,
        model_type: str,
        path: str,
        domain: str,
        status: str = "registered",
        accuracy: Optional[float] = None,
        f1_score: Optional[float] = None,
        training_date: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.version = version
        self.model_type = model_type
        self.path = path
        self.domain = domain
        self.status = status
        self.accuracy = accuracy
        self.f1_score = f1_score
        self.training_date = training_date or datetime.utcnow().isoformat()
        self.parameters = parameters or {}
        self.feature_count: Optional[int] = None
        self.file_hash: Optional[str] = None
        self.is_active: bool = False
        self.created_at: str = datetime.utcnow().isoformat()
        self.updated_at: str = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "model_type": self.model_type,
            "path": self.path,
            "domain": self.domain,
            "status": self.status,
            "accuracy": self.accuracy,
            "f1_score": self.f1_score,
            "training_date": self.training_date,
            "parameters": self.parameters,
            "feature_count": self.feature_count,
            "file_hash": self.file_hash,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelRegistryEntry":
        """Create entry from dictionary."""
        entry = cls(
            name=data["name"],
            version=data["version"],
            model_type=data["model_type"],
            path=data["path"],
            domain=data["domain"],
            status=data.get("status", "registered"),
            accuracy=data.get("accuracy"),
            f1_score=data.get("f1_score"),
            training_date=data.get("training_date"),
            parameters=data.get("parameters"),
        )
        entry.feature_count = data.get("feature_count")
        entry.file_hash = data.get("file_hash")
        entry.is_active = data.get("is_active", False)
        entry.created_at = data.get("created_at", entry.created_at)
        entry.updated_at = data.get("updated_at", entry.created_at)
        return entry


class ModelRegistry:
    """
    Centralized model registry for managing ML models.

    Features:
    - Register models with metadata
    - Track model versions
    - Activate/deactivate models
    - Query models by name, domain, or type
    - Persist registry to disk
    """

    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize registry.

        Args:
            registry_path: Path to persist registry data
        """
        self._entries: Dict[str, ModelRegistryEntry] = {}
        self._registry_path = registry_path
        self._active_models: Dict[str, str] = {}  # model_name -> version

        if registry_path and os.path.exists(registry_path):
            self._load_registry()

    def register(
        self,
        name: str,
        version: str,
        model_type: str,
        path: str,
        domain: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ModelRegistryEntry:
        """Register a model in the registry."""
        entry_key = f"{name}:{version}"

        if entry_key in self._entries:
            raise ValueError(f"Model {name}:{version} already registered")

        entry = ModelRegistryEntry(
            name=name,
            version=version,
            model_type=model_type,
            path=path,
            domain=domain,
            parameters=metadata,
        )

        self._entries[entry_key] = entry
        logger.info(f"Registered model: {name}:{version} ({model_type}) in domain {domain}")

        self._save_registry()
        return entry

    def unregister(self, name: str, version: str) -> None:
        """Unregister a model."""
        entry_key = f"{name}:{version}"
        if entry_key in self._entries:
            del self._entries[entry_key]
            logger.info(f"Unregistered model: {name}:{version}")

            if self._active_models.get(name) == version:
                del self._active_models[name]

            self._save_registry()

    def get_entry(self, name: str, version: str) -> Optional[ModelRegistryEntry]:
        """Get a specific model entry."""
        entry_key = f"{name}:{version}"
        return self._entries.get(entry_key)

    def get_active(self, name: str) -> Optional[ModelRegistryEntry]:
        """Get active version of a model."""
        version = self._active_models.get(name)
        if version:
            return self.get_entry(name, version)
        return None

    def activate(self, name: str, version: str) -> None:
        """Activate a model version."""
        entry_key = f"{name}:{version}"
        if entry_key not in self._entries:
            raise ValueError(f"Model {name}:{version} not found in registry")

        current_active = self._active_models.get(name)
        if current_active:
            old_entry = self._entries.get(f"{name}:{current_active}")
            if old_entry:
                old_entry.is_active = False

        self._entries[entry_key].is_active = True
        self._active_models[name] = version
        logger.info(f"Activated model: {name}:{version}")

        self._save_registry()

    def list_models(
        self,
        domain: Optional[str] = None,
        model_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[ModelRegistryEntry]:
        """List models, optionally filtered."""
        entries = list(self._entries.values())

        if domain:
            entries = [e for e in entries if e.domain == domain]
        if model_type:
            entries = [e for e in entries if e.model_type == model_type]
        if status:
            entries = [e for e in entries if e.status == status]

        return entries

    def get_versions(self, name: str) -> List[ModelRegistryEntry]:
        """Get all versions of a model."""
        return [entry for entry in self._entries.values() if entry.name == name]

    def update_metrics(
        self,
        name: str,
        version: str,
        accuracy: float,
        f1_score: float,
        **metrics
    ) -> None:
        """Update model performance metrics."""
        entry_key = f"{name}:{version}"
        if entry_key in self._entries:
            entry = self._entries[entry_key]
            entry.accuracy = accuracy
            entry.f1_score = f1_score
            entry.updated_at = datetime.utcnow().isoformat()
            self._save_registry()

    def _save_registry(self) -> None:
        """Persist registry to disk."""
        if not self._registry_path:
            return

        data = {
            "entries": [entry.to_dict() for entry in self._entries.values()],
            "active_models": self._active_models,
            "updated_at": datetime.utcnow().isoformat(),
        }

        os.makedirs(os.path.dirname(self._registry_path) or ".", exist_ok=True)
        with open(self._registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_registry(self) -> None:
        """Load registry from disk."""
        if not self._registry_path or not os.path.exists(self._registry_path):
            return

        try:
            with open(self._registry_path, "r") as f:
                data = json.load(f)

            for entry_data in data.get("entries", []):
                entry = ModelRegistryEntry.from_dict(entry_data)
                entry_key = f"{entry.name}:{entry.version}"
                self._entries[entry_key] = entry

            self._active_models = data.get("active_models", {})
            logger.info(f"Loaded {len(self._entries)} models from registry")
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get registry summary."""
        active_count = sum(1 for e in self._entries.values() if e.is_active)
        by_domain: Dict[str, int] = {}
        by_type: Dict[str, int] = {}

        for entry in self._entries.values():
            by_domain[entry.domain] = by_domain.get(entry.domain, 0) + 1
            by_type[entry.model_type] = by_type.get(entry.model_type, 0) + 1

        return {
            "total_models": len(self._entries),
            "active_models": active_count,
            "unique_models": len(set(e.name for e in self._entries.values())),
            "by_domain": by_domain,
            "by_type": by_type,
            "updated_at": datetime.utcnow().isoformat(),
        }

    def clear(self) -> None:
        """Clear all registry entries."""
        self._entries.clear()
        self._active_models.clear()
        self._save_registry()
        logger.info("Registry cleared")


# Singleton instance
model_registry = ModelRegistry()
