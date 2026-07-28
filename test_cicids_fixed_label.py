"""
Test CICIDS Models - Find Correct Label Column
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

print("🔍 Finding CICIDS Label Column")
print("="*60)

# Load data
df = pd.read_csv('/home/eroz/Documents/black_veil/master_dataset/CICIDS2017_Clean.csv', 
                 low_memory=False, nrows=50000)

print(f"📊 Data shape: {df.shape}")
print(f"\n📊 Columns (first 20):")
for i, col in enumerate(df.columns[:20]):
    print(f"   {i}: '{col}'")

# Find label column - it has a space!
label_candidates = ['Label', ' Label', 'Label ', ' label', 'label', 'attack', 'Attack']
found_label = None

for col in df.columns:
    if 'Label' in col or 'label' in col:
        found_label = col
        break

if found_label is None:
    # Check for attack or class columns
    for col in df.columns:
        if 'attack' in col.lower() or 'class' in col.lower():
            found_label = col
            break

print(f"\n✅ Found label: '{found_label}'")

if found_label:
    print(f"\n📊 Label distribution:")
    print(df[found_label].value_counts().head(10))
    
    X = df.drop(columns=[found_label])
    y = df[found_label]
    
    print(f"\n📊 Features: {X.shape[1]}, Target classes: {len(np.unique(y))}")
    
    # Encode categorical features
    print("\n🔄 Encoding categorical features...")
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        print(f"   ✅ {col}")
    
    # Encode target
    print("\n🔄 Encoding target...")
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    print(f"   ✅ Encoded {len(le.classes_)} classes: {le.classes_}")
    
    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.3, random_state=42)
    
    print(f"\n📊 Train: {len(X_train):,}, Test: {len(X_test):,}")
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
            
            print(f"\n{name}:")
            print(f"   Accuracy: {acc:.4f}")
            print(f"   F1-Score: {f1:.4f}")
            print(f"   Unique predictions: {np.unique(y_pred)}")
            
            if len(np.unique(y_pred)) > 1:
                print(f"   ✅ Model predicting multiple classes")
            else:
                print(f"   ⚠️ Model only predicting one class!")
                
        except Exception as e:
            print(f"   {name}: Error - {str(e)[:80]}")
else:
    print("❌ No label column found!")
    print(f"Available columns: {list(df.columns)}")
