"""
Test EDGE Models with Full Dataset (Both Classes)
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report

print("🔍 Testing EDGE Models on Full Dataset")
print("="*60)

# Load FULL dataset
df = pd.read_csv('/home/eroz/Documents/black_veil/master_dataset/EDGE_Clean.csv', 
                 low_memory=False, nrows=100000)  # 100k rows
label = 'label'

# Check class distribution
print("\n📊 Class Distribution:")
print(df[label].value_counts())

X = df.drop(columns=[label])
y = df[label]

# Encode categorical
for col in X.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

print(f"\n📊 Train: {len(X_train)}, Test: {len(X_test)}")
print(f"📊 Test class distribution: {pd.Series(y_test).value_counts().to_dict()}")

# Load models
models = {
    'RandomForest': joblib.load('/home/eroz/Documents/black_veil/models/EDGE_RandomForest.pkl'),
    'XGBoost': joblib.load('/home/eroz/Documents/black_veil/models/EDGE_XGBoost.pkl'),
    'LightGBM': joblib.load('/home/eroz/Documents/black_veil/models/EDGE_LightGBM.pkl'),
}

print("\n🧠 Testing EDGE Models:")
print("-"*60)

for name, model in models.items():
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    print(f"\n{name}:")
    print(f"   Accuracy: {acc:.4f}")
    print(f"   F1-Score: {f1:.4f}")
    print(f"   Unique predictions: {np.unique(y_pred)}")
    
    # Check if model is just guessing one class
    if len(np.unique(y_pred)) == 1:
        print(f"   ⚠️ Model only predicting one class!")

