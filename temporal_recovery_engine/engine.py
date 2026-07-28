"""
BLACK VEIL V5 — Temporal Trust Recovery Model (TTRM)
IEEE Research Contribution 1: Self-healing trust recovery with evidence-based temporal healing

Mathematical Model:
    Tᵣ(t) = T₀ · e^(-λt) + Σᵢ [Rᵢ · e^(-μ(t - tᵢ))] + D(t) · δ(t)

Key Novelty: First combination of stochastic trust decay with drift-aware compensation
and autonomous recovery triggering in a unified temporal model for multi-agent AI security.
"""
import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TrustDNA:
    """
    Multidimensional temporal trust state vector τ(t) ∈ ℝ⁷.
    
    τ(t) = ⟨n(t), ι(t), υ(t), κ(t), h(t), ξ(t), ρ(t)⟩
    """
    network_trust: float = 50.0       # n(t) — Network Trust (UNSW-NB15)
    iot_trust: float = 50.0           # ι(t) — IoT Trust (EDGE-IoT)
    user_trust: float = 50.0          # υ(t) — User Trust (CERT-r4.2)
    cicids_trust: float = 50.0        # κ(t) — CICIDS Trust (CICIDS2017)
    historical_window: list[float] = field(default_factory=list)  # h(t) — Window w
    context_vector: dict[str, float] = field(default_factory=dict)  # ξ(t)
    recovery_state: float = 0.0       # ρ(t) — 0=stable, 1=active recovery
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_vector(self) -> list[float]:
        """Convert to flat vector for distance computation"""
        return [
            self.network_trust, self.iot_trust, self.user_trust,
            self.cicids_trust, self.recovery_state,
        ]

    def euclidean_distance(self, other: "TrustDNA") -> float:
        """Compute Euclidean distance between two Trust DNA vectors"""
        a = self.to_vector()
        b = other.to_vector()
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def cosine_similarity(self, other: "TrustDNA") -> float:
        """Compute cosine similarity between two Trust DNA vectors"""
        a = self.to_vector()
        b = other.to_vector()
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x ** 2 for x in a))
        norm_b = math.sqrt(sum(y ** 2 for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


@dataclass
class RecoveryEvent:
    """A single recovery event with magnitude and timestamp"""
    magnitude: float           # Rᵢ — Recovery magnitude (0-50)
    timestamp: datetime        # tᵢ — Time of recovery event
    event_type: str            # Type of positive event
    confidence: float = 1.0    # Confidence in this event
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryPlan:
    """Generated recovery plan with steps and timeline"""
    entity_id: str
    current_trust: float
    target_trust: float
    estimated_time_seconds: float
    recovery_steps: list[dict[str, Any]]
    created_at: str
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class TTRMEngine:
    """
    Temporal Trust Recovery Model Engine (Algorithm 2).
    
    Implements:
    - Exponential trust decay with configurable decay constant λ
    - Recovery events with decay constant μ
    - CUSUM-based drift detection
    - Autonomous recovery triggering
    - Recovery plan generation
    
    Configuration (from config.settings.ttrm):
        healing_rate: λ — Trust decay constant (default: 0.02)
        confidence_recovery_rate: μ — Recovery decay constant (default: 0.01)
        max_recovery_time: Maximum recovery window in seconds (default: 86400)
        evidence_weight: Weight of evidence in healing (default: 0.3)
        time_decay_constant: Base time decay in seconds (default: 3600)
        drift_threshold: CUSUM decision threshold h (default: 3.0)
        cusum_allowance: CUSUM allowance k (default: 0.5)
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self._healing_rate = float(self.config.get("healing_rate", 0.02))
        self._confidence_recovery_rate = float(self.config.get("confidence_recovery_rate", 0.01))
        self._max_recovery_time = int(self.config.get("max_recovery_time", 86400))
        self._evidence_weight = float(self.config.get("evidence_weight", 0.3))
        self._time_decay_constant = int(self.config.get("time_decay_constant", 3600))
        self._drift_threshold = float(self.config.get("drift_threshold", 3.0))
        self._cusum_allowance = float(self.config.get("cusum_allowance", 0.5))

        # In-memory stores
        self._trust_history: dict[str, list[float]] = {}
        self._recovery_events: dict[str, list[RecoveryEvent]] = {}
        self._cusum_state: dict[str, float] = {}
        self._dna_states: dict[str, TrustDNA] = {}

        logger.info(
            "TTRM Engine initialized",
            extra={
                "extra": {
                    "healing_rate": self._healing_rate,
                    "confidence_recovery_rate": self._confidence_recovery_rate,
                    "max_recovery_time": self._max_recovery_time,
                }
            },
        )

    # ── Core Trust Computation ────────────────────────────────

    def calculate_trust(
        self,
        entity_id: str,
        initial_trust: float,
        current_time: Optional[datetime] = None,
    ) -> float:
        """
        Calculate current trust score using TTRM (Algorithm 2).
        
        Tᵣ(t) = T₀ · e^(-λt) + Σᵢ [Rᵢ · e^(-μ(t - tᵢ))]
        
        Args:
            entity_id: Entity to calculate trust for
            initial_trust: T₀ — Initial trust score (0-100)
            current_time: Current timestamp (defaults to UTC now)
            
        Returns:
            Recovered trust score clamped to [0, 100]
        """
        now = current_time or datetime.now(timezone.utc)
        events = self._recovery_events.get(entity_id, [])

        # Time decay component: T₀ · e^(-λt)
        time_since_start = self._get_time_since_first_event(entity_id, now)
        decay_component = initial_trust * math.exp(-self._healing_rate * time_since_start)

        # Recovery component: Σᵢ [Rᵢ · e^(-μ(t - tᵢ))]
        recovery_component = 0.0
        for event in events:
            delta = (now - event.timestamp).total_seconds()
            recovery_component += event.magnitude * math.exp(
                -self._confidence_recovery_rate * max(0, delta)
            )

        # Drift compensation: D(t) · δ(t)
        drift_component = self._detect_drift(entity_id, decay_component + recovery_component)

        # Composite trust
        trust = decay_component + recovery_component + drift_component
        trust = max(0.0, min(100.0, trust))

        # Update trust history
        if entity_id not in self._trust_history:
            self._trust_history[entity_id] = []
        self._trust_history[entity_id].append(trust)

        logger.debug(
            f"Trust calculated for {entity_id}: {trust:.2f}",
            extra={
                "extra": {
                    "entity_id": entity_id,
                    "initial_trust": initial_trust,
                    "decay_component": round(decay_component, 2),
                    "recovery_component": round(recovery_component, 2),
                    "drift_component": round(drift_component, 2),
                    "final_trust": round(trust, 2),
                }
            },
        )

        return trust

    def calculate_healing(
        self,
        entity_id: str,
        trust_score: float,
        incident_time: datetime,
        current_time: Optional[datetime] = None,
        evidence: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Calculate trust healing after an incident.
        
        Healing = Time-based healing + Evidence-based healing
        
        Args:
            entity_id: Entity being healed
            trust_score: Current trust score
            incident_time: When the incident occurred
            current_time: Current time (defaults to UTC now)
            evidence: Supporting evidence for healing
            
        Returns:
            Healed trust score
        """
        now = current_time or datetime.now(timezone.utc)
        delta_t = max(0, (now - incident_time).total_seconds())

        # Time-based healing: exponential approach
        time_healing = self._healing_rate * min(delta_t, self._max_recovery_time)
        healing_factor = 1.0 - math.exp(-time_healing / self._time_decay_constant)

        # Evidence-based healing
        evidence_factor = 1.0
        if evidence:
            evidence_score = self._calculate_evidence_score(evidence)
            evidence_factor = 1.0 + self._evidence_weight * evidence_score

        healed_trust = min(100.0, trust_score + (healing_factor * evidence_factor * 10.0))

        logger.info(
            f"Trust healing for {entity_id}: {trust_score:.2f} → {healed_trust:.2f}",
            extra={
                "extra": {
                    "entity_id": entity_id,
                    "delta_t": delta_t,
                    "healing_factor": round(healing_factor, 4),
                    "evidence_factor": round(evidence_factor, 4),
                    "healed_trust": round(healed_trust, 2),
                }
            },
        )

        return healed_trust

    def calculate_confidence_recovery(
        self,
        confidence: float,
        incident_time: datetime,
        current_time: Optional[datetime] = None,
    ) -> float:
        """
        Calculate confidence recovery after an incident.
        Uses exponential recovery: min_confidence + (confidence - min_confidence) * (1 + recovery)
        
        Args:
            confidence: Current confidence level (0-1)
            incident_time: When the incident occurred
            current_time: Current time (defaults to UTC now)
            
        Returns:
            Recovered confidence clamped to [0, 1]
        """
        now = current_time or datetime.now(timezone.utc)
        delta_t = max(0, (now - incident_time).total_seconds())

        recovery = 1.0 - math.exp(-self._confidence_recovery_rate * delta_t)

        min_confidence = 0.3
        max_confidence = 1.0
        recovered = min_confidence + (confidence - min_confidence) * (1.0 + recovery)

        return min(max_confidence, max(0.0, recovered))

    # ── Recovery Event Management ────────────────────────────

    def add_recovery_event(
        self,
        entity_id: str,
        magnitude: float,
        event_type: str = "positive_action",
        confidence: float = 1.0,
        evidence: Optional[dict[str, Any]] = None,
    ) -> RecoveryEvent:
        """
        Add a positive recovery event for an entity.
        
        Args:
            entity_id: Entity to add event for
            magnitude: Rᵢ — Recovery magnitude (0-50)
            event_type: Type of positive event
            confidence: Confidence in this event
            evidence: Supporting evidence
            
        Returns:
            Created RecoveryEvent
        """
        event = RecoveryEvent(
            magnitude=min(50.0, max(0.0, magnitude)),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            confidence=min(1.0, max(0.0, confidence)),
            evidence=evidence or {},
        )

        if entity_id not in self._recovery_events:
            self._recovery_events[entity_id] = []
        self._recovery_events[entity_id].append(event)

        logger.info(
            f"Recovery event added for {entity_id}: mag={magnitude:.2f}, type={event_type}",
            extra={"extra": {"entity_id": entity_id, "event_type": event_type, "magnitude": magnitude}},
        )

        return event

    def get_recovery_events(self, entity_id: str) -> list[RecoveryEvent]:
        """Get all recovery events for an entity"""
        return self._recovery_events.get(entity_id, [])

    def clear_recovery_events(self, entity_id: str) -> None:
        """Clear recovery events for an entity"""
        self._recovery_events.pop(entity_id, None)

    # ── Drift Detection ──────────────────────────────────────

    def detect_drift(self, entity_id: str, current_trust: float) -> dict[str, Any]:
        """
        Detect anomalous drift in trust scores using CUSUM.
        
        CUSUM: g₀ = 0, gₜ = max(0, gₜ₋₁ + |T(t) - T(t-1)| - k)
        Alarm: gₜ > h
        
        Args:
            entity_id: Entity to check
            current_trust: Current trust score
            
        Returns:
            Drift detection result with score and alarm status
        """
        return self._detect_drift(entity_id, current_trust)

    def _detect_drift(self, entity_id: str, current_trust: float) -> float:
        """
        Internal drift detection. Returns drift compensation value.
        """
        history = self._trust_history.get(entity_id, [])

        if len(history) < 2:
            # Initialize CUSUM state
            self._cusum_state[entity_id] = 0.0
            return 0.0

        prev_trust = history[-1]
        change = abs(current_trust - prev_trust)

        # CUSUM update: gₜ = max(0, gₜ₋₁ + change - k)
        g_prev = self._cusum_state.get(entity_id, 0.0)
        g_t = max(0.0, g_prev + change - self._cusum_amount)

        self._cusum_state[entity_id] = g_t

        if g_t > self._drift_threshold:
            # Significant drift detected — apply compensation
            drift_magnitude = change - self._cusum_allowance
            compensation = min(10.0, drift_magnitude * 0.5)
            logger.warning(
                f"Trust drift detected for {entity_id}: CUSUM={g_t:.2f}, compensation={compensation:.2f}"
            )
            return compensation

        return 0.0

    @property
    def _cusum_amount(self) -> float:
        """CUSUM reference value k"""
        return self._cusum_allowance

    # ── Recovery Plan Generation ─────────────────────────────

    def generate_recovery_plan(
        self,
        entity_id: str,
        trust_score: float,
        incident_severity: float = 0.5,
    ) -> RecoveryPlan:
        """
        Generate a trust recovery plan with steps and timeline.
        
        Args:
            entity_id: Entity to recover
            trust_score: Current trust score
            incident_severity: Severity of incident (0-1)
            
        Returns:
            RecoveryPlan with steps and estimated timeline
        """
        target_trust = 90.0

        if trust_score < target_trust:
            recovery_needed = target_trust - trust_score
            estimated_seconds = recovery_needed / (
                self._healing_rate * max(0.1, incident_severity)
            )
            estimated_seconds = min(estimated_seconds, float(self._max_recovery_time))
        else:
            estimated_seconds = 0.0

        # Generate recovery steps
        steps: list[dict[str, Any]] = []
        if estimated_seconds > 0:
            thresholds = [0.3, 0.5, 0.7, 0.9]
            actions = [
                "Intensive monitoring and logging",
                "Gradual permission restoration",
                "Normal operations with enhanced oversight",
                "Full trust restoration",
            ]
            for i, (threshold, action) in enumerate(zip(thresholds, actions)):
                time_to_step = estimated_seconds * threshold
                trigger_trust = trust_score + (target_trust - trust_score) * threshold
                steps.append({
                    "step": i + 1,
                    "action": action,
                    "trigger_trust": round(trigger_trust, 1),
                    "estimated_time_seconds": round(time_to_step),
                    "estimated_time_human": str(timedelta(seconds=round(time_to_step))),
                })

        plan = RecoveryPlan(
            entity_id=entity_id,
            current_trust=round(trust_score, 2),
            target_trust=target_trust,
            estimated_time_seconds=round(estimated_seconds),
            recovery_steps=steps,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        logger.info(
            f"Recovery plan generated for {entity_id}: {estimated_seconds:.0f}s to full recovery",
            extra={"extra": {"entity_id": entity_id, "estimated_seconds": estimated_seconds, "steps": len(steps)}},
        )

        return plan

    # ── Trust DNA Management ─────────────────────────────────

    def compute_trust_dna(
        self,
        entity_id: str,
        network_trust: float = 50.0,
        iot_trust: float = 50.0,
        user_trust: float = 50.0,
        cicids_trust: float = 50.0,
        context: Optional[dict[str, float]] = None,
    ) -> TrustDNA:
        """
        Compute and store a Trust DNA vector for an entity.
        
        Args:
            entity_id: Entity identifier
            network_trust: Network trust score
            iot_trust: IoT trust score
            user_trust: User trust score
            cicids_trust: CICIDS trust score
            context: Optional context vector
            
        Returns:
            Computed TrustDNA
        """
        # Get existing trust history for this entity if available
        history = self._trust_history.get(entity_id, [])

        dna = TrustDNA(
            network_trust=max(0.0, min(100.0, network_trust)),
            iot_trust=max(0.0, min(100.0, iot_trust)),
            user_trust=max(0.0, min(100.0, user_trust)),
            cicids_trust=max(0.0, min(100.0, cicids_trust)),
            historical_window=history[-100:],  # Keep last 100 entries
            context_vector=context or {},
            recovery_state=1.0 if self._recovery_events.get(entity_id) else 0.0,
            timestamp=datetime.now(timezone.utc),
        )

        self._dna_states[entity_id] = dna
        return dna

    def get_trust_dna(self, entity_id: str) -> Optional[TrustDNA]:
        """Get the current Trust DNA for an entity"""
        return self._dna_states.get(entity_id)

    def compare_trust_dna(self, entity_id_1: str, entity_id_2: str) -> dict[str, float]:
        """
        Compare Trust DNA between two entities using multiple distance metrics.
        
        Returns:
            Dict with 'euclidean_distance' and 'cosine_similarity'
        """
        dna1 = self._dna_states.get(entity_id_1)
        dna2 = self._dna_states.get(entity_id_2)

        if not dna1 or not dna2:
            raise ValueError(f"Trust DNA not found for one or both entities: {entity_id_1}, {entity_id_2}")

        return {
            "euclidean_distance": round(dna1.euclidean_distance(dna2), 4),
            "cosine_similarity": round(dna1.cosine_similarity(dna2), 4),
        }

    # ── Internal Helpers ─────────────────────────────────────

    def _calculate_evidence_score(self, evidence: dict[str, Any]) -> float:
        """Calculate evidence weight score from multiple dimensions"""
        score = 0.0
        weights = {
            "user_behavior": 0.4,
            "system_events": 0.3,
            "security_logs": 0.2,
            "external_intel": 0.1,
        }

        for key, weight in weights.items():
            if key in evidence:
                value = evidence[key]
                if isinstance(value, (int, float)):
                    score += weight * min(1.0, abs(value) / 100.0)
                elif isinstance(value, bool):
                    score += weight * (1.0 if value else 0.0)

        return min(1.0, score)

    def _get_time_since_first_event(self, entity_id: str, now: datetime) -> float:
        """Get time since first recovery event for an entity"""
        events = self._recovery_events.get(entity_id, [])
        if not events:
            return 0.0
        first_event_time = min(e.timestamp for e in events)
        return (now - first_event_time).total_seconds()

    # ── State Management ─────────────────────────────────────

    def get_trust_history(self, entity_id: str) -> list[float]:
        """Get trust score history for an entity"""
        return self._trust_history.get(entity_id, [])

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of current TTRM state"""
        return {
            "tracked_entities": len(self._trust_history),
            "recovery_events": sum(len(v) for v in self._recovery_events.values()),
            "config": {
                "healing_rate": self._healing_rate,
                "confidence_recovery_rate": self._confidence_recovery_rate,
                "max_recovery_time": self._max_recovery_time,
                "evidence_weight": self._evidence_weight,
                "drift_threshold": self._drift_threshold,
                "cusum_allowance": self._cusum_allowance,
            },
        }

