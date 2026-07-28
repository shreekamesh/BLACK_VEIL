"""
BLACK VEIL V5 - Training Endpoints
Trigger and manage model training jobs
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db
from src.backend.models.database_models import ModelRegistry
from src.backend.models.response_models import TrainingStatus

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Training"])

# In-memory training job tracking (use DB in production)
_training_jobs: dict = {}


class TrainingRequest(BaseModel):
    """Training job configuration"""
    model_name: str = Field(..., description="Name of the model to train")
    model_type: str = Field(..., description="Type of model (rf, xgboost, cnn, etc.)")
    dataset: str = Field(..., description="Dataset to use for training")
    hyperparameters: Optional[dict] = Field(None, description="Training hyperparameters")
    test_split: float = Field(0.2, ge=0.0, le=0.5, description="Test split ratio")
    max_epochs: int = Field(100, ge=1, le=10000, description="Maximum training epochs")


@router.post("/start", response_model=TrainingStatus)
async def start_training(
    request: TrainingRequest,
    db: AsyncSession = Depends(get_db),
):
    """Start a model training job"""
    job_id = str(uuid.uuid4())

    job = {
        "job_id": job_id,
        "model_name": request.model_name,
        "status": "pending",
        "progress": 0.0,
        "started_at": datetime.now(timezone.utc),
        "completed_at": None,
        "metrics": None,
        "error": None,
        "config": request.dict(),
    }
    _training_jobs[job_id] = job

    logger.info("Training job %s started for model %s", job_id, request.model_name)

    return TrainingStatus(
        job_id=job_id,
        model_name=request.model_name,
        status="pending",
        progress=0.0,
        started_at=job["started_at"],
    )


@router.get("/status/{job_id}", response_model=TrainingStatus)
async def get_training_status(job_id: str):
    """Get the status of a training job"""
    job = _training_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Training job not found: {job_id}")

    return TrainingStatus(
        job_id=job["job_id"],
        model_name=job["model_name"],
        status=job["status"],
        progress=job["progress"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
        metrics=job.get("metrics"),
        error=job.get("error"),
    )


@router.get("/jobs", summary="List all training jobs")
async def list_training_jobs(
    status: Optional[str] = None,
):
    """List all training jobs with optional status filter"""
    jobs = list(_training_jobs.values())
    if status:
        jobs = [j for j in jobs if j["status"] == status]

    return {
        "count": len(jobs),
        "jobs": [
            {
                "job_id": j["job_id"],
                "model_name": j["model_name"],
                "status": j["status"],
                "progress": j["progress"],
                "started_at": j.get("started_at"),
                "completed_at": j.get("completed_at"),
            }
            for j in jobs
        ],
    }
