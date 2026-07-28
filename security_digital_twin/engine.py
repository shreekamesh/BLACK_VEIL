"""
BLACK VEIL V5 — Security Digital Twin
System state simulation for response impact prediction, trust trajectory simulation,
and what-if analysis before deploying security actions

Mathematical Model:
    ΔT_twin(action) = T̂(t+τ) - T̂(t)         (simulated change)
    Prediction Error: PE = ||T_actual - T_twin||
    Twin Update: T_twin(t+1) = f(T_twin(t), PE(t))
    Deploy if: ΔT_twin > -δ  AND  P_recovery > ρ
"""
import copy
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TwinState:
    """A snapshot of the digital twin state"""
    state_id: str
    trust_scores: dict[str, float]
    risk_level: str
    agent_statuses: dict[str, str]
    active_threats: list[dict[str, Any]]
    deception_active: list[dict[str, Any]]
    timestamp: str


@dataclass
class SimulationResult:
    """Result of a digital twin simulation"""
    simulation_id: str
    action_simulated: str
    predicted_trust_delta: float
    predicted_risk: float
    predicted_threat_level: str
    recovery_probability: float
    confidence: float
    is_safe_to_deploy: bool
    recommendation: str
    timestamp: str


class DigitalTwinEngine:
    """
    Security Digital Twin for safe simulation of response actions.
    
    Creates a sandboxed copy of the current security state and simulates
    the impact of proposed actions before real-world deployment.
    """

    def __init__(self):
        self._current_state: Optional[TwinState] = None
        self._simulations: list[SimulationResult] = []
        self._simulation_accuracy: list[float] = []

        logger.info("Digital Twin Engine initialized")

    def sync_state(
        self,
        trust_scores: dict[str, float],
        risk_level: str,
        agent_statuses: dict[str, str],
        active_threats: Optional[list[dict[str, Any]]] = None,
        deception_active: Optional[list[dict[str, Any]]] = None,
    ) -> TwinState:
        """Sync current system state into the digital twin"""
        state = TwinState(
            state_id=str(uuid.uuid4()),
            trust_scores=trust_scores.copy(),
            risk_level=risk_level,
            agent_statuses=agent_statuses.copy(),
            active_threats=active_threats or [],
            deception_active=deception_active or [],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._current_state = state
        logger.info("Digital Twin state synced")
        return state

    def simulate_action(
        self,
        action_type: str,           # BLOCK, ISOLATE, ROTATE, DEPLOY_DECEPTION, RECOVER
        action_params: dict[str, Any],
    ) -> SimulationResult:
        """
        Simulate a security action in the twin environment.
        
        ΔT_twin(action) = T̂(t+τ) - T̂(t)
        """
        if not self._current_state:
            raise RuntimeError("No state synced. Call sync_state first.")

        sim_id = str(uuid.uuid4())

        # Simulate trust impact based on action type
        trust_delta, recovery_prob = self._simulate_trust_impact(
            action_type, action_params
        )

        # Simulate risk change
        current_avg_trust = (
            sum(self._current_state.trust_scores.values())
            / max(1, len(self._current_state.trust_scores))
        )
        predicted_trust = max(0, min(100, current_avg_trust + trust_delta))
        predicted_risk = 100.0 - predicted_trust

        # Determine threat level
        if predicted_risk >= 80:
            predicted_threat = "CRITICAL"
        elif predicted_risk >= 55:
            predicted_threat = "HIGH"
        elif predicted_risk >= 25:
            predicted_threat = "MEDIUM"
        else:
            predicted_threat = "LOW"

        # Decision: deploy if trust doesn't drop too much and recovery is likely
        is_safe = trust_delta > -10.0 and recovery_prob > 0.5

        if is_safe:
            recommendation = f"DEPLOY — Trust impact: {trust_delta:+.1f}, Recovery probability: {recovery_prob:.1%}"
        else:
            recommendation = (
                f"MODIFY or REJECT — "
                f"Trust impact: {trust_delta:+.1f}, "
                f"Recovery probability: {recovery_prob:.1%}"
            )

        result = SimulationResult(
            simulation_id=sim_id,
            action_simulated=action_type,
            predicted_trust_delta=round(trust_delta, 2),
            predicted_risk=round(predicted_risk, 2),
            predicted_threat_level=predicted_threat,
            recovery_probability=round(recovery_prob, 4),
            confidence=round(0.5 + recovery_prob * 0.5, 4),
            is_safe_to_deploy=is_safe,
            recommendation=recommendation,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self._simulations.append(result)

        logger.info(
            f"Simulation: {action_type} (trust_delta={trust_delta:+.1f}, "
            f"safe={is_safe})"
        )

        return result

    def record_accuracy(
        self, predicted_trust: float, actual_trust: float
    ) -> None:
        """Record prediction accuracy for twin fidelity tracking"""
        error = abs(predicted_trust - actual_trust)
        self._simulation_accuracy.append(error)
        # Keep last 100
        if len(self._simulation_accuracy) > 100:
            self._simulation_accuracy = self._simulation_accuracy[-100:]

    def _simulate_trust_impact(
        self, action_type: str, params: dict[str, Any]
    ) -> tuple[float, float]:
        """
        Simulate the trust impact of an action.
        
        Returns: (trust_delta, recovery_probability)
        """
        if action_type == "BLOCK":
            # Blocking traffic slightly improves trust (reduces risk)
            return (5.0, 0.9)

        elif action_type == "ISOLATE":
            # Isolation has immediate negative trust but high recovery
            severity = params.get("severity", "MEDIUM")
            impact = {"LOW": -2.0, "MEDIUM": -5.0, "HIGH": -10.0, "CRITICAL": -15.0}
            return (impact.get(severity, -5.0), 0.85)

        elif action_type == "ROTATE":
            # Credential rotation slightly dips then recovers
            return (-1.0, 0.95)

        elif action_type == "DEPLOY_DECEPTION":
            # Deception has no trust impact (transparent)
            return (1.0, 1.0)

        elif action_type == "RECOVER":
            # Active recovery
            magnitude = params.get("recovery_magnitude", 10.0)
            return (min(30.0, magnitude), 0.7)

        else:
            return (0.0, 0.5)

    def get_simulation_history(
        self, limit: int = 10
    ) -> list[SimulationResult]:
        """Get recent simulation results"""
        return self._simulations[-limit:]

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of Digital Twin state"""
        return {
            "state_synced": self._current_state is not None,
            "total_simulations": len(self._simulations),
            "avg_prediction_error": (
                round(sum(self._simulation_accuracy) / max(1, len(self._simulation_accuracy)), 2)
                if self._simulation_accuracy
                else 0.0
            ),
            "current_trust_avg": (
                round(sum(self._current_state.trust_scores.values()) / max(1, len(self._current_state.trust_scores)), 2)
                if self._current_state
                else 0.0
            ),
        }

