"""
BLACK VEIL V5 - Conflict Resolver
Intelligent conflict detection and resolution for multi-agent disagreements
"""
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class Conflict:
    """Represents a detected conflict."""
    type: str  # decision, evidence, trust, temporal
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    agents_involved: List[str]
    description: str
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None


@dataclass
class ResolutionStrategy:
    """Strategy for resolving a conflict."""
    name: str
    method: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0


class ConflictResolver:
    """
    Intelligent conflict resolution for multi-agent disagreements.

    Strategies:
    - Trust-weighted resolution
    - Evidence-based resolution
    - Temporal consistency resolution
    - Knowledge-based resolution
    - Hierarchical escalation
    """

    def __init__(self):
        self._conflict_history: List[Conflict] = []
        self._resolution_strategies: Dict[str, ResolutionStrategy] = {}
        self._escalation_thresholds = {
            "LOW": 0.3,
            "MEDIUM": 0.5,
            "HIGH": 0.7,
            "CRITICAL": 0.9,
        }

        # Register default strategies
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """Register default resolution strategies."""
        self.add_strategy(
            ResolutionStrategy(
                name="trust_weighted_majority",
                method="majority",
                parameters={"weight_by": "trust"},
                priority=1,
            )
        )
        self.add_strategy(
            ResolutionStrategy(
                name="evidence_based",
                method="evidence",
                parameters={"min_evidence_weight": 0.6},
                priority=2,
            )
        )
        self.add_strategy(
            ResolutionStrategy(
                name="temporal_consistency",
                method="temporal",
                parameters={"lookback_window": 10},
                priority=3,
            )
        )
        self.add_strategy(
            ResolutionStrategy(
                name="knowledge_lookup",
                method="knowledge",
                parameters={},
                priority=4,
            )
        )

    def add_strategy(self, strategy: ResolutionStrategy) -> None:
        """Add a resolution strategy."""
        self._resolution_strategies[strategy.name] = strategy

    def detect_decision_conflict(
        self,
        decisions: Dict[str, Any],
        confidences: Dict[str, float],
        threshold: float = 0.3
    ) -> Optional[Conflict]:
        """Detect conflicts between agent decisions."""
        if len(decisions) < 2:
            return None

        unique_decisions = set(str(v) for v in decisions.values())
        if len(unique_decisions) <= 1:
            return None

        # Calculate disagreement level
        decision_counts = {}
        for d in decisions.values():
            key = str(d)
            decision_counts[key] = decision_counts.get(key, 0) + 1

        total = len(decisions)
        max_agreement = max(decision_counts.values()) / total
        disagreement = 1.0 - max_agreement

        if disagreement < threshold:
            return None

        severity = self._calculate_severity(disagreement)

        conflicting_agents = [
            aid for aid, dec in decisions.items()
            if str(dec) != max(decision_counts, key=decision_counts.get)
        ]

        return Conflict(
            type="decision",
            severity=severity,
            agents_involved=conflicting_agents,
            description=f"Decision conflict: {len(conflicting_agents)}/{total} agents disagree",
        )

    def detect_evidence_conflict(
        self,
        evidence_sets: Dict[str, Dict[str, Any]]
    ) -> Optional[Conflict]:
        """Detect conflicts in evidence supporting decisions."""
        if len(evidence_sets) < 2:
            return None

        # Check for contradictory evidence
        all_evidence = []
        for agent_id, evidence in evidence_sets.items():
            for key, value in evidence.items():
                all_evidence.append((agent_id, key, value))

        # Simple contradiction detection
        contradictions = []
        for i, (a1, k1, v1) in enumerate(all_evidence):
            for a2, k2, v2 in all_evidence[i + 1:]:
                if k1 == k2 and v1 != v2:
                    contradictions.append((a1, a2, k1, v1, v2))

        if not contradictions:
            return None

        return Conflict(
            type="evidence",
            severity="HIGH",
            agents_involved=list(set(c[0] for c in contradictions) | set(c[1] for c in contradictions)),
            description=f"Evidence conflict: {len(contradictions)} contradictions found",
        )

    def resolve_trust_weighted(
        self,
        decisions: Dict[str, Any],
        confidences: Dict[str, float],
        trust_scores: Dict[str, float]
    ) -> Tuple[Any, float, Dict[str, Any]]:
        """Resolve conflict using trust-weighted voting."""
        weighted_votes: Dict[str, float] = {}
        total_weight = 0.0

        for agent_id, decision in decisions.items():
            trust = trust_scores.get(agent_id, 0.5)
            confidence = confidences.get(agent_id, 0.5)
            weight = trust * confidence

            decision_key = str(decision)
            weighted_votes[decision_key] = weighted_votes.get(decision_key, 0.0) + weight
            total_weight += weight

        if total_weight > 0:
            weighted_votes = {k: v / total_weight for k, v in weighted_votes.items()}

        winner = max(weighted_votes, key=weighted_votes.get)
        confidence = weighted_votes[winner]

        return winner, confidence, weighted_votes

    def resolve_evidence_based(
        self,
        decisions: Dict[str, Any],
        evidence_sets: Dict[str, Dict[str, Any]]
    ) -> Tuple[Any, float, Dict[str, Any]]:
        """Resolve conflict by evaluating supporting evidence strength."""
        evidence_scores: Dict[str, float] = {}

        for agent_id, decision in decisions.items():
            evidence = evidence_sets.get(agent_id, {})
            decision_key = str(decision)

            # Score evidence quality
            evidence_weight = sum(
                self._score_evidence(key, value)
                for key, value in evidence.items()
            )

            evidence_scores[decision_key] = evidence_scores.get(decision_key, 0.0) + evidence_weight

        total = sum(evidence_scores.values())
        if total > 0:
            evidence_scores = {k: v / total for k, v in evidence_scores.items()}

        winner = max(evidence_scores, key=evidence_scores.get)
        confidence = evidence_scores[winner]

        return winner, confidence, evidence_scores

    def resolve(
        self,
        decisions: Dict[str, Any],
        confidences: Dict[str, float],
        trust_scores: Optional[Dict[str, float]] = None,
        evidence_sets: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Tuple[Any, float, Dict[str, Any], List[Conflict]]:
        """
        Resolve conflicts using available strategies.

        Args:
            decisions: Agent decisions
            confidences: Agent confidences
            trust_scores: Agent trust scores
            evidence_sets: Agent evidence

        Returns:
            Tuple of (resolved_decision, confidence, vote_distribution, conflicts)
        """
        conflicts = []

        # Detect conflicts
        decision_conflict = self.detect_decision_conflict(decisions, confidences)
        if decision_conflict:
            conflicts.append(decision_conflict)

        if evidence_sets:
            evidence_conflict = self.detect_evidence_conflict(evidence_sets)
            if evidence_conflict:
                conflicts.append(evidence_conflict)

        if not conflicts:
            # No conflict, return majority decision
            decision_counts: Dict[str, int] = {}
            for d in decisions.values():
                key = str(d)
                decision_counts[key] = decision_counts.get(key, 0) + 1

            winner = max(decision_counts, key=decision_counts.get)
            confidence = decision_counts[winner] / len(decisions)

            return winner, confidence, {k: v / len(decisions) for k, v in decision_counts.items()}, []

        # Try resolution strategies in priority order
        sorted_strategies = sorted(
            self._resolution_strategies.values(),
            key=lambda s: s.priority
        )

        for strategy in sorted_strategies:
            if strategy.method == "majority" and trust_scores:
                winner, confidence, distribution = self.resolve_trust_weighted(
                    decisions, confidences, trust_scores
                )
                self._log_resolution(decision_conflict, f"Resolved via {strategy.name}")
                return winner, confidence, distribution, conflicts

            elif strategy.method == "evidence" and evidence_sets:
                winner, confidence, distribution = self.resolve_evidence_based(
                    decisions, evidence_sets
                )
                self._log_resolution(decision_conflict, f"Resolved via {strategy.name}")
                return winner, confidence, distribution, conflicts

        # Fallback: simple majority
        decision_counts = {}
        for d in decisions.values():
            key = str(d)
            decision_counts[key] = decision_counts.get(key, 0) + 1

        winner = max(decision_counts, key=decision_counts.get)
        confidence = decision_counts[winner] / len(decisions)

        self._log_resolution(decision_conflict, "Resolved via fallback majority")
        return winner, confidence, {k: v / len(decisions) for k, v in decision_counts.items()}, conflicts

    def _calculate_severity(self, disagreement: float) -> str:
        """Calculate conflict severity from disagreement level."""
        for severity, threshold in sorted(
            self._escalation_thresholds.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if disagreement >= threshold:
                return severity
        return "LOW"

    def _score_evidence(self, key: str, value: Any) -> float:
        """Score the quality/strength of a piece of evidence."""
        if isinstance(value, (int, float)):
            return min(1.0, abs(value) / 100.0)
        elif isinstance(value, str):
            return 0.8 if value else 0.0
        elif isinstance(value, dict):
            return 0.7
        return 0.5

    def _log_resolution(self, conflict: Optional[Conflict], resolution: str) -> None:
        """Log a conflict resolution."""
        if conflict:
            conflict.resolution = resolution
            conflict.resolved_at = datetime.utcnow()
            self._conflict_history.append(conflict)
            logger.info(f"Conflict resolved: {conflict.description} -> {resolution}")

    def get_conflict_history(self) -> List[Conflict]:
        """Get history of resolved conflicts."""
        return self._conflict_history
