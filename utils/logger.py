"""
BLACK VEIL V5 — Structured JSON Logging
Production-grade logging with correlation IDs, structured output, and multiple handlers
"""
import json
import logging
import logging.config
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Context variable for correlation ID propagation across async tasks
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs JSON structured logs"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string"""
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "correlation_id": correlation_id_var.get() or "",
            "process": record.process,
            "thread": record.thread,
        }

        # Add exception info if present
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields passed via extra={}
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_entry.update(record.extra)

        return json.dumps(log_entry, default=str)


class StructuredLogger:
    """
    Production-grade structured logger with JSON output.
    Supports console, file (rotating), and Loki handlers.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or self._default_config()
        self._setup_logging()

    @staticmethod
    def _default_config() -> dict[str, Any]:
        """Default logging configuration from environment"""
        return {
            "level": os.getenv("BV_LOG_LEVEL", "INFO").upper(),
            "format": os.getenv("BV_LOG_FORMAT", "json"),
            "handlers": os.getenv("BV_LOG_HANDLERS", "console,file").split(","),
            "file": {
                "path": os.getenv("BV_LOG_PATH", "logs"),
                "max_bytes": int(os.getenv("BV_LOG_MAX_BYTES", str(100 * 1024 * 1024))),
                "backup_count": int(os.getenv("BV_LOG_BACKUP_COUNT", "10")),
            },
        }

    def _setup_logging(self) -> None:
        """Configure structured logging with multiple handlers"""
        log_level = self.config.get("level", "INFO")
        log_handlers: dict[str, logging.Handler] = {}

        # Console handler
        if "console" in self.config.get("handlers", ["console"]):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(JSONFormatter())
            console_handler.setLevel(log_level)
            log_handlers["console"] = console_handler

        # File handler with rotation
        if "file" in self.config.get("handlers", []):
            file_config = self.config.get("file", {})
            log_path = Path(file_config.get("path", "logs"))
            log_path.mkdir(parents=True, exist_ok=True)

            from logging.handlers import RotatingFileHandler

            file_handler = RotatingFileHandler(
                filename=str(log_path / "blackveil.log"),
                maxBytes=file_config.get("max_bytes", 100 * 1024 * 1024),
                backupCount=file_config.get("backup_count", 10),
            )
            file_handler.setFormatter(JSONFormatter())
            file_handler.setLevel(log_level)
            log_handlers["file"] = file_handler

        # Configure root logger
        logging.basicConfig(
            level=log_level,
            handlers=list(log_handlers.values()),
            force=True,
        )

        # Suppress noisy library loggers
        for lib in ("uvicorn", "sqlalchemy.engine", "kafka", "urllib3", "asyncio"):
            logging.getLogger(lib).setLevel(logging.WARNING)

        self.logger = logging.getLogger("blackveil")

    def get_logger(self, name: str) -> logging.Logger:
        """Get a child logger with the specified name"""
        return logging.getLogger(f"blackveil.{name}")

    def set_correlation_id(self, correlation_id: Optional[str] = None) -> str:
        """Set correlation ID for the current async context"""
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
        return correlation_id

    def get_correlation_id(self) -> str:
        """Get current correlation ID"""
        return correlation_id_var.get()


# Global singleton
_logger_instance: Optional[StructuredLogger] = None


def get_logger(name: str) -> logging.Logger:
    """Get a structured child logger by name"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = StructuredLogger()
    return _logger_instance.get_logger(name)


def set_correlation_id(cid: Optional[str] = None) -> str:
    """Set correlation ID for current context"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = StructuredLogger()
    return _logger_instance.set_correlation_id(cid)


def get_correlation_id() -> str:
    """Get current correlation ID"""
    return correlation_id_var.get()


# --- Convenience logging functions ---

def log_debug(message: str, **kwargs: Any) -> None:
    """Log debug message with structured fields"""
    logging.getLogger("blackveil").debug(message, extra={"extra": kwargs})


def log_info(message: str, **kwargs: Any) -> None:
    """Log info message with structured fields"""
    logging.getLogger("blackveil").info(message, extra={"extra": kwargs})


def log_warning(message: str, **kwargs: Any) -> None:
    """Log warning message with structured fields"""
    logging.getLogger("blackveil").warning(message, extra={"extra": kwargs})


def log_error(message: str, **kwargs: Any) -> None:
    """Log error message with structured fields"""
    logging.getLogger("blackveil").error(message, extra={"extra": kwargs})


def log_critical(message: str, **kwargs: Any) -> None:
    """Log critical message with structured fields"""
    logging.getLogger("blackveil").critical(message, extra={"extra": kwargs})

