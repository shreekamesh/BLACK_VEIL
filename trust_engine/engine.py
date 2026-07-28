"""
BLACK VEIL V5 — Trust Engine
Cross-domain trust computation orchestration, aggregation, and dynamic weight adaptation

Implements:
- Multi-domain trust aggregation (Algorithm 3)
- Dynamic weight adaptation based on historical accuracy
- Context-aware trust adjustment (Algorithm 20)
- Composite risk index computation (Algorithm 12)
"""
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from temporal_recovery_engine.engine import TTRMEngine, TrustDNA
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DomainTrust:
    """Trust data from a single domain"""
    domain: str                  # network, iot, user, cicids
    trust_score: float           # 0-100
    risk_score: float            # 0-100
    threat_level: str            # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float            # 0-1
    accuracy: float              # Historical accuracy 0-1
    weight: float                # Current aggregation weight
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CompositeTrust:
    """Aggregated trust from all domains"""
    composite_score: float       # 0-100
    composite_risk: float        # 0-100
    threat_level: str
    confidence: float
    domain_scores: dict[str, dict[str, float]]
    domain_weights: dict[str, float]
    agreement_level: float       # 0-1 consensus level
    timestamp: str


class TrustEngine:
    """
    Central Trust Engine that orchestrates trust computation across all domains.
    
    Integrates:
    - TTRM for temporal trust recovery
    - ATCN for adaptive trust cognitive network
    - Dynamic weight adaptation
    - Context-aware trust adjustment
    - Composite risk index computation
    """

    def __init__(self):
        self.ttrm = TTRMEngine()
        self._default_weights: dict[str, float] = {
            "network": 0.30,
            "iot": 0.25,
            "user": 0.25,
            "cicids": 0.20,
        }
        self._historical_accuracy: dict[str, list[float]] = {
            d: [] for d in self._default_weights
        }
        self._learning_rate: float = 0.01

        logger.info("Trust Engine initialized")

    def compute_composite_trust(
        self,
        domains: list[DomainTrust],
        context: Optional[dict[str, Any]] = None,
    ) -> CompositeTrust:
        """
        Compute composite trust score across all domains (Algorithm 12).
        
        RI = w₁·(1 - T̄/100) + w₂·Σᵢ[Sᵢ·e^(-κtᵢ)] + w₃·V
        
        Args:
            domains: Trust data from each domain engine
            context: Optional context for adjustment
            
        Returns:
            CompositeTrust with aggregated scores
        """
        if not domains:
            raise ValueError("At least one domain trust input required")

        # Update weights based on historical accuracy
        weights = self._adapt_weights(domains)

        # Weighted fusion
        total_weight = sum(d.weight * weights.get(d.domain, 0) for d in domains)
        if total_weight == 0:
            total_weight = 1.0

        weighted_trust = sum(
            d.trust_score * d.weight * weights.get(d.domain, 0) for d in domains
        ) / total_weight

        # Geometric risk fusion (multiplicative)
        weighted_risk = 1.0
        for d in domains:
            w = d.weight * weights.get(d.domain, 0)
            weighted_risk *= (d.risk_score / 100.0 + 0.01) ** w

        total_w = sum(d.weight * weights.get(d.domain, 0) for d in domains)
        composite_risk = (weighted_risk ** (1.0 / max(0.001, total_w))) * 100.0

        # Determine threat level
        threat_level = self._determine_threat_level(
            composite_risk,
            [d.threat_level for d in domains],
        )

        # Agreement level (entropy-based)
        agreement = self._compute_agreement([d.threat_level for d in domains])

        # Average confidence
        avg_confidence = sum(d.confidence * d.weight * weights.get(d.domain, 0) for d in domains)
        avg_confidence /= total_weight if total_weight > 0 else 1
        ensemble_confidence = avg_confidence * (0.5 + 0.5 * agreement)

        # Context adjustment
        if context:
            weighted_trust = self._apply_context_adjustment(weighted_trust, context)

        # Build domain scores dict
        domain_scores = {
            d.domain: {
                "trust_score": d.trust_score,
                "risk_score": d.risk_score,
                "threat_level": d.threat_level,
                "confidence": d.confidence,
                "accuracy": d.accuracy,
            }
            for d in domains
        }

        result = CompositeTrust(
            composite_score=round(weighted_trust, 2),
            composite_risk=round(composite_risk, 2),
            threat_level=threat_level,
            confidence=round(ensemble_confidence, 4),
            domain_scores=domain_scores,
            domain_weights=weights.copy(),
            agreement_level=round(agreement, 4),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Update historical accuracy tracking
        self._update_accuracy(domains)

        logger.info(
            f"Composite trust: {result.composite_score:.1f} (risk={result.composite_risk:.1f}, level={result.threat_level})"
        )

        return result

    def compute_trust_dna(
        self,
        entity_id: str,
        network_trust: float = 50.0,
        iot_trust: float = 50.0,
        user_trust: float = 50.0,
        cicids_trust: float = 50.0,
        context: Optional[dict[str, float]] = None,
    ) -> TrustDNA:
        """
        Compute a Trust DNA vector for an entity via TTRM.
        """
        return self.ttrm.compute_trust_dna(
            entity_id=entity_id,
            network_trust=network_trust,
            iot_trust=iot_trust,
            user_trust=user_trust,
            cicids_trust=cicids_trust,
            context=context,
        )

    def compute_recovered_trust(
        self,
        entity_id: str,
        initial_trust: float,
        incident_time: Optional[datetime] = None,
    ) -> float:
        """
        Compute recovered trust using TTRM temporal model.
        """
        return self.ttrm.calculate_trust(
            entity_id=entity_id,
            initial_trust=initial_trust,
            current_time=incident_time,
        )

    def _adapt_weights(self, domains: list[DomainTrust]) -> dict[str, float]:
        """
        Dynamically adapt weights based on historical accuracy (Algorithm 3).
        
        wᵢ(t+1) = wᵢ(t) · [Aᵢ(t) · Cᵢ(t)] / Σⱼ[wⱼ(t) · Aⱼ(t) · Cⱼ(t)]
        """
        weights = self._default_weights.copy()

        for d in domains:
            domain = d.domain
            if domain not in weights:
                continue

            # Get recent accuracy from tracking
            acc_history = self._historical_accuracy.get(domain, [])
            recent_accuracy = sum(acc_history[-20:]) / max(1, len(acc_history[-20:])) if acc_history else 0.5

            # Update weight: proportional to accuracy
            weights[domain] = max(0.05, weights[domain] * (0.5 + recent_accuracy))

        # Normalize
        total = sum(weights.values())
        if total > 0:
            for k in weights:
                weights[k] /= total

        return weights

    def _determine_threat_level(self, risk_score: float, levels: list[str]) -> str:
        """Determine composite threat level from risk score and domain levels"""
        level_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        max_level = max(level_map.get(l, 0) for l in levels)

        if risk_score >= 80 or max_level >= 3:
            return "CRITICAL"
        elif risk_score >= 55 or max_level >= 2:
            return "HIGH"
        elif risk_score >= 25 or max_level >= 1:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _compute_agreement(levels: list[str]) -> float:
        """Compute entropy-based agreement level among domains"""
        if not levels:
            return 0.0
        level_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        counts = {}
        for l in levels:
            lv = level_map.get(l, 0)
            counts[lv] = counts.get(lv, 0) + 1

        n = len(levels)
        entropy = 0.0
        for count in counts.values():
            p = count / n
            if p > 0:
                entropy -= p * math.log2(p)

        max_entropy = math.log2(4)
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        return 1.0 - normalized_entropy

    @staticmethod
    def _apply_context_adjustment(
        trust_score: float,
        context: dict[str, Any],
    ) -> float:
        """
        Apply context-aware adjustment (Algorithm 20).
        
        T_c = T_base · Πₖ[1 + βₖ · Cₖ(context)]
        """
        modifier = 1.0

        # Time-based: night activity more suspicious
        hour = context.get("hour", 12)
        if 0 <= hour <= 6:
            modifier *= 1.05  # Slightly more trust needed at night

        # Location-based
        if context.get("unusual_location", False):
            modifier *= 0.9

        # Activity-based
        if context.get("high_risk_activity", False):
            modifier *= 0.85

        # Device-based
        if context.get("new_device", False):
            modifier *= 0.95

        return max(0.0, min(100.0, trust_score * modifier))

    def _update_accuracy(self, domains: list[DomainTrust]) -> None:
        """Update historical accuracy tracking for each domain"""
        for d in domains:
            if d.domain in self._historical_accuracy:
                self._historical_accuracy[d.domain].append(d.accuracy)
                # Keep last 100 entries
                if len(self._historical_accuracy[d.domain]) > 100:
                    self._historical_accuracy[d.domain] = self._historical_accuracy[d.domain][-100:]

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of Trust Engine state"""
        return {
            "domain_weights": self._default_weights,
            "historical_accuracy": {
                d: round(sum(v[-20:]) / max(1, len(v[-20:])), 4) if v else 0.5
                for d, v in self._historical_accuracy.items()
            },
            "ttrm_state": self.ttrm.get_state_summary(),
        }

