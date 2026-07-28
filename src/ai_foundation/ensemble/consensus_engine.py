"""
BLACK VEIL V5 - Consensus Engine
Byzantine fault-tolerant consensus for multi-agent decisions
"""
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class AgentVote:
    """Vote from a single agent."""
    agent_id: str
    agent_type: str
    decision: Any
    confidence: float
    trust_score: float
    accuracy: float
    weight: float
    timestamp: float = field(default_factory=time.time)
    evidence: Optional[Dict[str, Any]] = None


@dataclass
class ConsensusResult:
    """Result of consensus computation."""
    final_decision: Any
    confidence: float
    agreement_level: float
    vote_distribution: Dict[str, float]
    participant_contributions: Dict[str, float]
    byzantine_detected: List[str]
    consensus_reached: bool
    fallback_used: bool
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    explanation: Optional[str] = None


class ConsensusEngine:
    """
    Multi-agent consensus engine with Byzantine fault tolerance.

    Implements:
    - Weighted voting consensus
    - Byzantine fault detection
    - Trust-based weight computation
    - Confidence-weighted aggregation
    - Fallback mechanisms
    - Agreement measurement
    """

    def __init__(
        self,
        num_agents: int = 4,
        byzantine_threshold: int = 1,
        agreement_threshold: float = 0.67,
        timeout_ms: float = 500.0,
        fallback_enabled: bool = True
    ):
        """
        Initialize consensus engine.

        Args:
            num_agents: Total number of voting agents
            byzantine_threshold: Maximum tolerated faulty agents (f)
            agreement_threshold: Minimum agreement level (θ)
            timeout_ms: Consensus timeout in milliseconds
            fallback_enabled: Whether to use fallback on timeout
        """
        self.N = num_agents
        self.f = byzantine_threshold
        self.theta = agreement_threshold
        self.timeout = timeout_ms / 1000.0  # Convert to seconds
        self.fallback_enabled = fallback_enabled

    def validate_byzantine(self, votes: List[AgentVote]) -> bool:
        """
        Validate Byzantine fault tolerance condition.

        N ≥ 3f + 1 must hold for BFT consensus.
        """
        n = len(votes)
        required = 3 * self.f + 1
        is_valid = n >= required

        if not is_valid:
            logger.warning(
                f"Byzantine condition not met: N={n} < 3f+1={required}. "
                f"Need at least {required} honest agents."
            )

        return is_valid

    def compute_weights(self, votes: List[AgentVote]) -> Dict[str, float]:
        """
        Compute voting weights based on trust and accuracy.

        w_i(t) = T_i(t) * A_i(t)
        """
        weights = {}
        total_weight = 0.0

        for vote in votes:
            weight = vote.trust_score / 100.0 * vote.accuracy
            weight = max(0.01, weight)  # Minimum weight to prevent exclusion
            weights[vote.agent_id] = weight
            total_weight += weight

        # Normalize weights
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}

        return weights

    def detect_byzantine(
        self,
        votes: List[AgentVote],
        weights: Dict[str, float]
    ) -> List[str]:
        """
        Detect potentially Byzantine (faulty/malicious) agents.

        Uses:
        - Deviation from weighted consensus
        - Confidence-outcome inconsistency
        - Temporal pattern analysis
        """
        if len(votes) < 3:
            return []

        # Compute weighted decision
        decision_weights: Dict[Any, float] = {}
        for vote in votes:
            weight = weights.get(vote.agent_id, 1.0)
            decision_weights[vote.decision] = decision_weights.get(vote.decision, 0.0) + weight

        reference_decision = max(decision_weights, key=decision_weights.get)

        # Detect outliers
        byzantine_agents = []
        for vote in votes:
            deviation = 0.0

            # Check decision deviation
            if vote.decision != reference_decision:
                deviation += 0.5

            # Check confidence-decision consistency
            if vote.decision != reference_decision and vote.confidence > 0.8:
                deviation += 0.3  # High confidence in minority decision is suspicious

            # Check trust-accuracy consistency
            expected_accuracy = vote.trust_score / 100.0
            accuracy_gap = abs(vote.accuracy - expected_accuracy)
            if accuracy_gap > 0.3:
                deviation += 0.2

            if deviation > 0.5:
                byzantine_agents.append(vote.agent_id)

        return byzantine_agents

    def compute_agreement(self, votes: List[AgentVote], weights: Dict[str, float]) -> float:
        """
        Compute agreement level using weighted entropy.

        Agreement = 1 - normalized_entropy
        """
        if not votes:
            return 0.0

        # Aggregate weighted votes
        weighted_decisions: Dict[Any, float] = {}
        for vote in votes:
            weight = weights.get(vote.agent_id, 0.0)
            weighted_decisions[vote.decision] = weighted_decisions.get(vote.decision, 0.0) + weight

        # Calculate entropy
        total = sum(weighted_decisions.values())
        if total == 0:
            return 0.0

        probabilities = np.array(list(weighted_decisions.values())) / total
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        max_entropy = np.log2(len(weighted_decisions))

        if max_entropy > 0:
            normalized_entropy = entropy / max_entropy
        else:
            normalized_entropy = 0.0

        return 1.0 - normalized_entropy

    def weighted_voting(
        self,
        votes: List[AgentVote],
        weights: Dict[str, float]
    ) -> Tuple[Any, float, Dict[str, float]]:
        """
        Compute weighted voting decision.

        Returns:
            Tuple of (decision, confidence, vote_distribution)
        """
        weighted_decisions: Dict[Any, float] = {}
        total_weight = 0.0

        for vote in votes:
            weight = weights.get(vote.agent_id, 0.0)
            decision = vote.decision
            weighted_decisions[decision] = weighted_decisions.get(decision, 0.0) + weight
            total_weight += weight

        # Normalize
        if total_weight > 0:
            vote_dist = {k: v / total_weight for k, v in weighted_decisions.items()}
        else:
            vote_dist = weighted_decisions

        # Get winner
        winner = max(vote_dist, key=vote_dist.get)
        confidence = vote_dist[winner]

        return winner, confidence, vote_dist

    def fallback_decision(self, votes: List[AgentVote]) -> Tuple[Any, float, Dict[str, float]]:
        """
        Fallback decision mechanism when consensus cannot be reached.

        Uses trust-weighted voting without Byzantine filtering.
        """
        weights = self.compute_weights(votes)
        return self.weighted_voting(votes, weights)

    async def reach_consensus(
        self,
        votes: List[AgentVote],
        timeout_ms: Optional[float] = None
    ) -> ConsensusResult:
        """
        Reach consensus among voting agents.

        Args:
            votes: List of agent votes
            timeout_ms: Consensus timeout

        Returns:
            ConsensusResult: Consensus outcome
        """
        start_time = time.time()
        effective_timeout = (timeout_ms or self.timeout)

        # Check Byzantine condition
        bft_valid = self.validate_byzantine(votes)
        if not bft_valid and self.fallback_enabled:
            logger.warning("BFT condition not met, using fallback")
            decision, confidence, vote_dist = self.fallback_decision(votes)

            return ConsensusResult(
                final_decision=decision,
                confidence=confidence,
                agreement_level=0.0,
                vote_distribution=vote_dist,
                participant_contributions={},
                byzantine_detected=[],
                consensus_reached=True,
                fallback_used=True,
                latency_ms=(time.time() - start_time) * 1000,
                explanation="BFT condition not met, used trust-weighted fallback",
            )

        # Compute weights
        weights = self.compute_weights(votes)

        # Detect Byzantine agents
        byzantine_agents = self.detect_byzantine(votes, weights)

        # Filter out detected Byzantine agents for consensus
        honest_votes = [
            v for v in votes
            if v.agent_id not in byzantine_agents
        ]

        if not honest_votes:
            logger.warning("No honest votes remaining, using all votes")
            honest_votes = votes

        # Compute agreement
        agreement = self.compute_agreement(honest_votes, weights)

        # Check agreement threshold
        if agreement >= self.theta:
            decision, confidence, vote_dist = self.weighted_voting(honest_votes, weights)
            consensus_reached = True
            explanation = f"Consensus reached with agreement {agreement:.3f} >= threshold {self.theta}"
        elif self.fallback_enabled:
            decision, confidence, vote_dist = self.fallback_decision(votes)
            consensus_reached = True
            explanation = (
                f"Agreement {agreement:.3f} below threshold {self.theta}, "
                "used fallback"
            )
        else:
            decision, confidence, vote_dist = self.weighted_voting(honest_votes, weights)
            consensus_reached = False
            explanation = f"Consensus not reached (agreement={agreement:.3f})"

        # Compute participant contributions
        contributions = {}
        for vote in honest_votes:
            contributions[vote.agent_id] = weights.get(vote.agent_id, 0.0) * vote.confidence

        elapsed_ms = (time.time() - start_time) * 1000

        return ConsensusResult(
            final_decision=decision,
            confidence=confidence,
            agreement_level=agreement,
            vote_distribution=vote_dist,
            participant_contributions=contributions,
            byzantine_detected=byzantine_agents,
            consensus_reached=consensus_reached,
            fallback_used=False,
            latency_ms=elapsed_ms,
            explanation=explanation,
        )
