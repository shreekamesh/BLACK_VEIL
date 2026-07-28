"""
Decision Brain - Central decision-making with confidence scoring (ATCN Core)
BLACK VEIL Research Contribution: Adaptive Trust Cognitive Network

Pipeline:
1. Gather evidence from all intelligence layers
2. Run adversarial reasoning
3. Infer attacker intent
4. Evaluate strategies
5. Reach consensus
6. Make final decision with explainable justification
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DecisionContext:
    """Context for decision making"""
    event_id: str
    event_type: str
    severity: float
    source: Dict[str, Any]
    target: Dict[str, Any]
    timestamp: datetime
    confidence_threshold: float = 0.7
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """Final decision with full justification chain"""
    decision_id: str
    action: str  # block, allow, escalate, rotate, deceive, isolate, monitor
    confidence: float  # 0-1
    reasoning: List[str]
    alternatives: List[Dict[str, Any]]
    risk_score: float
    mission_impact: float
    adversarial_insights: Dict[str, Any]
    attacker_intent: Dict[str, Any]
    policy_violations: List[str]
    timestamp: str
    context: Optional[DecisionContext] = None


class DecisionBrain:
    """
    Central decision-making engine that combines inputs from all cognitive
    subsystems to produce coherent, explainable security decisions.

    Implements:
    - Risk-weighted decision selection
    - Multi-strategy evaluation
    - Confidence-based action selection
    - Mission impact assessment
    - Explainable decision trace
    """

    def __init__(self, confidence_threshold: float = 0.7):
        self.decision_history: List[Decision] = []
        self.confidence_threshold = confidence_threshold
        self._decision_rules = self._load_decision_rules()
        logger.info("DecisionBrain initialized")

    def _load_decision_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load severity-based decision rules"""
        return {
            'critical': {
                'threshold': 0.9,
                'require_consensus': True,
                'require_ethical_review': True,
                'actions': ['block', 'isolate', 'escalate'],
                'min_confidence': 0.8,
            },
            'high': {
                'threshold': 0.7,
                'require_consensus': True,
                'require_ethical_review': False,
                'actions': ['block', 'rotate', 'deceive', 'isolate'],
                'min_confidence': 0.7,
            },
            'medium': {
                'threshold': 0.4,
                'require_consensus': False,
                'require_ethical_review': False,
                'actions': ['monitor', 'deceive', 'notify', 'rotate'],
                'min_confidence': 0.5,
            },
            'low': {
                'threshold': 0.0,
                'require_consensus': False,
                'require_ethical_review': False,
                'actions': ['monitor', 'log', 'notify'],
                'min_confidence': 0.3,
            },
        }

    def decide(
        self,
        context: DecisionContext,
        adversarial_insights: Dict[str, Any],
        attacker_intent: Dict[str, Any],
        strategies: List[Dict[str, Any]],
        consensus: Dict[str, Any],
        policy_violations: Optional[List[str]] = None,
    ) -> Decision:
        """
        Make a decision based on all available intelligence.

        Args:
            context: Decision context with event details
            adversarial_insights: Output from AdversarialReasoningEngine
            attacker_intent: Output from IntentReasoningEngine
            strategies: Ranked list of possible strategies
            consensus: ConsensusEngine result
            policy_violations: Any policy violations detected

        Returns:
            Decision with full justification
        """
        # Determine severity level
        severity_level = self._get_severity_level(context.severity)
        rules = self._decision_rules[severity_level]

        # Select best strategy
        selected_strategy = self._select_best_strategy(
            strategies, rules, consensus, context
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            selected_strategy, consensus, context
        )

        # Generate reasoning chain
        reasoning = self._build_reasoning(
            context, adversarial_insights, attacker_intent,
            selected_strategy, policy_violations or []
        )

        # Check ethical constraints
        if rules.get('require_ethical_review', False) and confidence < 0.9:
            action = 'escalate'  # Defer to human
            reasoning.append("Ethical review required: deferring to human operator")
        else:
            action = selected_strategy.get('action', 'monitor')

        decision = Decision(
            decision_id=str(uuid.uuid4()),
            action=action,
            confidence=round(confidence, 4),
            reasoning=reasoning,
            alternatives=strategies[:3],
            risk_score=selected_strategy.get('risk_score', context.severity),
            mission_impact=selected_strategy.get('mission_impact', 0.5),
            adversarial_insights=adversarial_insights,
            attacker_intent=attacker_intent,
            policy_violations=policy_violations or [],
            timestamp=datetime.now(timezone.utc).isoformat(),
            context=context,
        )

        self.decision_history.append(decision)
        logger.info(
            f"Decision made: {decision.action} "
            f"(confidence={decision.confidence:.3f}, "
            f"severity={severity_level})"
        )
        return decision

    def _get_severity_level(self, severity: float) -> str:
        """Map severity score to level string"""
        if severity >= 0.9:
            return 'critical'
        elif severity >= 0.7:
            return 'high'
        elif severity >= 0.4:
            return 'medium'
        else:
            return 'low'

    def _select_best_strategy(
        self,
        strategies: List[Dict[str, Any]],
        rules: Dict[str, Any],
        consensus: Dict[str, Any],
        context: DecisionContext,
    ) -> Dict[str, Any]:
        """Select the best strategy considering constraints"""
        if not strategies:
            return {
                'action': 'monitor',
                'confidence': 0.5,
                'risk_score': context.severity,
                'mission_impact': 0.3,
                'effectiveness': 0.5,
                'resource_cost': 0.1,
            }

        # Filter to allowed actions for severity level
        allowed = rules['actions']
        valid = [s for s in strategies if s.get('action') in allowed]

        if not valid:
            valid = strategies

        # Score each strategy
        scored = []
        for s in valid:
            score = (
                s.get('effectiveness', 0.5) * 0.4
                + (1 - s.get('resource_cost', 0.5)) * 0.2
                + (1 - s.get('mission_impact', 0.5)) * 0.2
                + (1 - s.get('risk_score', 0.5)) * 0.2
            )
            scored.append((score, s))

        # Return highest-scored
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    def _calculate_confidence(
        self,
        strategy: Dict[str, Any],
        consensus: Dict[str, Any],
        context: DecisionContext,
    ) -> float:
        """Calculate overall confidence in decision"""
        strategy_conf = strategy.get('confidence', strategy.get('effectiveness', 0.5))
        consensus_conf = consensus.get('confidence', 0.5)
        agreement = consensus.get('agreement_level', 0.5)

        # Weighted combination
        confidence = (
            strategy_conf * 0.4
            + consensus_conf * 0.3
            + agreement * 0.3
        )

        return min(1.0, max(0.0, confidence))

    def _build_reasoning(
        self,
        context: DecisionContext,
        adversarial_insights: Dict[str, Any],
        attacker_intent: Dict[str, Any],
        strategy: Dict[str, Any],
        policy_violations: List[str],
    ) -> List[str]:
        """Build human-readable reasoning chain"""
        reasoning = [
            f"Event: {context.event_type} (severity={context.severity:.2f})",
        ]

        # Adversarial insights
        gap_count = len(adversarial_insights.get('defense_gaps', []))
        path_count = len(adversarial_insights.get('attack_paths', []))
        if gap_count > 0:
            reasoning.append(f"Defense gaps identified: {gap_count}")
        if path_count > 0:
            reasoning.append(f"Possible attack paths: {path_count}")

        # Attacker intent
        intent = attacker_intent.get('primary_goal', 'unknown')
        intent_conf = attacker_intent.get('confidence', 0.0)
        reasoning.append(
            f"Inferred attacker intent: {intent} "
            f"(confidence={intent_conf:.2f})"
        )

        # Strategy
        reasoning.append(
            f"Selected action: {strategy.get('action', 'monitor')} "
            f"(effectiveness={strategy.get('effectiveness', 0.5):.2f}, "
            f"cost={strategy.get('resource_cost', 0.5):.2f})"
        )

        # Policy violations
        if policy_violations:
            reasoning.append(f"Policy violations: {', '.join(policy_violations)}")

        return reasoning

    def get_decision_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decisions"""
        return [
            {
                'decision_id': d.decision_id,
                'action': d.action,
                'confidence': d.confidence,
                'risk_score': d.risk_score,
                'timestamp': d.timestamp,
            }
            for d in self.decision_history[-limit:]
        ]

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of decision brain state"""
        return {
            'total_decisions': len(self.decision_history),
            'confidence_threshold': self.confidence_threshold,
            'recent_actions': [
                d.action for d in self.decision_history[-20:]
            ],
            'action_distribution': {
                action: sum(1 for d in self.decision_history if d.action == action)
                for action in set(d.action for d in self.decision_history)
            } if self.decision_history else {},
        }

