"""
Test CICIDS Models with Proper Encoding
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report

print("🔍 Testing CICIDS Models with Proper Encoding")
print("="*60)

# Load data
df = pd.read_csv('/home/eroz/Documents/black_veil/master_dataset/CICIDS2017_Clean.csv', 
                 low_memory=False, nrows=50000)

label = 'Label'
print(f"✅ Found label: {label}")

X = df.drop(columns=[label])
y = df[label]

print(f"\n📊 Original label distribution:")
print(y.value_counts().head(10))

# Encode categorical features
print("\n🔄 Encoding features...")
for col in X.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))
    print(f"   ✅ Encoded: {col}")

# Encode target (critical!)
print("\n🔄 Encoding target...")
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
print(f"   ✅ Encoded {len(label_encoder.classes_)} classes")
print(f"   Classes: {label_encoder.classes_}")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.3, random_state=42)

print(f"\n📊 Train: {len(X_train):,}, Test: {len(X_test):,}")
print(f"📊 Classes in test: {np.unique(y_test)}")
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
        
        # Check if model is working properly
        if len(np.unique(y_pred)) == 1:
            print(f"   ⚠️ Model only predicting one class!")
        else:
            print(f"   ✅ Model predicting multiple classes")
            
    except Exception as e:
        print(f"   {name}: Error - {str(e)[:80]}")

# Save the label encoder for later use
import joblib
joblib.dump(label_encoder, '/home/eroz/Documents/black_veil/models/CICIDS_label_encoder.pkl')
print("\n💾 Saved label encoder to: CICIDS_label_encoder.pkl")
