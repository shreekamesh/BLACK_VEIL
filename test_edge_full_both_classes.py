"""
Test EDGE Models with FULL Dataset (Both Classes)
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

print("🔍 Testing EDGE Models on FULL Dataset")
print("="*60)

# Load FULL dataset (NO nrows limit!)
df = pd.read_csv('/home/eroz/Documents/black_veil/master_dataset/EDGE_Clean.csv', 
                 low_memory=False)

label = 'label'

print(f"📊 Full dataset shape: {df.shape}")
print(f"📊 Total rows: {len(df):,}")

# Check class distribution
print("\n📊 Class Distribution (FULL dataset):")
print(df[label].value_counts())

# Sample to get both classes (if dataset is too large)
if len(df) > 100000:
    # Get samples from each class
    class_0 = df[df[label] == 0]
    class_1 = df[df[label] == 1]
    
    print(f"\n📊 Class 0: {len(class_0):,} samples")
    print(f"📊 Class 1: {len(class_1):,} samples")
    
    # Sample equally from both classes
    sample_size = min(50000, len(class_1))
    class_0_sample = class_0.sample(n=sample_size, random_state=42)
    class_1_sample = class_1.sample(n=sample_size, random_state=42) if len(class_1) >= sample_size else class_1
    
    df_sampled = pd.concat([class_0_sample, class_1_sample])
    print(f"\n📊 Sampled: {len(df_sampled):,} rows ({len(class_0_sample):,} class 0, {len(class_1_sample):,} class 1)")
else:
    df_sampled = df

X = df_sampled.drop(columns=[label])
y = df_sampled[label]

print(f"\n📊 Features: {X.shape[1]}")
print(f"📊 Classes: {np.unique(y)}")

# Encode categorical
for col in X.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

print(f"\n📊 Train: {len(X_train):,}, Test: {len(X_test):,}")
print(f"📊 Test class distribution: {pd.Series(y_test).value_counts().to_dict()}")

# Load models
models = {
    'RandomForest': joblib.load('/home/eroz/Documents/black_veil/models/EDGE_RandomForest.pkl'),
    'XGBoost': joblib.load('/home/eroz/Documents/black_veil/models/EDGE_XGBoost.pkl'),
    'LightGBM': joblib.load('/home/eroz/Documents/black_veil/models/EDGE_LightGBM.pkl'),
}

print("\n🧠 Testing EDGE Models on BALANCED Dataset:")
print("-"*60)

for name, model in models.items():
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    print(f"\n{name}:")
    print(f"   Accuracy: {acc:.4f}")
    print(f"   F1-Score: {f1:.4f}")
    print(f"   Unique predictions: {np.unique(y_pred)}")
    
    # Check prediction distribution
    pred_dist = pd.Series(y_pred).value_counts().to_dict()
    print(f"   Prediction distribution: {pred_dist}")

