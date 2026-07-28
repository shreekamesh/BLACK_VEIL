"""
BLACK VEIL V5 - Model Management Endpoints
Register, query, activate, and manage ML models
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db
from src.backend.models.database_models import ModelRegistry
from src.backend.models.response_models import ModelInfo

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Model Management"])


@router.get("/", summary="List all registered models")
async def list_models(
    domain: Optional[str] = None,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """List all registered models with optional filtering"""
    stmt = select(ModelRegistry)
    if domain:
        stmt = stmt.where(ModelRegistry.domain == domain)
    if active_only:
        stmt = stmt.where(ModelRegistry.is_active == True)
    stmt = stmt.order_by(ModelRegistry.created_at.desc())

    result = await db.execute(stmt)
    models = result.scalars().all()

    return {
        "count": len(models),
        "models": [
            {
                "id": m.id,
                "name": m.model_name,
                "version": m.model_version,
                "type": m.model_type,
                "domain": m.domain,
                "active": m.is_active,
                "accuracy": m.accuracy,
                "feature_count": m.feature_count,
                "training_samples": m.training_samples,
                "created_at": m.created_at.isoformat(),
            }
            for m in models
        ],
    }


@router.get("/{model_name}", response_model=ModelInfo)
async def get_model(
    model_name: str,
    version: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific model"""
    stmt = select(ModelRegistry).where(ModelRegistry.model_name == model_name)
    if version:
        stmt = stmt.where(ModelRegistry.model_version == version)
    stmt = stmt.where(ModelRegistry.is_active == True)

    result = await db.execute(stmt)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")

    return ModelInfo(
        model_name=model.model_name,
        model_version=model.model_version,
        model_type=model.model_type,
        domain=model.domain,
        feature_count=model.feature_count,
        output_classes=list(model.output_classes.keys()) if model.output_classes else [],
        is_loaded=True,
        accuracy=model.accuracy,
        last_trained=model.created_at,
        training_samples=model.training_samples,
    )


@router.post("/register")
async def register_model(
    model_data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Register a new model in the registry"""
    required = ["model_name", "model_type", "model_version", "domain", "file_path"]
    for field in required:
        if field not in model_data:
            raise HTTPException(status_code=422, detail=f"Missing field: {field}")

    model = ModelRegistry(
        model_name=model_data["model_name"],
        model_type=model_data["model_type"],
        model_version=model_data["model_version"],
        domain=model_data["domain"],
        file_path=model_data["file_path"],
        feature_count=model_data.get("feature_count", 0),
        output_classes=model_data.get("output_classes"),
        description=model_data.get("description"),
        training_config=model_data.get("training_config"),
    )

    db.add(model)
    await db.commit()

    return {
        "status": "registered",
        "model_id": model.id,
        "model_name": model.model_name,
        "model_version": model.model_version,
    }


@router.put("/{model_name}/activate")
async def activate_model(
    model_name: str,
    version: str,
    db: AsyncSession = Depends(get_db),
):
    """Activate a specific model version"""
    stmt = select(ModelRegistry).where(
        ModelRegistry.model_name == model_name,
        ModelRegistry.model_version == version,
    )
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name} v{version}")

    # Deactivate all other versions
    deactivate_stmt = select(ModelRegistry).where(
        ModelRegistry.model_name == model_name,
        ModelRegistry.id != model.id,
    )
    deactivate_result = await db.execute(deactivate_stmt)
    for other in deactivate_result.scalars().all():
        other.is_active = False

    model.is_active = True
    await db.commit()

    return {
        "status": "activated",
        "model_name": model_name,
        "model_version": version,
    }


@router.delete("/{model_name}")
async def delete_model(
    model_name: str,
    version: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete a model from the registry"""
    stmt = select(ModelRegistry).where(ModelRegistry.model_name == model_name)
    if version:
        stmt = stmt.where(ModelRegistry.model_version == version)

    result = await db.execute(stmt)
    models = result.scalars().all()

    if not models:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")

    for model in models:
        await db.delete(model)

    await db.commit()

    return {
        "status": "deleted",
        "model_name": model_name,
        "deleted_count": len(models),
    }
