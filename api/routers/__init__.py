"""
BLACK VEIL V2 — API Router Registry
"""
from api.routers.health import router as health_router
from api.routers.predict import router as predict_router
from api.routers.trust import router as trust_router
from api.routers.deception import router as deception_router
from api.routers.response import router as response_router
from api.routers.agents import router as agents_router
from api.routers.reports import router as reports_router

__all__ = [
    "health_router",
    "predict_router",
    "trust_router",
    "deception_router",
    "response_router",
    "agents_router",
    "reports_router",
]
