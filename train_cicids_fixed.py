"""
BLACK VEIL - CICIDS Training with Rare Class Handling
"""

import pandas as pd
import numpy as np
import joblib
import os
import time
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

warnings.filterwarnings('ignore')

print("🚀 Training CICIDS with Rare Class Handling...")
print("="*60)

# Load data
df = pd.read_csv('/home/eroz/Documents/black_veil/master_dataset/CICIDS2017_Clean.csv', low_memory=False)
print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")

# Find label
label_col = 'Label' if 'Label' in df.columns else df.columns[-1]
print(f"✅ Label: {label_col}")

X = df.drop(columns=[label_col])
y = df[label_col]

# Check class distribution
print("\n📊 Class Distribution:")
class_counts = y.value_counts()
print(class_counts)

# Find rare classes (less than 10 samples)
rare_classes = class_counts[class_counts < 10].index.tolist()
print(f"\n⚠️ Rare classes (< 10 samples): {rare_classes}")

# Combine rare classes into 'Other'
if rare_classes:
    print(f"🔄 Combining rare classes into 'Other'...")
    y = y.replace(rare_classes, 'Other')
    print(f"   ✅ Combined {len(rare_classes)} classes into 'Other'")

# Sample with stratification
print(f"\n📊 Sampling 50,000 rows with stratification...")

# Get indices for sampling
try:
    # Try stratified sampling
    sampled_indices = []
    for class_name in y.unique():
        class_indices = y[y == class_name].index
        n_samples = min(5000, len(class_indices))  # Max 5000 per class
        if len(class_indices) > 0:
            sampled_indices.extend(np.random.choice(class_indices, n_samples, replace=False))
    
    if len(sampled_indices) < 50000:
        # Add more samples from largest classes
        remaining = 50000 - len(sampled_indices)
        for class_name in y.value_counts().head(3).index:
            if remaining <= 0:
                break
            class_indices = y[y == class_name].index
            available = [i for i in class_indices if i not in sampled_indices]
            if available:
                take = min(remaining, len(available))
                sampled_indices.extend(np.random.choice(available, take, replace=False))
                remaining -= take
    
    X = X.loc[sampled_indices]
    y = y.loc[sampled_indices]
    
except Exception as e:
    print(f"   ⚠️ Stratified sampling failed: {e}")
    # Fallback to random sampling
    idx = np.random.choice(len(X), 50000, replace=False)
    X = X.iloc[idx]
    y = y.iloc[idx]

print(f"   ✅ Sampled {len(X):,} rows")
print(f"   Classes: {y.nunique()}")

# Encode categorical columns
print("\n🔄 Encoding columns...")
encoders = {}
for col in X.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    X[col] = X[col].fillna('unknown').astype(str)
    X[col] = le.fit_transform(X[col])
    encoders[col] = le
    print(f"   ✅ Encoded: {col}")

# Encode target
le = LabelEncoder()
y = le.fit_transform(y)
encoders['target'] = le
print(f"   ✅ Encoded target ({len(le.classes_)} classes)")

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"   ✅ Scaled: {X_scaled.shape}")

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n📊 Train: {len(X_train):,}, Test: {len(X_test):,}, Classes: {len(np.unique(y))}")

# Train models
print("\n🧠 Training Models...")

models = {
    'RandomForest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
    'XGBoost': xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, use_label_encoder=False, eval_metric='logloss'),
    'LightGBM': lgb.LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1, verbose=-1),
    'CatBoost': cb.CatBoostClassifier(iterations=100, depth=6, learning_rate=0.1, random_state=42, verbose=False),
}

results = {}
models_path = '/home/eroz/Documents/black_veil/models'

for name, model in models.items():
    try:
        print(f"   Training {name}...", end='', flush=True)
        start = time.time()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        elapsed = time.time() - start
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        results[name] = {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1_score': f1, 'time': elapsed}
        print(f" ✅ Acc: {acc:.4f}, F1: {f1:.4f} ({elapsed:.2f}s)")
        
        # Save model
        model_path = os.path.join(models_path, f"CICIDS_{name}.pkl")
        joblib.dump(model, model_path)
        print(f"      💾 Saved: {model_path}")
        
    except Exception as e:
        print(f" ❌ Failed: {str(e)[:50]}")

# Save preprocessors
preprocessors = {'encoders': encoders, 'scaler': scaler}
joblib.dump(preprocessors, os.path.join(models_path, "CICIDS_preprocessors.pkl"))
print(f"💾 Preprocessors saved")

# Summary
print("\n" + "="*60)
print("📊 CICIDS TRAINING COMPLETE!")
print("="*60)
for name, metrics in results.items():
    if isinstance(metrics, dict) and 'accuracy' in metrics:
        print(f"   {name}: {metrics['accuracy']:.4f} (F1: {metrics['f1_score']:.4f})")
