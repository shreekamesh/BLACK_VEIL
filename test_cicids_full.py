"""
Test CICIDS Models with FULL Dataset
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

print("🔍 Testing CICIDS Models")
print("="*60)

# Load data
df = pd.read_csv('/home/eroz/Documents/black_veil/master_dataset/CICIDS2017_Clean.csv', 
                 low_memory=False, nrows=100000)

print(f"📊 Data shape: {df.shape}")

# Find label column
label_cols = ['Label', 'label', 'attack', 'Attack', 'class', 'Class']
label = None
for col in label_cols:
    if col in df.columns:
        label = col
        break

if label is None:
    # Check all columns for label-like names
    for col in df.columns:
        if any(kw in col.lower() for kw in ['label', 'attack', 'class', 'malicious', 'type']):
            label = col
            break

print(f"✅ Found label: {label}")

if label:
    print(f"\n📊 Label distribution (sample):")
    print(df[label].value_counts().head(10))
    
    X = df.drop(columns=[label])
    y = df[label]
    
    # Encode categorical
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    
    # Encode target
    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)
    
    print(f"\n📊 Train: {len(X_train):,}, Test: {len(X_test):,}")
    print(f"📊 Classes: {np.unique(y)}")
    print(f"📊 Test class distribution: {pd.Series(y_test).value_counts().to_dict()}")
    
    # Load models
    models = {
        'RandomForest': joblib.load('/home/eroz/Documents/black_veil/models/CICIDS_RandomForest.pkl'),
        'MLP': joblib.load('/home/eroz/Documents/black_veil/models/CICIDS_MLP.pkl'),
        'LogisticRegression': joblib.load('/home/eroz/Documents/black_veil/models/CICIDS_LogisticRegression.pkl'),
    }
    
    print("\n🧠 Testing CICIDS Models:")
    print("-"*60)
    
    for name, model in models.items():
        try:
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            print(f"   {name}: Acc={acc:.4f}, F1={f1:.4f}")
        except Exception as e:
            print(f"   {name}: Error - {str(e)[:50]}")
else:
    print("❌ Could not find label column")
    print(f"Available columns: {list(df.columns)[:20]}...")
