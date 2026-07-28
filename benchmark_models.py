"""
BLACK VEIL - Model Benchmarking Script
Validates all 11 deployed models
"""

import numpy as np
import joblib
import time
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
import os
import json

print("📊 BLACK VEIL - Model Benchmarking")
print("="*60)

MODELS_DIR = '/home/eroz/Documents/black_veil/models'
results = {}

# Define models to test
models = {
    'UNSW': ['UNSW_RandomForest.pkl', 'UNSW_XGBoost.pkl', 'UNSW_LightGBM.pkl', 'UNSW_CatBoost.pkl'],
    'EDGE': ['EDGE_RandomForest.pkl', 'EDGE_XGBoost.pkl', 'EDGE_LightGBM.pkl', 'EDGE_CatBoost.pkl'],
    'CICIDS': ['CICIDS_RandomForest.pkl', 'CICIDS_MLP.pkl', 'CICIDS_LogisticRegression.pkl']
}

for dataset, model_files in models.items():
    print(f"\n📁 {dataset}")
    print("-"*40)
    
    for model_file in model_files:
        try:
            model_path = os.path.join(MODELS_DIR, model_file)
            if not os.path.exists(model_path):
                print(f"   ⚠️ {model_file} not found")
                continue
            
            model = joblib.load(model_path)
            model_name = model_file.replace('.pkl', '')
            
            # Generate test data
            n_features = getattr(model, 'n_features_in_', 10)
            n_classes = getattr(model, 'n_classes_', 2)
            
            X_test = np.random.randn(1000, n_features)
            y_test = np.random.randint(0, n_classes, 1000)
            
            # Measure inference time
            start = time.time()
            y_pred = model.predict(X_test)
            inference_time = (time.time() - start) * 1000  # ms
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            # Get probabilities if available
            proba = None
            if hasattr(model, 'predict_proba'):
                try:
                    proba = model.predict_proba(X_test)
                except:
                    pass
            
            results[model_name] = {
                'dataset': dataset,
                'type': type(model).__name__,
                'features': n_features,
                'classes': n_classes,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'inference_time_ms': inference_time
            }
            
            print(f"   ✅ {model_name}:")
            print(f"      Acc: {accuracy:.4f}, F1: {f1:.4f}, Time: {inference_time:.2f}ms")
            
        except Exception as e:
            print(f"   ❌ {model_file}: {str(e)[:50]}")

# Save results
results_path = os.path.join(MODELS_DIR, 'benchmark_results.json')
with open(results_path, 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "="*60)
print("📊 Benchmark Results Summary")
print("="*60)

df = pd.DataFrame.from_dict(results, orient='index')
print(df[['dataset', 'type', 'accuracy', 'f1_score', 'inference_time_ms']].to_string())

print(f"\n✅ Results saved to: {results_path}")
