"""
BLACK VEIL V2 — IoT Inference Engine
EDGE-IoT Random Forest model for IoT device anomaly detection and trust scoring
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from ai_core.model_loader import model_loader, ModelLoadError

logger = logging.getLogger(__name__)

# EDGE-IoT feature columns in expected order
EDGE_FEATURES = [
    "fridge_temperature", "temp_condition", "latitude", "longitude",
    "door_state", "sphone_signal", "FC1_Read_Input_Register",
    "FC2_Read_Discrete_Value", "FC3_Read_Holding_Register", "FC4_Read_Coil",
    "motion_status", "light_status", "current_temperature", "thermostat_status",
    "temperature", "pressure", "humidity",
]


@dataclass
class IoTPrediction:
    """Prediction result from the IoT engine"""
    is_anomaly: bool
    probability: float
    confidence: float
    risk_score: float
    trust_score: float
    threat_level: str
    anomaly_type: Optional[str] = None
    sensor_readings: dict = field(default_factory=dict)


class IoTInferenceEngine:
    """
    IoT anomaly detection engine using EDGE-IoT trained Random Forest.
    Handles feature preprocessing with scaler/encoder and trust scoring.
    """

    def __init__(self):
        self._model = None
        self._scaler = None
        self._label_encoder = None
        self._loaded = False

    def load_model(self) -> bool:
        """Load the EDGE-IoT Random Forest model and preprocessors"""
        try:
            self._model = model_loader.load_model("edge_rf")
            try:
                self._scaler = model_loader.load_model("edge_minmax_scaler")
            except ModelLoadError:
                logger.warning("IoT scaler not available, using raw features")

            try:
                self._label_encoder = model_loader.load_model("edge_label_encoder")
            except ModelLoadError:
                logger.warning("IoT label encoder not available")

            self._loaded = True
            logger.info("IoTInferenceEngine: Model loaded successfully")
            return True
        except ModelLoadError as e:
            logger.error(f"IoTInferenceEngine: Failed to load model: {e}")
            return False

    def _validate_features(self, features: dict) -> np.ndarray:
        """Validate and convert input features to model-ready array"""
        missing = [f for f in EDGE_FEATURES if f not in features]
        if missing:
            raise ValueError(f"Missing features: {missing}")

        arr = np.array([[features[f] for f in EDGE_FEATURES]], dtype=np.float32)
        arr = np.nan_to_num(arr, nan=0.0, posinf=1e10, neginf=-1e10)

        # Apply scaler if available
        if self._scaler is not None:
            arr = self._scaler.transform(arr)

        return arr

    def _compute_risk_score(self, probability: float, is_anomaly: bool) -> float:
        """Compute risk score from prediction probability"""
        if is_anomaly:
            return min(100.0, probability * 100.0 * 1.3)
        return max(0.0, (1.0 - probability) * 15.0)

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

    def predict(self, features: dict) -> IoTPrediction:
        """
        Run IoT anomaly detection on sensor readings.

        Args:
            features: Dict of EDGE-IoT feature values

        Returns:
            IoTPrediction with anomaly detection, trust scores
        """
        if not self._loaded:
            if not self.load_model():
                raise RuntimeError("IoT model not available")

        X = self._validate_features(features)

        # Get prediction
        prediction = int(self._model.predict(X)[0])
        probabilities = self._model.predict_proba(X)[0]

        is_anomaly = bool(prediction == 1)
        probability = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[prediction])
        confidence = probability if is_anomaly else (1.0 - probability)

        # Compute scores
        risk_score = self._compute_risk_score(probability, is_anomaly)
        trust_score = self._compute_trust_score(risk_score)
        threat_level = self._get_threat_level(risk_score)

        return IoTPrediction(
            is_anomaly=is_anomaly,
            probability=probability,
            confidence=confidence,
            risk_score=risk_score,
            trust_score=trust_score,
            threat_level=threat_level,
            sensor_readings=features,
        )

    def predict_batch(self, features_list: list[dict]) -> list[IoTPrediction]:
        """Run predictions on multiple sensor reading sets"""
        return [self.predict(f) for f in features_list]

    @property
    def is_loaded(self) -> bool:
        return self._loaded
