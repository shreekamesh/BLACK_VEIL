"""
BLACK VEIL V2 — Database Connection Manager
Manages async connections to PostgreSQL, Redis, and MongoDB
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.pool import NullPool

from database.config import DatabaseConfig
from database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Centralized database connection manager"""

    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self._pg_engine: Optional[AsyncEngine] = None
        self._pg_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._redis: Optional[Redis] = None
        self._mongo_client: Optional[AsyncIOMotorClient] = None
        self._mongo_db: Optional[AsyncIOMotorDatabase] = None
        self._initialized = False

    # ── PostgreSQL ──────────────────────────────────────────────

    async def init_postgres(self) -> None:
        """Initialize PostgreSQL async engine and session factory"""
        if self._pg_engine is not None:
            return

        logger.info(
            "Connecting to PostgreSQL at %s:%s/%s",
            self.config.postgres.host,
            self.config.postgres.port,
            self.config.postgres.database,
        )

        self._pg_engine = create_async_engine(
            self.config.postgres.connection_string,
            pool_size=self.config.postgres.pool_size,
            max_overflow=self.config.postgres.max_overflow,
            echo=self.config.postgres.echo,
            pool_pre_ping=True,
        )

        self._pg_session_factory = async_sessionmaker(
            self._pg_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        logger.info("PostgreSQL connection established")

    async def create_all_tables(self) -> None:
        """Create all tables defined in ORM models"""
        if self._pg_engine is None:
            await self.init_postgres()
        async with self._pg_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("All database tables created")

    async def drop_all_tables(self) -> None:
        """Drop all tables (for testing only)"""
        if self._pg_engine is None:
            await self.init_postgres()
        async with self._pg_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session (context manager)"""
        if self._pg_session_factory is None:
            await self.init_postgres()

        session = self._pg_session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @asynccontextmanager
    async def get_transaction_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get session with explicit transaction control"""
        if self._pg_session_factory is None:
            await self.init_postgres()

        session = self._pg_session_factory()
        try:
            yield session
        finally:
            await session.close()

    # ── Redis ───────────────────────────────────────────────────

    async def init_redis(self) -> None:
        """Initialize Redis connection"""
        if self._redis is not None:
            return

        logger.info("Connecting to Redis at %s:%s", self.config.redis.host, self.config.redis.port)

        self._redis = Redis.from_url(
            self.config.redis.connection_string,
            decode_responses=self.config.redis.decode_responses,
        )

        # Test connection
        await self._redis.ping()
        logger.info("Redis connection established")

    @property
    def redis(self) -> Redis:
        """Get Redis client (must call init_redis first)"""
        if self._redis is None:
            raise RuntimeError("Redis not initialized. Call init_redis() first.")
        return self._redis

    # ── MongoDB ─────────────────────────────────────────────────

    async def init_mongodb(self) -> None:
        """Initialize MongoDB connection"""
        if self._mongo_client is not None:
            return

        logger.info(
            "Connecting to MongoDB at %s:%s/%s",
            self.config.mongodb.host,
            self.config.mongodb.port,
            self.config.mongodb.database,
        )

        self._mongo_client = AsyncIOMotorClient(self.config.mongodb.connection_string)
        self._mongo_db = self._mongo_client[self.config.mongodb.database]

        # Test connection
        await self._mongo_client.admin.command("ping")
        logger.info("MongoDB connection established")

    @property
    def mongo_db(self) -> AsyncIOMotorDatabase:
        """Get MongoDB database (must call init_mongodb first)"""
        if self._mongo_db is None:
            raise RuntimeError("MongoDB not initialized. Call init_mongodb() first.")
        return self._mongo_db

    # ── Lifecycle ───────────────────────────────────────────────

    async def initialize_all(self) -> None:
        """Initialize all database connections"""
        await self.init_postgres()
        await self.init_redis()
        await self.init_mongodb()
        self._initialized = True
        logger.info("All database connections initialized")

    async def close_all(self) -> None:
        """Close all database connections"""
        if self._pg_engine:
            await self._pg_engine.dispose()
            logger.info("PostgreSQL connection closed")

        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")

        if self._mongo_client:
            self._mongo_client.close()
            logger.info("MongoDB connection closed")

        self._initialized = False
        logger.info("All database connections closed")

    @property
    def is_initialized(self) -> bool:
        return self._initialized


# Singleton instance
db_manager = DatabaseManager()

