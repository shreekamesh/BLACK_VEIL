"""
BLACK VEIL V5 - Model Manager
Manages model lifecycle, training, evaluation, and deployment
"""
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging
import asyncio
from pathlib import Path

from src.ai_foundation.core.base_model import (
    BaseSecurityModel, ModelPrediction, TrainingMetrics, ModelStatus
)
from src.ai_foundation.core.model_registry import model_registry, ModelRegistryEntry

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages the lifecycle of ML models in BLACK VEIL.

    Features:
    - Model loading and unloading
    - Training orchestration
    - Evaluation and benchmarking
    - Deployment management
    - Model versioning
    - Resource management
    """

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self._loaded_models: Dict[str, BaseSecurityModel] = {}
        self._training_tasks: Dict[str, asyncio.Task] = {}
        self._model_factories: Dict[str, Callable[[Dict[str, Any]], BaseSecurityModel]] = {}

    def register_factory(
        self,
        model_type: str,
        factory: Callable[[Dict[str, Any]], BaseSecurityModel]
    ) -> None:
        """Register a model factory for creating model instances."""
        self._model_factories[model_type] = factory
        logger.info(f"Registered model factory: {model_type}")

    async def create_model(
        self,
        model_type: str,
        config: Dict[str, Any],
        register: bool = True
    ) -> BaseSecurityModel:
        """Create a model instance from factory."""
        if model_type not in self._model_factories:
            raise ValueError(f"Unknown model type: {model_type}. Available: {list(self._model_factories.keys())}")

        model = self._model_factories[model_type](config)
        await model.build_model()

        if register:
            model_registry.register(
                name=config.get("name", f"{model_type}_model"),
                version=config.get("version", "1.0.0"),
                model_type=model_type,
                path=str(self.models_dir / config.get("name", "model")),
                domain=config.get("domain", "general"),
                metadata=config,
            )

        return model

    async def load_model(
        self,
        name: str,
        version: Optional[str] = None,
        force_reload: bool = False
    ) -> BaseSecurityModel:
        """Load a model from the registry."""
        if not force_reload and name in self._loaded_models:
            logger.debug(f"Model already loaded: {name}")
            return self._loaded_models[name]

        if version:
            entry = model_registry.get_entry(name, version)
        else:
            entry = model_registry.get_active(name)

        if not entry:
            raise ValueError(f"Model {name}:{version or 'active'} not found in registry")

        if entry.model_type not in self._model_factories:
            raise ValueError(f"No factory for model type: {entry.model_type}")

        config = {
            "name": entry.name,
            "version": entry.version,
            "model_type": entry.model_type,
            "domain": entry.domain,
            **entry.parameters,
        }

        model = self._model_factories[entry.model_type](config)
        await model.load(entry.path)
        self._loaded_models[name] = model

        logger.info(f"Loaded model: {name}:{entry.version}")
        return model

    def unload_model(self, name: str) -> None:
        """Unload a model from memory."""
        if name in self._loaded_models:
            del self._loaded_models[name]
            logger.info(f"Unloaded model: {name}")

    async def train_model(
        self,
        name: str,
        data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> TrainingMetrics:
        """Train a loaded model."""
        if name not in self._loaded_models:
            raise ValueError(f"Model not loaded: {name}. Call load_model() first.")

        model = self._loaded_models[name]
        task = asyncio.create_task(model.train(data))
        self._training_tasks[name] = task

        try:
            metrics = await task
            logger.info(f"Training completed for {name}: accuracy={metrics.accuracy:.4f}")

            model_registry.update_metrics(
                name=name,
                version=model.model_version,
                accuracy=metrics.accuracy,
                f1_score=metrics.f1_score,
            )

            return metrics
        except Exception as e:
            logger.error(f"Training failed for {name}: {e}")
            raise
        finally:
            self._training_tasks.pop(name, None)

    async def predict(
        self,
        name: str,
        input_data: Dict[str, Any]
    ) -> ModelPrediction:
        """Run prediction with a loaded model."""
        if name not in self._loaded_models:
            await self.load_model(name)

        model = self._loaded_models[name]
        return await model.predict(input_data)

    async def predict_batch(
        self,
        name: str,
        batch_data: List[Dict[str, Any]]
    ) -> List[ModelPrediction]:
        """Run batch prediction."""
        if name not in self._loaded_models:
            await self.load_model(name)

        model = self._loaded_models[name]
        return await model.predict_batch(batch_data)

    async def evaluate_model(
        self,
        name: str,
        test_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Evaluate a loaded model."""
        if name not in self._loaded_models:
            raise ValueError(f"Model not loaded: {name}")

        model = self._loaded_models[name]
        metrics = await model.evaluate(test_data)
        logger.info(f"Evaluation for {name}: {metrics}")
        return metrics

    def get_model(self, name: str) -> Optional[BaseSecurityModel]:
        """Get a loaded model instance."""
        return self._loaded_models.get(name)

    def get_loaded_models(self) -> List[str]:
        """Get list of loaded model names."""
        return list(self._loaded_models.keys())

    def get_training_status(self, name: str) -> Optional[str]:
        """Get training status of a model."""
        if name in self._training_tasks:
            task = self._training_tasks[name]
            if task.done():
                if task.exception():
                    return "failed"
                return "completed"
            return "training"
        return None

    async def shutdown(self) -> None:
        """Shutdown all models gracefully."""
        for name, model in self._loaded_models.items():
            try:
                path = str(self.models_dir / f"{name}_{model.model_version}.pt")
                await model.save(path)
                logger.info(f"Saved model: {name}")
            except Exception as e:
                logger.error(f"Failed to save model {name}: {e}")

        self._loaded_models.clear()
        self._training_tasks.clear()
        logger.info("Model manager shutdown complete")


# Singleton instance
model_manager = ModelManager()
