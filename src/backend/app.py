"""
BLACK VEIL V5 - Main FastAPI Application
Application factory with all routes, middlewares, and lifecycle management
"""
import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.backend.config import (
    APP_NAME,
    APP_VERSION,
    DEBUG,
    CORS_ORIGINS,
    ALLOWED_HOSTS,
    API_PREFIX,
)
from src.backend.database import init_db, close_db
from src.backend.middlewares import (
    LoggingMiddleware,
    ErrorHandlerMiddleware,
    AuthMiddleware,
    RateLimitMiddleware,
)
from src.backend.utils.logger import get_logger, set_correlation_id

logger = get_logger(__name__)

# Global start time for uptime
_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan: startup/shutdown events"""
    set_correlation_id()
    logger.info("BLACK VEIL V5 - Starting up")

    # Initialize database connections
    try:
        await init_db()
        logger.info("Database connections initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed: %s", str(e))
        logger.warning("System will start with degraded functionality")

    # Log startup info
    logger.info("BLACK VEIL V5 v%s started", APP_VERSION)
    logger.info("Debug mode: %s", DEBUG)

    yield

    # Shutdown
    logger.info("BLACK VEIL V5 - Shutting down")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Error closing database connections: %s", str(e))
    logger.info("BLACK VEIL V5 shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title=APP_NAME,
        description=(
            "BLACK VEIL V5 - Cognitive Autonomous Cyber Defense Organism\n\n"
            "A multi-layered cognitive security system that perceives, understands, "
            "remembers, reasons, adapts, and evolves - creating an immune system "
            "for the digital world.\n\n"
            "## Architecture\n"
            "- **AI Foundation Layer**: Multiple ML models (CNN, DNN, RF, XGBoost) with ensemble encoding\n"
            "- **Cognitive Layer**: ATCN (trust), CCE (consensus), LAMG (memory)\n"
            "- **Response Layer**: TTRM (recovery), ACDM (deception), DCMM (credentials), SEE (evolution)\n"
            "- **Data Layer**: PostgreSQL, MongoDB, Neo4j, Redis\n\n"
            "## Research Contributions\n"
            "- Adaptive Trust Cognitive Network (ATCN)\n"
            "- Temporal Trust Recovery Model (TTRM)\n"
            "- Adaptive Cyber Deception Model (ACDM)\n"
            "- Dynamic Credential Mutation Model (DCMM)\n"
            "- Cognitive Consensus Engine (CCE)\n"
            "- Living Attack Memory Graph (LAMG)\n"
            "- Security Evolution Engine (SEE)"
        ),
        version=APP_VERSION,
        lifespan=lifespan,
        docs_url=f"{API_PREFIX}/docs",
        redoc_url=f"{API_PREFIX}/redoc",
        openapi_url=f"{API_PREFIX}/openapi.json",
    )

    # ── Middleware Setup ─────────────────────────────────────
    # Order matters: error handler should be outermost

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted Hosts
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_HOSTS,
    )

    # Custom middlewares
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Error handler (must be last to catch all)
    ErrorHandlerMiddleware.setup(app)

    # ── Root endpoint ───────────────────────────────────────
    @app.get(f"{API_PREFIX}/", tags=["System"])
    async def root():
        """Root endpoint with system information"""
        uptime = int(time.time() - _start_time)
        return {
            "name": APP_NAME,
            "version": APP_VERSION,
            "status": "operational",
            "uptime_seconds": uptime,
            "api_docs": f"{API_PREFIX}/docs",
            "health": f"{API_PREFIX}/health",
        }

    # ── Register Routers ────────────────────────────────────
    from src.backend.api import (
        health_router,
        auth_router,
        predictions_router,
        models_router,
        training_router,
        trust_router,
        cognitive_router,
        incidents_router,
        deception_router,
        credentials_router,
        evolution_router,
        agents_router,
        reports_router,
        memory_router,
        analytics_router,
        explain_router,
        metrics_router,
        admin_router,
    )

    app.include_router(health_router, prefix=API_PREFIX, tags=["Health"])
    app.include_router(auth_router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
    app.include_router(predictions_router, prefix=f"{API_PREFIX}/predict", tags=["Predictions"])
    app.include_router(models_router, prefix=f"{API_PREFIX}/models", tags=["Model Management"])
    app.include_router(training_router, prefix=f"{API_PREFIX}/training", tags=["Training"])
    app.include_router(trust_router, prefix=f"{API_PREFIX}/trust", tags=["Trust & Cognitive"])
    app.include_router(cognitive_router, prefix=f"{API_PREFIX}/cognitive", tags=["Cognitive Layer"])
    app.include_router(incidents_router, prefix=f"{API_PREFIX}/incidents", tags=["Incidents"])
    app.include_router(deception_router, prefix=f"{API_PREFIX}/deception", tags=["Deception"])
    app.include_router(credentials_router, prefix=f"{API_PREFIX}/credentials", tags=["Credentials"])
    app.include_router(evolution_router, prefix=f"{API_PREFIX}/evolution", tags=["Evolution"])
    app.include_router(agents_router, prefix=f"{API_PREFIX}/agents", tags=["Agents"])
    app.include_router(reports_router, prefix=f"{API_PREFIX}/reports", tags=["Reports"])
    app.include_router(memory_router, prefix=f"{API_PREFIX}/memory", tags=["Attack Memory"])
    app.include_router(analytics_router, prefix=f"{API_PREFIX}/analytics", tags=["Analytics"])
    app.include_router(explain_router, prefix=f"{API_PREFIX}/explain", tags=["Explainability"])
    app.include_router(metrics_router, prefix=f"{API_PREFIX}/metrics", tags=["Metrics"])
    app.include_router(admin_router, prefix=f"{API_PREFIX}/admin", tags=["Admin"])

    return app


# Create the application instance
app = create_app()
