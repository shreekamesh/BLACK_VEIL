"""
BLACK VEIL V2 — Network Inference Engine
UNSW-NB15 Random Forest model for network threat detection and trust scoring
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from ai_core.model_loader import model_loader, ModelLoadError

logger = logging.getLogger(__name__)

# UNSW-NB15 feature columns in expected order
UNSW_FEATURES = [
    "dur", "proto", "service", "state", "spkts", "dpkts", "sbytes", "dbytes",
    "rate", "sttl", "dttl", "sload", "dload", "sloss", "dloss", "sinpkt",
    "dinpkt", "sjit", "djit", "swin", "stcpb", "dtcpb", "dwin", "tcprtt",
    "synack", "ackdat", "smean", "dmean", "trans_depth", "response_body_len",
    "ct_srv_src", "ct_state_ttl", "ct_dst_ltm", "ct_src_dport_ltm",
    "ct_dst_sport_ltm", "ct_dst_src_ltm", "is_ftp_login", "ct_ftp_cmd",
    "ct_flw_http_mthd", "ct_src_ltm", "ct_srv_dst", "is_sm_ips_ports",
]


@dataclass
class NetworkPrediction:
    """Prediction result from the network engine"""
    is_attack: bool
    attack_category: Optional[str]
    probability: float
    confidence: float
    risk_score: float
    trust_score: float
    threat_level: str
    feature_importance: dict = field(default_factory=dict)


class NetworkInferenceEngine:
    """
    Network threat detection engine using UNSW-NB15 trained Random Forest.
    Handles feature preprocessing and trust scoring for network traffic.
    """

    def __init__(self):
        self._model = None
        self._loaded = False

    def load_model(self) -> bool:
        """Load the UNSW-NB15 Random Forest model"""
        try:
            self._model = model_loader.load_model("unsw_rf")
            self._loaded = True
            logger.info("NetworkInferenceEngine: Model loaded successfully")
            return True
        except ModelLoadError as e:
            logger.error(f"NetworkInferenceEngine: Failed to load model: {e}")
            return False

    def _validate_features(self, features: dict) -> np.ndarray:
        """Validate and convert input features to model-ready array"""
        missing = [f for f in UNSW_FEATURES if f not in features]
        if missing:
            raise ValueError(f"Missing features: {missing}")

        arr = np.array([[features[f] for f in UNSW_FEATURES]], dtype=np.float32)
        arr = np.nan_to_num(arr, nan=0.0, posinf=1e10, neginf=-1e10)
        return arr

    def _compute_risk_score(self, probability: float, is_attack: bool) -> float:
        """Compute risk score from prediction probability"""
        if is_attack:
            return min(100.0, probability * 100.0 * 1.2)
        return max(0.0, (1.0 - probability) * 10.0)

    def _compute_trust_score(self, risk_score: float) -> float:
        """Compute trust score inversely related to risk"""
        trust = 100.0 - risk_score
        return max(0.0, min(100.0, trust))

    def _get_threat_level(self, risk_score: float) -> str:
        """Map risk score to threat level"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 55:
            return "HIGH"
        elif risk_score >= 25:
            return "MEDIUM"
        return "LOW"

    def predict(self, features: dict) -> NetworkPrediction:
        """
        Run network threat detection on traffic features.

        Args:
            features: Dict of UNSW-NB15 feature values

        Returns:
            NetworkPrediction with threat detection and trust scores
        """
        if not self._loaded:
            if not self.load_model():
                raise RuntimeError("Network model not available")

        X = self._validate_features(features)

        prediction = int(self._model.predict(X)[0])
        probabilities = self._model.predict_proba(X)[0]

        is_attack = bool(prediction == 1)
        probability = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[prediction])
        confidence = probability if is_attack else (1.0 - probability)

        attack_category = None
        if is_attack and hasattr(self._model, "classes_"):
            attack_category = str(self._model.classes_[prediction])

        risk_score = self._compute_risk_score(probability, is_attack)
        trust_score = self._compute_trust_score(risk_score)
        threat_level = self._get_threat_level(risk_score)

        return NetworkPrediction(
            is_attack=is_attack,
            attack_category=attack_category,
            probability=probability,
            confidence=confidence,
            risk_score=risk_score,
            trust_score=trust_score,
            threat_level=threat_level,
        )

    def predict_batch(self, features_list: list[dict]) -> list[NetworkPrediction]:
        """Run predictions on multiple traffic feature sets"""
        return [self.predict(f) for f in features_list]

    @property
    def is_loaded(self) -> bool:
        return self._loaded
