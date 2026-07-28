"""
BLACK VEIL V5 - Reporting Endpoints
Generate trust, threat, and system reports
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db
from src.backend.models.database_models import (
    TrustRelationship,
    TrustEvent,
    Incident,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Reports"])


@router.get("/trust/summary")
async def get_trust_report(
    db: AsyncSession = Depends(get_db),
):
    """Generate trust score report"""
    result = await db.execute(
        select(
            func.avg(TrustRelationship.trust_score).label("avg_trust"),
            func.min(TrustRelationship.trust_score).label("min_trust"),
            func.max(TrustRelationship.trust_score).label("max_trust"),
            func.count(TrustRelationship.id).label("total"),
        ).where(TrustRelationship.is_active == True)
    )
    stats = result.one()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trust_statistics": {
            "average": round(stats.avg_trust, 2) if stats.avg_trust else 0,
            "minimum": round(stats.min_trust, 2) if stats.min_trust else 0,
            "maximum": round(stats.max_trust, 2) if stats.max_trust else 0,
            "total_relationships": stats.total,
        },
    }


@router.get("/threat/summary")
async def get_threat_report(
    db: AsyncSession = Depends(get_db),
):
    """Generate threat/incident report"""
    result = await db.execute(
        select(
            Incident.severity,
            func.count(Incident.id).label("count"),
        ).group_by(Incident.severity)
    )
    severity_counts = {row.severity: row.count for row in result.all()}

    total_result = await db.execute(select(func.count(Incident.id)))
    total = total_result.scalar() or 0

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_incidents": total,
        "by_severity": severity_counts,
    }


@router.get("/system/status")
async def get_system_status_report(
    db: AsyncSession = Depends(get_db),
):
    """Generate comprehensive system status report"""
    # Trust stats
    trust_result = await db.execute(
        select(
            func.avg(TrustRelationship.trust_score).label("avg_trust"),
            func.count(TrustRelationship.id).label("trust_count"),
        )
    )
    trust_stats = trust_result.one()

    # Incident stats
    incident_result = await db.execute(
        select(func.count(Incident.id).label("total"))
    )
    incident_total = incident_result.scalar() or 0

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system_name": "BLACK VEIL V5",
        "status": "operational",
        "trust_system": {
            "avg_trust_score": round(trust_stats.avg_trust, 2) if trust_stats.avg_trust else 0,
            "total_relationships": trust_stats.trust_count or 0,
        },
        "incidents": {
            "total": incident_total,
        },
    }


@router.get("/custom")
async def generate_custom_report(
    report_type: str = Query("summary", description="Type of report"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
):
    """Generate a custom report with specified parameters"""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_type": report_type,
        "parameters": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "data": {
            "message": f"Custom {report_type} report generated",
            "timestamp_range": f"{start_date or 'beginning'} to {end_date or 'now'}",
        },
    }
