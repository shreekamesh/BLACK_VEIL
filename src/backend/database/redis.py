"""
BLACK VEIL V5 - Redis Database Connection
Async caching and real-time data with Redis
"""
import logging
from typing import Optional, Any

from redis.asyncio import Redis as AsyncRedis, ConnectionPool

from src.backend.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DB,
    REDIS_MAX_CONNECTIONS,
    REDIS_SOCKET_TIMEOUT,
    REDIS_SOCKET_CONNECT_TIMEOUT,
)

logger = logging.getLogger(__name__)


class RedisDatabase:
    """Redis async caching and real-time data manager"""

    def __init__(self):
        self._client: Optional[AsyncRedis] = None
        self._pool: Optional[ConnectionPool] = None

    def _build_url(self) -> str:
        """Build Redis connection URL"""
        if REDIS_PASSWORD:
            return f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        return f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    async def initialize(self) -> None:
        """Initialize Redis connection with pool"""
        if self._client is not None:
            logger.debug("Redis already initialized")
            return

        connection_url = self._build_url()
        logger.info("Connecting to Redis at %s:%s/%s", REDIS_HOST, REDIS_PORT, REDIS_DB)

        try:
            self._pool = ConnectionPool.from_url(
                connection_url,
                max_connections=REDIS_MAX_CONNECTIONS,
                socket_timeout=REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=REDIS_SOCKET_CONNECT_TIMEOUT,
                decode_responses=True,
                health_check_interval=30,
            )
            self._client = AsyncRedis(connection_pool=self._pool)

            # Verify connection
            await self._client.ping()
            logger.info("Redis connection verified")
        except Exception as e:
            logger.warning("Redis connection failed: %s. Running in degraded mode.", e)
            self._client = None
            self._pool = None

    async def close(self) -> None:
        """Close Redis connection"""
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None
        if self._pool:
            try:
                await self._pool.disconnect()
            except Exception:
                pass
            self._pool = None
        logger.debug("Redis connection closed")

    async def get(self, key: str) -> Optional[str]:
        """Get a value from cache"""
        if not self._client:
            await self.initialize()
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL (seconds)"""
        if not self._client:
            await self.initialize()
        if ttl:
            return await self._client.setex(key, ttl, value)
        return await self._client.set(key, value)

    async def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self._client:
            await self.initialize()
        return await self._client.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """Check if a key exists"""
        if not self._client:
            await self.initialize()
        return await self._client.exists(key) > 0

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on an existing key"""
        if not self._client:
            await self.initialize()
        return await self._client.expire(key, ttl)

    async def publish(self, channel: str, message: str) -> int:
        """Publish a message to a Redis channel"""
        if not self._client:
            await self.initialize()
        return await self._client.publish(channel, message)

    async def subscribe(self, channel: str):
        """Subscribe to a Redis channel (returns pubsub object)"""
        if not self._client:
            await self.initialize()
        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    async def incr(self, key: str) -> int:
        """Increment a counter"""
        if not self._client:
            await self.initialize()
        return await self._client.incr(key)

    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get a hash field"""
        if not self._client:
            await self.initialize()
        return await self._client.hget(key, field)

    async def hset(self, key: str, field: str, value: Any) -> int:
        """Set a hash field"""
        if not self._client:
            await self.initialize()
        return await self._client.hset(key, field, value)

    async def hgetall(self, key: str) -> dict:
        """Get all hash fields"""
        if not self._client:
            await self.initialize()
        return await self._client.hgetall(key)

    async def lpush(self, key: str, *values: Any) -> int:
        """Push values to a list"""
        if not self._client:
            await self.initialize()
        return await self._client.lpush(key, *values)

    async def lrange(self, key: str, start: int, stop: int) -> list:
        """Get a range of list values"""
        if not self._client:
            await self.initialize()
        return await self._client.lrange(key, start, stop)

    async def sadd(self, key: str, *members: Any) -> int:
        """Add members to a set"""
        if not self._client:
            await self.initialize()
        return await self._client.sadd(key, *members)

    async def smembers(self, key: str) -> set:
        """Get all members of a set"""
        if not self._client:
            await self.initialize()
        return await self._client.smembers(key)

    async def clear_all(self) -> None:
        """Clear all keys in current database (use with caution)"""
        if not self._client:
            await self.initialize()
        await self._client.flushdb()
        logger.warning("Redis database %s cleared", REDIS_DB)

    @property
    def client(self) -> Optional[AsyncRedis]:
        return self._client

    @property
    def is_initialized(self) -> bool:
        return self._client is not None


# Global singleton
redis_db = RedisDatabase()

