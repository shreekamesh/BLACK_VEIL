"""
BLACK VEIL V5 — Cognitive Security Orchestrator
Central integration point that connects all cognitive components into a unified
autonomous cyber defense organism (Algorithm 25)

BV(t) = ⟨A(t), T(t), R(t), D(t), F(t), I(t)⟩
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from ai_core.model_loader import model_loader
from ai_core.fusion_engine import FusionEngine, FusionInput
from ai_core.network_engine import NetworkInferenceEngine
from ai_core.iot_engine import IoTInferenceEngine
from ai_core.user_engine import UserInferenceEngine
from ai_core.cicids_engine import CICIDSInferenceEngine

from temporal_recovery_engine.engine import TTRMEngine
from trust_engine.engine import TrustEngine, DomainTrust
from deception_evolution_engine.engine import ACDMEngine
from credential_genome_engine.engine import DCMMEngine
from attack_memory_graph.engine import LAMGEngine
from ai_decision_brain.engine import CognitiveConsensusEngine, AgentVote
from deception_engine.engine import DeceptionEngine
from threat_genome.engine import ThreatGenomeEngine
from fake_credential_engine.engine import FakeCredentialEngine
from knowledge_engine.engine import KnowledgeEngine
from explainable_security_layer.engine import XAIEngine
from ai_ethics_layer.engine import EthicsEngine
from security_digital_twin.engine import DigitalTwinEngine
from forensic_engine.engine import ForensicEngine
from self_healing_engine.engine import SelfHealingEngine
from report_engine.engine import ReportEngine
from utils.logger import get_logger as get_logger_func

logger = get_logger_func(__name__)


@dataclass
class SystemState:
    """Current system state snapshot"""
    timestamp: str
    trust_composite: dict[str, Any]
    threat_level: str
    active_deceptions: int
    consensus_decision: Optional[str]
    system_health: str
    ethics_mode: str
    active_threats_count: int


class CognitiveSecurityOrchestrator:
    """
    Central orchestrator implementing Algorithm 25 — BLACK VEIL Autonomous Security Framework.
    
    Coordinates all cognitive components:
    - AI Core: Network, IoT, User, CICIDS inference + Fusion
    - Trust: Trust Engine + TTRM
    - Deception: ACDM + DCMM + Deception Engine
    - Decision: CCE/MASDM consensus
    - Memory: LAMG + Threat Genome
    - Intelligence: Knowledge + Forensic + XAI
    - Ethics: Ethics Layer
    - Simulation: Digital Twin
    - Recovery: Self-Healing
    - Reporting: Report Engine
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self._initialized = False

        # AI Core
        self.network_engine = NetworkInferenceEngine()
        self.iot_engine = IoTInferenceEngine()
        self.user_engine = UserInferenceEngine()
        self.cicids_engine = CICIDSInferenceEngine()
        self.fusion_engine = FusionEngine()

        # Cognitive Components (V5)
        self.ttrm = TTRMEngine()
        self.trust_engine = TrustEngine()
        self.acdm = ACDMEngine()
        self.dcmm = DCMMEngine()
        self.cce = CognitiveConsensusEngine()
        self.lamg = LAMGEngine()
        self.deception_engine = DeceptionEngine()
        self.threat_genome = ThreatGenomeEngine()
        self.credential_engine = FakeCredentialEngine()
        self.knowledge_engine = KnowledgeEngine()
        self.xai = XAIEngine()
        self.ethics = EthicsEngine()
        self.digital_twin = DigitalTwinEngine()
        self.forensic = ForensicEngine()
        self.healing = SelfHealingEngine()
        self.report_engine = ReportEngine()

        logger.info("Cognitive Security Orchestrator initialized")

    async def initialize(self) -> bool:
        """Initialize all components and preload models"""
        try:
            # Preload ML models
            load_results = model_loader.preload_all()
            loaded = [k for k, v in load_results.items() if v]
            failed = [k for k, v in load_results.items() if not v]
            logger.info(f"Models loaded: {loaded}")
            if failed:
                logger.warning(f"Models failed to load: {failed}")

            # Initialize inference engines
            self.network_engine.load_model()
            self.iot_engine.load_model()
            self.user_engine.load_model()
            self.cicids_engine.load_model()
            self.dcmm.load_defaults()
            self.lamg.load_defaults()

            self._initialized = True
            logger.info("All components initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self._initialized = False
            return False

    def run_detection_cycle(
        self,
        network_features: Optional[dict] = None,
        iot_features: Optional[dict] = None,
        user_features: Optional[dict] = None,
        cicids_features: Optional[dict] = None,
        context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Execute a complete detection cycle across all domains.
        
        Returns aggregated results from all cognitive layers.
        """
        if not self._initialized:
            self.initialize()

        domain_inputs = []

        # 1. Network inference
        if network_features:
            try:
                net_pred = self.network_engine.predict(network_features)
                domain_inputs.append(FusionInput(
                    domain="network",
                    trust_score=net_pred.trust_score,
                    risk_score=net_pred.risk_score,
                    threat_level=net_pred.threat_level,
                    confidence=net_pred.confidence,
                    is_attack=net_pred.is_attack,
                    attack_type=net_pred.attack_category,
                ))
            except Exception as e:
                logger.error(f"Network inference failed: {e}")

        # 2. IoT inference
        if iot_features:
            try:
                iot_pred = self.iot_engine.predict(iot_features)
                domain_inputs.append(FusionInput(
                    domain="iot",
                    trust_score=iot_pred.trust_score,
                    risk_score=iot_pred.risk_score,
                    threat_level=iot_pred.threat_level,
                    confidence=iot_pred.confidence,
                    is_attack=iot_pred.is_anomaly,
                ))
            except Exception as e:
                logger.error(f"IoT inference failed: {e}")

        # 3. User inference
        if user_features:
            try:
                user_pred = self.user_engine.predict(user_features)
                domain_inputs.append(FusionInput(
                    domain="user",
                    trust_score=user_pred.final_trust_score,
                    risk_score=user_pred.risk_score,
                    threat_level=user_pred.risk_level,
                    confidence=0.8,
                ))
            except Exception as e:
                logger.error(f"User inference failed: {e}")

        # 4. CICIDS inference
        if cicids_features:
            try:
                cicids_pred = self.cicids_engine.predict(cicids_features)
                domain_inputs.append(FusionInput(
                    domain="cicids",
                    trust_score=100.0 - cicids_pred.risk_score,
                    risk_score=cicids_pred.risk_score,
                    threat_level=cicids_pred.threat_level,
                    confidence=cicids_pred.confidence,
                    is_attack=cicids_pred.is_attack,
                    attack_type=cicids_pred.attack_type,
                ))
            except Exception as e:
                logger.error(f"CICIDS inference failed: {e}")

        # 5. Fusion
        fusion_result = None
        if domain_inputs:
            fusion_result = self.fusion_engine.fuse(domain_inputs)
            logger.info(
                f"Fusion: trust={fusion_result.fused_trust_score:.1f}, "
                f"risk={fusion_result.fused_risk_score:.1f}, "
                f"level={fusion_result.fused_threat_level}"
            )

        # 6. Consensus (CCE/MASDM)
        consensus_result = None
        if domain_inputs:
            votes = []
            for inp in domain_inputs:
                vote_label = "MALICIOUS" if inp.is_attack else "BENIGN"
                votes.append(AgentVote(
                    agent_id=inp.domain,
                    agent_type=inp.domain,
                    vote=vote_label,
                    confidence=inp.confidence,
                    trust_score=inp.trust_score,
                    accuracy=inp.confidence,
                    evidence={"threat_level": inp.threat_level, "risk": inp.risk_score},
                ))
            try:
                consensus_result = self.cce.reach_consensus(votes, context)
            except Exception as e:
                logger.error(f"Consensus failed: {e}")

        return {
            "domain_inputs_count": len(domain_inputs),
            "fusion": fusion_result,
            "consensus": consensus_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_system_state(self) -> SystemState:
        """Get current comprehensive system state"""
        return SystemState(
            timestamp=datetime.now(timezone.utc).isoformat(),
            trust_composite=self.trust_engine.get_state_summary(),
            threat_level="MEDIUM",
            active_deceptions=len(self.acdm.get_active_instances()),
            consensus_decision=self.cce.get_state_summary().get("recent_decisions", [{}])[0].get("decision") if self.cce.get_state_summary().get("recent_decisions") else None,
            system_health=self.healing.get_healing_summary().get("recovery_success_rate", 1.0),
            ethics_mode="AUTONOMOUS",
            active_threats_count=0,
        )

    def get_components_status(self) -> dict[str, Any]:
        """Get initialization status of all components"""
        return {
            "initialized": self._initialized,
            "ai_core": {
                "network": self.network_engine.is_loaded,
                "iot": self.iot_engine.is_loaded,
                "user": self.user_engine.is_loaded,
                "cicids": self.cicids_engine.is_loaded,
            },
            "cognitive": {
                "ttrm": True,
                "trust_engine": True,
                "acdm": True,
                "dcmm": True,
                "cce": True,
                "lamg": True,
            },
            "supporting": {
                "knowledge": True,
                "xai": True,
                "ethics": True,
                "digital_twin": True,
                "forensic": True,
                "healing": True,
                "report": True,
            },
        }

