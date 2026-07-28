"""
BLACK VEIL V5 — Cognitive Consensus Engine (CCE) / Multi-Agent Security Decision Model (MASDM)
IEEE Research Contribution 4: Byzantine fault-tolerant consensus with trust-weighted voting

Mathematical Model:
    Decision(t) = argmaxₖ Σᵢ [wᵢ(t)·voteᵢₖ(t)] / Σᵢ wᵢ(t)
    wᵢ(t) = Tᵢ(t) · Aᵢ(t)   (weight = Trust DNA norm · accuracy)

Key Novelty: First combination of Byzantine fault-tolerant consensus with trust-weighted
voting and structured explainable decision fusion for collaborative threat detection.
"""
import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentVote:
    """A single agent's vote in the consensus process"""
    agent_id: str
    agent_type: str                # network, iot, user, cicids
    vote: str                      # BENIGN, MALICIOUS, SUSPICIOUS, UNKNOWN
    confidence: float              # 0-1
    trust_score: float             # Current trust score (0-100)
    accuracy: float                # Historical accuracy (0-1)
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusResult:
    """Result of a consensus decision"""
    decision_id: str
    final_decision: str
    confidence: float
    agreement_level: float
    weighted_vote_distribution: dict[str, float]
    agent_votes: list[dict[str, Any]]
    byzantine_faults_detected: int
    timestamp: str
    explanation: Optional[str] = None


