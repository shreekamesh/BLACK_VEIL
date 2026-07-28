"""
BLACK VEIL V2 — FastAPI Application Factory
Creates and configures the FastAPI application with all routes, middleware, and startup/shutdown events
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from api.routers import (
    health_router,
    predict_router,
    trust_router,
    deception_router,
    response_router,
    agents_router,
    reports_router,
)
from database.connection import db_manager
from security.auth import verify_token

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan: startup/shutdown events"""
    logger.info("BLACK VEIL V2 — Starting up")
    # Initialize database connections
    try:
        await db_manager.initialize_all()
        logger.info("Database connections initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed (will retry on demand): {e}")

    # Preload ML models
    from ai_core.model_loader import model_loader
    load_results = model_loader.preload_all()
    loaded = [k for k, v in load_results.items() if v]
    failed = [k for k, v in load_results.items() if not v]
    logger.info(f"Models loaded: {loaded}")
    if failed:
        logger.warning(f"Models failed to load: {failed}")

    yield

    # Shutdown
    logger.info("BLACK VEIL V2 — Shutting down")
    await db_manager.close_all()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="BLACK VEIL V2 — Trust & Deception API",
        description=(
            "IEEE Research: Temporal Trust Recovery and Adaptive Cyber Deception "
            "Framework for Multi-Agent AI Systems"
        ),
        version="2.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # ── Middleware ─────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # Restrict in production
    )

    # ── Global Exception Handler ──────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    # ── Register Routers ──────────────────────────────────
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])
    app.include_router(predict_router, prefix="/api/v1/predict", tags=["Predictions"])
    app.include_router(trust_router, prefix="/api/v1/trust", tags=["Trust"])
    app.include_router(deception_router, prefix="/api/v1/deception", tags=["Deception"])
    app.include_router(response_router, prefix="/api/v1/response", tags=["Response"])
    app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"])
    app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])

    return app
