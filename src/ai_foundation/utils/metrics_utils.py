"""
BLACK VEIL V5 - Metrics Utilities
Common classification and regression metrics
"""
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error, r2_score,
    log_loss, matthews_corrcoef, cohen_kappa_score,
    average_precision_score,
)
import torch
import torch.nn.functional as F


class MetricsUtils:
    """Utility class for computing evaluation metrics."""

    @staticmethod
    def classification_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None,
        average: str = "weighted",
        labels: Optional[List[str]] = None,
    ) -> Dict[str, float]:
        """
        Compute comprehensive classification metrics.

        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            y_prob: Predicted probabilities
            average: Averaging method
            labels: Label names

        Returns:
            Dict[str, float]: Classification metrics
        """
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average=average),
            "recall": recall_score(y_true, y_pred, average=average),
            "f1_score": f1_score(y_true, y_pred, average=average),
            "mcc": matthews_corrcoef(y_true, y_pred),
            "kappa": cohen_kappa_score(y_true, y_pred),
        }

        # Add per-class metrics if binary
        if len(np.unique(y_true)) == 2:
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            metrics.update({
                "specificity": tn / (tn + fp) if (tn + fp) > 0 else 0.0,
                "sensitivity": tp / (tp + fn) if (tp + fn) > 0 else 0.0,
                "ppv": tp / (tp + fp) if (tp + fp) > 0 else 0.0,
                "npv": tn / (tn + fn) if (tn + fn) > 0 else 0.0,
            })

        # Add probability-based metrics
        if y_prob is not None:
            try:
                metrics["auc_roc"] = roc_auc_score(
                    y_true, y_prob[:, 1] if y_prob.ndim > 1 else y_prob
                )
                metrics["avg_precision"] = average_precision_score(
                    y_true, y_prob[:, 1] if y_prob.ndim > 1 else y_prob
                )
                metrics["log_loss"] = log_loss(y_true, y_prob)
            except Exception:
                pass

        return metrics

    @staticmethod
    def regression_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict[str, float]:
        """
        Compute comprehensive regression metrics.

        Args:
            y_true: Ground truth values
            y_pred: Predicted values

        Returns:
            Dict[str, float]: Regression metrics
        """
        return {
            "mse": mean_squared_error(y_true, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
            "mae": mean_absolute_error(y_true, y_pred),
            "r2": r2_score(y_true, y_pred),
            "mape": np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1e-10))) * 100,
        }

    @staticmethod
    def confusion_matrix_metrics(
        cm: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Compute metrics from confusion matrix.

        Args:
            cm: Confusion matrix

        Returns:
            Dict[str, Any]: Confusion matrix metrics
        """
        n_classes = cm.shape[0]
        metrics = {
            "matrix": cm.tolist(),
            "per_class": {},
            "total": int(np.sum(cm)),
        }

        for i in range(n_classes):
            tp = cm[i, i]
            fp = cm[:, i].sum() - tp
            fn = cm[i, :].sum() - tp
            tn = cm.sum() - tp - fp - fn

            metrics["per_class"][f"class_{i}"] = {
                "tp": int(tp),
                "fp": int(fp),
                "fn": int(fn),
                "tn": int(tn),
                "precision": tp / (tp + fp) if (tp + fp) > 0 else 0.0,
                "recall": tp / (tp + fn) if (tp + fn) > 0 else 0.0,
                "f1": 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0,
                "support": int(tp + fn),
            }

        return metrics

    @staticmethod
    def detection_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None,
    ) -> Dict[str, float]:
        """
        Compute security-specific detection metrics.

        Args:
            y_true: Ground truth (0=benign, 1=malicious)
            y_pred: Predicted labels
            y_prob: Predicted probabilities

        Returns:
            Dict[str, float]: Detection metrics
        """
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()

        metrics = {
            "detection_rate": tp / (tp + fn) if (tp + fn) > 0 else 0.0,
            "false_positive_rate": fp / (fp + tn) if (fp + tn) > 0 else 0.0,
            "false_negative_rate": fn / (tp + fn) if (tp + fn) > 0 else 0.0,
            "precision": tp / (tp + fp) if (tp + fp) > 0 else 0.0,
            "false_discovery_rate": fp / (tp + fp) if (tp + fp) > 0 else 0.0,
            "accuracy": (tp + tn) / (tp + tn + fp + fn),
            "f1_score": 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0,
        }

        if y_prob is not None:
            try:
                metrics["auc_roc"] = roc_auc_score(y_true, y_prob[:, 1])
            except Exception:
                pass

        return metrics

    @staticmethod
    def calculate_confidence(
        probabilities: np.ndarray,
        method: str = "max_probability",
    ) -> float:
        """
        Calculate confidence from model probabilities.

        Args:
            probabilities: Predicted probabilities
            method: Confidence calculation method

        Returns:
            float: Confidence score
        """
        if method == "max_probability":
            return float(np.max(probabilities))
        elif method == "margin":
            sorted_probs = np.sort(probabilities)[::-1]
            return float(sorted_probs[0] - sorted_probs[1])
        elif method == "entropy":
            entropy = -np.sum(probabilities * np.log(probabilities + 1e-10))
            max_entropy = -np.log(1.0 / len(probabilities))
            return 1.0 - (entropy / max_entropy)
        else:
            raise ValueError(f"Unknown confidence method: {method}")

    @staticmethod
    def confidence_calibration(
        confidences: np.ndarray,
        accuracies: np.ndarray,
        n_bins: int = 10,
    ) -> Dict[str, Any]:
        """
        Compute confidence calibration metrics.

        Args:
            confidences: Predicted confidences
            accuracies: Binary accuracy per prediction
            n_bins: Number of calibration bins

        Returns:
            Dict[str, Any]: Calibration metrics
        """
        bin_edges = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(confidences, bin_edges) - 1

        ece = 0.0
        mce = 0.0
        bin_data = []

        for i in range(n_bins):
            mask = bin_indices == i
            if mask.sum() > 0:
                bin_conf = confidences[mask].mean()
                bin_acc = accuracies[mask].mean()
                bin_count = mask.sum()
                bin_diff = abs(bin_conf - bin_acc)

                ece += (bin_count / len(confidences)) * bin_diff
                mce = max(mce, bin_diff)

                bin_data.append({
                    "bin": i,
                    "confidence": float(bin_conf),
                    "accuracy": float(bin_acc),
                    "count": int(bin_count),
                    "gap": float(bin_diff),
                })

        return {
            "expected_calibration_error": float(ece),
            "max_calibration_error": float(mce),
            "bins": bin_data,
            "reliability_diagram": {
                "confidences": [b["confidence"] for b in bin_data],
                "accuracies": [b["accuracy"] for b in bin_data],
            },
        }

    @staticmethod
    def compute_metric_summary(
        metrics_dict: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Compute summary statistics for a metrics dictionary.

        Args:
            metrics_dict: Dictionary of metrics

        Returns:
            Dict[str, float]: Summary statistics
        """
        values = [v for v in metrics_dict.values() if isinstance(v, (int, float))]
        if not values:
            return {}

        return {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "median": float(np.median(values)),
            "count": len(values),
        }
