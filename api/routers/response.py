"""
BLACK VEIL V2 — Response Engine Endpoints
Execute and manage automated security response actions
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc

from database.connection import db_manager
from database.models import ResponseAction, ThreatEvent
from security.auth import get_current_user
from security.rbac import Permission, require_permission

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Response"])


@router.post("/execute")
async def execute_response(
    response_data: dict,
    current_user: dict = Depends(get_current_user),
):
    """Execute a response action against a threat"""
    required = ["response_type", "action"]
    for field in required:
        if field not in response_data:
            raise HTTPException(status_code=422, detail=f"Missing field: {field}")

    response = ResponseAction(
        threat_id=response_data.get("threat_id"),
        response_type=response_data["response_type"],
        target=response_data.get("target"),
        action=response_data["action"],
        status="EXECUTED",
        initiated_by=current_user.get("sub"),
        executed_at=datetime.now(timezone.utc),
        result_json=response_data.get("result"),
    )

    async with db_manager.get_session() as session:
        session.add(response)

    return {
        "status": "executed",
        "response_id": response.response_id,
        "type": response.response_type,
        "action": response.action,
        "timestamp": response.executed_at.isoformat(),
    }


@router.get("/history")
async def get_response_history(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
):
    """Get response action history"""
    async with db_manager.get_session() as session:
        stmt = select(ResponseAction)
        if status:
            stmt = stmt.where(ResponseAction.status == status)
        stmt = stmt.order_by(desc(ResponseAction.executed_at)).limit(limit)
        result = await session.execute(stmt)
        actions = result.scalars().all()

    return {
        "count": len(actions),
        "actions": [
            {
                "id": a.response_id,
                "type": a.response_type,
                "target": a.target,
                "action": a.action,
                "status": a.status,
                "executed_at": a.executed_at.isoformat() if a.executed_at else None,
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            }
            for a in actions
        ],
    }


@router.get("/{response_id}")
async def get_response_detail(
    response_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get details of a specific response action"""
    async with db_manager.get_session() as session:
        stmt = select(ResponseAction).where(
            ResponseAction.response_id == response_id
        )
        result = await session.execute(stmt)
        action = result.scalar_one_or_none()

    if not action:
        raise HTTPException(status_code=404, detail=f"Response not found: {response_id}")

    return {
        "id": action.response_id,
        "type": action.response_type,
        "target": action.target,
        "action": action.action,
        "status": action.status,
        "initiated_by": action.initiated_by,
        "executed_at": action.executed_at.isoformat() if action.executed_at else None,
        "completed_at": action.completed_at.isoformat() if action.completed_at else None,
        "duration_ms": action.duration_ms,
        "result": action.result_json,
        "error": action.error_message,
    }


from datetime import datetime, timezone
