"""
Consensus Engine — Multi-agent decision consensus with BFT
BLACK VEIL Research Contribution: Adaptive Trust Cognitive Network (ATCN)

Implements trust-weighted voting and Byzantine fault-tolerant consensus
for multi-agent threat detection decisions.

Mathematical Model:
    Decision(t) = argmaxₖ Σᵢ [wᵢ(t)·voteᵢₖ(t)] / Σᵢ wᵢ(t)
    wᵢ(t) = Tᵢ(t) · Aᵢ(t)   (weight = Trust DNA norm · accuracy)
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import logging
import uuid
import math

logger = logging.getLogger(__name__)


class ConsensusEngine:
    """
    Multi-agent consensus engine with Byzantine fault tolerance.

    Supports:
    - Trust-weighted voting
    - Byzantine fault detection and filtering
    - Agreement measurement via entropy
    - Fallback mechanisms for degraded operation
    - Confidence-calibrated decisions
    """

    def __init__(
        self,
        agreement_threshold: float = 0.67,
        byzantine_fault_tolerance: int = 1,
        min_agents_required: int = 2,
    ):
        self._agreement_threshold = agreement_threshold
        self._byzantine_f = byzantine_fault_tolerance
        self._min_agents = min_agents_required
        self._consensus_history: List[Dict[str, Any]] = []
        logger.info(
            f"ConsensusEngine initialized: θ={agreement_threshold}, "
            f"f={byzantine_fault_tolerance}, min_agents={min_agents_required}"
        )

    def reach_consensus(
        self,
        agent_votes: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Reach consensus among multiple AI agents.

        Args:
            agent_votes: List of {'agent_id': str, 'agent_type': str, 'vote': str,
                                   'confidence': float, 'trust_score': float,
                                   'accuracy': float, 'evidence': dict}
            context: Optional context for explanation

        Returns:
            ConsensusResult with final decision, confidence, and details
        """
        if len(agent_votes) < self._min_agents:
            raise ValueError(
                f"Insufficient agents: {len(agent_votes)} < {self._min_agents}"
            )

        decision_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Validate Byzantine tolerance
        n = len(agent_votes)
        max_f = (n - 1) // 2
        bft_valid = n >= (3 * self._byzantine_f + 1)

        if not bft_valid:
            logger.warning(
                f"BFT condition not met: N={n} < 3f+1={3*self._byzantine_f+1}. "
                f"Using trust-weighted fallback."
            )

        # Detect and filter potentially faulty agents
        filtered_votes, faults = self._detect_byzantine_faults(agent_votes)

        # Compute weighted votes
        weighted_votes: Dict[str, float] = {}
        total_weight = 0.0
        agent_details = []

        for vote in filtered_votes:
            weight = self._compute_vote_weight(vote)
            decision = vote.get('vote', 'UNKNOWN')

            weighted_votes[decision] = weighted_votes.get(decision, 0.0) + weight
            total_weight += weight

            agent_details.append({
                'agent_id': vote.get('agent_id', 'unknown'),
                'agent_type': vote.get('agent_type', 'unknown'),
                'vote': decision,
                'confidence': vote.get('confidence', 0.5),
                'weight': round(weight, 4),
                'trust_score': vote.get('trust_score', 50.0),
                'accuracy': vote.get('accuracy', 0.5),
            })

        # Normalize votes
        normalized_votes = {
            d: round(w / total_weight, 4)
            for d, w in weighted_votes.items()
        } if total_weight > 0 else {}

        # Determine final decision
        if normalized_votes:
            final_decision = max(normalized_votes, key=normalized_votes.get)
            max_weight = normalized_votes[final_decision]
        else:
            final_decision = 'UNKNOWN'
            max_weight = 0.0

        # Calculate metrics
        agreement = self._calculate_agreement(normalized_votes)
        confidence = self._calculate_confidence(
            normalized_votes, agreement, filtered_votes
        )

        # Generate explanation
        explanation = self._generate_explanation(
            final_decision, normalized_votes, agent_details, faults
        )

        result = {
            'decision_id': decision_id,
            'final_decision': final_decision,
            'confidence': round(confidence, 4),
            'agreement_level': round(agreement, 4),
            'vote_distribution': normalized_votes,
            'agent_votes': agent_details,
            'byzantine_faults_detected': faults,
            'bft_condition_met': bft_valid,
            'fallback_used': not bft_valid,
            'explanation': explanation,
            'timestamp': timestamp,
        }

        self._consensus_history.append(result)

        logger.info(
            f"Consensus: {final_decision} "
            f"(confidence={confidence:.3f}, agreement={agreement:.3f}, "
            f"faults={faults})"
        )
        return result

    def _compute_vote_weight(self, vote: Dict[str, Any]) -> float:
        """Compute wᵢ(t) = Tᵢ(t) · Aᵢ(t)"""
        trust_norm = vote.get('trust_score', 50.0) / 100.0
        accuracy = vote.get('accuracy', 0.5)
        weight = trust_norm * accuracy
        return max(0.01, weight)  # Minimum weight to prevent zero

    def _detect_byzantine_faults(
        self,
        votes: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Detect potentially faulty agents via outlier analysis"""
        if len(votes) < 3:
            return votes, 0

        # First pass: simple majority
        vote_counts = {}
        for vote in votes:
            decision = vote.get('vote', 'UNKNOWN')
            vote_counts[decision] = vote_counts.get(decision, 0) + 1
        majority = max(vote_counts, key=vote_counts.get)

        # Second pass: detect outliers
        filtered = []
        faults = 0

        for vote in votes:
            is_outlier = (
                vote.get('vote') != majority
                and vote.get('trust_score', 50) < 40.0
                and vote.get('accuracy', 0) < 0.6
            )

            if is_outlier and faults < self._byzantine_f:
                faults += 1
                logger.warning(
                    f"Byzantine fault: agent={vote.get('agent_id')} "
                    f"(trust={vote.get('trust_score')}, "
                    f"accuracy={vote.get('accuracy')})"
                )
            else:
                filtered.append(vote)

        return filtered, faults

    def _calculate_agreement(
        self,
        normalized_votes: Dict[str, float],
    ) -> float:
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

        max_entropy = math.log2(n)
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        return 1.0 - normalized_entropy

    def _calculate_confidence(
        self,
        normalized_votes: Dict[str, float],
        agreement: float,
        votes: List[Dict[str, Any]],
    ) -> float:
        """Calculate overall confidence in consensus decision"""
        max_weight = max(normalized_votes.values()) if normalized_votes else 0
        avg_conf = (
            sum(v.get('confidence', 0.5) for v in votes) / max(1, len(votes))
        )
        return max_weight * (0.5 + 0.5 * agreement) * avg_conf

    def _generate_explanation(
        self,
        decision: str,
        vote_dist: Dict[str, float],
        agent_details: List[Dict[str, Any]],
        faults: int,
    ) -> str:
        """Generate human-readable explanation"""
        lines = [
            f"Consensus: {decision}",
            f"Confidence: {max(vote_dist.values()):.1%}" if vote_dist else "N/A",
            f"Faulty Agents: {faults}",
        ]
        if vote_dist:
            lines.append("Vote Distribution:")
            for d, w in sorted(vote_dist.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  - {d}: {w:.1%}")
        return '\n'.join(lines)

    def get_consensus_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent consensus results"""
        return [
            {
                'decision_id': h['decision_id'],
                'final_decision': h['final_decision'],
                'confidence': h['confidence'],
                'agreement_level': h['agreement_level'],
                'timestamp': h['timestamp'],
            }
            for h in self._consensus_history[-limit:]
        ]

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of consensus engine state"""
        return {
            'total_consensuses': len(self._consensus_history),
            'config': {
                'agreement_threshold': self._agreement_threshold,
                'byzantine_f': self._byzantine_f,
                'min_agents': self._min_agents,
            },
            'recent_decisions': [
                h['final_decision'] for h in self._consensus_history[-10:]
            ],
        }

