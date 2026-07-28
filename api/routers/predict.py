"""
BLACK VEIL V2 — Prediction Endpoints
Multi-domain AI inference (Network, IoT, User, CICIDS) + Fusion
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ai_core.network_engine import NetworkInferenceEngine
from ai_core.iot_engine import IoTInferenceEngine
from ai_core.user_engine import UserInferenceEngine
from ai_core.cicids_engine import CICIDSInferenceEngine
from ai_core.fusion_engine import FusionEngine, FusionInput
from security.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Predictions"])

network_engine = NetworkInferenceEngine()
iot_engine = IoTInferenceEngine()
user_engine = UserInferenceEngine()
cicids_engine = CICIDSInferenceEngine()
fusion_engine = FusionEngine()


@router.post("/network")
async def predict_network(
    features: dict,
    current_user: dict = Depends(get_current_user),
):
    """Run network threat prediction (UNSW-NB15)"""
    try:
        result = network_engine.predict(features)
        return {
            "domain": "network",
            "is_attack": result.is_attack,
            "attack_category": result.attack_category,
            "probability": result.probability,
            "confidence": result.confidence,
            "risk_score": result.risk_score,
            "trust_score": result.trust_score,
            "threat_level": result.threat_level,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/iot")
async def predict_iot(
    features: dict,
    current_user: dict = Depends(get_current_user),
):
    """Run IoT anomaly detection (EDGE-IoT)"""
    try:
        result = iot_engine.predict(features)
        return {
            "domain": "iot",
            "is_anomaly": result.is_anomaly,
            "probability": result.probability,
            "confidence": result.confidence,
            "risk_score": result.risk_score,
            "trust_score": result.trust_score,
            "threat_level": result.threat_level,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/user")
async def predict_user(
    features: dict,
    user_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Run user behavior analysis (CERT-r4.2)"""
    try:
        result = user_engine.predict(features, user_id)
        return {
            "domain": "user",
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "trust_score": result.trust_score,
            "behavior_score": result.behavior_score,
            "personality_score": result.personality_score,
            "final_trust_score": result.final_trust_score,
            "trust_category": result.trust_category,
            "user_id": result.user_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/cicids")
async def predict_cicids(
    features: dict,
    current_user: dict = Depends(get_current_user),
):
    """Run CICIDS2017 traffic analysis"""
    try:
        result = cicids_engine.predict(features)
        return {
            "domain": "cicids",
            "is_attack": result.is_attack,
            "attack_type": result.attack_type,
            "probability": result.probability,
            "confidence": result.confidence,
            "risk_score": result.risk_score,
            "threat_level": result.threat_level,
            "protocol_analysis": result.protocol_analysis,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/fusion")
async def predict_fusion(
    inputs: list[dict],
    current_user: dict = Depends(get_current_user),
):
    """Fuse predictions from multiple domains (Algorithm 1)"""
    try:
        fusion_inputs = []
        for inp in inputs:
            fusion_inputs.append(FusionInput(
                domain=inp["domain"],
                trust_score=inp["trust_score"],
                risk_score=inp["risk_score"],
                threat_level=inp["threat_level"],
                confidence=inp.get("confidence", 0.8),
                is_attack=inp.get("is_attack"),
                attack_type=inp.get("attack_type"),
            ))
        result = fusion_engine.fuse(fusion_inputs)
        return {
            "fused_trust_score": result.fused_trust_score,
            "fused_risk_score": result.fused_risk_score,
            "fused_threat_level": result.fused_threat_level,
            "ensemble_confidence": result.ensemble_confidence,
            "agreement_level": result.agreement_level,
            "domain_scores": result.domain_scores,
            "domain_weights": result.domain_weights,
            "fusion_method": result.fusion_method,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Missing field: {e}")
