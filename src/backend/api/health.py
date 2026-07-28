"""
BLACK VEIL V5 - Health & System Status Endpoints
"""
import time
import logging
from datetime import datetime, timezone

from fastapi import APIRouter

from src.backend.database import postgres_db, mongo_db, neo4j_db, redis_db
from src.backend.utils.metrics import get_metrics

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

START_TIME = time.time()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    uptime = int(time.time() - START_TIME)
    return {
        "status": "ok",
        "service": "BLACK VEIL V5",
        "version": "5.0.0",
        "uptime_seconds": uptime,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with component status"""
    db_status = {}
    try:
        async with postgres_db.get_session() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        db_status["postgresql"] = "healthy"
    except Exception as e:
        db_status["postgresql"] = f"unhealthy: {str(e)[:50]}"

    try:
        if mongo_db.is_initialized:
            await mongo_db.db.command("ping")
            db_status["mongodb"] = "healthy"
        else:
            db_status["mongodb"] = "not_initialized"
    except Exception as e:
        db_status["mongodb"] = f"unhealthy: {str(e)[:50]}"

    try:
        if neo4j_db.is_initialized:
            await neo4j_db.driver.verify_connectivity()
            db_status["neo4j"] = "healthy"
        else:
            db_status["neo4j"] = "not_initialized"
    except Exception as e:
        db_status["neo4j"] = f"unhealthy: {str(e)[:50]}"

    try:
        if redis_db.is_initialized:
            await redis_db.client.ping()
            db_status["redis"] = "healthy"
        else:
            db_status["redis"] = "not_initialized"
    except Exception as e:
        db_status["redis"] = f"unhealthy: {str(e)[:50]}"

    overall = all(
        v == "healthy" for v in db_status.values()
    )

    uptime = int(time.time() - START_TIME)
    return {
        "status": "healthy" if overall else "degraded",
        "version": "5.0.0",
        "uptime_seconds": uptime,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/ready")
async def readiness():
    """Readiness probe for Kubernetes/Docker"""
    try:
        async with postgres_db.get_session() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Not ready")


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return get_metrics()
