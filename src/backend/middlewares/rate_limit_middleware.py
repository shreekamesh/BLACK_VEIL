"""
BLACK VEIL V5 - Rate Limiting Middleware
Token-bucket based rate limiting with Redis backend
"""
import logging
import time
from typing import Dict, Tuple

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.backend.database import redis_db
from src.backend.config import RATE_LIMIT_ENABLED, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis.
    Falls back to in-memory if Redis is unavailable.
    """

    def __init__(self, app, requests_per_window: int = RATE_LIMIT_REQUESTS,
                 window_seconds: int = RATE_LIMIT_WINDOW):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds

        # In-memory fallback: {identifier: [(timestamp, count)]}
        self._memory_store: Dict[str, list] = {}

        # Rate limit exempt paths
        self.exempt_paths = {
            "/api/v1/health",
            "/api/v1/health/",
            "/api/v1/health/detailed",
            "/api/v1/health/ready",
            "/metrics",
        }

    def _get_identifier(self, request: Request) -> str:
        """Get a unique identifier for the client"""
        # Use API key if present, fall back to IP
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"apikey:{api_key}"

        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"

    async def _check_redis_rate_limit(self, identifier: str) -> Tuple[bool, int]:
        """Check rate limit using Redis. Falls back to memory if Redis unavailable."""
        if not redis_db.is_initialized or redis_db.client is None:
            return await self._check_memory_rate_limit(identifier)

        try:
            key = f"ratelimit:{identifier}"
            now = int(time.time())
            window_start = now - self.window_seconds

            # Remove old entries and count current
            await redis_db.client.zremrangebyscore(key, 0, window_start)
            count = await redis_db.client.zcard(key)

            if count >= self.requests_per_window:
                return False, self.requests_per_window

            # Add current request
            await redis_db.client.zadd(key, {str(now): now})
            await redis_db.client.expire(key, self.window_seconds + 10)
            remaining = self.requests_per_window - count - 1
            return True, max(0, remaining)

        except Exception as e:
            logger.warning("Redis rate limit check failed, using memory: %s", e)
            return await self._check_memory_rate_limit(identifier)

    async def _check_memory_rate_limit(self, identifier: str) -> Tuple[bool, int]:
        """Fallback rate limit using in-memory store"""
        now = time.time()
        window_start = now - self.window_seconds

        if identifier not in self._memory_store:
            self._memory_store[identifier] = []

        # Clean old entries
        self._memory_store[identifier] = [
            t for t in self._memory_store[identifier] if t > window_start
        ]

        count = len(self._memory_store[identifier])
        if count >= self.requests_per_window:
            return False, self.requests_per_window

        self._memory_store[identifier].append(now)
        remaining = self.requests_per_window - count - 1
        return True, max(0, remaining)

    async def dispatch(self, request: Request, call_next):
        """Process the request with rate limiting"""
        if not RATE_LIMIT_ENABLED or request.url.path in self.exempt_paths:
            return await call_next(request)

        identifier = self._get_identifier(request)
        allowed, remaining = await self._check_redis_rate_limit(identifier)

        if not allowed:
            logger.warning("Rate limit exceeded for %s", identifier)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Try again later.",
                    "retry_after": self.window_seconds,
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + self.window_seconds),
                    "Retry-After": str(self.window_seconds),
                },
            )

        # Process the request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response

