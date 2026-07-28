"""
BLACK VEIL V5 - Deception Engine Endpoints
ACDM: Adaptive Cyber Deception Model operations
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db
from src.backend.models.database_models import DeceptionInstance
from src.backend.models.response_models import DeceptionResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Deception"])


@router.post("/deploy", summary="Deploy a new deception technique")
async def deploy_deception(
    config: dict,
    db: AsyncSession = Depends(get_db),
):
    """Deploy a new deception technique (ACDM)"""
    deception = DeceptionInstance(
        deception_type=config.get("deception_type", "HONEYPOT"),
        deception_subtype=config.get("deception_subtype"),
        target_entity=config.get("target_entity"),
        status="active",
        effectiveness_score=config.get("initial_effectiveness", 0.7),
        detection_probability=config.get("initial_detection_prob", 0.1),
        payload_json=config.get("payload"),
        config_json=config.get("config"),
        generation=1,
    )
    db.add(deception)
    await db.commit()

    logger.info(
        "Deception deployed: %s (type=%s, target=%s)",
        deception.deception_id, deception.deception_type, deception.target_entity,
    )

    return {
        "status": "deployed",
        "deception_id": deception.deception_id,
        "type": deception.deception_type,
        "generation": deception.generation,
        "timestamp": deception.deployed_at.isoformat(),
    }


@router.get("/", summary="List all deception instances")
async def list_deceptions(
    status: Optional[str] = Query(None),
    deception_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List all deception instances with optional filters"""
    stmt = select(DeceptionInstance)
    if status:
        stmt = stmt.where(DeceptionInstance.status == status)
    if deception_type:
        stmt = stmt.where(DeceptionInstance.deception_type == deception_type)
    stmt = stmt.order_by(desc(DeceptionInstance.deployed_at)).limit(limit)

    result = await db.execute(stmt)
    deceptions = result.scalars().all()

    return {
        "count": len(deceptions),
        "deceptions": [
            {
                "id": d.deception_id,
                "type": d.deception_type,
                "subtype": d.deception_subtype,
                "status": d.status,
                "effectiveness": d.effectiveness_score,
                "detection_prob": d.detection_probability,
                "interactions": d.interaction_count,
                "generation": d.generation,
                "deployed_at": d.deployed_at.isoformat(),
            }
            for d in deceptions
        ],
    }


@router.get("/{deception_id}", response_model=DeceptionResponse)
async def get_deception(
    deception_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific deception instance"""
    result = await db.execute(
        select(DeceptionInstance).where(
            DeceptionInstance.deception_id == deception_id
        )
    )
    deception = result.scalar_one_or_none()

    if not deception:
        raise HTTPException(status_code=404, detail=f"Deception not found: {deception_id}")

    return DeceptionResponse(
        deception_id=deception.deception_id,
        deception_type=deception.deception_type,
        status=deception.status,
        effectiveness_score=deception.effectiveness_score,
        detection_probability=deception.detection_probability,
        interaction_count=deception.interaction_count,
        generation=deception.generation,
        deployed_at=deception.deployed_at,
        payload_summary={
            "subtype": deception.deception_subtype,
            "target": deception.target_entity,
        },
    )


@router.put("/{deception_id}/evolve")
async def evolve_deception(
    deception_id: str,
    evolution_config: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
):
    """Evolve a deception technique to the next generation"""
    result = await db.execute(
        select(DeceptionInstance).where(
            DeceptionInstance.deception_id == deception_id
        )
    )
    deception = result.scalar_one_or_none()

    if not deception:
        raise HTTPException(status_code=404, detail=f"Deception not found: {deception_id}")

    # Increment generation
    deception.generation += 1
    deception.status = "active" if deception.status == "evolved" else deception.status

    # Apply evolution if config provided
    if evolution_config:
        if "effectiveness" in evolution_config:
            deception.effectiveness_score = evolution_config["effectiveness"]
        if "detection_prob" in evolution_config:
            deception.detection_probability = evolution_config["detection_prob"]

    # Track parent
    parent_id = deception.id

    # Create new evolved instance
    evolved = DeceptionInstance(
        deception_id=f"{deception_id}_gen{deception.generation}",
        deception_type=deception.deception_type,
        deception_subtype=deception.deception_subtype,
        target_entity=deception.target_entity,
        status="active",
        effectiveness_score=deception.effectiveness_score,
        detection_probability=deception.detection_probability,
        generation=deception.generation,
        parent_id=parent_id,
        payload_json=deception.payload_json,
        config_json=evolution_config,
    )
    db.add(evolved)

    # Mark old as evolved
    deception.status = "evolved"
    await db.commit()

    return {
        "status": "evolved",
        "deception_id": evolved.deception_id,
        "new_generation": evolved.generation,
        "effectiveness": evolved.effectiveness_score,
        "detection_prob": evolved.detection_probability,
        "timestamp": evolved.deployed_at.isoformat(),
    }


@router.post("/{deception_id}/interact")
async def record_interaction(
    deception_id: str,
    interaction_data: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
):
    """Record an attacker interaction with a deception"""
    result = await db.execute(
        select(DeceptionInstance).where(
            DeceptionInstance.deception_id == deception_id
        )
    )
    deception = result.scalar_one_or_none()

    if not deception:
        raise HTTPException(status_code=404, detail=f"Deception not found: {deception_id}")

    deception.interaction_count += 1
    deception.last_interaction = datetime.now(timezone.utc)

    # Update effectiveness based on interaction
    if interaction_data and interaction_data.get("detected"):
        deception.detection_probability = min(
            1.0, deception.detection_probability + 0.1
        )
        deception.effectiveness_score = max(
            0.0, deception.effectiveness_score - 0.05
        )
    else:
        deception.effectiveness_score = min(
            1.0, deception.effectiveness_score + 0.02
        )

    await db.commit()

    return {
        "status": "recorded",
        "deception_id": deception_id,
        "interaction_count": deception.interaction_count,
        "effectiveness": deception.effectiveness_score,
        "detection_prob": deception.detection_probability,
    }
