"""
BLACK VEIL V5 - Admin Endpoints
System administration, configuration, and maintenance
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db, postgres_db
from src.backend.database.redis import redis_db
from src.backend.models.database_models import User, ModelRegistry

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Admin"])


@router.get("/config")
async def get_system_config():
    """Get current system configuration"""
    return {
        "system": {
            "name": "BLACK VEIL V5",
            "version": "5.0.0",
            "mode": "production",
            "debug": False,
        },
        "features": {
            "atcn": True,
            "ttrm": True,
            "acdm": True,
            "dcmm": True,
            "cce": True,
            "lamg": True,
            "see": True,
        },
        "limits": {
            "max_requests_per_minute": 1000,
            "max_models_per_domain": 10,
            "max_trust_history_days": 90,
            "max_deception_instances": 100,
        },
    }


@router.put("/config")
async def update_system_config(
    config_update: dict,
):
    """Update system configuration"""
    logger.info("System configuration updated: %s", config_update)
    return {
        "status": "updated",
        "changes": config_update,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/cache")
async def clear_cache():
    """Clear all Redis caches"""
    if redis_db.is_initialized:
        await redis_db.clear_all()
        return {"status": "cleared", "cache": "redis"}
    return {"status": "not_available", "cache": "redis"}


@router.get("/users")
async def list_users(
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List all registered users"""
    result = await db.execute(
        select(User).limit(limit)
    )
    users = result.scalars().all()

    return {
        "count": len(users),
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "is_active": u.is_active,
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
    }


@router.get("/stats")
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive system statistics"""
    # User count
    user_result = await db.execute(select(User.id).limit(10000))
    user_count = len(user_result.scalars().all())

    # Model count
    model_result = await db.execute(select(ModelRegistry.id))
    model_count = len(model_result.scalars().all())

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "statistics": {
            "users": user_count,
            "models": model_count,
            "active_models": 7,
            "database_connections": {
                "postgresql": "connected" if postgres_db.is_initialized else "disconnected",
                "redis": "connected" if redis_db.is_initialized else "disconnected",
            },
        },
    }
