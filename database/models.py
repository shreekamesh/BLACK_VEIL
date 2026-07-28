"""
BLACK VEIL V2 — SQLAlchemy ORM Models

All database tables defined as SQLAlchemy 2.0 declarative models.
Covers: agents, trust_scores, temporal_recovery_log, threat_events,
deception_events, response_actions, fake_credentials, forensic_events,
user_activity_log, threat_heatmap, model_registry
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass


def utcnow() -> datetime:
    """Return current UTC datetime"""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate UUID string"""
    return str(uuid.uuid4())


# ── Agent ───────────────────────────────────────────────────────

class Agent(Base):
    """AI agent registered in the BLACK VEIL system"""
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    agent_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="network | iot | user | cicids | fusion | decision | trust | response"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="ACTIVE",
        comment="ACTIVE | SUSPENDED | COMPROMISED | RECOVERING"
    )
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    config_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    trust_scores = relationship("TrustScore", back_populates="agent", lazy="selectin")
    recovery_logs = relationship("TemporalRecoveryLog", back_populates="agent", lazy="selectin")
    threat_events = relationship("ThreatEvent", back_populates="agent", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name={self.name}, type={self.agent_type}, status={self.status})>"


# ── Trust Scores ────────────────────────────────────────────────

class TrustScore(Base):
    """Trust score record for an agent at a point in time"""
    __tablename__ = "trust_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("agents.id"), nullable=False, index=True
    )
    domain: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="network | iot | user | cicids | composite"
    )
    trust_score: Mapped[float] = mapped_column(
        Float, nullable=False,
        comment="Trust score 0.0 - 100.0"
    )
    risk_score: Mapped[float] = mapped_column(
        Float, nullable=False,
        comment="Risk score 0.0 - 100.0"
    )
    threat_level: Mapped[str] = mapped_column(
        String(16), nullable=False,
        comment="LOW | MEDIUM | HIGH | CRITICAL"
    )
    confidence: Mapped[float] = mapped_column(
        Float, nullable=False,
        comment="Confidence in trust score 0.0 - 1.0"
    )
    trust_dna_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True,
        comment="Full Trust DNA vector as JSON"
    )
    model_version: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    data_source: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )

    # Relationships
    agent = relationship("Agent", back_populates="trust_scores")

    __table_args__ = (
        {"comment": "Trust score history for all agents across domains"}
    )

    def __repr__(self) -> str:
        return (
            f"<TrustScore(agent={self.agent_id}, domain={self.domain}, "
            f"trust={self.trust_score:.1f}, threat={self.threat_level})>"
        )


# ── Temporal Recovery Log ──────────────────────────────────────

class TemporalRecoveryLog(Base):
    """Log of trust recovery events"""
    __tablename__ = "temporal_recovery_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("agents.id"), nullable=False, index=True
    )
    recovery_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="AUTO | MANUAL | TRIGGERED"
    )
    previous_trust: Mapped[float] = mapped_column(
        Float, nullable=False,
        comment="Trust score before recovery"
    )
    current_trust: Mapped[float] = mapped_column(
        Float, nullable=False,
        comment="Trust score after recovery"
    )
    recovery_action: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    drift_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    drift_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recovery_prob: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Estimated recovery probability 0.0 - 1.0"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    duration_sec: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    success: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    details_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="recovery_logs")

    def __repr__(self) -> str:
        return (
            f"<RecoveryLog(agent={self.agent_id}, type={self.recovery_type}, "
            f"{self.previous_trust:.1f}→{self.current_trust:.1f})>"
        )


# ── Threat Events ──────────────────────────────────────────────

class ThreatEvent(Base):
    """Detected threat event from any domain"""
    __tablename__ = "threat_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("agents.id"), nullable=False, index=True
    )
    threat_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, default=generate_uuid
    )
    threat_type: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="e.g., SQL_INJECTION, PORT_SCAN, MALWARE, INSIDER_THREAT"
    )
    severity: Mapped[str] = mapped_column(
        String(16), nullable=False,
        comment="LOW | MEDIUM | HIGH | CRITICAL"
    )
    confidence: Mapped[float] = mapped_column(
        Float, nullable=False,
        comment="Detection confidence 0.0 - 1.0"
    )
    source_ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    destination_ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    protocol: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mitre_technique: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True,
        comment="MITRE ATT&CK technique ID (e.g., T1190)"
    )
    mitre_tactic: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True,
        comment="MITRE ATT&CK tactic"
    )
    payload_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="threat_events")
    deception_events = relationship("DeceptionEvent", back_populates="threat", lazy="selectin")
    response_actions = relationship("ResponseAction", back_populates="threat", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<ThreatEvent(id={self.threat_id}, type={self.threat_type}, "
            f"severity={self.severity})>"
        )


# ── Deception Events ───────────────────────────────────────────

class DeceptionEvent(Base):
    """Deployment and interaction log for cyber deception"""
    __tablename__ = "deception_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    threat_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("threat_events.id"), nullable=True
    )
    deception_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, default=generate_uuid
    )
    deception_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="HONEYPOT | FAKE_CREDENTIAL | DECOY_SERVICE | NETWORK_DECEPTION"
    )
    deception_subtype: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True,
        comment="e.g., SSH_HONEYPOT, WEB_HONEYPOT, API_CREDENTIAL"
    )
    target_agent: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("agents.id"), nullable=True
    )
    generation: Mapped[int] = mapped_column(
        Integer, default=1,
        comment="Evolution generation counter (ACDM)"
    )
    attacker_ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    effectiveness: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Current effectiveness score 0.0 - 1.0"
    )
    detection_prob: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Estimated detection probability 0.0 - 1.0"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="ACTIVE",
        comment="ACTIVE | TRIGGERED | EXPIRED | EVOLVED"
    )
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    deployed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expired_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    payload_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    response_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    threat = relationship("ThreatEvent", back_populates="deception_events")

    def __repr__(self) -> str:
        return (
            f"<DeceptionEvent(id={self.deception_id}, type={self.deception_type}, "
            f"status={self.status}, gen={self.generation})>"
        )


