"""
BLACK VEIL Inference API - FULLY WORKING WITH METRICS
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import numpy as np
from typing import List, Optional
import joblib
import time
import os
import threading

# Import metrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY

# Define metrics
REQUEST_COUNT = Counter('blackveil_requests_total', 'Total requests', ['endpoint', 'method', 'status'])
REQUEST_LATENCY = Histogram('blackveil_request_latency_seconds', 'Request latency', ['endpoint', 'method'])
MODELS_LOADED = Gauge('blackveil_models_loaded', 'Number of loaded models')
PREDICTION_COUNT = Counter('blackveil_predictions_total', 'Total predictions', ['model', 'prediction'])
THREAT_DETECTED = Counter('blackveil_threats_detected_total', 'Threats detected', ['model'])
ERROR_COUNT = Counter('blackveil_errors_total', 'Total errors', ['endpoint', 'error_type'])
ACTIVE_REQUESTS = Gauge('blackveil_active_requests', 'Active requests')

app = FastAPI(
    title="BLACK VEIL Inference API",
    description="Machine Learning Inference API with Metrics",
    version="2.0.0"
)

# Global variables
MODELS = {}
PREPROCESSORS = {}
MODELS_DIR = '/home/eroz/Documents/black_veil/models'

@app.on_event("startup")
async def load_models():
    """Load all models on startup"""
    print("🔄 Loading BLACK VEIL models...")
    
    try:
        # Load UNSW models
        MODELS['unsw_rf'] = joblib.load(f'{MODELS_DIR}/UNSW_RandomForest.pkl')
        MODELS['unsw_xgb'] = joblib.load(f'{MODELS_DIR}/UNSW_XGBoost.pkl')
        MODELS['unsw_lgb'] = joblib.load(f'{MODELS_DIR}/UNSW_LightGBM.pkl')
        MODELS['unsw_cat'] = joblib.load(f'{MODELS_DIR}/UNSW_CatBoost.pkl')
        
        # Load EDGE models
        MODELS['edge_rf'] = joblib.load(f'{MODELS_DIR}/EDGE_RandomForest.pkl')
        MODELS['edge_xgb'] = joblib.load(f'{MODELS_DIR}/EDGE_XGBoost.pkl')
        MODELS['edge_lgb'] = joblib.load(f'{MODELS_DIR}/EDGE_LightGBM.pkl')
        MODELS['edge_cat'] = joblib.load(f'{MODELS_DIR}/EDGE_CatBoost.pkl')
        
        # Load CICIDS models
        MODELS['cicids_rf'] = joblib.load(f'{MODELS_DIR}/CICIDS_RandomForest.pkl')
        MODELS['cicids_mlp'] = joblib.load(f'{MODELS_DIR}/CICIDS_MLP.pkl')
        MODELS['cicids_lr'] = joblib.load(f'{MODELS_DIR}/CICIDS_LogisticRegression.pkl')
        
        # Load preprocessors
        PREPROCESSORS['unsw'] = joblib.load(f'{MODELS_DIR}/UNSW_preprocessors.pkl')
        PREPROCESSORS['edge'] = joblib.load(f'{MODELS_DIR}/EDGE_preprocessors.pkl')
        PREPROCESSORS['cicids'] = joblib.load(f'{MODELS_DIR}/CICIDS_preprocessors.pkl')
        
        # UPDATE METRICS - SET MODELS LOADED
        MODELS_LOADED.set(len(MODELS))
        
        print(f"✅ Loaded {len(MODELS)} models successfully!")
        print(f"📊 Models loaded metric set to: {len(MODELS)}")
        
    except Exception as e:
        print(f"❌ Failed to load models: {e}")

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to track request metrics"""
    start_time = time.time()
    
    # Increment active requests
    ACTIVE_REQUESTS.inc()
    
    # Process request
    response = await call_next(request)
    
    # Record metrics
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
    
    # Decrement active requests
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
        "service": "BLACK VEIL Inference API",
        "status": "running",
        "models_loaded": len(MODELS),
        "metrics": "http://localhost:9090/metrics",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Root info"},
            {"path": "/models", "method": "GET", "description": "List models"},
            {"path": "/predict", "method": "POST", "description": "Make prediction"},
            {"path": "/health", "method": "GET", "description": "Health check"}
        ]
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
    """List all loaded models"""
    model_list = []
    for name, model in MODELS.items():
        model_list.append({
            "name": name,
            "type": type(model).__name__,
            "features": getattr(model, 'n_features_in_', 'N/A'),
            "classes": getattr(model, 'n_classes_', 'N/A'),
            "is_fitted": hasattr(model, 'classes_')
        })
    return {
        "total_models": len(model_list),
        "models": model_list
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make prediction using specified model"""
    if request.model_name not in MODELS:
        ERROR_COUNT.labels(endpoint='predict', error_type='model_not_found').inc()
        raise HTTPException(
            status_code=404, 
            detail=f"Model '{request.model_name}' not found. Available: {list(MODELS.keys())}"
        )
    
    model = MODELS[request.model_name]
    features = np.array(request.features).reshape(1, -1)
    
    # Validate features count
    n_features = getattr(model, 'n_features_in_', None)
    if n_features is not None and features.shape[1] != n_features:
        ERROR_COUNT.labels(endpoint='predict', error_type='feature_mismatch').inc()
        raise HTTPException(
            status_code=400,
            detail=f"Expected {n_features} features, got {features.shape[1]}"
        )
    
    # Make prediction
    try:
        prediction = model.predict(features)[0]
        
        # TRACK PREDICTION METRIC
        PREDICTION_COUNT.labels(model=request.model_name, prediction=str(prediction)).inc()
        
        # Track threat detected
        if prediction == 1:
            THREAT_DETECTED.labels(model=request.model_name).inc()
        
        # Get probability if available
        probability = None
        confidence = 1.0
        
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0]
            probability = proba.tolist()
            confidence = float(max(proba))
        
        return PredictionResponse(
            prediction=int(prediction),
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
