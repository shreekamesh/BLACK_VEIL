"""
BLACK VEIL V5 - Agent Management Endpoints
Register, monitor, and manage AI agents in the system
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Agents"])


# In-memory agent store
_agents: dict = {}


@router.post("/register")
async def register_agent(agent_data: dict):
    """Register a new AI agent"""
    agent_id = agent_data.get("id", f"agent-{len(_agents) + 1}")
    agent = {
        "id": agent_id,
        "name": agent_data.get("name", f"Agent-{agent_id}"),
        "type": agent_data.get("type", "inference"),
        "status": "active",
        "version": agent_data.get("version", "1.0.0"),
        "capabilities": agent_data.get("capabilities", []),
        "config": agent_data.get("config", {}),
        "registered_at": datetime.now(timezone.utc),
        "last_heartbeat": datetime.now(timezone.utc),
    }
    _agents[agent_id] = agent

    return {
        "status": "registered",
        "agent_id": agent_id,
        "timestamp": agent["registered_at"].isoformat(),
    }


@router.get("/")
async def list_agents(
    agent_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    """List all registered agents"""
    agents = list(_agents.values())
    if agent_type:
        agents = [a for a in agents if a["type"] == agent_type]
    if status:
        agents = [a for a in agents if a["status"] == status]

    return {
        "count": len(agents),
        "agents": [
            {
                "id": a["id"],
                "name": a["name"],
                "type": a["type"],
                "status": a["status"],
                "version": a["version"],
                "last_heartbeat": a["last_heartbeat"].isoformat(),
            }
            for a in agents
        ],
    }


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get detailed information about a specific agent"""
    agent = _agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    return agent


@router.put("/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str):
    """Update agent heartbeat timestamp"""
    agent = _agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    agent["last_heartbeat"] = datetime.now(timezone.utc)
    agent["status"] = "active"

    return {
        "status": "ok",
        "agent_id": agent_id,
        "last_heartbeat": agent["last_heartbeat"].isoformat(),
    }


@router.put("/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status_update: dict,
):
    """Update agent status"""
    agent = _agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    new_status = status_update.get("status")
    if new_status and new_status in ["active", "suspended", "compromised", "recovering"]:
        agent["status"] = new_status

    return {
        "status": "updated",
        "agent_id": agent_id,
        "new_status": agent["status"],
    }


@router.post("/{agent_id}/assign")
async def assign_task(
    agent_id: str,
    task_data: dict,
):
    """Assign a task to an agent"""
    agent = _agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    return {
        "status": "assigned",
        "agent_id": agent_id,
        "task": task_data.get("task", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
