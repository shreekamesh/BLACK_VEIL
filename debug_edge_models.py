"""
Debug EDGE Models - Check predictions
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

print("🔍 Debugging EDGE Models")
print("="*50)

# Load data
df = pd.read_csv('/home/eroz/Documents/black_veil/master_dataset/EDGE_Clean.csv', 
                 low_memory=False, nrows=20000)
label = 'label'

X = df.drop(columns=[label])
y = df[label]

print(f"📊 Data shape: {X.shape}")
print(f"📊 Classes: {np.unique(y)}")
print(f"📊 Class distribution: {pd.Series(y).value_counts().to_dict()}")

# Encode
for col in X.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

print(f"\n📊 Train: {len(X_train)}, Test: {len(X_test)}")

# Load models
models = {
    'RandomForest': joblib.load('/home/eroz/Documents/black_veil/models/EDGE_RandomForest.pkl'),
    'XGBoost': joblib.load('/home/eroz/Documents/black_veil/models/EDGE_XGBoost.pkl'),
    'LightGBM': joblib.load('/home/eroz/Documents/black_veil/models/EDGE_LightGBM.pkl'),
}

for name, model in models.items():
    print(f"\n🧠 {name}:")
    print(f"   Features expected: {model.n_features_in_}")
    print(f"   Classes: {model.n_classes_}")
    
    # Predict on test
    y_pred = model.predict(X_test)
    
    # Check predictions
    unique_preds = np.unique(y_pred)
    print(f"   Unique predictions: {unique_preds}")
    print(f"   Prediction distribution: {pd.Series(y_pred).value_counts().to_dict()}")
    
    # Check accuracy
    from sklearn.metrics import accuracy_score
    acc = accuracy_score(y_test, y_pred)
    print(f"   Accuracy: {acc:.4f}")
    
    # Check if problem is feature mismatch
    print(f"   Feature count mismatch: {X_test.shape[1]} vs {model.n_features_in_}")
    if X_test.shape[1] != model.n_features_in_:
        print(f"   ⚠️ FEATURE MISMATCH! Expected {model.n_features_in_}, got {X_test.shape[1]}")
