"""
BLACK VEIL V5 - Logger Utility
Structured JSON logging for AI foundation layer
"""
import logging
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry)


def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JsonFormatter())
        logger.addHandler(console_handler)

        # File handler (optional)
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "ai_foundation.log")
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger


def log_prediction(
    logger: logging.Logger,
    model_name: str,
    prediction: Any,
    confidence: float,
    latency_ms: float,
    **kwargs
) -> None:
    """
    Log a prediction event with structured data.

    Args:
        logger: Logger instance
        model_name: Name of the model
        prediction: Prediction value
        confidence: Confidence score
        latency_ms: Processing latency in milliseconds
        **kwargs: Additional metadata
    """
    extra = {
        "event": "prediction",
        "model": model_name,
        "prediction": str(prediction),
        "confidence": round(confidence, 4),
        "latency_ms": round(latency_ms, 2),
    }
    extra.update(kwargs)
    logger.info("Prediction completed", extra=extra)


def log_training(
    logger: logging.Logger,
    model_name: str,
    epoch: int,
    loss: float,
    accuracy: float,
    **kwargs
) -> None:
    """
    Log a training event with structured data.

    Args:
        logger: Logger instance
        model_name: Name of the model
        epoch: Current epoch
        loss: Training loss
        accuracy: Training accuracy
        **kwargs: Additional metadata
    """
    extra = {
        "event": "training",
        "model": model_name,
        "epoch": epoch,
        "loss": round(loss, 4),
        "accuracy": round(accuracy, 4),
    }
    extra.update(kwargs)
    logger.info(f"Training epoch {epoch}", extra=extra)


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an error with context.

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Optional context dictionary
    """
    extra = {
        "event": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    if context:
        extra["context"] = context
    logger.error(f"Error: {error}", extra=extra, exc_info=True)
