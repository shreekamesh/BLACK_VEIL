"""
BLACK VEIL V5 - Incident Management Endpoints
Create, query, and manage security incidents
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db
from src.backend.models.database_models import Incident, IncidentResponse
from src.backend.models.request_models import IncidentCreateRequest, IncidentRespondRequest

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Incidents"])


@router.post("/", summary="Create a new incident")
async def create_incident(
    request: IncidentCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new security incident record"""
    incident = Incident(
        incident_type=request.incident_type,
        severity=request.severity,
        title=request.title,
        description=request.description,
        source_entity=request.source_entity,
        target_entity=request.target_entity,
        attack_vector=request.attack_vector,
        mitre_technique_id=request.mitre_technique_id,
        confidence=request.confidence,
        risk_score=request.risk_score,
        evidence_json=request.evidence,
    )
    db.add(incident)
    await db.commit()

    logger.info(
        "Incident created: %s (type=%s, severity=%s)",
        incident.id, incident.incident_type, incident.severity,
    )

    return {
        "status": "created",
        "incident_id": incident.id,
        "timestamp": incident.detected_at.isoformat(),
    }


@router.get("/")
async def list_incidents(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    incident_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List incidents with optional filters"""
    stmt = select(Incident)
    if status:
        stmt = stmt.where(Incident.status == status)
    if severity:
        stmt = stmt.where(Incident.severity == severity)
    if incident_type:
        stmt = stmt.where(Incident.incident_type == incident_type)
    stmt = stmt.order_by(desc(Incident.detected_at)).limit(limit)

    result = await db.execute(stmt)
    incidents = result.scalars().all()

    return {
        "count": len(incidents),
        "incidents": [
            {
                "id": i.id,
                "type": i.incident_type,
                "severity": i.severity,
                "status": i.status,
                "title": i.title,
                "confidence": i.confidence,
                "risk_score": i.risk_score,
                "detected_at": i.detected_at.isoformat(),
                "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
            }
            for i in incidents
        ],
    }


@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific incident"""
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident not found: {incident_id}")

    return {
        "id": incident.id,
        "type": incident.incident_type,
        "severity": incident.severity,
        "status": incident.status,
        "title": incident.title,
        "description": incident.description,
        "source": incident.source_entity,
        "target": incident.target_entity,
        "attack_vector": incident.attack_vector,
        "mitre_id": incident.mitre_technique_id,
        "confidence": incident.confidence,
        "risk_score": incident.risk_score,
        "evidence": incident.evidence_json,
        "timeline": incident.timeline_json,
        "detected_at": incident.detected_at.isoformat(),
        "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
        "responses": [
            {
                "id": r.id,
                "type": r.response_type,
                "action": r.action,
                "status": r.status,
                "executed_at": r.executed_at.isoformat() if r.executed_at else None,
            }
            for r in incident.responses
        ],
    }


@router.post("/{incident_id}/respond")
async def respond_to_incident(
    incident_id: str,
    request: IncidentRespondRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a response action for an incident"""
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident not found: {incident_id}")

    response = IncidentResponse(
        incident_id=incident_id,
        response_type=request.response_type,
        action=request.action,
        status="executed",
        executed_at=datetime.now(timezone.utc),
    )
    db.add(response)

    # Update incident status
    incident.status = "responded"
    await db.commit()

    return {
        "status": "responded",
        "response_id": response.id,
        "incident_id": incident_id,
        "action": request.action,
        "timestamp": response.executed_at.isoformat(),
    }


@router.get("/summary")
async def get_incident_summary(
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated incident summary"""
    result = await db.execute(
        select(
            func.count(Incident.id).label("total"),
            Incident.severity,
            Incident.status,
        ).group_by(Incident.severity, Incident.status)
    )
    rows = result.all()

    summary = {
        "total": sum(r.total for r in rows),
        "by_severity": {},
        "by_status": {},
    }
    for row in rows:
        sev = row.severity
        if sev not in summary["by_severity"]:
            summary["by_severity"][sev] = 0
        summary["by_severity"][sev] += row.total

    status_result = await db.execute(
        select(Incident.status, func.count(Incident.id))
        .group_by(Incident.status)
    )
    for status, count in status_result.all():
        summary["by_status"][status] = count

    return summary


@router.put("/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str,
    resolution_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Mark an incident as resolved"""
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident not found: {incident_id}")

    incident.status = "resolved"
    incident.resolved_at = datetime.now(timezone.utc)
    if resolution_notes:
        incident.resolution_notes = resolution_notes
    await db.commit()

    return {
        "status": "resolved",
        "incident_id": incident_id,
        "resolved_at": incident.resolved_at.isoformat(),
    }
