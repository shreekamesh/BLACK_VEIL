"""
BLACK VEIL V2 — Database Package
SQLAlchemy ORM models, connection management, and configuration
"""
from database.config import DatabaseConfig
from database.connection import DatabaseManager
from database.models import (
    Base,
    Agent,
    TrustScore,
    TemporalRecoveryLog,
    ThreatEvent,
    DeceptionEvent,
    ResponseAction,
    FakeCredential,
    ForensicEvent,
    UserActivityLog,
    ThreatHeatmap,
    ModelRegistry
)

__all__ = [
    "DatabaseConfig",
    "DatabaseManager",
    "Base",
    "Agent",
    "TrustScore",
    "TemporalRecoveryLog",
    "ThreatEvent",
    "DeceptionEvent",
    "ResponseAction",
    "FakeCredential",
    "ForensicEvent",
    "UserActivityLog",
    "ThreatHeatmap",
    "ModelRegistry",
]

