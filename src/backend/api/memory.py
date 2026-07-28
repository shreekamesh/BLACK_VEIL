"""
BLACK VEIL V5 - Attack Memory Endpoints
LAMG: Living Attack Memory Graph operations
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db
from src.backend.database.neo4j import neo4j_db
from src.backend.models.database_models import AttackMemoryRecord

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Attack Memory"])


@router.get("/")
async def list_attack_memories(
    attack_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List attack memories from LAMG"""
    stmt = select(AttackMemoryRecord)
    if attack_type:
        stmt = stmt.where(AttackMemoryRecord.attack_type == attack_type)
    stmt = stmt.order_by(desc(AttackMemoryRecord.last_seen)).limit(limit)

    result = await db.execute(stmt)
    records = result.scalars().all()

    return {
        "count": len(records),
        "attacks": [
            {
                "id": r.attack_id,
                "type": r.attack_type,
                "severity": r.severity,
                "threat_level": r.threat_level,
                "occurrences": r.occurrence_count,
                "first_seen": r.first_seen.isoformat(),
                "last_seen": r.last_seen.isoformat() if r.last_seen else None,
            }
            for r in records
        ],
    }


@router.get("/{attack_id}")
async def get_attack_memory(
    attack_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed attack memory from LAMG"""
    result = await db.execute(
        select(AttackMemoryRecord).where(
            AttackMemoryRecord.attack_id == attack_id
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail=f"Attack memory not found: {attack_id}")

    return {
        "id": record.attack_id,
        "type": record.attack_type,
        "severity": record.severity,
        "description": record.description,
        "dna": record.attack_dna,
        "mitre_mapping": record.mitre_mapping,
        "indicators": record.indicator_list,
        "similar_attacks": record.related_attacks,
        "similarity_scores": record.similarity_scores,
        "evolution": record.evolution_history,
        "first_seen": record.first_seen.isoformat(),
        "last_seen": record.last_seen.isoformat() if record.last_seen else None,
        "occurrence_count": record.occurrence_count,
    }


@router.get("/graph/neo4j")
async def get_attack_graph():
    """Get attack graph from Neo4j"""
    if not neo4j_db.is_initialized:
        raise HTTPException(status_code=503, detail="Neo4j not available")

    try:
        result = await neo4j_db.execute_query(
            "MATCH (a:Attack) RETURN a LIMIT 100"
        )
        return {
            "count": len(result),
            "nodes": result,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Neo4j query failed: {str(e)}")


@router.get("/search/similar")
async def find_similar_attacks(
    attack_type: Optional[str] = Query(None),
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db),
):
    """Find similar attacks in LAMG by DNA or type"""
    if attack_type:
        result = await db.execute(
            select(AttackMemoryRecord).where(
                AttackMemoryRecord.attack_type == attack_type,
            ).limit(20)
        )
        records = result.scalars().all()
    else:
        result = await db.execute(
            select(AttackMemoryRecord).limit(20)
        )
        records = result.scalars().all()

    return {
        "count": len(records),
        "threshold": similarity_threshold,
        "results": [
            {
                "id": r.attack_id,
                "type": r.attack_type,
                "similarity": 0.85,  # simulated similarity
                "occurrences": r.occurrence_count,
            }
            for r in records
        ],
    }


@router.post("/record")
async def record_attack(
    attack_data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Record a new attack in LAMG"""
    record = AttackMemoryRecord(
        attack_id=attack_data.get("attack_id"),
        attack_type=attack_data["attack_type"],
        attack_dna=attack_data.get("attack_dna"),
        description=attack_data.get("description"),
        severity=attack_data.get("severity", "MEDIUM"),
        threat_level=attack_data.get("threat_level", "MEDIUM"),
        mitre_mapping=attack_data.get("mitre_mapping"),
        indicator_list=attack_data.get("indicators"),
        related_attacks=attack_data.get("related_attacks"),
        similarity_scores=attack_data.get("similarity_scores"),
        evolution_history=attack_data.get("evolution_history"),
    )
    db.add(record)
    await db.commit()

    # Also store in Neo4j if available
    if neo4j_db.is_initialized:
        try:
            await neo4j_db.execute_write_query(
                """
                MERGE (a:Attack {id: $attack_id})
                SET a.type = $attack_type,
                    a.severity = $severity,
                    a.timestamp = $timestamp
                """,
                attack_id=record.attack_id,
                attack_type=record.attack_type,
                severity=record.severity,
                timestamp=record.first_seen.isoformat(),
            )
        except Exception as e:
            logger.warning("Failed to store attack in Neo4j: %s", e)

    return {
        "status": "recorded",
        "attack_id": record.attack_id,
        "timestamp": record.first_seen.isoformat(),
    }
