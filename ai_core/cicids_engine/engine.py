"""
BLACK VEIL V2 — CICIDS2017 Inference Engine
CICIDS2017 network traffic analysis for multi-class attack detection
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from ai_core.model_loader import model_loader, ModelLoadError

logger = logging.getLogger(__name__)

# CICIDS2017 feature columns
CICIDS_FEATURES = [
    "Destination Port", "Flow Duration", "Total Fwd Packets",
    "Total Backward Packets", "Total Length of Fwd Packets",
    "Total Length of Bwd Packets", "Fwd Packet Length Max",
    "Fwd Packet Length Min", "Fwd Packet Length Mean",
    "Fwd Packet Length Std", "Bwd Packet Length Max",
    "Bwd Packet Length Min", "Bwd Packet Length Mean",
    "Bwd Packet Length Std", "Flow Bytes/s", "Flow Packets/s",
    "Flow IAT Mean", "Flow IAT Std", "Flow IAT Max", "Flow IAT Min",
    "Fwd IAT Total", "Fwd IAT Mean", "Fwd IAT Std", "Fwd IAT Max",
    "Fwd IAT Min", "Bwd IAT Total", "Bwd IAT Mean", "Bwd IAT Std",
    "Bwd IAT Max", "Bwd IAT Min", "Fwd PSH Flags", "Bwd PSH Flags",
    "Fwd URG Flags", "Bwd URG Flags", "Fwd Header Length",
    "Bwd Header Length", "Fwd Packets/s", "Bwd Packets/s",
    "Min Packet Length", "Max Packet Length", "Packet Length Mean",
    "Packet Length Std", "Packet Length Variance", "FIN Flag Count",
    "SYN Flag Count", "RST Flag Count", "PSH Flag Count",
    "ACK Flag Count", "URG Flag Count", "CWE Flag Count",
    "ECE Flag Count", "Down/Up Ratio", "Average Packet Size",
    "Avg Fwd Segment Size", "Avg Bwd Segment Size",
    "Fwd Header Length.1", "Fwd Avg Bytes/Bulk", "Fwd Avg Packets/Bulk",
    "Fwd Avg Bulk Rate", "Bwd Avg Bytes/Bulk", "Bwd Avg Packets/Bulk",
    "Bwd Avg Bulk Rate", "Subflow Fwd Packets", "Subflow Fwd Bytes",
    "Subflow Bwd Packets", "Subflow Bwd Bytes",
    "Init_Win_bytes_forward", "Init_Win_bytes_backward",
    "act_data_pkt_fwd", "min_seg_size_forward",
    "Active Mean", "Active Std", "Active Max", "Active Min",
    "Idle Mean", "Idle Std", "Idle Max", "Idle Min",
]

# Known attack types from CICIDS2017 label mapping
ATTACK_TYPES = [
    "BENIGN", "Bot", "DDoS", "DoS GoldenEye", "DoS Hulk",
    "DoS Slowhttptest", "DoS slowloris", "FTP-Patator",
    "Heartbleed", "Infiltration", "PortScan", "SSH-Patator",
    "Web Attack Brute Force", "Web Attack Sql Injection",
    "Web Attack XSS",
]


@dataclass
class CICIDSPrediction:
    """Prediction result from the CICIDS2017 engine"""
    is_attack: bool
    attack_type: Optional[str]
    probability: float
    confidence: float
    risk_score: float
    threat_level: str
    protocol_analysis: dict = field(default_factory=dict)


class CICIDSInferenceEngine:
    """
    CICIDS2017 traffic analysis engine.
    No trained model exists yet, so uses heuristic/anomaly-based detection
    with scaler/encoder preprocessing from existing dataset pipeline.
    """

    def __init__(self):
        self._scaler = None
        self._label_encoder = None
        self._loaded = False

    def load_model(self) -> bool:
        """Load CICIDS2017 scaler and label encoder"""
        try:
            self._scaler = model_loader.load_model("cicids2017_minmax_scaler")
            logger.info("CICIDSInferenceEngine: Scaler loaded")
        except ModelLoadError:
            logger.warning("CICIDS2017 scaler not available, using raw features")

        try:
            self._label_encoder = model_loader.load_model("cicids2017_label_encoder")
            logger.info("CICIDSInferenceEngine: Label encoder loaded")
        except ModelLoadError:
            logger.warning("CICIDS2017 label encoder not available")

        self._loaded = True
        return True

    def _validate_features(self, features: dict) -> np.ndarray:
        """Validate and convert input features to array"""
        missing = [f for f in CICIDS_FEATURES if f not in features]
        if missing:
            raise ValueError(f"Missing features: {missing}")

        arr = np.array([[features[f] for f in CICIDS_FEATURES]], dtype=np.float32)
        arr = np.nan_to_num(arr, nan=0.0, posinf=1e10, neginf=-1e10)

        if self._scaler is not None:
            arr = self._scaler.transform(arr)

        return arr

    def _heuristic_detection(self, features: dict) -> tuple[bool, Optional[str], float]:
        """
        Heuristic-based attack detection when no ML model is available.
        Uses rule-based thresholds for common attack patterns.
        """
        is_attack = False
        attack_type = None
        confidence = 0.0

        dst_port = features.get("Destination Port", 0)
        fwd_pkts = features.get("Total Fwd Packets", 0)
        bwd_pkts = features.get("Total Backward Packets", 0)
        fwd_len = features.get("Total Length of Fwd Packets", 0)
        bwd_len = features.get("Total Length of Bwd Packets", 0)
        flow_dur = features.get("Flow Duration", 0)
        fwd_iat = features.get("Fwd IAT Mean", 0)
        syn = features.get("SYN Flag Count", 0)
        fin = features.get("FIN Flag Count", 0)

        # Port scan detection
        if dst_port in [22, 23, 3389] and fwd_pkts > 100 and bwd_pkts < 5:
            is_attack = True
            attack_type = "PortScan"
            confidence = 0.7

        # DDoS detection: high packet count, low IAT
        if fwd_pkts > 1000 and flow_dur > 0 and (fwd_iat < 0.001 or confidence == 0):
            ratio = fwd_pkts / (flow_dur / 1_000_000)
            if ratio > 1000:
                is_attack = True
                attack_type = "DDoS"
                confidence = min(0.9, ratio / 10000)

        # DoS detection: many packets, high data volume
        if (fwd_len > 10_000_000 or bwd_len > 10_000_000) and not is_attack:
            is_attack = True
            attack_type = "DoS Hulk"
            confidence = 0.6

        # Brute force detection: many SYN packets, few FIN
        if syn > 50 and fin < syn * 0.1 and dst_port in [21, 22, 443, 8080]:
            is_attack = True
            attack_type = "FTP-Patator" if dst_port == 21 else "SSH-Patator"
            confidence = 0.75

        # Heartbleed detection
        if dst_port == 443 and fwd_len > 10000 and bwd_len > 100000:
            is_attack = True
            attack_type = "Heartbleed"
            confidence = 0.5

        return is_attack, attack_type, confidence

    def _compute_risk_score(self, is_attack: bool, confidence: float) -> float:
        """Compute risk score from detection result"""
        if is_attack:
            return min(100.0, confidence * 100.0 * 1.3)
        return max(0.0, (1.0 - confidence) * 5.0)

    def _get_threat_level(self, risk_score: float) -> str:
        """Map risk score to threat level"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 55:
            return "HIGH"
        elif risk_score >= 25:
            return "MEDIUM"
        return "LOW"

    def _analyze_protocol(self, features: dict) -> dict:
        """Analyze protocol-level features"""
        dst_port = features.get("Destination Port", 0)
        fwd_len = features.get("Total Length of Fwd Packets", 0)
        bwd_len = features.get("Total Length of Bwd Packets", 0)
        fwd_pkts = features.get("Total Fwd Packets", 0)
        bwd_pkts = features.get("Total Backward Packets", 0)

        # Identify protocol by port
        protocol = "UNKNOWN"
        if dst_port == 80:
            protocol = "HTTP"
        elif dst_port == 443:
            protocol = "HTTPS"
        elif dst_port == 22:
            protocol = "SSH"
        elif dst_port == 21:
            protocol = "FTP"
        elif dst_port == 53:
            protocol = "DNS"
        elif dst_port == 25:
            protocol = "SMTP"
        elif dst_port == 3389:
            protocol = "RDP"

        return {
            "protocol": protocol,
            "destination_port": dst_port,
            "fwd_packets": int(fwd_pkts),
            "bwd_packets": int(bwd_pkts),
            "fwd_bytes": int(fwd_len),
            "bwd_bytes": int(bwd_len),
            "packet_ratio": round(fwd_pkts / max(1, bwd_pkts), 2),
        }

    def predict(self, features: dict) -> CICIDSPrediction:
        """
        Run CICIDS2017 traffic analysis.

        Args:
            features: Dict of CICIDS2017 feature values

        Returns:
            CICIDSPrediction with attack detection and analysis
        """
        if not self._loaded:
            self.load_model()

        X = self._validate_features(features)

        is_attack, attack_type, confidence = self._heuristic_detection(features)
        risk_score = self._compute_risk_score(is_attack, confidence)
        threat_level = self._get_threat_level(risk_score)
        proto_analysis = self._analyze_protocol(features)

        return CICIDSPrediction(
            is_attack=is_attack,
            attack_type=attack_type,
            probability=confidence,
            confidence=confidence,
            risk_score=risk_score,
            threat_level=threat_level,
            protocol_analysis=proto_analysis,
        )

    def predict_batch(self, features_list: list[dict]) -> list[CICIDSPrediction]:
        """Run predictions on multiple traffic samples"""
        return [self.predict(f) for f in features_list]

    @property
    def is_loaded(self) -> bool:
        return self._loaded
