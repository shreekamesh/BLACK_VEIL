"""
BLACK VEIL V2 — Agent Management Endpoints
Register, query, and manage AI agents in the system
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc

from database.connection import db_manager
from database.models import Agent
from security.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Agents"])


@router.get("/")
async def list_agents(
    agent_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """List all registered AI agents"""
    async with db_manager.get_session() as session:
        stmt = select(Agent)
        if agent_type:
            stmt = stmt.where(Agent.agent_type == agent_type)
        if status:
            stmt = stmt.where(Agent.status == status)
        stmt = stmt.order_by(Agent.created_at)
        result = await session.execute(stmt)
        agents = result.scalars().all()

    return {
        "count": len(agents),
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "type": a.agent_type,
                "status": a.status,
                "version": a.version,
                "last_heartbeat": a.last_heartbeat.isoformat() if a.last_heartbeat else None,
                "created_at": a.created_at.isoformat(),
            }
            for a in agents
        ],
    }


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get detailed information about a specific agent"""
    async with db_manager.get_session() as session:
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await session.execute(stmt)
        agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    return {
        "id": agent.id,
        "name": agent.name,
        "type": agent.agent_type,
        "status": agent.status,
        "ip_address": str(agent.ip_address) if agent.ip_address else None,
        "port": agent.port,
        "version": agent.version,
        "config": agent.config_json,
        "metadata": agent.metadata_json,
        "last_heartbeat": agent.last_heartbeat.isoformat() if agent.last_heartbeat else None,
        "created_at": agent.created_at.isoformat(),
    }


@router.post("/register")
async def register_agent(
    agent_data: dict,
    current_user: dict = Depends(get_current_user),
):
    """Register a new AI agent in the system"""
    required = ["name", "agent_type"]
    for field in required:
        if field not in agent_data:
            raise HTTPException(status_code=422, detail=f"Missing field: {field}")

    agent = Agent(
        name=agent_data["name"],
        agent_type=agent_data["agent_type"],
        status=agent_data.get("status", "ACTIVE"),
        ip_address=agent_data.get("ip_address"),
        port=agent_data.get("port"),
        version=agent_data.get("version"),
        config_json=agent_data.get("config"),
        metadata_json=agent_data.get("metadata"),
    )

    async with db_manager.get_session() as session:
        session.add(agent)

    return {
        "status": "registered",
        "agent_id": agent.id,
        "name": agent.name,
        "type": agent.agent_type,
        "timestamp": agent.created_at.isoformat(),
    }


@router.put("/{agent_id}/heartbeat")
async def agent_heartbeat(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Update agent heartbeat timestamp"""
    async with db_manager.get_session() as session:
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await session.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

        from datetime import datetime, timezone
        agent.last_heartbeat = datetime.now(timezone.utc)

    return {
        "status": "ok",
        "agent_id": agent_id,
        "last_heartbeat": agent.last_heartbeat.isoformat(),
    }
