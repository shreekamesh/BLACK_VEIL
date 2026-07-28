"""
BLACK VEIL V5 - Confidence Calibrator
Model confidence calibration and uncertainty estimation
"""
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
import logging

logger = logging.getLogger(__name__)


class ConfidenceCalibrator:
    """
    Confidence calibration for model predictions.

    Supports:
    - Platt scaling (logistic regression)
    - Isotonic regression
    - Temperature scaling
    - Histogram binning
    - Beta calibration
    - Ensemble calibration
    """

    def __init__(self, method: str = "platt"):
        """
        Initialize calibrator.

        Args:
            method: Calibration method
        """
        self.method = method
        self._calibrator = None
        self._temperature: float = 1.0
        self._is_fitted = False
        self._calibration_stats: Dict[str, Any] = {}

    def fit_platt(
        self,
        confidences: np.ndarray,
        accuracies: np.ndarray
    ) -> None:
        """
        Fit Platt scaling (logistic regression).

        Args:
            confidences: Uncalibrated confidence scores
            accuracies: Binary accuracy labels
        """
        X = confidences.reshape(-1, 1)
        y = accuracies

        self._calibrator = LogisticRegression(C=1.0, class_weight="balanced")
        self._calibrator.fit(X, y)
        self._is_fitted = True

        logger.info("Fitted Platt scaling calibrator")

    def fit_isotonic(
        self,
        confidences: np.ndarray,
        accuracies: np.ndarray
    ) -> None:
        """
        Fit isotonic regression.

        Args:
            confidences: Uncalibrated confidence scores
            accuracies: Binary accuracy labels
        """
        self._calibrator = IsotonicRegression(out_of_bounds="clip")
        self._calibrator.fit(confidences, accuracies)
        self._is_fitted = True

        logger.info("Fitted isotonic regression calibrator")

    def fit_temperature(
        self,
        logits: np.ndarray,
        labels: np.ndarray,
        lr: float = 0.01,
        max_iter: int = 100
    ) -> float:
        """
        Fit temperature scaling parameter.

        Args:
            logits: Raw model logits
            labels: True labels
            lr: Learning rate
            max_iter: Maximum iterations

        Returns:
            float: Optimal temperature
        """
        import torch
        import torch.nn.functional as F

        logits_t = torch.FloatTensor(logits)
        labels_t = torch.LongTensor(labels)

        temperature = torch.nn.Parameter(torch.ones(1) * 1.0)
        optimizer = torch.optim.LBFGS([temperature], lr=lr, max_iter=max_iter)

        def eval_func() -> torch.Tensor:
            optimizer.zero_grad()
            loss = F.cross_entropy(logits_t / temperature, labels_t)
            loss.backward()
            return loss

        optimizer.step(eval_func)

        self._temperature = temperature.item()
        self._is_fitted = True

        logger.info(f"Fitted temperature scaling: T={self._temperature:.4f}")
        return self._temperature

    def fit_histogram(
        self,
        confidences: np.ndarray,
        accuracies: np.ndarray,
        n_bins: int = 10
    ) -> None:
        """
        Fit histogram binning calibration.

        Args:
            confidences: Uncalibrated confidence scores
            accuracies: Binary accuracy labels
            n_bins: Number of bins
        """
        bin_edges = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(confidences, bin_edges) - 1

        bin_accuracies = []
        for i in range(n_bins):
            mask = bin_indices == i
            if mask.sum() > 0:
                bin_accuracies.append(accuracies[mask].mean())
            else:
                bin_accuracies.append(0.0)

        self._calibrator = {
            "bin_edges": bin_edges,
            "bin_accuracies": np.array(bin_accuracies),
        }
        self._is_fitted = True

        logger.info(f"Fitted histogram binning calibrator ({n_bins} bins)")

    def calibrate(self, confidences: np.ndarray) -> np.ndarray:
        """
        Calibrate confidence scores.

        Args:
            confidences: Uncalibrated confidence scores

        Returns:
            np.ndarray: Calibrated confidence scores
        """
        if not self._is_fitted:
            logger.warning("Calibrator not fitted, returning uncalibrated confidences")
            return confidences

        if self.method == "platt":
            X = confidences.reshape(-1, 1)
            calibrated = self._calibrator.predict_proba(X)[:, 1]
        elif self.method == "isotonic":
            calibrated = self._calibrator.predict(confidences)
        elif self.method == "temperature":
            calibrated = confidences / self._temperature
        elif self.method == "histogram":
            bin_edges = self._calibrator["bin_edges"]
            bin_accs = self._calibrator["bin_accuracies"]
            indices = np.digitize(confidences, bin_edges) - 1
            indices = np.clip(indices, 0, len(bin_accs) - 1)
            calibrated = bin_accs[indices]
        else:
            logger.warning(f"Unknown calibration method: {self.method}")
            calibrated = confidences

        return np.clip(calibrated, 0.0, 1.0)

    def calibrate_single(self, confidence: float) -> float:
        """Calibrate a single confidence value."""
        return float(self.calibrate(np.array([confidence]))[0])

    def compute_uncertainty(self, confidences: np.ndarray) -> Dict[str, float]:
        """
        Compute uncertainty metrics.

        Args:
            confidences: Calibrated confidence scores

        Returns:
            Dict[str, float]: Uncertainty metrics
        """
        return {
            "mean_confidence": float(np.mean(confidences)),
            "std_confidence": float(np.std(confidences)),
            "entropy": float(-np.mean(
                confidences * np.log(confidences + 1e-10) +
                (1 - confidences) * np.log(1 - confidences + 1e-10)
            )),
            "min_confidence": float(np.min(confidences)),
            "max_confidence": float(np.max(confidences)),
            "uncertainty": float(1.0 - np.mean(confidences ** 2)),
        }

    def get_calibration_stats(self) -> Dict[str, Any]:
        """Get calibration statistics."""
        return self._calibration_stats

    def reset(self) -> None:
        """Reset calibrator state."""
        self._calibrator = None
        self._temperature = 1.0
        self._is_fitted = False
        self._calibration_stats = {}
        logger.info("Calibrator reset")
