"""
BLACK VEIL V5 - PostgreSQL Database Connection
Async connection management with SQLAlchemy 2.0
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.backend.config import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DATABASE,
    POSTGRES_POOL_SIZE,
    POSTGRES_MAX_OVERFLOW,
    POSTGRES_POOL_TIMEOUT,
    POSTGRES_POOL_RECYCLE,
    DEBUG,
)

logger = logging.getLogger(__name__)

Base = declarative_base()


class PostgresDatabase:
    """PostgreSQL async database connection manager"""

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_maker: Optional[async_sessionmaker[AsyncSession]] = None

    def _build_url(self) -> str:
        """Build async PostgreSQL connection URL"""
        return (
            f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
        )

    async def initialize(self) -> None:
        """Initialize the database connection pool"""
        if self._engine is not None:
            logger.debug("PostgreSQL already initialized")
            return

        database_url = self._build_url()
        logger.info("Connecting to PostgreSQL at %s:%s/%s",
                     POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE)

        try:
            self._engine = create_async_engine(
                database_url,
                pool_size=POSTGRES_POOL_SIZE,
                max_overflow=POSTGRES_MAX_OVERFLOW,
                pool_timeout=POSTGRES_POOL_TIMEOUT,
                pool_recycle=POSTGRES_POOL_RECYCLE,
                echo=DEBUG,
                future=True,
            )

            self._session_maker = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )

            # Create all tables
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created/verified")

            logger.info("PostgreSQL connection pool established")
        except Exception as e:
            logger.warning("PostgreSQL connection failed: %s. Running in degraded mode.", e)
            self._engine = None
            self._session_maker = None

    async def close(self) -> None:
        """Close all database connections"""
        if self._engine:
            try:
                await self._engine.dispose()
            except Exception:
                pass
            self._engine = None
            self._session_maker = None
        logger.debug("PostgreSQL connections closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session via context manager"""
        if self._session_maker is None:
            await self.initialize()

        async with self._session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @property
    def is_initialized(self) -> bool:
        return self._engine is not None


# Global singleton
postgres_db = PostgresDatabase()


# FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get a database session"""
    async with postgres_db.get_session() as session:
        yield session

