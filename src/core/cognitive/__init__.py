"""
Cognitive Intelligence Layer - The Brain of BLACK VEIL
ATCN (Adaptive Trust Cognitive Network) - Research Contribution 1

Core components for adversarial reasoning, intent inference,
strategy evaluation, and consensus-based decision making.
"""
from .decision_brain import DecisionBrain, Decision, DecisionContext
from .adversarial_reasoning import AdversarialReasoningEngine
from .intent_reasoning import IntentReasoningEngine, AttackerGoal, AttackerProfile
from .strategy_engine import StrategyEngine, Strategy
from .consensus_engine import ConsensusEngine
from .ai_core import AICore

__all__ = [
    'DecisionBrain', 'Decision', 'DecisionContext',
    'AdversarialReasoningEngine',
    'IntentReasoningEngine', 'AttackerGoal', 'AttackerProfile',
    'StrategyEngine', 'Strategy',
    'ConsensusEngine',
    'AICore',
]

