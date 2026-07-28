"""
BLACK VEIL - Model Validation with REAL Test Data
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import json

print("📊 BLACK VEIL - Real Data Validation")
print("="*60)

MODELS_DIR = '/home/eroz/Documents/black_veil/models'
DATA_DIR = '/home/eroz/Documents/black_veil/master_dataset'

results = {}

# 1. Validate UNSW Model
print("\n🔍 Validating UNSW Models with REAL data...")
try:
    df = pd.read_csv(f"{DATA_DIR}/UNSW_clean.csv", low_memory=False, nrows=20000)
    label = 'label'
    X = df.drop(columns=[label])
    y = df[label]
    
    # Encode categorical
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    
    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)
    
    # Load UNSW models
    models = {
        'UNSW_RandomForest': joblib.load(f"{MODELS_DIR}/UNSW_RandomForest.pkl"),
        'UNSW_XGBoost': joblib.load(f"{MODELS_DIR}/UNSW_XGBoost.pkl"),
        'UNSW_LightGBM': joblib.load(f"{MODELS_DIR}/UNSW_LightGBM.pkl"),
    }
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        results[name] = {
            'dataset': 'UNSW',
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
            'test_samples': len(y_test)
        }
        print(f"   ✅ {name}: Acc={results[name]['accuracy']:.4f}, F1={results[name]['f1_score']:.4f}")
        
except Exception as e:
    print(f"   ❌ UNSW validation failed: {e}")

# 2. Validate EDGE Model
print("\n🔍 Validating EDGE Models with REAL data...")
try:
    df = pd.read_csv(f"{DATA_DIR}/EDGE_Clean.csv", low_memory=False, nrows=20000)
    label = 'label'
    X = df.drop(columns=[label])
    y = df[label]
    
    # Encode categorical
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)
    
    models = {
        'EDGE_RandomForest': joblib.load(f"{MODELS_DIR}/EDGE_RandomForest.pkl"),
        'EDGE_XGBoost': joblib.load(f"{MODELS_DIR}/EDGE_XGBoost.pkl"),
        'EDGE_LightGBM': joblib.load(f"{MODELS_DIR}/EDGE_LightGBM.pkl"),
    }
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        results[name] = {
            'dataset': 'EDGE',
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
            'test_samples': len(y_test)
        }
        print(f"   ✅ {name}: Acc={results[name]['accuracy']:.4f}, F1={results[name]['f1_score']:.4f}")
        
except Exception as e:
    print(f"   ❌ EDGE validation failed: {e}")

# 3. Validate CICIDS Model
print("\n🔍 Validating CICIDS Models with REAL data...")
try:
    df = pd.read_csv(f"{DATA_DIR}/CICIDS2017_Clean.csv", low_memory=False, nrows=20000)
    label = 'Label'
    X = df.drop(columns=[label])
    y = df[label]
    
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)
    
    models = {
        'CICIDS_RandomForest': joblib.load(f"{MODELS_DIR}/CICIDS_RandomForest.pkl"),
        'CICIDS_MLP': joblib.load(f"{MODELS_DIR}/CICIDS_MLP.pkl"),
    }
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        results[name] = {
            'dataset': 'CICIDS',
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
            'test_samples': len(y_test)
        }
        print(f"   ✅ {name}: Acc={results[name]['accuracy']:.4f}, F1={results[name]['f1_score']:.4f}")
        
except Exception as e:
    print(f"   ❌ CICIDS validation failed: {e}")

# Save results
results_path = os.path.join(MODELS_DIR, 'real_data_results.json')
with open(results_path, 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "="*60)
print("📊 REAL DATA VALIDATION SUMMARY")
print("="*60)
print(f"✅ Results saved to: {results_path}")

# Summary table
print("\nModel Performance on REAL Data:")
print("-"*60)
print(f"{'Model':<25} {'Dataset':<10} {'Accuracy':<10} {'F1-Score':<10}")
print("-"*60)

for name, metrics in results.items():
    print(f"{name:<25} {metrics['dataset']:<10} {metrics['accuracy']:.4f}    {metrics['f1_score']:.4f}")

