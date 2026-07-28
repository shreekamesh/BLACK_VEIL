"""
BLACK VEIL V5 - Structured Logging Configuration
Provides structured JSON logging with correlation ID support
"""
import json
import logging
import sys
import threading
import uuid
from datetime import datetime, timezone
from typing import Optional

# Thread-local storage for correlation IDs
_local = threading.local()


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set correlation ID for current thread/request"""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    _local.correlation_id = correlation_id
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get the current thread's correlation ID"""
    return getattr(_local, "correlation_id", None)


class CorrelationIDFilter(logging.Filter):
    """Logging filter that adds correlation ID to log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = getattr(_local, "correlation_id", None) or "-"
        return True


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "-"),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)

        if level:
            logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        else:
            logger.setLevel(logging.INFO)

        # Add correlation ID filter
        handler.addFilter(CorrelationIDFilter())

        # Use JSON formatter for production, text for debug
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def setup_logging(level: str = "INFO", json_format: bool = True) -> None:
    """Configure root logger and global logging settings"""
    root_logger = logging.getLogger()

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(CorrelationIDFilter())

    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s "
            "[correlation_id=%(correlation_id)s]"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Set correlation ID for root thread
    set_correlation_id()

    root_logger.info("Logging configured at level %s", level)


# Initialize with default settings when imported
setup_logging(level="INFO", json_format=True)
