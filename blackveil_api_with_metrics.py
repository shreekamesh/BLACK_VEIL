"""
BLACK VEIL API - COMPLETE WITH METRICS
Single file - everything works together
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import numpy as np
from typing import List, Optional
import joblib
import time
import os
import threading

# ==================== METRICS SETUP ====================
from prometheus_client import Counter, Histogram, Gauge, start_http_server, REGISTRY

# Clear any existing metrics
for metric in list(REGISTRY._names_to_collectors.keys()):
    if metric.startswith('blackveil_'):
        REGISTRY.unregister(REGISTRY._names_to_collectors[metric])

# Define metrics
REQUEST_COUNT = Counter('blackveil_requests_total', 'Total requests', ['endpoint', 'method', 'status'])
REQUEST_LATENCY = Histogram('blackveil_request_latency_seconds', 'Request latency', ['endpoint', 'method'])
MODELS_LOADED = Gauge('blackveil_models_loaded', 'Number of loaded models')
PREDICTION_COUNT = Counter('blackveil_predictions_total', 'Total predictions', ['model', 'prediction'])
THREAT_DETECTED = Counter('blackveil_threats_detected_total', 'Threats detected', ['model'])
ERROR_COUNT = Counter('blackveil_errors_total', 'Total errors', ['endpoint', 'error_type'])
ACTIVE_REQUESTS = Gauge('blackveil_active_requests', 'Active requests')

# Start metrics server
start_http_server(9090)
print("📊 Metrics server started on port 9090")
print("   http://localhost:9090/metrics")

# ==================== FASTAPI APP ====================
app = FastAPI(title="BLACK VEIL API", version="2.0.0")

# Global variables
MODELS = {}
MODELS_DIR = '/home/eroz/Documents/black_veil/models'

@app.on_event("startup")
async def load_models():
    """Load all models on startup"""
    print("🔄 Loading BLACK VEIL models...")
    
    try:
        # Load all models
        model_files = {
            'unsw_rf': 'UNSW_RandomForest.pkl',
            'unsw_xgb': 'UNSW_XGBoost.pkl',
            'unsw_lgb': 'UNSW_LightGBM.pkl',
            'unsw_cat': 'UNSW_CatBoost.pkl',
            'edge_rf': 'EDGE_RandomForest.pkl',
            'edge_xgb': 'EDGE_XGBoost.pkl',
            'edge_lgb': 'EDGE_LightGBM.pkl',
            'edge_cat': 'EDGE_CatBoost.pkl',
            'cicids_rf': 'CICIDS_RandomForest.pkl',
            'cicids_mlp': 'CICIDS_MLP.pkl',
            'cicids_lr': 'CICIDS_LogisticRegression.pkl'
        }
        
        loaded = 0
        for name, filename in model_files.items():
            try:
                model_path = f"{MODELS_DIR}/{filename}"
                if os.path.exists(model_path):
                    MODELS[name] = joblib.load(model_path)
                    loaded += 1
                    print(f"   ✅ Loaded: {name}")
                else:
                    print(f"   ⚠️ Not found: {filename}")
            except Exception as e:
                print(f"   ❌ Failed: {name} - {e}")
        
        # UPDATE METRICS - DIRECTLY SET THE VALUE
        MODELS_LOADED.set(loaded)
        print(f"\n✅ Loaded {loaded} models successfully!")
        print(f"📊 Models loaded metric set to: {loaded}")
        
    except Exception as e:
        print(f"❌ Failed to load models: {e}")

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to track request metrics"""
    start_time = time.time()
    ACTIVE_REQUESTS.inc()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        endpoint=request.url.path,
        method=request.method,
        status=str(response.status_code)
    ).inc()
    REQUEST_LATENCY.labels(
        endpoint=request.url.path,
        method=request.method
    ).observe(duration)
    
    ACTIVE_REQUESTS.dec()
    return response

class PredictionRequest(BaseModel):
    model_name: str
    features: List[float]

class PredictionResponse(BaseModel):
    prediction: int
    probability: Optional[List[float]] = None
    model: str
    confidence: float
    features_expected: int

@app.get("/")
async def root():
    return {
        "service": "BLACK VEIL API",
        "status": "running",
        "models_loaded": len(MODELS),
        "metrics": "http://localhost:9090/metrics"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": len(MODELS),
        "models": list(MODELS.keys())
    }

@app.get("/models")
async def list_models():
    model_list = []
    for name, model in MODELS.items():
        model_list.append({
            "name": name,
            "type": type(model).__name__,
            "features": getattr(model, 'n_features_in_', 'N/A'),
            "classes": getattr(model, 'n_classes_', 'N/A')
        })
    return {"total_models": len(model_list), "models": model_list}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    if request.model_name not in MODELS:
        ERROR_COUNT.labels(endpoint='predict', error_type='model_not_found').inc()
        raise HTTPException(status_code=404, detail=f"Model not found")
    
    model = MODELS[request.model_name]
    features = np.array(request.features).reshape(1, -1)
    
    n_features = getattr(model, 'n_features_in_', None)
    if n_features is not None and features.shape[1] != n_features:
        ERROR_COUNT.labels(endpoint='predict', error_type='feature_mismatch').inc()
        raise HTTPException(
            status_code=400,
            detail=f"Expected {n_features} features, got {features.shape[1]}"
        )
    
    try:
        prediction = int(model.predict(features)[0])
        
        # Track metrics
        PREDICTION_COUNT.labels(model=request.model_name, prediction=str(prediction)).inc()
        if prediction == 1:
            THREAT_DETECTED.labels(model=request.model_name).inc()
        
        probability = None
        confidence = 1.0
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0]
            probability = proba.tolist()
            confidence = float(max(proba))
        
        return PredictionResponse(
            prediction=prediction,
            probability=probability,
            model=request.model_name,
            confidence=confidence,
            features_expected=n_features if n_features is not None else len(request.features)
        )
        
    except Exception as e:
        ERROR_COUNT.labels(endpoint='predict', error_type=str(e)[:50]).inc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
