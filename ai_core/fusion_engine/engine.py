"""
BLACK VEIL V2 — Multi-Agent AI Fusion Engine (Algorithm 1)
Fuses predictions from Network, IoT, User, and CICIDS agents into unified trust/threat assessment
"""
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_WEIGHTS = {
    "network": 0.30,
    "iot": 0.25,
    "user": 0.25,
    "cicids": 0.20,
}

THREAT_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


@dataclass
class FusionInput:
    """Input from a single domain engine"""
    domain: str
    trust_score: float
    risk_score: float
    threat_level: str
    confidence: float
    is_attack: Optional[bool] = None
    attack_type: Optional[str] = None
    weight: float = 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FusionOutput:
    """Fused output from all domain engines"""
    fused_trust_score: float
    fused_risk_score: float
    fused_threat_level: str
    ensemble_confidence: float
    agreement_level: float
    domain_scores: dict
    domain_weights: dict
    weighted_contributions: dict
    fusion_timestamp: datetime
    fusion_method: str = "weighted_ensemble"


class FusionEngine:
    """
    Multi-Agent Fusion Engine implementing Algorithm 1.
    Combines predictions from all four domain engines using dynamic weighted ensemble.
    """

    def __init__(self, weights: Optional[dict[str, float]] = None):
        self._weights = weights or DEFAULT_WEIGHTS.copy()
        self._normalize_weights()

    def _normalize_weights(self):
        total = sum(self._weights.values())
        if total > 0:
            for k in self._weights:
                self._weights[k] /= total

    def update_weights(self, new_weights: dict[str, float]):
        self._weights.update(new_weights)
        self._normalize_weights()

    def _fuse_trust_scores(self, inputs: list[FusionInput]) -> float:
        weighted_sum = sum(
            inp.trust_score * inp.weight * self._weights.get(inp.domain, 0)
            for inp in inputs
        )
        weight_total = sum(
            inp.weight * self._weights.get(inp.domain, 0)
            for inp in inputs
        )
        return weighted_sum / weight_total if weight_total > 0 else 50.0

    def _fuse_risk_scores(self, inputs: list[FusionInput]) -> float:
        weighted_risk = 1.0
        weight_total = 0.0
        for inp in inputs:
            w = inp.weight * self._weights.get(inp.domain, 0)
            weighted_risk *= (inp.risk_score / 100.0 + 0.01) ** w
            weight_total += w
        if weight_total > 0:
            geometric_risk = (weighted_risk ** (1.0 / weight_total)) * 100.0
            return min(100.0, geometric_risk)
        return 0.0

    def _determine_threat_level(self, risk_score: float, inputs: list[FusionInput]) -> str:
        levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        max_level = max(levels.get(inp.threat_level, 0) for inp in inputs)
        if risk_score >= 80 or max_level >= 3:
            return "CRITICAL"
        elif risk_score >= 55 or max_level >= 2:
            return "HIGH"
        elif risk_score >= 25 or max_level >= 1:
            return "MEDIUM"
        return "LOW"

    def _compute_agreement(self, inputs: list[FusionInput]) -> float:
        if not inputs:
            return 0.0
        levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        level_counts = {}
        for inp in inputs:
            lv = levels.get(inp.threat_level, 0)
            level_counts[lv] = level_counts.get(lv, 0) + 1
        n = len(inputs)
        entropy = 0.0
        for count in level_counts.values():
            p = count / n
            if p > 0:
                entropy -= p * math.log2(p)
        max_entropy = math.log2(len(levels))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        return 1.0 - normalized_entropy

    def fuse(self, inputs: list[FusionInput]) -> FusionOutput:
        if not inputs:
            raise ValueError("At least one input required for fusion")

        fused_trust = self._fuse_trust_scores(inputs)
        fused_risk = self._fuse_risk_scores(inputs)
        fused_threat = self._determine_threat_level(fused_risk, inputs)
        agreement = self._compute_agreement(inputs)

        avg_confidence = sum(
            inp.confidence * inp.weight * self._weights.get(inp.domain, 0)
            for inp in inputs
        )
        avg_confidence /= sum(
            inp.weight * self._weights.get(inp.domain, 0)
            for inp in inputs
        ) if inputs else 1
        ensemble_confidence = avg_confidence * (0.5 + 0.5 * agreement)

        domain_scores = {
            inp.domain: {
                "trust_score": inp.trust_score,
                "risk_score": inp.risk_score,
                "threat_level": inp.threat_level,
                "confidence": inp.confidence,
            }
            for inp in inputs
        }

        weighted_contributions = {
            inp.domain: round(
                (inp.trust_score * inp.weight * self._weights.get(inp.domain, 0)) /
                max(0.001, fused_trust), 4
            )
            for inp in inputs
        }

        return FusionOutput(
            fused_trust_score=round(fused_trust, 2),
            fused_risk_score=round(fused_risk, 2),
            fused_threat_level=fused_threat,
            ensemble_confidence=round(ensemble_confidence, 4),
            agreement_level=round(agreement, 4),
            domain_scores=domain_scores,
            domain_weights=self._weights.copy(),
            weighted_contributions=weighted_contributions,
            fusion_timestamp=datetime.now(timezone.utc),
        )

    def fuse_simple(self, trust_score: float, risk_score: float,
                    threat_level: str, confidence: float) -> FusionOutput:
        inp = FusionInput(
            domain="single",
            trust_score=trust_score,
            risk_score=risk_score,
            threat_level=threat_level,
            confidence=confidence,
        )
        return self.fuse([inp])
