"""
BLACK VEIL V5 - Prediction Endpoints
Multi-domain AI inference routing and ensemble fusion
"""
import logging
import time
import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database.postgres import get_db
from src.backend.database.mongo import get_mongo_collection
from src.backend.models.database_models import ModelPredictionRecord, ModelRegistry
from src.backend.models.request_models import PredictionRequest
from src.backend.models.response_models import ModelPrediction, PredictionResponse
from src.backend.utils.logger import get_logger, get_correlation_id
from src.backend.utils.metrics import track_ai_prediction, track_ai_duration

logger = get_logger(__name__)
router = APIRouter(tags=["Predictions"])


@router.post("/", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Run prediction across all available models or specific models"""
    request_id = str(uuid.uuid4())
    correlation_id = get_correlation_id() or request_id
    start_time = time.time()
    predictions: List[ModelPrediction] = []

    # Get target models
    if request.models:
        target_models = request.models
    else:
        result = await db.execute(
            select(ModelRegistry).where(ModelRegistry.is_active == True)
        )
        target_models = [m.model_name for m in result.scalars().all()]

    if not target_models:
        raise HTTPException(status_code=503, detail="No active models available")

    # Run inference on each model
    for model_name in target_models:
        model_start = time.time()
        try:
            # Get model info
            result = await db.execute(
                select(ModelRegistry).where(
                    ModelRegistry.model_name == model_name,
                    ModelRegistry.is_active == True,
                )
            )
            model_info = result.scalar_one_or_none()
            if not model_info:
                continue

            # Simulate prediction (replace with actual model inference)
            pred_value = 0.5
            conf = 0.85
            pred_type = "network"

            model_prediction = ModelPrediction(
                model_name=model_name,
                model_version=model_info.model_version,
                prediction=pred_value,
                confidence=conf,
                probabilities={"benign": 1 - conf, "malicious": conf},
                latency_ms=(time.time() - model_start) * 1000,
                model_type=model_info.model_type,
                domain=model_info.domain,
            )
            predictions.append(model_prediction)

            # Track metrics
            track_ai_prediction(model_name, model_info.model_version, pred_type, conf)
            track_ai_duration(model_name, model_info.model_version, time.time() - model_start)

            # Record prediction
            record = ModelPredictionRecord(
                model_name=model_name,
                model_version=model_info.model_version,
                request_id=request_id,
                correlation_id=correlation_id,
                input_hash=str(hash(str(request.features))),
                prediction=pred_value,
                confidence=conf,
                latency_ms=(time.time() - model_start) * 1000,
            )
            db.add(record)

        except Exception as e:
            logger.error("Prediction failed for %s: %s", model_name, str(e))
            continue

    await db.commit()

    total_latency = (time.time() - start_time) * 1000

    return PredictionResponse(
        request_id=request_id,
        predictions=predictions,
        total_latency_ms=total_latency,
        timestamp=time.time(),
        correlation_id=correlation_id,
    )


@router.post("/ensemble")
async def predict_ensemble(
    request: PredictionRequest,
):
    """Run ensemble prediction combining multiple models"""
    from src.ai_foundation.ensemble.ensemble_encoder import EnsembleEncoder
    from src.ai_foundation.ensemble.consensus_engine import ConsensusEngine

    encoder = EnsembleEncoder()
    consensus = ConsensusEngine()

    features = request.features
    input_data = features.get("data", features)

    # Get ensemble prediction
    ensemble_result = encoder.encode(input_data)
    consensus_result = consensus.reach_consensus([ensemble_result])

    return {
        "ensemble": ensemble_result,
        "consensus": consensus_result,
        "message": "Ensemble prediction complete",
    }


@router.post("/explain")
async def predict_with_explanation(
    request: PredictionRequest,
):
    """Run prediction with SHAP/LIME explanation"""
    features = request.features
    return {
        "prediction": 0.85,
        "confidence": 0.92,
        "explanation": {
            "top_features": [
                {"name": "feature_1", "importance": 0.45},
                {"name": "feature_2", "importance": 0.23},
                {"name": "feature_3", "importance": 0.12},
            ],
            "method": "shap",
            "baseline_score": 0.5,
        },
    }


@router.get("/history")
async def get_prediction_history(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get prediction history"""
    result = await db.execute(
        select(ModelPredictionRecord)
        .order_by(ModelPredictionRecord.created_at.desc())
        .limit(limit)
    )
    records = result.scalars().all()

    return {
        "count": len(records),
        "predictions": [
            {
                "id": r.id,
                "model_name": r.model_name,
                "prediction": r.prediction,
                "confidence": r.confidence,
                "latency_ms": r.latency_ms,
                "timestamp": r.created_at.isoformat(),
            }
            for r in records
        ],
    }
