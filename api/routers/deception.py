"""
BLACK VEIL V2 — Deception Engine Endpoints
Manage honeypots, fake credentials, and cyber deception operations
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc

from database.connection import db_manager
from database.models import DeceptionEvent, FakeCredential
from security.auth import get_current_user
from security.rbac import Permission, require_permission

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Deception"])


@router.post("/deploy")
async def deploy_deception(
    config: dict,
    current_user: dict = Depends(get_current_user),
):
    """Deploy a new deception technique"""
    deception = DeceptionEvent(
        deception_id=config.get("deception_id"),
        deception_type=config.get("deception_type", "HONEYPOT"),
        deception_subtype=config.get("deception_subtype"),
        target_agent=config.get("target_agent"),
        status="ACTIVE",
        payload_json=config.get("payload"),
    )

    async with db_manager.get_session() as session:
        session.add(deception)

    return {
        "status": "deployed",
        "deception_id": deception.deception_id,
        "type": deception.deception_type,
        "timestamp": deception.deployed_at.isoformat(),
    }


@router.get("/active")
async def get_active_deceptions(
    deception_type: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Get all active deception deployments"""
    async with db_manager.get_session() as session:
        stmt = select(DeceptionEvent).where(DeceptionEvent.status == "ACTIVE")
        if deception_type:
            stmt = stmt.where(DeceptionEvent.deception_type == deception_type)
        stmt = stmt.order_by(desc(DeceptionEvent.deployed_at))
        result = await session.execute(stmt)
        deceptions = result.scalars().all()

    return {
        "count": len(deceptions),
        "deceptions": [
            {
                "id": d.deception_id,
                "type": d.deception_type,
                "subtype": d.deception_subtype,
                "status": d.status,
                "generation": d.generation,
                "effectiveness": d.effectiveness,
                "interactions": d.interaction_count,
                "deployed_at": d.deployed_at.isoformat(),
            }
            for d in deceptions
        ],
    }


@router.put("/{deception_id}/mutate")
async def mutate_deception(
    deception_id: str,
    mutation_config: Optional[dict] = None,
    current_user: dict = Depends(get_current_user),
):
    """Trigger mutation of a deception technique (Algorithm 5/6)"""
    async with db_manager.get_session() as session:
        stmt = select(DeceptionEvent).where(
            DeceptionEvent.deception_id == deception_id
        )
        result = await session.execute(stmt)
        deception = result.scalar_one_or_none()

        if not deception:
            raise HTTPException(status_code=404, detail=f"Deception not found: {deception_id}")

        deception.generation += 1
        deception.status = "EVOLVED"

    return {
        "status": "mutated",
        "deception_id": deception_id,
        "new_generation": deception.generation,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/credentials")
async def get_fake_credentials(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Get all managed fake credentials"""
    async with db_manager.get_session() as session:
        stmt = select(FakeCredential)
        if status:
            stmt = stmt.where(FakeCredential.status == status)
        stmt = stmt.order_by(desc(FakeCredential.created_at))
        result = await session.execute(stmt)
        creds = result.scalars().all()

    return {
        "count": len(creds),
        "credentials": [
            {
                "id": c.credential_id,
                "service": c.service_name,
                "type": c.credential_type,
                "status": c.status,
                "generation": c.generation,
                "fitness": c.fitness_score,
                "mutations": c.mutated_count,
                "lifetime_sec": c.lifetime_sec,
                "created_at": c.created_at.isoformat(),
            }
            for c in creds
        ],
    }


from datetime import datetime, timezone
