"""
BLACK VEIL V5 - Database Connections Package
"""
import logging

from src.backend.database.postgres import postgres_db, Base, get_db
from src.backend.database.mongo import mongo_db, get_mongo_collection
from src.backend.database.neo4j import neo4j_db
from src.backend.database.redis import redis_db

logger = logging.getLogger(__name__)


async def init_db():
    """Initialize all database connections"""
    logger.info("Initializing database connections...")
    await postgres_db.initialize()
    await mongo_db.initialize()
    await neo4j_db.initialize()
    await redis_db.initialize()
    logger.info("All database connections initialized")


async def close_db():
    """Close all database connections"""
    logger.info("Closing database connections...")
    await postgres_db.close()
    await mongo_db.close()
    await neo4j_db.close()
    await redis_db.close()
    logger.info("All database connections closed")


__all__ = [
    "postgres_db",
    "Base",
    "get_db",
    "mongo_db",
    "get_mongo_collection",
    "neo4j_db",
    "redis_db",
    "init_db",
    "close_db",
]