# ── Response Actions ───────────────────────────────────────────

class ResponseAction(Base):
    """Automated response actions executed by the system"""
    __tablename__ = "response_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    threat_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("threat_events.id"), nullable=True
    )
    response_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, default=generate_uuid
    )
    response_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="ISOLATE | BLOCK | ROTATE | ALERT | DEPLOY_DECEPTION | MUTATE_CREDENTIAL"
    )
    target: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    action: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="PENDING",
        comment="PENDING | EXECUTED | FAILED | ROLLED_BACK"
    )
    initiated_by: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("agents.id"), nullable=True
    )
    confidence_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    result_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    threat = relationship("ThreatEvent", back_populates="response_actions")

    def __repr__(self) -> str:
        return (
            f"<ResponseAction(id={self.response_id}, type={self.response_type}, "
            f"status={self.status})>"
        )


# ── Fake Credentials ───────────────────────────────────────────

class FakeCredential(Base):
    """Fake credentials managed by DCMM (Credential Genome Engine)"""
    __tablename__ = "fake_credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    credential_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, default=generate_uuid
    )
    service_name: Mapped[str] = mapped_column(String(128), nullable=False)
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    credential_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="SSH | HTTP | FTP | DB | API"
    )
    genome_sequence: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Full genome sequence (DCMM)"
    )
    genome_entropy: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Shannon entropy of genome"
    )
    fitness_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Current fitness score 0.0 - 1.0"
    )
    mutation_rate: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Current mutation rate 0.0 - 1.0"
    )
    generation: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="ACTIVE",
        comment="ACTIVE | MUTATED | DETECTED | EXPIRED"
    )
    lifetime_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    mutated_count: Mapped[int] = mapped_column(Integer, default=0)
    mutation_history: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("fake_credentials.id"), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<FakeCredential(id={self.credential_id}, service={self.service_name}, "
            f"gen={self.generation}, status={self.status})>"
        )


# ── Forensic Events ────────────────────────────────────────────

class ForensicEvent(Base):
    """Forensic evidence and intelligence events"""
    __tablename__ = "forensic_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, default=generate_uuid
    )
    event_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="TIMELINE_RECONSTRUCTION | IOC_EXTRACTION | PATTERN_MATCH | INTELLIGENCE"
    )
    source: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="Engine that generated this event"
    )
    severity: Mapped[str] = mapped_column(
        String(16), nullable=False,
        comment="INFO | LOW | MEDIUM | HIGH | CRITICAL"
    )
    ioc_list: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True,
        comment="Extracted Indicators of Compromise"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    chain_of_events: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evidence_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    timeline_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    reconstruction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hash_chain: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<ForensicEvent(id={self.event_id}, type={self.event_type}, "
            f"severity={self.severity})>"
        )


# ── User Activity Log ──────────────────────────────────────────

class UserActivityLog(Base):
    """User activity monitoring for insider threat detection"""
    __tablename__ = "user_activity_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="LOGIN | FILE_ACCESS | EMAIL | USB | WEB | COMMAND"
    )
    resource: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    action: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True,
        comment="LOW | MEDIUM | HIGH | CRITICAL"
    )
    trust_impact: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Impact on user trust score (-100 to 100)"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<UserActivity(user={self.user_id}, type={self.activity_type}, "
            f"risk={self.risk_level})>"
        )


# ── Threat Heatmap ────────────────────────────────────────────

class ThreatHeatmap(Base):
    """Aggregated threat data for heatmap visualization"""
    __tablename__ = "threat_heatmap"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    time_slot: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    source_ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    destination_ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    threat_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_severity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threat_types: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True,
        comment="Count per threat type"
    )
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    trust_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("time_slot", "source_ip", "destination_ip",
                         name="uq_heatmap_slot_source_dest"),
    )

    def __repr__(self) -> str:
        return (
            f"<ThreatHeatmap(slot={self.time_slot}, "
            f"count={self.threat_count}, risk={self.risk_score})>"
        )


# ── Model Registry ────────────────────────────────────────────

class ModelRegistry(Base):
    """Registry of trained ML models"""
    __tablename__ = "model_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    model_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="RF | XGBOOST | NN | ENSEMBLE"
    )
    domain: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="network | iot | user | cicids | fusion"
    )
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    feature_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recall: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    training_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    training_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    __table_args__ = (
        UniqueConstraint("model_name", "model_version",
                         name="uq_model_name_version"),
    )

    def __repr__(self) -> str:
        return (
            f"<ModelRegistry(name={self.model_name}, version={self.model_version}, "
            f"active={self.is_active})>"
        )
