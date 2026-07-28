"""
BLACK VEIL V5 - Metrics Endpoint
Expose Prometheus metrics for monitoring
"""
import logging

from fastapi import APIRouter
from src.backend.utils.metrics import get_metrics

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Metrics"])


@router.get("/")
async def get_prometheus_metrics():
    """Get all Prometheus metrics in text format"""
    return get_metrics()
