"""
ACDO v1.0 — Autonomous Cognitive Defense Orchestrator
BLACK VEIL Research Contribution 5: Top-level orchestration intelligence

v1.0 New Features:
- Dependency Injection Registration (register_engine instead of hard-coded init)
- Unified SecurityContext (single source of truth)
- Public API Exposure (all internal methods prefixed with _)
- Enhanced Event Bus (priority, retry, dead-letter queue)
- Decision Trace (complete audit trail)
- Async pipeline support
- All v0.9 synchronous methods preserved for backward compatibility

Pipeline:
Incoming Event → Normalize → Analyze → Adversarial Think → Infer Intent →
Evaluate Strategies → Consensus → Decide → Execute → Learn → Update
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging
import uuid
import asyncio

from ..cognitive.decision_brain import DecisionBrain, Decision, DecisionContext
from ..cognitive.adversarial_reasoning import AdversarialReasoningEngine
from ..cognitive.intent_reasoning import IntentReasoningEngine
from ..cognitive.strategy_engine import StrategyEngine
from ..cognitive.consensus_engine import ConsensusEngine
from ..cognitive.ai_core import AICore
from ..threat.analyzer import ThreatAnalyzer
from ..threat.threat_prediction import ThreatPredictionEngine
from ..threat.threat_genome import ThreatGenome
from ..trust.engine import TrustEngine
from ..trust.confidence_engine import ConfidenceEngine
from ..credential.genome_engine import CredentialGenomeEngine
from ..deception.fabric import RealityFabricEngine
from ..knowledge.graph import KnowledgeGraph
from ..policy.engine import PolicyEngine
from ..policy.security_score import SecurityScoreEngine
from ..response.engine import ResponseEngine
from ..response.recovery_engine import RecoveryIntelligenceEngine

# v1.0 New imports
from ..event_bus.unified_event_bus import EventBus
from ..models.security_context import SecurityContext

logger = logging.getLogger(__name__)


class ACDO:
    """
    Autonomous Cognitive Defense Orchestrator (ACDO) v1.0

    The central brain that coordinates all security subsystems through
    an intelligent pipeline of analysis, reasoning, strategy, and action.

    v1.0 Enhancements:
    - Dependency Injection: register_engine() / get_engine() / register_all()
    - Unified SecurityContext: Single object flowing through pipeline
    - DecisionTrace: Complete audit trail per event
    - EventBus: Priority queuing, retry, DLQ, correlation IDs
    - Async pipeline: process_event_async() for non-blocking use
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.orchestrator_id = str(uuid.uuid4())[:8]

        # ── v1.0: Dependency Injection Registry ──
        self._engines: Dict[str, Any] = {}
        self._registered_engines: List[str] = []

        # ── v1.0: Event Bus ──
        self.event_bus = EventBus()

        # ── v1.0: Metrics ──
        self.total_processed = 0
        self.metrics: Dict[str, Any] = {}

        # ── v0.9 Backward Compat: Direct engine initialization ──
        self._init_legacy_engines()

        # State
        self.event_history: List[Dict[str, Any]] = []
        self._learning_loop_active = False
        self._event_count = 0

        logger.info(f"ACDO v1.0 initialized: {self.orchestrator_id}")

    # ==================== v0.9 BACKWARD COMPATIBLE ENGINE INIT ====================

    def _init_legacy_engines(self) -> None:
        """Initialize all legacy engines for backward compatibility (v0.9 API)"""
        # Cognitive Layer
        self.decision_brain = DecisionBrain()
        self.adversarial_reasoning = AdversarialReasoningEngine()
        self.intent_reasoning = IntentReasoningEngine()
        self.strategy_engine = StrategyEngine()
        self.consensus_engine = ConsensusEngine()
        self.ai_core = AICore()

        # Threat Layer
        self.threat_analyzer = ThreatAnalyzer()
        self.threat_prediction = ThreatPredictionEngine()
        self.threat_genome = ThreatGenome()

        # Trust Layer
        self.trust_engine = TrustEngine()
        self.confidence_engine = ConfidenceEngine()

        # Credential Layer
        self.credential_genome = CredentialGenomeEngine()

        # Deception Layer
        self.reality_fabric = RealityFabricEngine()

        # Knowledge Layer
        self.knowledge_graph = KnowledgeGraph()

        # Policy Layer
        self.policy_engine = PolicyEngine()
        self.security_score = SecurityScoreEngine()

        # Response Layer
        self.response_engine = ResponseEngine()
        self.recovery_intelligence = RecoveryIntelligenceEngine()

        # Also register all in DI registry for v1.0 API
        self._engines.update({
            'decision': self.decision_brain,
            'adversarial': self.adversarial_reasoning,
            'intent': self.intent_reasoning,
            'strategy': self.strategy_engine,
            'consensus': self.consensus_engine,
            'ai_core': self.ai_core,
            'threat': self.threat_analyzer,
            'threat_prediction': self.threat_prediction,
            'threat_genome': self.threat_genome,
            'trust': self.trust_engine,
            'confidence': self.confidence_engine,
            'credential': self.credential_genome,
            'deception': self.reality_fabric,
            'knowledge': self.knowledge_graph,
            'policy': self.policy_engine,
            'security_score': self.security_score,
            'response': self.response_engine,
            'recovery': self.recovery_intelligence,
        })
        self._registered_engines = list(self._engines.keys())

    # ==================== v1.0: DEPENDENCY INJECTION ====================

    def register_engine(self, name: str, engine: Any) -> None:
        """Register an engine via dependency injection"""
        if name in self._engines:
            logger.warning(f"Engine {name} already registered, overwriting")
        self._engines[name] = engine
        if name not in self._registered_engines:
            self._registered_engines.append(name)
        logger.info(f"Registered engine: {name}")

    def get_engine(self, name: str) -> Optional[Any]:
        """Get registered engine by name"""
        return self._engines.get(name)

    def register_all(self, engines: Dict[str, Any]) -> None:
        """Register multiple engines at once"""
        for name, engine in engines.items():
            self.register_engine(name, engine)

    # ==================== v1.0: PUBLIC API (Async Pipeline) ====================

    async def process_event_async(self, raw_event: Dict[str, Any]) -> SecurityContext:
        """
        v1.0: Process an event through the complete ACDO pipeline (async).

        Uses the Unified SecurityContext as single source of truth.
        This is the MAIN PUBLIC API for v1.0.
        """
        start_time = datetime.now(timezone.utc)
        context = SecurityContext()
        context.raw_event = raw_event

        try:
            # Stage 1: Threat Analysis
            context = await self._analyze_threat(context)

            # Stage 2: Trust Evaluation
            context = await self._evaluate_trust(context)

            # Stage 3: Intent Reasoning
            context = await self._reason_intent(context)

            # Stage 4: Adversarial Reasoning
            context = await self._adversarial_reason(context)

            # Stage 5: Mission Policy
            context = await self._apply_mission_policy(context)

            # Stage 6: Credential Intelligence
            context = await self._manage_credentials(context)

            # Stage 7: Encryption Planning
            context = await self._plan_encryption(context)

            # Stage 8: Deception Planning
            context = await self._plan_deception(context)

            # Stage 9: Decision
            context = await self._make_decision(context)

            # Stage 10: Execute
            context = await self._execute_decision(context)

            # Stage 11: Update Memory
            context = await self._update_memory(context)

            # Stage 12: Learn
            context = await self._learn_from_event(context)

            # Record metrics
            context.execution.time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.total_processed += 1

            # Publish event
            await self.event_bus.publish("event_processed", context.to_dict())

            logger.info(
                f"v1.0 Event {context.event_id[:8]} processed in {context.execution.time:.3f}s"
            )
            return context

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            context.execution.status = "failed"
            context.execution.error = str(e)
            context.execution.time = (datetime.now(timezone.utc) - start_time).total_seconds()
            return context

    # ==================== v1.0: PIPELINE STAGES ====================

    async def _analyze_threat(self, context: SecurityContext) -> SecurityContext:
        """Stage 1: Threat Analysis"""
        engine = self.get_engine("threat")
        if engine:
            result = engine.analyze(context.raw_event)
            context.threat.score = result.get('score', 0.0)
            context.threat.type = result.get('type', 'unknown')
            context.threat.techniques = result.get('techniques', [])
            context.threat.tactics = result.get('tactics', [])
            context.decision_trace.threat_analysis = result
        return context

    async def _evaluate_trust(self, context: SecurityContext) -> SecurityContext:
        """Stage 2: Trust Evaluation"""
        engine = self.get_engine("trust")
        if engine:
            result = engine.evaluate(
                context.raw_event.get('source', {}).get('id', 'unknown'),
                context.raw_event.get('source', {}).get('type', 'unknown'),
                context.raw_event,
            )
            context.trust.score = result.get('trust_score', 0.5)
            context.trust.confidence = result.get('confidence', 0.5)
            context.trust.risk = result.get('risk_score', 0.0)
            context.trust.level = result.get('trust_level', 'medium')
            context.decision_trace.trust_evaluation = result
        return context

    async def _reason_intent(self, context: SecurityContext) -> SecurityContext:
        """Stage 3: Intent Reasoning"""
        engine = self.get_engine("intent")
        if engine:
            recent = self._get_recent_events(10)
            result = engine.infer_intent(recent + [context.raw_event])
            context.intent.primary_goal = result.get('primary_goal', 'unknown')
            context.intent.confidence = result.get('confidence', 0.0)
            context.intent.next_steps = result.get('predicted_next_steps', [])
            context.decision_trace.intent_inference = result
        return context

    async def _adversarial_reason(self, context: SecurityContext) -> SecurityContext:
        """Stage 4: Adversarial Reasoning"""
        engine = self.get_engine("adversarial")
        if engine:
            result = engine.analyze_defenses(
                threat_context={
                    'score': context.threat.score,
                    'type': context.threat.type,
                    'techniques': context.threat.techniques,
                }
            )
            context.intent.next_steps = result.get('next_steps', context.intent.next_steps)
            context.decision_trace.adversarial_reasoning = result
        return context

    async def _apply_mission_policy(self, context: SecurityContext) -> SecurityContext:
        """Stage 5: Mission Policy"""
        engine = self.get_engine("policy")
        if engine:
            result = engine.get_policy('response')
            context.mission.action = result.get('rules', {}).get('auto_block_threshold', 0.8)
            context.decision_trace.mission_policy = {'policy': 'response', 'data': result}
        return context

    async def _manage_credentials(self, context: SecurityContext) -> SecurityContext:
        """Stage 6: Credential Intelligence"""
        engine = self.get_engine("credential")
        if engine and (context.trust.score < 0.3 or context.threat.score > 0.7):
            result = engine.generate_credential()
            context.credential.id = result.get('id', '')
            context.credential.health = result.get('fitness', 0.5)
            context.credential.rotation_needed = True
            context.decision_trace.credential_intelligence = result
        return context

    async def _plan_encryption(self, context: SecurityContext) -> SecurityContext:
        """Stage 7: Encryption Planning"""
        context.decision_trace.encryption_plan = {
            'status': 'planned',
            'risk_level': context.trust.risk,
        }
        return context

    async def _plan_deception(self, context: SecurityContext) -> SecurityContext:
        """Stage 8: Deception Planning"""
        engine = self.get_engine("deception")
        if engine and (context.threat.score > 0.6 or context.trust.score < 0.3):
            deception = engine.create_deception(
                'honeypot',
                context.raw_event.get('target', {}).get('id', 'unknown'),
            )
            context.deception.used = True
            context.deception.type = 'honeypot'
            context.deception.id = deception.get('deception_id', '')
            context.deception.triggered_by = f"threat_{context.threat.score:.2f}"
            context.decision_trace.deception_plan = deception
        return context

    async def _make_decision(self, context: SecurityContext) -> SecurityContext:
        """Stage 9: Decision Making"""
        engine = self.get_engine("decision")
        if engine:
            decision_context = DecisionContext(
                event_id=context.event_id,
                event_type=context.raw_event.get('type', 'unknown'),
                severity=context.threat.score,
                source=context.raw_event.get('source', {}),
                target=context.raw_event.get('target', {}),
                timestamp=datetime.now(timezone.utc),
            )
            decision = engine.decide(
                context=decision_context,
                adversarial_insights=context.decision_trace.adversarial_reasoning,
                attacker_intent={
                    'primary_goal': context.intent.primary_goal,
                    'confidence': context.intent.confidence,
                    'predicted_next_steps': context.intent.next_steps,
                },
                strategies=[],
                consensus={},
                policy_violations=[],
            )
            context.decision.action = decision.action
            context.decision.confidence = decision.confidence
            context.decision.reasoning = decision.reasoning[:3]
            context.decision_trace.decision_rationale = {
                'action': decision.action,
                'confidence': decision.confidence,
                'reasoning': decision.reasoning,
            }
        return context

    async def _execute_decision(self, context: SecurityContext) -> SecurityContext:
        """Stage 10: Execution"""
        engine = self.get_engine("response")
        if engine:
            result = engine.execute(
                action=context.decision.action,
                target=context.raw_event.get('target', {}).get('id', 'unknown'),
                params={
                    'decision_id': context.event_id,
                    'confidence': context.decision.confidence,
                },
            )
            context.execution.status = 'completed'
            context.execution.result = result
            context.execution.success = result.get('status') == 'executed'
            context.decision_trace.execution_result = result
        return context

    async def _update_memory(self, context: SecurityContext) -> SecurityContext:
        """Stage 11: Memory Update"""
        engine = self.get_engine("knowledge")
        if engine:
            source = context.raw_event.get('source', {})
            target = context.raw_event.get('target', {})
            if source.get('id'):
                engine.add_entity(
                    source.get('type', 'unknown'),
                    source['id'],
                    source.get('properties'),
                )
            if target.get('id'):
                engine.add_entity(
                    target.get('type', 'unknown'),
                    target['id'],
                    target.get('properties'),
                )
            if source.get('id') and target.get('id'):
                engine.add_relationship(
                    f"{source.get('type', 'unknown')}:{source['id']}",
                    f"{target.get('type', 'unknown')}:{target['id']}",
                    context.raw_event.get('type', 'unknown'),
                    {'action': context.decision.action},
                )
        return context

    async def _learn_from_event(self, context: SecurityContext) -> SecurityContext:
        """Stage 12: Learning"""
        feedback = 1.0 if context.execution.success else 0.0
        context.learning.feedback = feedback
        context.decision_trace.outcome_feedback = {
            'feedback': feedback,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        return context

    # ==================== v0.9 BACKWARD COMPATIBLE SYNC PIPELINE ====================

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        v0.9: Legacy synchronous event processing (backward compatible).

        This method is IDENTICAL to the original ACDO.process_event().
        All existing tests and callers continue to work unchanged.
        """
        self._event_count += 1
        event_id = str(uuid.uuid4())[:8]
        logger.info(f"Processing event #{self._event_count}: {event.get('type', 'unknown')}")

        try:
            # ── Step 1: Normalize ──
            normalized = self._normalize_event(event)

            # ── Step 2: Analyze Threat ──
            threat_analysis = self.threat_analyzer.analyze(normalized)

            # ── Step 3: Evaluate Trust ──
            entity_id = normalized.get('source', {}).get('id', 'unknown')
            entity_type = normalized.get('source', {}).get('type', 'unknown')
            trust_assessment = self.trust_engine.evaluate(
                entity_id, entity_type, normalized
            )

            # ── Step 4: Run Adversarial Reasoning ──
            adversarial_insights = self.adversarial_reasoning.analyze_defenses(
                threat_context=threat_analysis
            )

            # ── Step 5: Infer Attacker Intent ──
            recent_events = self._get_recent_events(10)
            intent = self.intent_reasoning.infer_intent(recent_events + [normalized])

            # ── Step 6: Predict Next Moves ──
            prediction = self.threat_prediction.predict_next_objective(
                recent_events + [normalized],
                attacker_profile=intent.get('attacker_profile'),
            )

            # ── Step 7: Build Decision Context ──
            decision_context = DecisionContext(
                event_id=event_id,
                event_type=normalized.get('type', 'unknown'),
                severity=threat_analysis.get('severity', 0.5),
                source=normalized.get('source', {}),
                target=normalized.get('target', {}),
                timestamp=datetime.fromisoformat(
                    normalized.get('timestamp', datetime.now(timezone.utc).isoformat())
                ),
            )

            # ── Step 8: Evaluate Strategies ──
            strategies = self.strategy_engine.evaluate_strategies(
                threat_context=threat_analysis,
                attacker_intent=intent,
                adversarial_insights=adversarial_insights,
            )

            # ── Step 9: Reach Consensus ──
            agent_votes = self._build_agent_votes(normalized, threat_analysis)
            consensus = self.consensus_engine.reach_consensus(agent_votes)

            # ── Step 10: Check Policies ──
            policy_checks = self._check_policies(normalized, threat_analysis)

            # ── Step 11: Make Decision ──
            decision = self.decision_brain.decide(
                context=decision_context,
                adversarial_insights=adversarial_insights,
                attacker_intent=intent,
                strategies=strategies.get('strategies', []),
                consensus=consensus,
                policy_violations=policy_checks.get('violations', []),
            )

            # ── Step 12: Execute Response ──
            response = self.response_engine.execute(
                action=decision.action,
                target=normalized.get('target', {}).get('id', 'unknown'),
                params={
                    'decision_id': decision.decision_id,
                    'confidence': decision.confidence,
                    'attack_type': threat_analysis.get('attack_type', 'unknown'),
                },
            )

            # ── Step 13: Update Knowledge Graph ──
            self._update_knowledge_graph(normalized, decision, response)

            # ── Step 14: Run Recovery Intelligence ──
            recovery_analysis = self.recovery_intelligence.analyze_incident({
                'attack_type': threat_analysis.get('attack_type', 'unknown'),
                'detection_time': 0,
                'response_time': 0,
                'was_blocked': response['status'] == 'executed',
                'forensics_collected': True,
            })

            # ── Step 15: Calculate Security Score ──
            score = self.security_score.calculate_score(
                trust_score=trust_assessment.get('trust_score', 0.5),
                credential_health=self._get_credential_health(),
                deception_coverage=self._get_deception_coverage(),
                attack_surface=1.0 - trust_assessment.get('trust_score', 0.5),
                policy_compliance=self._get_policy_compliance(),
            )

            # ── Step 16: Update Threat Genome ──
            self.threat_genome.register_genome(
                attack_type=threat_analysis.get('attack_type', 'unknown'),
                techniques=threat_analysis.get('techniques', []),
                indicators=threat_analysis.get('indicators', []),
                severity=threat_analysis.get('severity', 0.5),
            )

            # ── Build Result ──
            result = {
                'event_id': event_id,
                'status': 'processed',
                'pipeline': {
                    'threat_analysis': threat_analysis,
                    'trust_assessment': trust_assessment,
                    'adversarial_insights': {
                        'weakest_layer': adversarial_insights.get('weakest_layer'),
                        'gap_count': len(adversarial_insights.get('defense_gaps', [])),
                        'attack_paths': len(adversarial_insights.get('attack_paths', [])),
                        'adversarial_score': adversarial_insights.get('overall_adversarial_score'),
                    },
                    'attacker_intent': {
                        'primary_goal': intent.get('primary_goal'),
                        'confidence': intent.get('confidence'),
                        'predicted_next_steps': intent.get('predicted_next_steps', [])[:2],
                    },
                    'prediction': {
                        'next_objective': prediction.get('predicted_objective'),
                        'confidence': prediction.get('confidence'),
                    },
                    'strategies_evaluated': len(strategies.get('strategies', [])),
                    'consensus': {
                        'decision': consensus.get('final_decision'),
                        'confidence': consensus.get('confidence'),
                        'agreement': consensus.get('agreement_level'),
                    },
                    'decision': {
                        'action': decision.action,
                        'confidence': decision.confidence,
                        'reasoning': decision.reasoning[:3],
                    },
                    'response': response,
                    'recovery_analysis': {
                        'recommendations': recovery_analysis.get('recommendations', [])[:2],
                    },
                    'security_score': score.get('overall_score'),
                    'security_level': score.get('level'),
                },
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

            # Record event
            self.event_history.append({
                'event_id': event_id,
                'event_type': normalized.get('type', 'unknown'),
                'decision_action': decision.action,
                'decision_confidence': decision.confidence,
                'severity': threat_analysis.get('severity'),
                'timestamp': result['timestamp'],
            })

            # Calibrate confidence
            confidence_calibrated = self.confidence_engine.calibrate(
                base_confidence=decision.confidence,
                factors={
                    'trust': trust_assessment.get('trust_score', 0.5),
                    'consensus': consensus.get('agreement_level', 0.5),
                    'adversarial': 1.0 - adversarial_insights.get('overall_adversarial_score', 0.5),
                },
            )
            result['pipeline']['confidence_calibration'] = confidence_calibrated

            logger.info(
                f"Event processed: {normalized.get('type', 'unknown')} -> "
                f"{decision.action} (confidence={decision.confidence:.3f})"
            )
            return result

        except Exception as e:
            logger.error(f"Event processing failed: {e}")
            return {
                'event_id': event_id,
                'status': 'error',
                'error': str(e),
                'fallback_action': 'monitor',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

    # ==================== SHARED HELPER METHODS ====================

    def _normalize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize event to standard format"""
        return {
            'id': event.get('id', str(uuid.uuid4())[:8]),
            'type': event.get('type', 'unknown'),
            'source': event.get('source', {}),
            'target': event.get('target', {}),
            'severity': event.get('severity', 0.5),
            'confidence': event.get('confidence', 0.5),
            'technique_id': event.get('technique_id', ''),
            'techniques': event.get('techniques', []),
            'indicators': event.get('indicators', []),
            'timestamp': event.get('timestamp', datetime.now(timezone.utc).isoformat()),
            'metadata': event.get('metadata', {}),
        }

    def _build_agent_votes(
        self,
        event: Dict[str, Any],
        threat: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Build agent votes for consensus from available intelligence"""
        votes = []
        severity = threat.get('severity', 0.5)
        vote = 'MALICIOUS' if severity > 0.5 else ('SUSPICIOUS' if severity > 0.3 else 'BENIGN')

        votes.append({
            'agent_id': 'network_ai',
            'agent_type': 'network',
            'vote': vote,
            'confidence': event.get('confidence', 0.7),
            'trust_score': 75.0,
            'accuracy': 0.85,
            'evidence': threat,
        })
        votes.append({
            'agent_id': 'iot_ai',
            'agent_type': 'iot',
            'vote': vote,
            'confidence': 0.7,
            'trust_score': 70.0,
            'accuracy': 0.80,
            'evidence': {},
        })
        votes.append({
            'agent_id': 'user_ai',
            'agent_type': 'user',
            'vote': vote,
            'confidence': 0.75,
            'trust_score': 80.0,
            'accuracy': 0.82,
            'evidence': {},
        })
        return votes

    def _check_policies(
        self,
        event: Dict[str, Any],
        threat: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Check all relevant policies"""
        violations = []
        access_check = self.policy_engine.check_policy(
            'access', 'access', {'failed_attempts': 0}
        )
        if not access_check['allowed']:
            violations.extend(access_check['violations'])
        response_check = self.policy_engine.check_policy(
            'response', 'auto_respond', {
                'severity': threat.get('severity', 0.5),
            }
        )
        if not response_check['allowed']:
            violations.extend(response_check['violations'])
        return {'violations': violations, 'allowed': len(violations) == 0}

    def _update_knowledge_graph(
        self,
        event: Dict[str, Any],
        decision: Decision,
        response: Dict[str, Any],
    ) -> None:
        """Update knowledge graph with event data"""
        source = event.get('source', {})
        target = event.get('target', {})
        if source.get('id'):
            self.knowledge_graph.add_entity(
                source.get('type', 'unknown'),
                source['id'],
                source.get('properties'),
            )
        if target.get('id'):
            self.knowledge_graph.add_entity(
                target.get('type', 'unknown'),
                target['id'],
                target.get('properties'),
            )
        if source.get('id') and target.get('id'):
            self.knowledge_graph.add_relationship(
                f"{source.get('type', 'unknown')}:{source['id']}",
                f"{target.get('type', 'unknown')}:{target['id']}",
                event.get('type', 'unknown'),
                {'action': decision.action, 'response': response.get('status')},
            )

    def _get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events for context"""
        return [
            {
                'type': e['event_type'],
                'timestamp': e['timestamp'],
                'severity': e.get('severity', 0.5),
            }
            for e in self.event_history[-limit:]
        ]

    def _get_credential_health(self) -> float:
        return 0.75

    def _get_deception_coverage(self) -> float:
        active = len(self.reality_fabric.get_active_deceptions())
        return min(1.0, active / 10.0)

    def _get_policy_compliance(self) -> float:
        return 0.85

    # ==================== v1.0: PUBLIC UTILITY METHODS ====================

    def get_decision_trace(self, context: SecurityContext) -> Dict[str, Any]:
        """Get decision trace for explainability"""
        return context.decision_trace.to_dict()

    def get_status(self) -> Dict[str, Any]:
        """Get ACDO status"""
        return {
            'orchestrator_id': self.orchestrator_id,
            'status': 'running',
            'version': '1.0',
            'total_events': self.total_processed,
            'registered_engines': self._registered_engines,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

    async def start(self) -> None:
        """Start ACDO v1.0"""
        await self.event_bus.start_event_loop()
        logger.info("ACDO v1.0 started")

    def stop(self) -> None:
        """Stop ACDO"""
        self.event_bus.stop()
        logger.info("ACDO v1.0 stopped")

    # ==================== v0.9 BACKWARD COMPATIBLE STATE METHODS ====================

    def get_system_state(self) -> Dict[str, Any]:
        """Get comprehensive system state summary (v0.9 compatible)"""
        return {
            'orchestrator_id': self.orchestrator_id,
            'status': 'active',
            'total_events_processed': self._event_count,
            'active_deceptions': len(self.reality_fabric.get_active_deceptions()),
            'adversarial_state': self.adversarial_reasoning.get_state_summary(),
            'trust_state': self.trust_engine.get_state_summary(),
            'credential_state': self.credential_genome.get_state_summary(),
            'knowledge_graph': self.knowledge_graph.get_state_summary(),
            'policy_state': self.policy_engine.get_state_summary(),
            'intent_state': self.intent_reasoning.get_state_summary(),
            'security_score': self.security_score.calculate_score(
                trust_score=0.75,
                credential_health=0.70,
                deception_coverage=self._get_deception_coverage(),
                attack_surface=0.30,
                policy_compliance=0.85,
            ),
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

    def get_components_status(self) -> Dict[str, bool]:
        """Get initialization status of all components (v0.9 compatible)"""
        return {
            'decision_brain': True,
            'adversarial_reasoning': True,
            'intent_reasoning': True,
            'strategy_engine': True,
            'consensus_engine': True,
            'ai_core': True,
            'threat_analyzer': True,
            'threat_prediction': True,
            'threat_genome': True,
            'trust_engine': True,
            'confidence_engine': True,
            'credential_genome': True,
            'reality_fabric': True,
            'knowledge_graph': True,
            'policy_engine': True,
            'security_score': True,
            'response_engine': True,
            'recovery_intelligence': True,
        }
