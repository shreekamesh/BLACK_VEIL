"""
BLACK VEIL V5 - Trust & Cognitive Network Endpoints
ATCN: Adaptive Trust Cognitive Network operations
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db
from src.backend.models.database_models import (
    TrustRelationship,
    TrustEvent,
)
from src.backend.models.response_models import TrustResponse, TrustHistory
from src.backend.utils.metrics import update_trust_score

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Trust & Cognitive"])


class TrustCalculationRequest(BaseModel):
    """Trust calculation request payload"""
    entity_id: str = Field(..., description="Entity to calculate trust for")
    scores: Optional[dict] = Field(None, description="Domain-specific trust scores")
    context: Optional[dict] = Field(None, description="Contextual factors")


@router.post("/calculate", response_model=TrustResponse)
async def calculate_trust(
    request: TrustCalculationRequest,
):
    """Calculate trust score using ATCN (Adaptive Trust Cognitive Network)"""
    from src.ai_foundation.ensemble.confidence_calibrator import ConfidenceCalibrator

    calibrator = ConfidenceCalibrator()

    # Simulate trust calculation (replace with actual ATCN logic)
    trust_score = 75.0
    risk_score = 25.0
    confidence = 0.85

    # Determine trust level
    if trust_score >= 80:
        trust_level = "VERY_HIGH"
    elif trust_score >= 60:
        trust_level = "HIGH"
    elif trust_score >= 40:
        trust_level = "MEDIUM"
    elif trust_score >= 20:
        trust_level = "LOW"
    else:
        trust_level = "CRITICAL"

    return TrustResponse(
        entity_id=request.entity_id,
        trust_score=trust_score,
        trust_level=trust_level,
        confidence=confidence,
        risk_score=risk_score,
        trust_dna={
            "network": trust_score * 0.3,
            "iot": trust_score * 0.25,
            "user": trust_score * 0.25,
            "cicids": trust_score * 0.20,
        },
        contributing_factors={
            "historical_behavior": 0.4,
            "recent_activity": 0.3,
            "context_score": 0.2,
            "peer_consensus": 0.1,
        },
        explanation=f"Trust score {trust_score:.1f} calculated from multi-domain ATCN analysis",
    )


@router.get("/score/{entity_id}")
async def get_trust_score(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get current trust score for an entity"""
    result = await db.execute(
        select(TrustRelationship).where(
            TrustRelationship.target_id == entity_id,
            TrustRelationship.is_active == True,
        )
    )
    relationship = result.scalar_one_or_none()

    if not relationship:
        raise HTTPException(status_code=404, detail=f"No trust data for entity: {entity_id}")

    return {
        "entity_id": entity_id,
        "trust_score": relationship.trust_score,
        "previous_trust": relationship.previous_trust,
        "interaction_count": relationship.interaction_count,
        "last_interaction": relationship.last_interaction.isoformat() if relationship.last_interaction else None,
    }


@router.get("/history/{entity_id}", response_model=TrustHistory)
async def get_trust_history(
    entity_id: str,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Get trust score history for an entity"""
    result = await db.execute(
        select(TrustEvent)
        .where(TrustEvent.entity_id == entity_id)
        .order_by(desc(TrustEvent.created_at))
        .limit(limit)
    )
    events = result.scalars().all()

    scores = [
        {
            "timestamp": e.created_at.isoformat(),
            "trust_score": e.trust_after,
            "change": e.delta,
            "reason": e.reason,
            "event_type": e.event_type,
        }
        for e in events
    ]

    return TrustHistory(
        entity_id=entity_id,
        scores=scores,
        count=len(scores),
    )


@router.get("/graph")
async def get_trust_graph(
    db: AsyncSession = Depends(get_db),
):
    """Get all trust relationships as a graph"""
    result = await db.execute(
        select(TrustRelationship).where(TrustRelationship.is_active == True)
    )
    relationships = result.scalars().all()

    return {
        "nodes": list(set(
            [r.source_id for r in relationships] +
            [r.target_id for r in relationships]
        )),
        "edges": [
            {
                "source": r.source_id,
                "target": r.target_id,
                "trust_score": r.trust_score,
                "type": r.relationship_type,
            }
            for r in relationships
        ],
        "count": len(relationships),
    }


@router.get("/summary")
async def get_trust_summary(
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated trust summary"""
    result = await db.execute(
        select(
            func.avg(TrustRelationship.trust_score).label("avg_trust"),
            func.count(TrustRelationship.id).label("total_relationships"),
        ).where(TrustRelationship.is_active == True)
    )
    row = result.one()

    # Count by trust level
    level_counts = {}
    for level in ["CRITICAL", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]:
        level_result = await db.execute(
            select(func.count(TrustRelationship.id)).where(
                TrustRelationship.is_active == True,
                TrustRelationship.trust_score < (
                    20 if level == "CRITICAL" else
                    40 if level == "LOW" else
                    60 if level == "MEDIUM" else
                    80 if level == "HIGH" else 101
                ),
                TrustRelationship.trust_score >= (
                    0 if level == "CRITICAL" else
                    20 if level == "LOW" else
                    40 if level == "MEDIUM" else
                    60 if level == "HIGH" else 80
                ),
            )
        )
        level_counts[level] = level_result.scalar() or 0

    return {
        "avg_trust": round(row.avg_trust, 2) if row.avg_trust else 0,
        "total_relationships": row.total_relationships,
        "by_level": level_counts,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
