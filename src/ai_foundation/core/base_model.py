"""
BLACK VEIL V5 - Base Model Interface
Abstract base class for all AI models in the foundation layer
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union
import numpy as np
import torch
from enum import Enum


class ModelStatus(str, Enum):
    """Model lifecycle status"""
    INITIALIZED = "initialized"
    TRAINING = "training"
    TRAINED = "trained"
    EVALUATING = "evaluating"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass
class ModelPrediction:
    """Container for model prediction results"""
    value: Any
    confidence: float
    model_name: str
    model_version: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    feature_importance: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_output: Any = None
    processing_time_ms: float = 0.0
    input_hash: Optional[str] = None


@dataclass
class TrainingMetrics:
    """Container for training metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    loss: float
    training_time: float
    epochs_completed: int
    validation_metrics: Dict[str, float] = field(default_factory=dict)
    training_samples: int = 0
    validation_samples: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ModelConfig:
    """Model configuration container"""
    name: str
    version: str
    model_type: str
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    parameters: Dict[str, Any]
    device: str = "cpu"
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 100
    validation_split: float = 0.2
    early_stopping_patience: int = 10


class BaseSecurityModel(ABC):
    """
    Abstract base class for all security models in BLACK VEIL.

    All model implementations must inherit from this class and implement
    all abstract methods. This ensures consistency across the AI foundation.

    Features:
    - Device-aware computation (CPU, CUDA, MPS)
    - Configuration validation
    - Input validation
    - Status tracking
    - Training metrics tracking
    - Feature importance computation
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the model with configuration.

        Args:
            config: Model configuration dictionary

        Raises:
            ValueError: If required config fields are missing
        """
        self.config = config
        self._model_config = self._parse_config(config)
        self.model = None
        self.device = self._get_device()
        self.is_trained = False
        self.training_metrics: Optional[TrainingMetrics] = None
        self.model_version: str = config.get("version", "1.0.0")
        self.created_at: datetime = datetime.utcnow()
        self.status = ModelStatus.INITIALIZED
        self._feature_importances: Dict[str, float] = {}

    @abstractmethod
    def build_model(self) -> None:
        """
        Build the model architecture.

        This method should construct the model layers and prepare it for
        training/inference. Called during initialization or when architecture
        changes dynamically.
        """
        pass

    @abstractmethod
    async def train(self, data: Dict[str, Any]) -> TrainingMetrics:
        """
        Train the model with the provided data.

        Args:
            data: Dictionary containing training data with keys:
                - X_train: Training features
                - y_train: Training labels
                - X_val: Optional validation features
                - y_val: Optional validation labels

        Returns:
            TrainingMetrics: Training results and metrics
        """
        pass

    @abstractmethod
    async def predict(self, input_data: Dict[str, Any]) -> ModelPrediction:
        """
        Make a prediction on the input data.

        Args:
            input_data: Dictionary containing input data

        Returns:
            ModelPrediction: Prediction results with confidence
        """
        pass

    @abstractmethod
    async def predict_batch(self, batch_data: List[Dict[str, Any]]) -> List[ModelPrediction]:
        """
        Make predictions on a batch of inputs.

        Args:
            batch_data: List of input dictionaries

        Returns:
            List[ModelPrediction]: List of prediction results
        """
        pass

    @abstractmethod
    def calculate_confidence(self, raw_output: Any) -> float:
        """
        Calculate confidence score from raw model output.

        Args:
            raw_output: Raw model output

        Returns:
            float: Confidence score in [0, 1]
        """
        pass

    @abstractmethod
    def get_feature_importance(self, input_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Get feature importance scores for the prediction.

        Args:
            input_data: Input data

        Returns:
            Dict[str, float]: Feature importance mapping
        """
        pass

    @abstractmethod
    async def evaluate(self, test_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Evaluate model performance on test data.

        Args:
            test_data: Test dataset with X_test and y_test

        Returns:
            Dict[str, float]: Evaluation metrics
        """
        pass

    @abstractmethod
    async def save(self, path: str) -> None:
        """
        Save model to disk.

        Args:
            path: Path to save the model
        """
        pass

    @abstractmethod
    async def load(self, path: str) -> None:
        """
        Load model from disk.

        Args:
            path: Path to load the model from
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.

        Returns:
            Dict[str, Any]: Model metadata
        """
        pass

    def _get_device(self) -> str:
        """
        Get the optimal device for model computation.

        Returns:
            str: Device identifier ('cuda', 'mps', or 'cpu')
        """
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch, "mps") and torch.mps.is_available():
            return "mps"
        return "cpu"

    def _parse_config(self, config: Dict[str, Any]) -> ModelConfig:
        """Parse and validate configuration."""
        required_fields = ["name", "version", "model_type"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required config field: {field}")

        return ModelConfig(
            name=config["name"],
            version=config["version"],
            model_type=config["model_type"],
            input_shape=tuple(config.get("input_shape", (1,))),
            output_shape=tuple(config.get("output_shape", (1,))),
            parameters=config.get("parameters", {}),
            device=config.get("device", self._get_device()),
            batch_size=config.get("batch_size", 32),
            learning_rate=config.get("learning_rate", 0.001),
            epochs=config.get("epochs", 100),
            validation_split=config.get("validation_split", 0.2),
            early_stopping_patience=config.get("early_stopping_patience", 10),
        )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data structure.

        Args:
            input_data: Input data to validate

        Returns:
            bool: True if valid, raises ValueError otherwise
        """
        required_fields = self.config.get("required_input_fields", [])
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")

        for key, value in input_data.items():
            expected_type = self.config.get("field_types", {}).get(key)
            if expected_type and not isinstance(value, expected_type):
                raise ValueError(
                    f"Field '{key}' expected type {expected_type}, got {type(value)}"
                )

        return True

    def log_prediction(self, prediction: ModelPrediction) -> None:
        """Log prediction for audit trail."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Prediction: model={prediction.model_name}, "
            f"value={prediction.value}, confidence={prediction.confidence:.4f}, "
            f"latency_ms={prediction.processing_time_ms:.2f}"
        )

    def update_status(self, status: ModelStatus) -> None:
        """Update model status."""
        self.status = status
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Model {self.config.get('name', 'unknown')} status: {status.value}")
