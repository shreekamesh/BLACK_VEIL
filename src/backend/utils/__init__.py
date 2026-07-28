"""
BLACK VEIL V5 - Utilities Package
"""
from src.backend.utils.logger import (
    get_logger,
    setup_logging,
    set_correlation_id,
    CorrelationIDFilter,
    JsonFormatter,
)
from src.backend.utils.metrics import (
    track_request_metrics,
    track_ai_prediction,
    track_ai_duration,
    update_trust_score,
    get_metrics,
    request_count,
    request_duration,
    ai_predictions,
    ai_prediction_duration,
    ai_confidence,
    trust_scores,
    attacks_detected,
    attack_response_time,
)
from src.backend.utils.crypto import CryptoUtils
from src.backend.utils.validators import Validators

crypto = CryptoUtils()
validators = Validators()

# Alias for backward compatibility
track_request = track_request_metrics

__all__ = [
    "get_logger",
    "setup_logging",
    "set_correlation_id",
    "CorrelationIDFilter",
    "JsonFormatter",
    "track_request",
    "track_request_metrics",
    "track_ai_prediction",
    "track_ai_duration",
    "update_trust_score",
    "get_metrics",
    "request_count",
    "request_duration",
    "ai_predictions",
    "ai_prediction_duration",
    "ai_confidence",
    "trust_scores",
    "attacks_detected",
    "attack_response_time",
    "crypto",
    "validators",
    "CryptoUtils",
    "Validators",
]
