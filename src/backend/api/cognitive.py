"""
BLACK VEIL V5 - Cognitive Layer Endpoints
Perception, Reasoning, Memory, and Meta-Cognitive operations
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db
from src.backend.models.database_models import CognitiveState
from src.backend.models.response_models import CognitiveStateResponse
from src.backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Cognitive Layer"])


@router.get("/state/{state_type}")
async def get_cognitive_state(
    state_type: str,
    current_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Get the current cognitive state by type"""
    stmt = select(CognitiveState).where(
        CognitiveState.state_type == state_type,
    )
    if current_only:
        stmt = stmt.where(CognitiveState.is_current == True)
    stmt = stmt.order_by(desc(CognitiveState.created_at)).limit(1)

    result = await db.execute(stmt)
    state = result.scalar_one_or_none()

    if not state:
        raise HTTPException(status_code=404, detail=f"No state found for type: {state_type}")

    return {
        "state_id": state.id,
        "state_type": state.state_type,
        "state_data": state.state_data,
        "schema_version": state.schema_version,
        "is_current": state.is_current,
        "created_at": state.created_at.isoformat(),
    }


@router.post("/state/{state_type}")
async def update_cognitive_state(
    state_type: str,
    state_data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update the cognitive state for a type"""
    # Deactivate current state
    result = await db.execute(
        select(CognitiveState).where(
            CognitiveState.state_type == state_type,
            CognitiveState.is_current == True,
        )
    )
    for current in result.scalars().all():
        current.is_current = False

    # Create new state
    new_state = CognitiveState(
        state_type=state_type,
        state_data=state_data,
        is_current=True,
    )
    db.add(new_state)
    await db.commit()

    return {
        "status": "updated",
        "state_id": new_state.id,
        "state_type": state_type,
        "timestamp": new_state.created_at.isoformat(),
    }


@router.get("/perception")
async def get_perception_state():
    """Get current perception layer state"""
    return {
        "state": "active",
        "sensors": ["network", "system", "endpoint", "cloud", "threat_intel"],
        "last_update": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/reasoning")
async def get_reasoning_state():
    """Get current reasoning layer state"""
    return {
        "state": "active",
        "engines": ["context", "pattern", "causal", "decision"],
        "last_update": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/memory")
async def get_memory_state():
    """Get current memory layer state"""
    return {
        "state": "active",
        "memory_types": ["episodic", "semantic", "procedural"],
        "total_memories": 1250,
        "last_update": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/meta-cognitive")
async def get_meta_cognitive_state():
    """Get meta-cognitive monitoring state"""
    return {
        "state": "monitoring",
        "awareness_level": "high",
        "anomalies_detected": 0,
        "self_health_checks": {
            "perception": "healthy",
            "reasoning": "healthy",
            "memory": "healthy",
            "decision": "healthy",
        },
        "last_update": datetime.now(timezone.utc).isoformat(),
    }
