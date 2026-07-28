"""
BLACK VEIL V2 — User Inference Engine
CERT-r4.2 insider threat detection and user behavior trust scoring
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from ai_core.model_loader import model_loader, ModelLoadError

logger = logging.getLogger(__name__)

# CERT-r4.2 user feature columns
USER_FEATURES = [
    "login_count", "usb_count", "email_count", "file_count", "web_count",
    "O", "C", "E", "A", "N",
]

PERSONALITY_LABELS = ["O", "C", "E", "A", "N"]


@dataclass
class UserPrediction:
    """Prediction result from the user engine"""
    risk_score: float
    risk_level: str
    trust_score: float
    behavior_score: float
    personality_score: float
    final_trust_score: float
    trust_category: str
    user_id: Optional[str] = None


class UserInferenceEngine:
    """
    Insider threat detection engine using CERT-r4.2 features.
    Computes risk, behavior, personality, and trust scores.
    No ML model exists for CERT yet, so uses heuristic scoring.
    """

    def __init__(self):
        self._scaler = None
        self._loaded = False

    def load_model(self) -> bool:
        """Load the CERT MinMax scaler"""
        try:
            self._scaler = model_loader.load_model("cert_minmax_scaler")
            self._loaded = True
            logger.info("UserInferenceEngine: Scaler loaded successfully")
            return True
        except ModelLoadError as e:
            logger.warning(f"UserInferenceEngine: Scaler not available: {e}")
            self._loaded = True  # Still usable without scaler
            return False

    def _compute_risk_score(self, features: dict) -> tuple[float, str]:
        """
        Compute user risk score from behavioral features.
        Higher values in login_count, usb_count, file_count indicate riskier behavior.
        """
        login_risk = min(100, (features.get("login_count", 0) / 5000) * 100)
        usb_risk = min(100, (features.get("usb_count", 0) / 5000) * 100)
        email_risk = min(100, (features.get("email_count", 0) / 20000) * 100)
        file_risk = min(100, (features.get("file_count", 0) / 5000) * 100)
        web_risk = min(100, (features.get("web_count", 0) / 100000) * 100)

        risk_score = (login_risk * 0.25 + usb_risk * 0.25 +
                      email_risk * 0.15 + file_risk * 0.20 + web_risk * 0.15)

        if risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return round(risk_score, 2), risk_level

    def _compute_behavior_score(self, features: dict) -> float:
        """Compute behavior score based on activity patterns"""
        # Normal distribution assumption for healthy behavior
        login_norm = min(1.0, features.get("login_count", 0) / 3000)
        email_norm = min(1.0, features.get("email_count", 0) / 15000)
        web_norm = min(1.0, features.get("web_count", 0) / 80000)

        # Ideal behavior is moderate activity (not too little, not too much)
        login_health = 1.0 - abs(0.5 - login_norm) * 2
        email_health = 1.0 - abs(0.5 - email_norm) * 2
        web_health = 1.0 - abs(0.5 - web_norm) * 2

        score = (login_health * 0.4 + email_health * 0.3 + web_health * 0.3) * 100
        return max(0, min(100, round(score, 2)))

    def _compute_personality_score(self, features: dict) -> float:
        """Compute personality-based trust score from OCEAN traits"""
        scores = []
        for trait in PERSONALITY_LABELS:
            val = features.get(trait, 50)
            # Normalize to 0-100 assuming 0-100 range
            scores.append(min(100, max(0, val)))

        # O (Openness) and A (Agreeableness) weighted positively
        weights = {"O": 0.25, "C": 0.20, "E": 0.15, "A": 0.25, "N": -0.15}
        weighted_sum = sum(s * weights[t] for s, t in zip(scores, PERSONALITY_LABELS))

        # Normalize to 0-100
        score = (weighted_sum + 15) / 0.70  # Scale adjustment
        return max(0, min(100, round(score, 2)))

    def _compute_final_trust(self, risk_score: float, behavior_score: float,
                             personality_score: float) -> tuple[float, str]:
        """Compute final composite trust score"""
        trust_from_risk = 100.0 - risk_score
        final_trust = (trust_from_risk * 0.4 + behavior_score * 0.35 +
                       personality_score * 0.25)

        if final_trust >= 80:
            category = "TRUSTED"
        elif final_trust >= 60:
            category = "WATCHLIST"
        elif final_trust >= 40:
            category = "SUSPICIOUS"
        else:
            category = "BLOCKED"

        return round(final_trust, 2), category

    def predict(self, features: dict, user_id: Optional[str] = None) -> UserPrediction:
        """
        Run user behavior analysis and trust scoring.

        Args:
            features: Dict of CERT-r4.2 user features
            user_id: Optional user identifier

        Returns:
            UserPrediction with risk, behavior, and trust scores
        """
        if not self._loaded:
            self.load_model()

        risk_score, risk_level = self._compute_risk_score(features)
        behavior_score = self._compute_behavior_score(features)
        personality_score = self._compute_personality_score(features)
        final_trust, trust_category = self._compute_final_trust(
            risk_score, behavior_score, personality_score
        )

        return UserPrediction(
            risk_score=risk_score,
            risk_level=risk_level,
            trust_score=round(100.0 - risk_score, 2),
            behavior_score=behavior_score,
            personality_score=personality_score,
            final_trust_score=final_trust,
            trust_category=trust_category,
            user_id=user_id,
        )

    def predict_batch(self, features_list: list[dict],
                      user_ids: Optional[list[str]] = None) -> list[UserPrediction]:
        """Run predictions on multiple user feature sets"""
        results = []
        for i, features in enumerate(features_list):
            uid = user_ids[i] if user_ids else None
            results.append(self.predict(features, uid))
        return results

    @property
    def is_loaded(self) -> bool:
        return self._loaded
