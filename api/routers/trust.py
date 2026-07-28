"""
BLACK VEIL V2 — Trust Score Endpoints
Query and manage trust scores for agents across all domains
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc

from database.connection import db_manager
from database.models import TrustScore, Agent
from security.auth import get_current_user
from security.rbac import Permission, require_permission

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Trust"])


@router.get("/scores/{agent_id}")
async def get_trust_scores(
    agent_id: str,
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
):
    """Get trust score history for an agent"""
    async with db_manager.get_session() as session:
        stmt = (
            select(TrustScore)
            .where(TrustScore.agent_id == agent_id)
            .order_by(desc(TrustScore.timestamp))
            .limit(limit)
        )
        result = await session.execute(stmt)
        scores = result.scalars().all()

    if not scores:
        raise HTTPException(status_code=404, detail=f"No trust scores for agent: {agent_id}")

    return {
        "agent_id": agent_id,
        "count": len(scores),
        "scores": [
            {
                "id": s.id,
                "domain": s.domain,
                "trust_score": s.trust_score,
                "risk_score": s.risk_score,
                "threat_level": s.threat_level,
                "confidence": s.confidence,
                "timestamp": s.timestamp.isoformat(),
            }
            for s in scores
        ],
    }


@router.get("/latest")
async def get_latest_trust_scores(
    domain: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Get latest trust scores for all agents (optionally filtered by domain)"""
    async with db_manager.get_session() as session:
        stmt = select(TrustScore).distinct(TrustScore.agent_id).order_by(
            TrustScore.agent_id, desc(TrustScore.timestamp)
        )
        if domain:
            stmt = stmt.where(TrustScore.domain == domain)
        result = await session.execute(stmt)
        scores = result.scalars().all()

    return {
        "count": len(scores),
        "scores": [
            {
                "agent_id": s.agent_id,
                "domain": s.domain,
                "trust_score": s.trust_score,
                "risk_score": s.risk_score,
                "threat_level": s.threat_level,
                "timestamp": s.timestamp.isoformat(),
            }
            for s in scores
        ],
    }


@router.post("/scores")
async def record_trust_score(
    trust_data: dict,
    current_user: dict = Depends(get_current_user),
):
    """Record a new trust score (used by AI agents)"""
    required = ["agent_id", "domain", "trust_score", "risk_score", "threat_level", "confidence"]
    for field in required:
        if field not in trust_data:
            raise HTTPException(status_code=422, detail=f"Missing field: {field}")

    score = TrustScore(
        agent_id=trust_data["agent_id"],
        domain=trust_data["domain"],
        trust_score=trust_data["trust_score"],
        risk_score=trust_data["risk_score"],
        threat_level=trust_data["threat_level"],
        confidence=trust_data["confidence"],
        trust_dna_json=trust_data.get("trust_dna"),
        model_version=trust_data.get("model_version"),
        data_source=trust_data.get("data_source"),
    )

    async with db_manager.get_session() as session:
        session.add(score)

    return {
        "status": "recorded",
        "id": score.id,
        "timestamp": score.timestamp.isoformat(),
    }


@router.delete("/scores/{agent_id}")
async def clear_trust_history(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Clear trust score history for an agent"""
    async with db_manager.get_session() as session:
        stmt = select(TrustScore).where(TrustScore.agent_id == agent_id)
        result = await session.execute(stmt)
        scores = result.scalars().all()
        for s in scores:
            await session.delete(s)

    return {
        "status": "cleared",
        "agent_id": agent_id,
        "deleted_count": len(scores),
    }
