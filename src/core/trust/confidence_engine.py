"""
Confidence Engine - Confidence calibration for trust scores
"""
from typing import Dict, Any, List, Optional
import math
import logging

logger = logging.getLogger(__name__)


class ConfidenceEngine:
    """
    Confidence calibration engine that provides explainable confidence
    scores for all BLACK VEIL decisions.

    Instead of just saying "Malicious", it returns:
    "Malicious with 82% confidence based on: credential anomaly (45%),
     device anomaly (25%), trust drop (20%), behavior anomaly (10%)"
    """

    def __init__(self):
        self._calibration_history: List[Dict[str, Any]] = []
        logger.info("ConfidenceEngine initialized")

    def calibrate(
        self,
        base_confidence: float,
        factors: Optional[Dict[str, float]] = None,
        historical_accuracy: float = 0.8,
    ) -> Dict[str, Any]:
        """
        Calibrate confidence score with factor breakdown.

        Args:
            base_confidence: Raw confidence from model (0-1)
            factors: Dict of factor_name -> contribution_weight
            historical_accuracy: Model's historical accuracy

        Returns:
            {
                'calibrated_confidence': float,
                'factors': List[Dict],
                'uncertainty': float,
                'reliability': str,
            }
        """
        # Apply historical accuracy adjustment
        calibrated = base_confidence * (0.5 + 0.5 * historical_accuracy)

        # Apply factor adjustments
        if factors:
            factor_adjustment = sum(factors.values()) / len(factors)
            calibrated = calibrated * 0.7 + factor_adjustment * 0.3

        # Calculate uncertainty
        uncertainty = 1.0 - calibrated

        # Determine reliability
        if calibrated >= 0.8:
            reliability = 'high'
        elif calibrated >= 0.5:
            reliability = 'medium'
        else:
            reliability = 'low'

        # Build factor breakdown
        factor_breakdown = []
        if factors:
            total = sum(factors.values()) or 1
            for name, weight in sorted(factors.items(), key=lambda x: x[1], reverse=True):
                factor_breakdown.append({
                    'factor': name,
                    'contribution': round(weight / total, 4),
                    'percentage': f"{weight / total * 100:.1f}%",
                })

        result = {
            'calibrated_confidence': round(min(1.0, max(0.0, calibrated)), 4),
            'uncertainty': round(uncertainty, 4),
            'reliability': reliability,
            'factors': factor_breakdown,
            'base_confidence': base_confidence,
            'historical_accuracy': historical_accuracy,
        }

        self._calibration_history.append(result)
        return result

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of confidence engine state"""
        return {
            'total_calibrations': len(self._calibration_history),
        }

