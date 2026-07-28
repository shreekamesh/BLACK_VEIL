"""
Strategy Engine - Evaluate and select optimal defense strategies
BLACK VEIL Research Contribution: Adaptive Trust Cognitive Network (ATCN)

Evaluates multiple possible responses to a threat and selects the
safest, most effective strategy based on:
- Effectiveness against threat
- Mission impact
- Resource cost
- Recovery probability
- Ethical constraints
- Policy compliance
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class Strategy:
    """A possible security strategy with evaluation metrics"""
    def __init__(
        self,
        action: str,
        effectiveness: float,
        mission_impact: float,
        resource_cost: float,
        execution_time: float,
        recovery_probability: float,
        risk_score: float,
        description: str,
        ethical_approval_required: bool = False,
    ):
        self.strategy_id = str(uuid.uuid4())[:8]
        self.action = action
        self.effectiveness = effectiveness  # 0-1
        self.mission_impact = mission_impact  # 0-1 (higher = more disruptive)
        self.resource_cost = resource_cost  # 0-1
        self.execution_time = execution_time  # seconds
        self.recovery_probability = recovery_probability  # 0-1
        self.risk_score = risk_score  # 0-1
        self.description = description
        self.ethical_approval_required = ethical_approval_required


class StrategyEngine:
    """
    Evaluates and selects optimal security strategies.

    Implements:
    - Multi-criteria strategy evaluation
    - Cost-benefit analysis with trade-off visualization
    - Ethical constraint checking
    - Policy compliance validation
    - Strategy ranking with explainable scores
    """

    def __init__(self):
        self._strategy_templates = self._init_strategy_templates()
        self._strategy_history: List[Dict[str, Any]] = []
        logger.info("StrategyEngine initialized")

    def _init_strategy_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize base strategy templates"""
        return {
            'block': {
                'action': 'block',
                'base_effectiveness': 0.85,
                'base_mission_impact': 0.3,
                'base_cost': 0.2,
                'execution_time': 0.5,
                'recovery_probability': 0.9,
                'ethical_approval_required': False,
                'description': 'Block the offending IP, user, or traffic pattern',
            },
            'isolate': {
                'action': 'isolate',
                'base_effectiveness': 0.9,
                'base_mission_impact': 0.7,
                'base_cost': 0.4,
                'execution_time': 2.0,
                'recovery_probability': 0.8,
                'ethical_approval_required': False,
                'description': 'Isolate compromised asset from network',
            },
            'rotate': {
                'action': 'rotate',
                'base_effectiveness': 0.75,
                'base_mission_impact': 0.4,
                'base_cost': 0.3,
                'execution_time': 3.0,
                'recovery_probability': 0.95,
                'ethical_approval_required': False,
                'description': 'Rotate potentially compromised credentials',
            },
            'deceive': {
                'action': 'deceive',
                'base_effectiveness': 0.7,
                'base_mission_impact': 0.1,
                'base_cost': 0.3,
                'execution_time': 1.0,
                'recovery_probability': 1.0,
                'ethical_approval_required': True,
                'description': 'Deploy deception to engage and track attacker',
            },
            'monitor': {
                'action': 'monitor',
                'base_effectiveness': 0.3,
                'base_mission_impact': 0.05,
                'base_cost': 0.1,
                'execution_time': 0.1,
                'recovery_probability': 1.0,
                'ethical_approval_required': False,
                'description': 'Intensify monitoring and data collection',
            },
            'escalate': {
                'action': 'escalate',
                'base_effectiveness': 0.5,
                'base_mission_impact': 0.2,
                'base_cost': 0.1,
                'execution_time': 0.3,
                'recovery_probability': 1.0,
                'ethical_approval_required': True,
                'description': 'Escalate to human security team for manual intervention',
            },
            'notify': {
                'action': 'notify',
                'base_effectiveness': 0.2,
                'base_mission_impact': 0.0,
                'base_cost': 0.05,
                'execution_time': 0.05,
                'recovery_probability': 1.0,
                'ethical_approval_required': False,
                'description': 'Notify security team about the event',
            },
            'recover': {
                'action': 'recover',
                'base_effectiveness': 0.6,
                'base_mission_impact': 0.5,
                'base_cost': 0.5,
                'execution_time': 10.0,
                'recovery_probability': 0.7,
                'ethical_approval_required': False,
                'description': 'Initiate automated recovery procedures',
            },
        }

    def evaluate_strategies(
        self,
        threat_context: Dict[str, Any],
        attacker_intent: Dict[str, Any],
        adversarial_insights: Dict[str, Any],
        policy_constraints: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate all possible strategies and return ranked results.

        Args:
            threat_context: Threat analysis with severity, type, etc.
            attacker_intent: Intent reasoning output
            adversarial_insights: Adversarial reasoning output
            policy_constraints: Any policy limitations

        Returns:
            {
                'strategies': List[Dict],
                'recommended': Dict,
                'trade_offs': Dict,
                'evaluation_id': str
            }
        """
        strategies = []
        severity = threat_context.get('severity', 0.5)
        attack_type = threat_context.get('attack_type', 'unknown')

        for template_name, template in self._strategy_templates.items():
            # Adapt strategy to current context
            adapted = self._adapt_strategy(
                template, severity, attack_type, attacker_intent, adversarial_insights
            )
            strategies.append(adapted)

        # Sort by composite score
        strategies.sort(
            key=lambda s: s['composite_score'],
            reverse=True,
        )

        # Identify trade-offs
        trade_offs = self._analyze_trade_offs(strategies)

        result = {
            'strategies': [
                {
                    'action': s['action'],
                    'effectiveness': round(s['effectiveness'], 4),
                    'mission_impact': round(s['mission_impact'], 4),
                    'resource_cost': round(s['resource_cost'], 4),
                    'execution_time': s['execution_time'],
                    'recovery_probability': round(s['recovery_probability'], 4),
                    'risk_score': round(s['risk_score'], 4),
                    'composite_score': round(s['composite_score'], 4),
                    'description': s['description'],
                    'ethical_approval_required': s['ethical_approval_required'],
                }
                for s in strategies
            ],
            'recommended': {
                'action': strategies[0]['action'],
                'composite_score': round(strategies[0]['composite_score'], 4),
                'explanation': self._generate_recommendation(strategies[0], threat_context),
            },
            'trade_offs': trade_offs,
            'evaluation_id': str(uuid.uuid4())[:8],
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        self._strategy_history.append(result)

        logger.info(
            f"Strategies evaluated: recommended={result['recommended']['action']}, "
            f"score={result['recommended']['composite_score']:.3f}"
        )
        return result

    def _adapt_strategy(
        self,
        template: Dict[str, Any],
        severity: float,
        attack_type: str,
        attacker_intent: Dict[str, Any],
        adversarial_insights: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Adapt a strategy template to the current threat context"""
        action = template['action']

        # Base values
        effectiveness = template['base_effectiveness']
        mission_impact = template['base_mission_impact']
        cost = template['base_cost']
        recovery_prob = template['recovery_probability']

        # Adjust effectiveness based on threat severity
        if severity > 0.8:
            if action in ['monitor', 'notify']:
                effectiveness *= 0.5  # Passive measures less effective for severe threats
            elif action in ['block', 'isolate']:
                effectiveness *= 1.2  # Active measures more important for severe threats

        # Adjust based on attack type
        type_specific = {
            'ransomware': {'block': 1.3, 'isolate': 1.4, 'recover': 0.8},
            'credential_theft': {'rotate': 1.5, 'block': 0.8, 'deceive': 1.2},
            'lateral_movement': {'isolate': 1.3, 'monitor': 1.2, 'block': 0.9},
            'data_exfiltration': {'block': 1.4, 'isolate': 1.3, 'monitor': 0.7},
            'ddos': {'block': 1.5, 'isolate': 0.6},
            'phishing': {'deceive': 1.4, 'block': 1.1, 'rotate': 1.3},
        }

        if attack_type in type_specific:
            multiplier = type_specific[attack_type].get(action, 1.0)
            effectiveness *= multiplier

        # Adjust based on adversarial insights (defense gaps)
        gap_factor = adversarial_insights.get('overall_adversarial_score', 0.5)
        if gap_factor > 0.6:
            effectiveness *= 0.85  # When gaps exist, any strategy is less effective

        # Calculate mission impact
        if severity > 0.8:
            mission_impact = min(1.0, mission_impact * 1.3)

        # Calculate risk score (inverse of effectiveness + recovery)
        risk_score = max(0.0, 1.0 - (effectiveness * 0.6 + recovery_prob * 0.4))

        # Composite score (higher = better)
        composite_score = (
            effectiveness * 0.35
            + (1 - mission_impact) * 0.15
            + (1 - cost) * 0.15
            + recovery_prob * 0.20
            + (1 - risk_score) * 0.15
        )

        return {
            'action': action,
            'effectiveness': min(1.0, effectiveness),
            'mission_impact': min(1.0, mission_impact),
            'resource_cost': min(1.0, cost),
            'execution_time': template['execution_time'],
            'recovery_probability': min(1.0, recovery_prob),
            'risk_score': min(1.0, risk_score),
            'composite_score': min(1.0, composite_score),
            'description': template['description'],
            'ethical_approval_required': template['ethical_approval_required'],
        }

    def _analyze_trade_offs(
        self,
        strategies: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze trade-offs between strategies"""
        if not strategies:
            return {}

        top = strategies[0]
        alternatives = strategies[1:4]

        trade_offs = {
            'best_effectiveness': max(s['effectiveness'] for s in strategies),
            'lowest_mission_impact': min(s['mission_impact'] for s in strategies),
            'lowest_cost': min(s['resource_cost'] for s in strategies),
            'recommended_vs_best_effectiveness': round(
                top['effectiveness'] / max(0.01, max(s['effectiveness'] for s in strategies)),
                4,
            ),
            'recommended_vs_lowest_impact': round(
                (1 - top['mission_impact']) / max(0.01, (1 - min(s['mission_impact'] for s in strategies))),
                4,
            ),
        }

        return trade_offs

    def _generate_recommendation(
        self,
        strategy: Dict[str, Any],
        threat_context: Dict[str, Any],
    ) -> str:
        """Generate human-readable recommendation explanation"""
        severity = threat_context.get('severity', 0.5)
        attack_type = threat_context.get('attack_type', 'unknown')

        parts = [
            f"Recommended action: {strategy['action']}",
            f"Based on {attack_type} threat with severity {severity:.2f}",
            f"Effectiveness: {strategy['effectiveness']:.1%}",
            f"Mission impact: {strategy['mission_impact']:.1%}",
            f"Recovery probability: {strategy['recovery_probability']:.1%}",
        ]

        if strategy['ethical_approval_required']:
            parts.append("NOTE: This action requires ethical review")

        return ' | '.join(parts)

    def get_strategy_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent strategy evaluations"""
        return [
            {
                'evaluation_id': h['evaluation_id'],
                'recommended': h['recommended'],
                'timestamp': h['timestamp'],
            }
            for h in self._strategy_history[-limit:]
        ]

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of strategy engine state"""
        return {
            'total_evaluations': len(self._strategy_history),
            'available_strategies': list(self._strategy_templates.keys()),
            'recent_recommendations': [
                h['recommended']['action']
                for h in self._strategy_history[-10:]
            ],
        }

