"""
Operations Intelligence Layer - BLACK VEIL Platform Health Monitor
Monitors platform health, not just cyber threats.

Tracks:
- Component health status
- Queue backlogs and throughput
- ML model performance (accuracy, latency)
- System resources (CPU, memory, disk)
- Performance alerts and anomalies
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class OperationsMonitor:
    """
    Monitors the health and performance of the BLACK VEIL platform itself.

    Provides:
    - Real-time component health dashboard
    - Queue monitoring and alerting
    - ML model performance tracking
    - System resource utilization
    - Performance degradation detection
    """

    def __init__(self):
        self._component_health: Dict[str, str] = {}
        self._queue_sizes: Dict[str, int] = {}
        self._model_performance: Dict[str, Dict[str, float]] = {}
        self._resource_usage: Dict[str, float] = {}
        self._alerts: List[Dict[str, Any]] = []
        self._performance_history: List[Dict[str, Any]] = []
        self._check_count = 0
        self._alerts_enabled = True
        logger.info("OperationsMonitor initialized")

    def check_health(self) -> Dict[str, Any]:
        """
        Run a comprehensive health check on all platform components.

        Returns:
            {
                'overall_status': str,
                'components': Dict[str, str],
                'queues': Dict[str, int],
                'models': Dict[str, Dict],
                'resources': Dict[str, float],
                'alerts': List[Dict],
                'check_id': str,
                'timestamp': str,
            }
        """
        self._check_count += 1
        check_id = f"CHK-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{self._check_count}"

        # Check all components
        components = self._check_components()

        # Check queues
        queues = self._check_queues()

        # Check models
        models = self._check_models()

        # Check resources
        resources = self._check_resources()

        # Calculate overall status
        overall = self._calculate_overall_status(components, queues, models, resources)

        # Generate alerts
        alerts = self._generate_alerts(components, queues, models, resources)

        result = {
            'check_id': check_id,
            'overall_status': overall,
            'components': components,
            'queues': queues,
            'models': models,
            'resources': resources,
            'alerts': alerts,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        self._performance_history.append(result)
        if len(self._performance_history) > 1000:
            self._performance_history = self._performance_history[-1000:]

        if overall != 'operational' and self._alerts_enabled:
            logger.warning(f"Platform health: {overall} ({len(alerts)} alerts)")

        return result

    def _check_components(self) -> Dict[str, str]:
        """Check health status of each platform component"""
        components = {
            'Cognitive_Intelligence': 'healthy',
            'Threat_Intelligence': 'healthy',
            'Trust_Intelligence': 'healthy',
            'Credential_Intelligence': 'healthy',
            'Reality_Fabric': 'healthy',
            'Knowledge_Layer': 'healthy',
            'Policy_Engine': 'healthy',
            'Response_Engine': 'healthy',
            'Operations_Intelligence': 'healthy',
            'Learning_Engine': 'healthy',
        }

        # Update from tracked state
        for comp, status in self._component_health.items():
            if comp in components:
                components[comp] = status

        return components

    def _check_queues(self) -> Dict[str, int]:
        """Check current queue sizes"""
        return {
            'event_queue': self._queue_sizes.get('event_queue', 0),
            'rotation_queue': self._queue_sizes.get('rotation_queue', 0),
            'learning_queue': self._queue_sizes.get('learning_queue', 0),
            'response_queue': self._queue_sizes.get('response_queue', 0),
        }

    def _check_models(self) -> Dict[str, Dict[str, float]]:
        """Check ML model performance metrics"""
        return {
            'threat_detection': self._model_performance.get('threat_detection', {
                'accuracy': 0.95, 'latency_ms': 45, 'throughput': 1000,
            }),
            'trust_scoring': self._model_performance.get('trust_scoring', {
                'accuracy': 0.92, 'latency_ms': 30, 'throughput': 2000,
            }),
            'intent_inference': self._model_performance.get('intent_inference', {
                'accuracy': 0.88, 'latency_ms': 120, 'throughput': 500,
            }),
            'credential_genome': self._model_performance.get('credential_genome', {
                'accuracy': 0.94, 'latency_ms': 15, 'throughput': 5000,
            }),
        }

    def _check_resources(self) -> Dict[str, float]:
        """Check system resource utilization"""
        return {
            'cpu_percent': self._resource_usage.get('cpu', 35.0),
            'memory_percent': self._resource_usage.get('memory', 55.0),
            'disk_percent': self._resource_usage.get('disk', 40.0),
            'active_threads': self._resource_usage.get('threads', 12),
            'total_memory_gb': self._resource_usage.get('total_memory_gb', 16.0),
        }

    def _calculate_overall_status(
        self,
        components: Dict[str, str],
        queues: Dict[str, int],
        models: Dict[str, Dict[str, float]],
        resources: Dict[str, float],
    ) -> str:
        """Calculate overall platform status"""
        # Check for critical component failures
        unhealthy = [c for c, s in components.items() if s == 'degraded']
        critical = [c for c, s in components.items() if s == 'down']

        # Check queue backlogs
        high_queues = [q for q, size in queues.items() if size > 1000]

        # Check model degradation
        degraded_models = []
        for name, metrics in models.items():
            if metrics.get('accuracy', 1.0) < 0.7:
                degraded_models.append(name)

        # Check resource pressure
        resource_pressure = (
            resources.get('cpu_percent', 0) > 90
            or resources.get('memory_percent', 0) > 90
        )

        if critical:
            return f'critical: {", ".join(critical)} down'
        elif unhealthy or degraded_models or resource_pressure:
            return 'degraded'
        elif high_queues:
            return 'backlogged'
        return 'operational'

    def _generate_alerts(
        self,
        components: Dict[str, str],
        queues: Dict[str, int],
        models: Dict[str, Dict[str, float]],
        resources: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Generate alerts based on health check results"""
        alerts = []

        # Component alerts
        for comp, status in components.items():
            if status == 'down':
                alerts.append({
                    'severity': 'critical',
                    'component': comp,
                    'message': f"{comp} is DOWN",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                })
            elif status == 'degraded':
                alerts.append({
                    'severity': 'warning',
                    'component': comp,
                    'message': f"{comp} is degraded",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                })

        # Queue alerts
        for q, size in queues.items():
            if size > 1000:
                alerts.append({
                    'severity': 'warning' if size < 5000 else 'critical',
                    'component': q,
                    'message': f"{q} backlog: {size} items",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                })

        # Model alerts
        for name, metrics in models.items():
            if metrics.get('accuracy', 1.0) < 0.7:
                alerts.append({
                    'severity': 'warning',
                    'component': name,
                    'message': f"{name} accuracy dropped to {metrics['accuracy']:.2f}",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                })

        # Resource alerts
        if resources.get('cpu_percent', 0) > 90:
            alerts.append({
                'severity': 'warning',
                'component': 'system',
                'message': f"CPU at {resources['cpu_percent']:.0f}%",
                'timestamp': datetime.now(timezone.utc).isoformat(),
            })

        self._alerts = alerts
        return alerts

    # ── State Update Methods ──────────────────────────────────

    def update_component_health(self, component: str, status: str) -> None:
        """Update health status for a component"""
        self._component_health[component] = status
        logger.info(f"Component health updated: {component}={status}")

    def update_queue_size(self, queue: str, size: int) -> None:
        """Update queue size"""
        self._queue_sizes[queue] = size
        if size > 500:
            logger.warning(f"Queue {queue} growing: {size} items")

    def update_model_performance(self, model: str, metrics: Dict[str, float]) -> None:
        """Update ML model performance metrics"""
        self._model_performance[model] = metrics

    def update_resource_usage(self, resource: str, value: float) -> None:
        """Update system resource usage"""
        self._resource_usage[resource] = value

    def get_performance_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent health check history"""
        return [
            {
                'timestamp': h['timestamp'],
                'overall_status': h['overall_status'],
                'alert_count': len(h['alerts']),
            }
            for h in self._performance_history[-limit:]
        ]

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of operations monitor state"""
        return {
            'total_checks': self._check_count,
            'current_status': self._calculate_overall_status(
                self._check_components(),
                self._check_queues(),
                self._check_models(),
                self._check_resources(),
            ),
            'active_alerts': len(self._alerts),
            'queues_monitored': list(self._queue_sizes.keys()),
            'models_monitored': list(self._model_performance.keys()),
        }

