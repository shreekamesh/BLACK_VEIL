"""
BLACK VEIL - CICIDS GPU-Accelerated Training
"""

import pandas as pd
import numpy as np
import joblib
import time
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')

print("🚀 CICIDS GPU Training (Optimized)")
print("="*60)

# Check GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"💻 Using device: {device}")

# Load data - use only necessary columns
print("📊 Loading data...")
start = time.time()
df = pd.read_csv(
    '/home/eroz/Documents/black_veil/master_dataset/CICIDS2017_Clean.csv',
    low_memory=False,
    nrows=100000  # Use 100k rows for speed
)
print(f"✅ Loaded {len(df):,} rows in {time.time()-start:.2f}s")

# Find label
label = 'Label' if 'Label' in df.columns else df.columns[-1]
print(f"✅ Label: {label}")

# Sample
if len(df) > 50000:
    df = df.sample(n=50000, random_state=42)
    print(f"📊 Sampled to {len(df):,} rows")

# Split features and labels
X = df.drop(columns=[label])
y = df[label]

# Quick encoding (only categorical columns)
print("🔄 Encoding categorical columns...")
start = time.time()
for col in X.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))
print(f"   ✅ Encoded in {time.time()-start:.2f}s")

# Encode target
le = LabelEncoder()
y = le.fit_transform(y)
num_classes = len(le.classes_)
print(f"   ✅ Target: {num_classes} classes")

# Scale
print("📏 Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"   ✅ Scaled: {X_scaled.shape}")

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)
print(f"📊 Train: {len(X_train):,}, Test: {len(X_test):,}")

# ==================== GPU Models ====================

print("\n🧠 Training Models...")

results = {}
models_path = '/home/eroz/Documents/black_veil/models'

# 1. LightGBM (fastest)
print("   Training LightGBM...", end='', flush=True)
start = time.time()
lgb_model = lgb.LGBMClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1,
    verbose=-1
)
lgb_model.fit(X_train, y_train)
y_pred = lgb_model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
elapsed = time.time() - start
print(f" ✅ Acc: {acc:.4f}, F1: {f1:.4f} ({elapsed:.2f}s)")
joblib.dump(lgb_model, f"{models_path}/CICIDS_LightGBM.pkl")
results['LightGBM'] = {'accuracy': acc, 'f1_score': f1}

# 2. XGBoost
print("   Training XGBoost...", end='', flush=True)
start = time.time()
xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss',
    n_jobs=-1
)
xgb_model.fit(X_train, y_train)
y_pred = xgb_model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
elapsed = time.time() - start
print(f" ✅ Acc: {acc:.4f}, F1: {f1:.4f} ({elapsed:.2f}s)")
joblib.dump(xgb_model, f"{models_path}/CICIDS_XGBoost.pkl")
results['XGBoost'] = {'accuracy': acc, 'f1_score': f1}

# 3. RandomForest (CPU)
print("   Training RandomForest...", end='', flush=True)
start = time.time()
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
y_pred = rf_model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
elapsed = time.time() - start
print(f" ✅ Acc: {acc:.4f}, F1: {f1:.4f} ({elapsed:.2f}s)")
joblib.dump(rf_model, f"{models_path}/CICIDS_RandomForest.pkl")
results['RandomForest'] = {'accuracy': acc, 'f1_score': f1}

# 4. PyTorch (GPU)
print("   Training PyTorch (GPU)...", end='', flush=True)
start = time.time()

# Convert to PyTorch tensors
X_train_t = torch.FloatTensor(X_train).to(device)
y_train_t = torch.LongTensor(y_train).to(device)
X_test_t = torch.FloatTensor(X_test).to(device)
y_test_t = torch.LongTensor(y_test).to(device)

# Simple model
class SimpleNN(torch.nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(input_dim, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, num_classes)
        )
    def forward(self, x):
        return self.net(x)

model = SimpleNN(X_train.shape[1], num_classes).to(device)
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Train quickly
for epoch in range(10):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_t)
    loss = criterion(outputs, y_train_t)
    loss.backward()
    optimizer.step()

# Evaluate
model.eval()
with torch.no_grad():
    outputs = model(X_test_t)
    _, pred = torch.max(outputs, 1)
    acc = (pred == y_test_t).float().mean().item()
    f1 = f1_score(y_test_t.cpu().numpy(), pred.cpu().numpy(), average='weighted', zero_division=0)

elapsed = time.time() - start
print(f" ✅ Acc: {acc:.4f}, F1: {f1:.4f} ({elapsed:.2f}s)")

# Save PyTorch model
torch.save({
    'model_state_dict': model.state_dict(),
    'input_dim': X_train.shape[1],
    'num_classes': num_classes,
}, f"{models_path}/CICIDS_PyTorch.pt")
results['PyTorch'] = {'accuracy': acc, 'f1_score': f1}

# Save preprocessors
joblib.dump({'scaler': scaler, 'encoders': {'target': le}}, 
            f"{models_path}/CICIDS_preprocessors.pkl")

print("\n" + "="*60)
print("📊 CICIDS TRAINING COMPLETE!")
print("="*60)
for name, metrics in results.items():
    print(f"   {name}: {metrics['accuracy']:.4f} (F1: {metrics['f1_score']:.4f})")
print(f"\n✅ Models saved to: {models_path}/")
