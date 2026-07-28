"""
BLACK VEIL V2 — Health Check & System Status Endpoints
"""
import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from database.connection import db_manager
from ai_core.model_loader import model_loader

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

START_TIME = time.time()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "ok",
        "service": "BLACK VEIL V2",
        "version": "2.0.0",
        "uptime_seconds": int(time.time() - START_TIME),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with component status"""
    statuses = {
        "database": "unknown",
        "redis": "unknown",
        "models": {},
    }
    try:
        async with db_manager.get_session() as session:
            await session.execute(text("SELECT 1"))
        statuses["database"] = "healthy"
    except Exception as e:
        statuses["database"] = f"unhealthy: {e}"
    try:
        if db_manager.is_initialized:
            await db_manager.redis.ping()
            statuses["redis"] = "healthy"
        else:
            statuses["redis"] = "not_initialized"
    except Exception as e:
        statuses["redis"] = f"unhealthy: {e}"
    for name in model_loader.list_available_models():
        info = model_loader.get_model_info(name)
        statuses["models"][name] = "loaded" if info and info.is_loaded else "not_loaded"
    overall = all(
        v == "healthy" or v == "loaded" or isinstance(v, dict)
        for v in statuses.values()
    )
    return {
        "status": "healthy" if overall else "degraded",
        "components": statuses,
        "uptime_seconds": int(time.time() - START_TIME),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready")
async def readiness():
    """Readiness probe for Kubernetes/Docker"""
    try:
        async with db_manager.get_session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Not ready")
