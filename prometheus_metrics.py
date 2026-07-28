"""
BLACK VEIL - Prometheus Metrics Integration
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from prometheus_client import start_http_server
import time
import threading

# Define metrics
REQUEST_COUNT = Counter('blackveil_requests_total', 'Total requests', ['endpoint', 'method', 'status'])
REQUEST_LATENCY = Histogram('blackveil_request_latency_seconds', 'Request latency', ['endpoint', 'method'])
MODELS_LOADED = Gauge('blackveil_models_loaded', 'Number of loaded models')
PREDICTION_COUNT = Counter('blackveil_predictions_total', 'Total predictions', ['model', 'prediction'])
THREAT_DETECTED = Counter('blackveil_threats_detected', 'Threats detected', ['model'])
ERROR_COUNT = Counter('blackveil_errors_total', 'Total errors', ['endpoint', 'error_type'])
ACTIVE_REQUESTS = Gauge('blackveil_active_requests', 'Active requests')

class MetricsMiddleware:
    """Middleware to track request metrics"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        
        start = time.time()
        endpoint = scope.get('path', '/unknown')
        method = scope.get('method', 'UNKNOWN')
        
        ACTIVE_REQUESTS.inc()
        
        # Store response status
        status = [200]
        
        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                status[0] = message['status']
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            status[0] = 500
            raise
        finally:
            elapsed = time.time() - start
            REQUEST_COUNT.labels(endpoint=endpoint, method=method, status=str(status[0])).inc()
            REQUEST_LATENCY.labels(endpoint=endpoint, method=method).observe(elapsed)
            ACTIVE_REQUESTS.dec()

def track_prediction(model_name: str, prediction: int):
    """Track prediction metrics"""
    PREDICTION_COUNT.labels(model=model_name, prediction=str(prediction)).inc()
    if prediction == 1:  # Threat detected
        THREAT_DETECTED.labels(model=model_name).inc()

def track_error(endpoint: str, error_type: str):
    """Track error metrics"""
    ERROR_COUNT.labels(endpoint=endpoint, error_type=error_type).inc()

def update_models_loaded(count: int):
    """Update models loaded metric"""
    MODELS_LOADED.set(count)

def start_metrics_server(port: int = 9090):
    """Start Prometheus metrics server"""
    start_http_server(port)
    print(f"📊 Metrics server started on port {port}")
    print(f"   Metrics URL: http://localhost:{port}/metrics")

if __name__ == "__main__":
    # Test metrics
    start_metrics_server(9090)
    print("✅ Metrics server running!")
    print("   Send requests to test metrics collection")
