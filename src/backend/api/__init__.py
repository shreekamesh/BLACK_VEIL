"""
BLACK VEIL V5 - API Routers Package
"""
from src.backend.api.health import router as health_router
from src.backend.api.auth import router as auth_router
from src.backend.api.predictions import router as predictions_router
from src.backend.api.models import router as models_router
from src.backend.api.training import router as training_router
from src.backend.api.trust import router as trust_router
from src.backend.api.cognitive import router as cognitive_router
from src.backend.api.incidents import router as incidents_router
from src.backend.api.deception import router as deception_router
from src.backend.api.credentials import router as credentials_router
from src.backend.api.evolution import router as evolution_router
from src.backend.api.agents import router as agents_router
from src.backend.api.reports import router as reports_router
from src.backend.api.memory import router as memory_router
from src.backend.api.analytics import router as analytics_router
from src.backend.api.explain import router as explain_router
from src.backend.api.metrics_endpoint import router as metrics_router
from src.backend.api.admin import router as admin_router

__all__ = [
    "health_router",
    "auth_router",
    "predictions_router",
    "models_router",
    "training_router",
    "trust_router",
    "cognitive_router",
    "incidents_router",
    "deception_router",
    "credentials_router",
    "evolution_router",
    "agents_router",
    "reports_router",
    "memory_router",
    "analytics_router",
    "explain_router",
    "metrics_router",
    "admin_router",
]
