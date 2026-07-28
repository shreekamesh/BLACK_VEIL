"""
BLACK VEIL V5 - Ensemble Encoder
Multi-model aggregation and weighted encoding for ensemble predictions
"""
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import logging

from src.ai_foundation.core.base_model import ModelPrediction

logger = logging.getLogger(__name__)


@dataclass
class EnsemblePrediction:
    """Result from ensemble encoding."""
    final_prediction: Any
    confidence: float
    agreement: float
    model_votes: Dict[str, Any]
    model_confidences: Dict[str, float]
    weights: Dict[str, float]
    weighted_contributions: Dict[str, float]
    fusion_method: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class EnsembleEncoder:
    """
    Ensemble encoder for combining multiple model predictions.

    Supports multiple fusion strategies:
    - Weighted voting (hard voting)
    - Weighted averaging (soft voting)
    - Stacking (meta-learner)
    - Entropy-based fusion
    - Dynamic weight calibration
    """

    def __init__(self, method: str = "weighted_average"):
        """
        Initialize ensemble encoder.

        Args:
            method: Fusion method
        """
        self.method = method
        self._weights: Dict[str, float] = {}
        self._model_accuracies: Dict[str, float] = {}
        self._calibration_history: List[Dict[str, Any]] = []

    def set_weights(self, weights: Dict[str, float]) -> None:
        """Set fixed weights for models."""
        total = sum(weights.values())
        if total > 0:
            self._weights = {k: v / total for k, v in weights.items()}
        else:
            self._weights = weights

    def update_weights_dynamic(
        self,
        predictions: List[ModelPrediction],
        actual: Any
    ) -> None:
        """Update weights based on recent accuracy."""
        for pred in predictions:
            key = f"{pred.model_name}:{pred.model_version}"
            correct = pred.value == actual
            alpha = 0.1  # learning rate

            current = self._model_accuracies.get(key, 0.5)
            updated = current + alpha * (1.0 if correct else 0.0 - current)
            self._model_accuracies[key] = updated

        # Recompute weights from accuracies
        total_acc = sum(self._model_accuracies.values())
        if total_acc > 0:
            self._weights = {
                k: v / total_acc
                for k, v in self._model_accuracies.items()
            }

        self._calibration_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "weights": self._weights.copy(),
            "accuracies": self._model_accuracies.copy(),
        })

    def fuse_weighted_voting(
        self,
        predictions: List[ModelPrediction]
    ) -> EnsemblePrediction:
        """Weighted hard voting."""
        votes: Dict[Any, float] = {}

        for pred in predictions:
            weight = self._get_weight(pred)
            value = pred.value if not isinstance(pred.value, (list, np.ndarray)) else pred.value[0]
            votes[value] = votes.get(value, 0.0) + weight

        total_weight = sum(votes.values())
        if total_weight > 0:
            normalized = {k: v / total_weight for k, v in votes.items()}
        else:
            normalized = votes

        winner = max(normalized, key=normalized.get)
        confidence = normalized[winner]
        agreement = max(normalized.values()) - sorted(normalized.values())[-2] if len(normalized) > 1 else 1.0

        return EnsemblePrediction(
            final_prediction=winner,
            confidence=confidence,
            agreement=agreement,
            model_votes={p.model_name: p.value for p in predictions},
            model_confidences={p.model_name: p.confidence for p in predictions},
            weights=self._weights.copy(),
            weighted_contributions=normalized,
            fusion_method="weighted_voting",
        )

    def fuse_weighted_average(
        self,
        predictions: List[ModelPrediction]
    ) -> EnsemblePrediction:
        """Weighted soft voting (averaging probabilities)."""
        if not predictions:
            raise ValueError("No predictions to fuse")

        # Check if predictions have probabilities
        has_probs = all(
            hasattr(p, "raw_output") and p.raw_output is not None
            for p in predictions
        )

        if has_probs:
            # Weighted average of probabilities
            avg_probs = None
            total_weight = 0.0

            for pred in predictions:
                weight = self._get_weight(pred)
                probs = np.array(pred.raw_output) if isinstance(pred.raw_output, (list, np.ndarray)) else np.array([pred.raw_output])

                if avg_probs is None:
                    avg_probs = np.zeros_like(probs)

                avg_probs += weight * probs
                total_weight += weight

            if total_weight > 0:
                avg_probs /= total_weight

            final_class = int(np.argmax(avg_probs))
            confidence = float(np.max(avg_probs))
        else:
            # Fall back to confidence-weighted averaging
            weighted_sum = sum(
                self._get_weight(p) * (p.confidence if isinstance(p.value, (int, float)) else 0.5)
                for p in predictions
            )
            total_weight = sum(self._get_weight(p) for p in predictions)
            avg_confidence = weighted_sum / total_weight if total_weight > 0 else 0.5

            # Majority vote for class
            votes: Dict[Any, float] = {}
            for p in predictions:
                weight = self._get_weight(p)
                value = p.value if not isinstance(p.value, (list, np.ndarray)) else p.value[0]
                votes[value] = votes.get(value, 0.0) + weight

            final_class = max(votes, key=votes.get)
            confidence = avg_confidence

        # Calculate agreement
        values = [str(p.value) for p in predictions]
        unique, counts = np.unique(values, return_counts=True)
        agreement = float(max(counts) / len(values))

        return EnsemblePrediction(
            final_prediction=final_class,
            confidence=confidence,
            agreement=agreement,
            model_votes={p.model_name: p.value for p in predictions},
            model_confidences={p.model_name: p.confidence for p in predictions},
            weights=self._weights.copy(),
            weighted_contributions={
                p.model_name: self._get_weight(p) * p.confidence
                for p in predictions
            },
            fusion_method="weighted_average",
        )

    def fuse_entropy_based(
        self,
        predictions: List[ModelPrediction]
    ) -> EnsemblePrediction:
        """Entropy-based fusion with dynamic confidence weighting."""
        if not predictions:
            raise ValueError("No predictions to fuse")

        # Calculate entropy for each prediction
        entropies = []
        for pred in predictions:
            if hasattr(pred, "raw_output") and pred.raw_output is not None:
                probs = np.array(pred.raw_output)
                probs = np.clip(probs, 1e-10, 1.0)
                probs /= probs.sum()
                entropy = -np.sum(probs * np.log(probs))
                max_entropy = np.log(len(probs))
                confidence_weight = 1.0 - (entropy / max_entropy)
            else:
                confidence_weight = pred.confidence

            weight = self._get_weight(pred) * confidence_weight
            entropies.append(weight)

        total_weight = sum(entropies)
        if total_weight > 0:
            normalized_weights = [w / total_weight for w in entropies]
        else:
            normalized_weights = [1.0 / len(entropies)] * len(entropies)

        # Weighted voting with entropy-based weights
        votes: Dict[Any, float] = {}
        for pred, weight in zip(predictions, normalized_weights):
            value = pred.value if not isinstance(pred.value, (list, np.ndarray)) else pred.value[0]
            votes[value] = votes.get(value, 0.0) + weight

        winner = max(votes, key=votes.get)
        confidence = votes[winner]

        agreement = max(votes.values()) - sorted(votes.values())[-2] if len(votes) > 1 else 1.0

        return EnsemblePrediction(
            final_prediction=winner,
            confidence=confidence,
            agreement=agreement,
            model_votes={p.model_name: p.value for p in predictions},
            model_confidences={p.model_name: p.confidence for p in predictions},
            weights=self._weights.copy(),
            weighted_contributions={p.model_name: w for p, w in zip(predictions, normalized_weights)},
            fusion_method="entropy_based",
        )

    def fuse(self, predictions: List[ModelPrediction]) -> EnsemblePrediction:
        """
        Fuse predictions using configured method.

        Args:
            predictions: List of model predictions

        Returns:
            EnsemblePrediction: Fused result
        """
        if not predictions:
            raise ValueError("No predictions to fuse")

        if self.method == "weighted_voting":
            return self.fuse_weighted_voting(predictions)
        elif self.method == "weighted_average":
            return self.fuse_weighted_average(predictions)
        elif self.method == "entropy_based":
            return self.fuse_entropy_based(predictions)
        else:
            logger.warning(f"Unknown fusion method: {self.method}, falling back to weighted_average")
            return self.fuse_weighted_average(predictions)

    def _get_weight(self, prediction: ModelPrediction) -> float:
        """Get weight for a prediction."""
        key = f"{prediction.model_name}:{prediction.model_version}"
        if key in self._weights:
            return self._weights[key]
        return 1.0 / max(len(self._weights), 1)

    def get_calibration_history(self) -> List[Dict[str, Any]]:
        """Get weight calibration history."""
        return self._calibration_history
