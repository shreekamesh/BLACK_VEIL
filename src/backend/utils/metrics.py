"""
BLACK VEIL V5 - Prometheus Metrics Definition
Custom metrics for monitoring AI performance, trust scores, and system health
"""
import time
from functools import wraps
from typing import Optional

from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY

# ── Request Metrics ───────────────────────────────────────────

request_count = Counter(
    "blackveil_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status"],
)

request_duration = Histogram(
    "blackveil_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

active_requests = Gauge(
    "blackveil_active_requests",
    "Number of currently active requests",
)


# ── AI Model Metrics ─────────────────────────────────────────

ai_predictions = Counter(
    "blackveil_ai_predictions_total",
    "Total AI predictions made",
    ["model_name", "model_version", "prediction_type"],
)

ai_prediction_duration = Histogram(
    "blackveil_ai_prediction_duration_seconds",
    "AI prediction duration in seconds",
    ["model_name", "model_version"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

ai_confidence = Gauge(
    "blackveil_ai_confidence",
    "AI prediction confidence score",
    ["model_name", "model_version"],
)

model_accuracy = Gauge(
    "blackveil_model_accuracy",
    "Model accuracy score",
    ["model_name", "model_version"],
)

model_drift_score = Gauge(
    "blackveil_model_drift_score",
    "Model drift detection score",
    ["model_name"],
)


# ── Trust Metrics ────────────────────────────────────────────

trust_scores = Gauge(
    "blackveil_trust_score",
    "Current trust score for entities",
    ["entity_type", "entity_id"],
)

trust_changes = Counter(
    "blackveil_trust_changes_total",
    "Total trust score changes",
    ["entity_type", "change_type"],
)

recovery_count = Counter(
    "blackveil_recovery_total",
    "Total trust recovery events",
    ["recovery_type", "success"],
)


# ── Attack Detection Metrics ─────────────────────────────────

attacks_detected = Counter(
    "blackveil_attacks_detected_total",
    "Total attacks detected",
    ["attack_type", "severity", "detection_method"],
)

attack_response_time = Histogram(
    "blackveil_attack_response_time_seconds",
    "Time to respond to detected attacks",
    ["severity"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
)

false_positives = Counter(
    "blackveil_false_positives_total",
    "Total false positive alerts",
    ["model_name"],
)


# ── Deception Metrics ────────────────────────────────────────

deception_deployments = Counter(
    "blackveil_deception_deployments_total",
    "Total deception technique deployments",
    ["deception_type", "result"],
)

deception_interactions = Counter(
    "blackveil_deception_interactions_total",
    "Total attacker interactions with deception",
    ["deception_type"],
)


# ── System Metrics ───────────────────────────────────────────

system_uptime = Gauge(
    "blackveil_system_uptime_seconds",
    "System uptime in seconds",
)

active_agents = Gauge(
    "blackveil_active_agents",
    "Number of active AI agents",
    ["agent_type"],
)

database_connections = Gauge(
    "blackveil_database_connections",
    "Number of active database connections",
    ["database_type"],
)

memory_usage = Gauge(
    "blackveil_memory_usage_bytes",
    "Memory usage in bytes",
    ["component"],
)

cpu_usage = Gauge(
    "blackveil_cpu_usage_percent",
    "CPU usage percentage",
    ["component"],
)


# ── Tracking Decorators ──────────────────────────────────────

def track_request_metrics(func):
    """Decorator to track request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        active_requests.inc()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            active_requests.dec()
            request_duration.labels(
                method=getattr(func, "__name__", "unknown"),
                endpoint=func.__name__,
            ).observe(duration)
    return wrapper


def track_ai_prediction(model_name: str, model_version: str, prediction_type: str, confidence: float):
    """Record an AI prediction metric"""
    ai_predictions.labels(
        model_name=model_name,
        model_version=model_version,
        prediction_type=prediction_type,
    ).inc()
    ai_confidence.labels(
        model_name=model_name,
        model_version=model_version,
    ).set(confidence)


def track_ai_duration(model_name: str, model_version: str, duration_seconds: float):
    """Record AI prediction duration"""
    ai_prediction_duration.labels(
        model_name=model_name,
        model_version=model_version,
    ).observe(duration_seconds)


def update_trust_score(entity_type: str, entity_id: str, score: float):
    """Update trust score gauge"""
    trust_scores.labels(
        entity_type=entity_type,
        entity_id=entity_id,
    ).set(score)


def get_metrics() -> str:
    """Get all metrics in Prometheus format"""
    return generate_latest(REGISTRY).decode()


# ── Performance Tracking ─────────────────────────────────────

class PerformanceTracker:
    """Context manager for tracking operation performance"""

    def __init__(self, metric_name: str, labels: Optional[dict] = None):
        self.metric_name = metric_name
        self.labels = labels or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        request_duration.labels(
            method=self.metric_name,
            endpoint=self.labels.get("endpoint", "unknown"),
        ).observe(duration)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.__exit__(exc_type, exc_val, exc_tb)
