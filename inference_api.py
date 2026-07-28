"""
BLACK VEIL Inference API - Complete Working Version
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from typing import List, Optional, Dict, Any
import joblib
import os

app = FastAPI(
    title="BLACK VEIL Inference API",
    description="Machine Learning Inference API for BLACK VEIL",
    version="1.0.0"
)

# Global variables for models
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
        
        print(f"✅ Loaded {len(MODELS)} models successfully!")
        
    except Exception as e:
        print(f"❌ Failed to load models: {e}")

class PredictionRequest(BaseModel):
    model_name: str
    features: List[float]

class PredictionResponse(BaseModel):
    prediction: int
    probability: Optional[List[float]] = None
    model: str
    confidence: float
    features_expected: int

class ModelInfo(BaseModel):
    name: str
    type: str
    features: int
    classes: int

@app.get("/")
async def root():
    return {
        "service": "BLACK VEIL Inference API",
        "status": "running",
        "models_loaded": len(MODELS),
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
    """List all loaded models with details"""
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
        raise HTTPException(
            status_code=404, 
            detail=f"Model '{request.model_name}' not found. Available: {list(MODELS.keys())}"
        )
    
    model = MODELS[request.model_name]
    features = np.array(request.features).reshape(1, -1)
    
    # Validate features count
    n_features = getattr(model, 'n_features_in_', None)
    if n_features is not None and features.shape[1] != n_features:
        raise HTTPException(
            status_code=400,
            detail=f"Expected {n_features} features, got {features.shape[1]}"
        )
    
    # Make prediction
    try:
        prediction = model.predict(features)[0]
        
        # Get probability if available
        probability = None
        confidence = 1.0
        
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0]
            probability = proba.tolist()
            confidence = float(max(proba))
        elif hasattr(model, 'predict'):
            # For models without probability, use prediction confidence
            confidence = 0.9
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=probability,
            model=request.model_name,
            confidence=confidence,
            features_expected=n_features if n_features is not None else len(request.features)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/info/{model_name}")
async def model_info(model_name: str):
    """Get detailed information about a specific model"""
    if model_name not in MODELS:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    
    model = MODELS[model_name]
    
    return {
        "name": model_name,
        "type": type(model).__name__,
        "features": getattr(model, 'n_features_in_', 'N/A'),
        "classes": getattr(model, 'n_classes_', 'N/A'),
        "is_fitted": hasattr(model, 'classes_'),
        "has_probability": hasattr(model, 'predict_proba'),
        "available_methods": [m for m in dir(model) if not m.startswith('_') and callable(getattr(model, m, None))]
    }

# For running directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
