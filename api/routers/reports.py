"""
BLACK VEIL V2 — Reporting Endpoints
Generate trust, threat, and system reports
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, func

from database.connection import db_manager
from database.models import TrustScore, ThreatEvent, ResponseAction
from security.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Reports"])


@router.get("/trust/summary")
async def get_trust_summary(
    current_user: dict = Depends(get_current_user),
):
    """Get aggregated trust score summary across all domains"""
    async with db_manager.get_session() as session:
        stmt = select(
            TrustScore.domain,
            func.avg(TrustScore.trust_score).label("avg_trust"),
            func.avg(TrustScore.risk_score).label("avg_risk"),
            func.count(TrustScore.id).label("count"),
            func.max(TrustScore.timestamp).label("latest"),
        ).group_by(TrustScore.domain)

        result = await session.execute(stmt)
        rows = result.all()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "domains": {
            row.domain: {
                "avg_trust": round(row.avg_trust, 2) if row.avg_trust else 0,
                "avg_risk": round(row.avg_risk, 2) if row.avg_risk else 0,
                "sample_count": row.count,
                "latest_update": row.latest.isoformat() if row.latest else None,
            }
            for row in rows
        },
    }


@router.get("/threat/summary")
async def get_threat_summary(
    current_user: dict = Depends(get_current_user),
):
    """Get aggregated threat event summary"""
    async with db_manager.get_session() as session:
        stmt = select(
            ThreatEvent.severity,
            func.count(ThreatEvent.id).label("count"),
            func.max(ThreatEvent.detected_at).label("latest"),
        ).group_by(ThreatEvent.severity)

        result = await session.execute(stmt)
        rows = result.all()

    total_stmt = select(func.count(ThreatEvent.id))
    total_result = await session.execute(total_stmt)
    total = total_result.scalar() or 0

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_events": total,
        "by_severity": {
            row.severity: {
                "count": row.count,
                "latest": row.latest.isoformat() if row.latest else None,
            }
            for row in rows
        },
    }


@router.get("/system/status")
async def get_system_status(
    current_user: dict = Depends(get_current_user),
):
    """Get comprehensive system status report"""
    async with db_manager.get_session() as session:
        # Agent counts
        from database.models import Agent
        agent_stmt = select(Agent.status, func.count(Agent.id)).group_by(Agent.status)
        agent_result = await session.execute(agent_stmt)
        agent_counts = dict(agent_result.all())

        # Recent trust scores
        trust_stmt = select(TrustScore).order_by(desc(TrustScore.timestamp)).limit(5)
        trust_result = await session.execute(trust_stmt)
        recent_trust = trust_result.scalars().all()

        # Recent threats
        threat_stmt = select(ThreatEvent).order_by(desc(ThreatEvent.detected_at)).limit(5)
        threat_result = await session.execute(threat_stmt)
        recent_threats = threat_result.scalars().all()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "agents": {
            "total": sum(agent_counts.values()),
            "by_status": agent_counts,
        },
        "recent_trust_scores": [
            {
                "agent_id": s.agent_id,
                "domain": s.domain,
                "trust_score": s.trust_score,
                "threat_level": s.threat_level,
                "timestamp": s.timestamp.isoformat(),
            }
            for s in recent_trust
        ],
        "recent_threats": [
            {
                "id": t.threat_id,
                "type": t.threat_type,
                "severity": t.severity,
                "confidence": t.confidence,
                "detected_at": t.detected_at.isoformat(),
            }
            for t in recent_threats
        ],
    }
