"""
BLACK VEIL V5 - Authentication Middleware
JWT token verification and user context injection via FastAPI middleware
"""
import logging
from typing import Optional

import jwt
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.backend.config import AUTH_SECRET_KEY, AUTH_ALGORITHM, AUTH_TOKEN_TYPE

logger = logging.getLogger(__name__)

# Public paths that don't require authentication
PUBLIC_PATHS = {
    "/api/v1/health",
    "/api/v1/health/",
    "/api/v1/health/detailed",
    "/api/v1/health/ready",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
    "/metrics",
}

# OpenAPI paths
OPENAPI_PATHS = {"/api/docs", "/api/redoc", "/api/openapi.json"}


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware that validates JWT tokens and attaches user context"""

    def __init__(self, app, exclude_paths: Optional[set] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or PUBLIC_PATHS

    async def dispatch(self, request: Request, call_next):
        """Process the request with authentication check"""

        # Skip auth for public paths
        if request.url.path in self.exclude_paths or request.url.path.startswith("/api/docs"):
            return await call_next(request)

        # For OPTIONS requests (CORS preflight), proceed without auth
        if request.method == "OPTIONS":
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            response = await call_next(request)
            return response

        try:
            # Parse Bearer token
            scheme, _, token = auth_header.partition(" ")
            if scheme.lower() != "bearer" or not token:
                response = await call_next(request)
                return response

            # Decode JWT
            payload = jwt.decode(
                token,
                AUTH_SECRET_KEY,
                algorithms=[AUTH_ALGORITHM],
                options={"verify_exp": True},
            )

            # Attach user info to request state
            request.state.user_id = payload.get("sub")
            request.state.user_role = payload.get("role", "viewer")
            request.state.user_permissions = payload.get("permissions", [])
            request.state.token_type = payload.get("type", AUTH_TOKEN_TYPE)
            request.state.is_authenticated = True

        except jwt.ExpiredSignatureError:
            logger.warning("Expired token used on %s", request.url.path)
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token on %s: %s", request.url.path, str(e))
        except Exception as e:
            logger.error("Auth error on %s: %s", request.url.path, str(e))

        # Proceed with the request (auth failure doesn't block, routes handle their own auth)
        response = await call_next(request)
        return response