class CognitiveConsensusEngine:
    """
    Cognitive Consensus Engine implementing MASDM (Algorithm 19).
    
    Implements:
    - Trust-weighted voting aggregation
    - Byzantine fault tolerance (f ≤ ⌊(N-1)/2⌋)
    - Conflict resolution
    - Evidence correlation
    - Decision explanation generation
    
    Configuration (from config.settings.cce):
        confidence_threshold: Minimum confidence for autonomous action (default: 0.7)
        agreement_threshold: θ — Consensus threshold (default: 0.67)
        max_iterations: Max consensus rounds (default: 10)
        min_models_required: Minimum agents for valid consensus (default: 2)
        byzantine_fault_tolerance: f — Max faulty agents tolerated (default: 1)
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self._confidence_threshold = float(self.config.get("confidence_threshold", 0.7))
        self._agreement_threshold = float(self.config.get("agreement_threshold", 0.67))
        self._max_iterations = int(self.config.get("max_iterations", 10))
        self._min_models = int(self.config.get("min_models_required", 2))
        self._byzantine_f = int(self.config.get("byzantine_fault_tolerance", 1))

        self._vote_history: list[ConsensusResult] = []

        logger.info(
            "CCE Engine initialized",
            extra={
                "extra": {
                    "agreement_threshold": self._agreement_threshold,
                    "byzantine_f": self._byzantine_f,
                    "min_models": self._min_models,
                }
            },
        )

    def reach_consensus(
        self,
        votes: list[AgentVote],
        context: Optional[dict[str, Any]] = None,
    ) -> ConsensusResult:
        """
        Reach consensus among multiple AI agents (Algorithm 19).
        
        Consensus = majority(weighted_votes) if agreement ≥ θ
        Fallback (<500ms): Decision = argmaxₖ [Σᵢ Tᵢ(t) · voteᵢₖ(t)]
        
        Args:
            votes: Votes from participating agents
            context: Optional context for explanation
            
        Returns:
            ConsensusResult with final decision and confidence
        """
        if len(votes) < self._min_models:
            raise ValueError(
                f"Insufficient agents: {len(votes)} < {self._min_models}"
            )

        decision_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Validate Byzantine tolerance
        n = len(votes)
        max_f = (n - 1) // 2
        if self._byzantine_f > max_f:
            logger.warning(
                f"Byzantine tolerance {self._byzantine_f} exceeds max {max_f} for N={n}"
            )

        # Detect and filter potentially faulty agents
        filtered_votes, faults_detected = self._detect_byzantine_faults(votes)

        # Compute weighted votes
        weighted_votes = {}
        total_weight = 0.0
        agent_details = []

        for vote in filtered_votes:
            weight = self._compute_vote_weight(vote)
            decision = vote.vote

            weighted_votes[decision] = weighted_votes.get(decision, 0.0) + weight
            total_weight += weight

            agent_details.append({
                "agent_id": vote.agent_id,
                "agent_type": vote.agent_type,
                "vote": vote.vote,
                "confidence": vote.confidence,
                "weight": round(weight, 4),
                "trust_score": vote.trust_score,
                "accuracy": vote.accuracy,
            })

        # Normalize weighted votes
        normalized_votes = {}
        if total_weight > 0:
            for decision, w in weighted_votes.items():
                normalized_votes[decision] = round(w / total_weight, 4)

        # Determine final decision
        final_decision = max(normalized_votes, key=normalized_votes.get)
        max_weight = normalized_votes[final_decision]

        # Calculate agreement level
        agreement = self._calculate_agreement(normalized_votes)

        # Calculate confidence
        confidence = self._calculate_confidence(
            normalized_votes, agreement, filtered_votes
        )

        # Generate explanation
        explanation = self._generate_explanation(
            final_decision, normalized_votes, agent_details, faults_detected
        )

        result = ConsensusResult(
            decision_id=decision_id,
            final_decision=final_decision,
            confidence=round(confidence, 4),
            agreement_level=round(agreement, 4),
            weighted_vote_distribution=normalized_votes,
            agent_votes=agent_details,
            byzantine_faults_detected=faults_detected,
            timestamp=timestamp,
            explanation=explanation,
        )

        self._vote_history.append(result)

        logger.info(
            f"Consensus reached: {final_decision} "
            f"(confidence={confidence:.3f}, agreement={agreement:.3f}, "
            f"faults={faults_detected})",
            extra={
                "extra": {
                    "decision_id": decision_id,
                    "final_decision": final_decision,
                    "confidence": round(confidence, 4),
                    "agreement": round(agreement, 4),
                    "faults": faults_detected,
                    "vote_distribution": normalized_votes,
                }
            },
        )

        return result

    def _compute_vote_weight(self, vote: AgentVote) -> float:
        """
        Compute weight for an agent's vote.
        
        wᵢ(t) = Tᵢ(t) · Aᵢ(t)
        where Tᵢ = trust score (normalized 0-1), Aᵢ = historical accuracy
        """
        trust_norm = vote.trust_score / 100.0  # Normalize to 0-1
        weight = trust_norm * vote.accuracy
        return max(0.01, weight)  # Minimum weight to prevent zero

    def _detect_byzantine_faults(
        self, votes: list[AgentVote]
    ) -> tuple[list[AgentVote], int]:
        """
        Detect potentially faulty agents by identifying outliers.
        
        Byzantine: agents whose votes deviate significantly from consensus.
        """
        if len(votes) < 3:
            return votes, 0

        # First pass: compute simple majority
        vote_counts = {}
        for vote in votes:
            vote_counts[vote.vote] = vote_counts.get(vote.vote, 0) + 1

        majority_vote = max(vote_counts, key=vote_counts.get)

        # Second pass: detect outliers (low trust + disagree with majority)
        filtered = []
        faults = 0

        for vote in votes:
            is_outlier = (
                vote.vote != majority_vote
                and vote.trust_score < 40.0  # Low trust threshold
                and vote.accuracy < 0.6       # Low accuracy threshold
            )

            if is_outlier and faults < self._byzantine_f:
                faults += 1
                logger.warning(
                    f"Byzantine fault detected: agent={vote.agent_id} "
                    f"(trust={vote.trust_score:.1f}, accuracy={vote.accuracy:.2f})"
                )
            else:
                filtered.append(vote)

        return filtered, faults

    def _calculate_agreement(self, normalized_votes: dict[str, float]) -> float:
        """Calculate agreement level using entropy-based metric"""
        if not normalized_votes:
            return 0.0

        values = list(normalized_votes.values())
        n = len(values)

        if n <= 1:
            return 1.0

        # Normalized entropy
        entropy = 0.0
        for v in values:
            if v > 0:
                entropy -= v * math.log2(v)

        max_entropy = math.log2(n) if n > 0 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        return 1.0 - normalized_entropy

    def _calculate_confidence(
        self,
        normalized_votes: dict[str, float],
        agreement: float,
        votes: list[AgentVote],
    ) -> float:
        """
        Calculate overall confidence in the consensus decision.
        
        confidence = max_weight × agreement × avg_agent_confidence
        """
        max_weight = max(normalized_votes.values()) if normalized_votes else 0

        avg_agent_confidence = (
            sum(v.confidence for v in votes) / len(votes) if votes else 0
        )

        return max_weight * (0.5 + 0.5 * agreement) * avg_agent_confidence

    def _generate_explanation(
        self,
        decision: str,
        vote_distribution: dict[str, float],
        agent_details: list[dict[str, Any]],
        faults: int,
    ) -> str:
        """Generate a human-readable explanation of the consensus decision"""
        lines = [
            f"Consensus Decision: {decision}",
            f"Confidence: {max(vote_distribution.values()):.1%}",
            f"Agreement Level: {self._calculate_agreement(vote_distribution):.1%}",
            f"Faulty Agents Detected: {faults}",
            "",
            "Vote Distribution:",
        ]

        for decision_label, weight in sorted(
            vote_distribution.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"  - {decision_label}: {weight:.1%}")

        lines.append("")
        lines.append("Agent Votes:")
        for agent in agent_details:
            lines.append(
                f"  - {agent['agent_type']}/{agent['agent_id']}: "
                f"{agent['vote']} (weight={agent['weight']:.2f}, "
                f"trust={agent['trust_score']:.1f})"
            )

        return "\n".join(lines)

    def get_consensus_history(
        self, limit: int = 10
    ) -> list[ConsensusResult]:
        """Get recent consensus results"""
        return self._vote_history[-limit:]

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of CCE state"""
        return {
            "total_consensuses": len(self._vote_history),
            "config": {
                "confidence_threshold": self._confidence_threshold,
                "agreement_threshold": self._agreement_threshold,
                "byzantine_f": self._byzantine_f,
                "min_models": self._min_models,
            },
            "recent_decisions": [
                {
                    "decision": r.final_decision,
                    "confidence": r.confidence,
                    "agreement": r.agreement_level,
                    "timestamp": r.timestamp,
                }
                for r in self._vote_history[-5:]
            ],
        }

