"""
BLACK VEIL V5 - Global Error Handler Middleware
Catches and formats all exceptions with proper error responses
"""
import logging
import traceback
from typing import Union

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.backend.utils.logger import get_correlation_id

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """Global error handler for the FastAPI application"""

    @staticmethod
    def setup(app: FastAPI):
        """Register all exception handlers on the FastAPI app"""

        @app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": exc.status_code,
                        "message": exc.detail,
                        "type": "http_error",
                    },
                    "correlation_id": get_correlation_id() or "-",
                },
            )

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(
            request: Request, exc: RequestValidationError
        ):
            errors = exc.errors()
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": {
                        "code": 422,
                        "message": "Validation error",
                        "type": "validation_error",
                        "details": [
                            {
                                "field": ".".join(str(loc) for loc in err["loc"]),
                                "message": err["msg"],
                                "type": err["type"],
                            }
                            for err in errors
                        ],
                    },
                    "correlation_id": get_correlation_id() or "-",
                },
            )

        @app.exception_handler(ValidationError)
        async def pydantic_validation_handler(
            request: Request, exc: ValidationError
        ):
            errors = exc.errors()
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": {
                        "code": 422,
                        "message": "Validation error",
                        "type": "validation_error",
                        "details": [
                            {
                                "field": ".".join(str(loc) for loc in err["loc"]),
                                "message": err["msg"],
                                "type": err["type"],
                            }
                            for err in errors
                        ],
                    },
                    "correlation_id": get_correlation_id() or "-",
                },
            )

        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            correlation_id = get_correlation_id() or "-"
            logger.error(
                "Unhandled exception",
                extra={
                    "extra_fields": {
                        "correlation_id": correlation_id,
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                    }
                },
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": 500,
                        "message": "Internal server error",
                        "type": "internal_error",
                    },
                    "correlation_id": correlation_id,
                },
            )
