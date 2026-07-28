"""
BLACK VEIL V5 - Request Logging Middleware
Logs all requests and responses with correlation IDs
"""
import time
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.backend.utils.logger import set_correlation_id, get_correlation_id

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all HTTP requests and responses"""

    async def dispatch(self, request: Request, call_next):
        # Set correlation ID for this request
        correlation_id = request.headers.get("X-Correlation-ID")
        set_correlation_id(correlation_id)

        # Request metadata
        start_time = time.time()
        request_id = get_correlation_id()
        method = request.method
        path = request.url.path
        query = str(request.url.query)
        client_host = request.client.host if request.client else "unknown"

        # Log request
        logger.info(
            "Request started",
            extra={
                "extra_fields": {
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "query": query,
                    "client_ip": client_host,
                    "user_agent": request.headers.get("user-agent", ""),
                }
            },
        )

        # Process request
        try:
            response: Response = await call_next(request)
            duration = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                extra={
                    "extra_fields": {
                        "request_id": request_id,
                        "method": method,
                        "path": path,
                        "status_code": response.status_code,
                        "duration_ms": round(duration * 1000, 2),
                    }
                },
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = request_id
            response.headers["X-Request-Duration-Ms"] = str(round(duration * 1000, 2))

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "extra_fields": {
                        "request_id": request_id,
                        "method": method,
                        "path": path,
                        "error": str(e),
                        "duration_ms": round(duration * 1000, 2),
                    }
                },
            )
            raise
