"""
AI Core — Central AI inference coordination
BLACK VEIL Research Contribution: Adaptive Trust Cognitive Network (ATCN)

Coordinates all ML model inference engines and provides
unified prediction interface with confidence calibration.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class AICore:
    """
    Central AI inference coordination.

    Manages and coordinates:
    - Network inference engine (UNSW-NB15)
    - IoT inference engine (EDGE-IoT)
    - User behavior engine (CERT-r4.2)
    - CICIDS inference engine
    - Ensemble/fusion engine
    - Confidence calibration
    """

    def __init__(self):
        self._engines: Dict[str, Any] = {}
        self._is_initialized = False
        self._inference_count = 0
        logger.info("AICore initialized")

    def register_engine(self, name: str, engine: Any) -> None:
        """Register an inference engine"""
        self._engines[name] = engine
        logger.info(f"Engine registered: {name}")

    def predict_all(
        self,
        features: Dict[str, Dict[str, Any]],
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run prediction across all or specific domains.

        Args:
            features: Dict of {domain_name: feature_dict}
            domain: Optional specific domain to run

        Returns:
            Dict of {domain_name: prediction_result}
        """
        results = {}
        domains = [domain] if domain else self._engines.keys()

        for d in domains:
            if d in features and d in self._engines:
                try:
                    engine = self._engines[d]
                    if hasattr(engine, 'predict'):
                        pred = engine.predict(features[d])
                        results[d] = pred
                    else:
                        logger.warning(f"Engine '{d}' has no predict method")
                except Exception as e:
                    logger.error(f"Prediction failed for {d}: {e}")
                    results[d] = {'error': str(e)}

        self._inference_count += 1
        return results

    def get_ensemble_prediction(
        self,
        predictions: List[Dict[str, Any]],
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Get ensemble prediction from multiple models"""
        if not predictions:
            return {'decision': 'UNKNOWN', 'confidence': 0.0}

        # Simple weighted averaging
        total_weight = 0.0
        weighted_scores: Dict[str, float] = {}

        for pred in predictions:
            domain = pred.get('domain', 'unknown')
            weight = weights.get(domain, 1.0) if weights else 1.0
            decision = pred.get('prediction', 'BENIGN')

            weighted_scores[decision] = weighted_scores.get(decision, 0.0) + weight
            total_weight += weight

        if total_weight == 0:
            return {'decision': 'UNKNOWN', 'confidence': 0.0}

        # Normalize
        normalized = {
            k: v / total_weight for k, v in weighted_scores.items()
        }
        final_decision = max(normalized, key=normalized.get)

        return {
            'decision': final_decision,
            'confidence': normalized[final_decision],
            'distribution': normalized,
            'models_used': len(predictions),
        }

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of AI core state"""
        return {
            'initialized': self._is_initialized,
            'registered_engines': list(self._engines.keys()),
            'total_inferences': self._inference_count,
        }

