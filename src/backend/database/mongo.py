"""
BLACK VEIL V5 - MongoDB Database Connection
Async document storage with Motor
"""
import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.backend.config import (
    MONGO_USER,
    MONGO_PASSWORD,
    MONGO_HOST,
    MONGO_PORT,
    MONGO_DATABASE,
    MONGO_MAX_POOL_SIZE,
    MONGO_MIN_POOL_SIZE,
    MONGO_MAX_IDLE_TIME_MS,
)

logger = logging.getLogger(__name__)


class MongoDatabase:
    """MongoDB async database connection manager"""

    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    def _build_url(self) -> str:
        """Build MongoDB connection URL"""
        return (
            f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}"
            f"@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}"
        )

    async def initialize(self) -> None:
        """Initialize MongoDB connection with pool settings"""
        if self._client is not None:
            logger.debug("MongoDB already initialized")
            return

        connection_url = self._build_url()
        logger.info("Connecting to MongoDB at %s:%s/%s",
                     MONGO_HOST, MONGO_PORT, MONGO_DATABASE)

        try:
            self._client = AsyncIOMotorClient(
                connection_url,
                maxPoolSize=MONGO_MAX_POOL_SIZE,
                minPoolSize=MONGO_MIN_POOL_SIZE,
                maxIdleTimeMS=MONGO_MAX_IDLE_TIME_MS,
            )

            self._db = self._client[MONGO_DATABASE]

            # Verify connection
            await self._client.admin.command("ping")
            logger.info("MongoDB connection verified")

            # Create indexes for performance
            await self._create_indexes()
            logger.info("MongoDB indexes created")
        except Exception as e:
            logger.warning("MongoDB connection failed: %s. Running in degraded mode.", e)
            self._client = None
            self._db = None

    async def close(self) -> None:
        """Close MongoDB connection"""
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
            self._db = None
        logger.debug("MongoDB connection closed")

    async def _create_indexes(self) -> None:
        """Create recommended indexes for common query patterns"""
        collections = await self._db.list_collection_names()

        # Events collection indexes
        if "raw_events" in collections:
            await self._db.raw_events.create_index("timestamp")
            await self._db.raw_events.create_index("source")
            await self._db.raw_events.create_index("event_type")

        # Processed events indexes
        if "processed_events" in collections:
            await self._db.processed_events.create_index("input_hash", unique=True)
            await self._db.processed_events.create_index("timestamp")

        # Predictions indexes
        if "ai_predictions" in collections:
            await self._db.ai_predictions.create_index("request_id", unique=True)
            await self._db.ai_predictions.create_index("prediction_timestamp")

        # Behavioral profiles indexes
        if "behavioral_profiles" in collections:
            await self._db.behavioral_profiles.create_index("entity_id", unique=True)
            await self._db.behavioral_profiles.create_index("last_updated")

    def get_collection(self, name: str):
        """Get a MongoDB collection by name"""
        if self._db is None:
            raise RuntimeError("MongoDB not initialized. Call initialize() first.")
        return self._db[name]

    @property
    def db(self) -> Optional[AsyncIOMotorDatabase]:
        """Get the MongoDB database instance"""
        return self._db

    @property
    def is_initialized(self) -> bool:
        return self._client is not None


# Global singleton
mongo_db = MongoDatabase()


# Convenience function
async def get_mongo_collection(name: str):
    """Get a MongoDB collection (initializes connection if needed)"""
    if not mongo_db.is_initialized:
        await mongo_db.initialize()
    return mongo_db.get_collection(name)

