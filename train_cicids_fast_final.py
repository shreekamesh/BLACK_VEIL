"""
BLACK VEIL - CICIDS Fast Training (No LightGBM issues)
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
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import warnings
warnings.filterwarnings('ignore')

print("🚀 CICIDS FAST TRAINING (Optimized)")
print("="*60)

# GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"💻 GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

# Load data
print("📊 Loading data...")
df = pd.read_csv(
    '/home/eroz/Documents/black_veil/master_dataset/CICIDS2017_Clean.csv',
    low_memory=False,
    nrows=100000
)
print(f"✅ Loaded {len(df):,} rows")

# Sample
df = df.sample(n=50000, random_state=42)
print(f"📊 Sampled to {len(df):,} rows")

# Find label
label = 'Label' if 'Label' in df.columns else df.columns[-1]
print(f"✅ Label: {label}")

X = df.drop(columns=[label])
y = df[label]

# Encode categorical columns
print("🔄 Encoding...")
for col in X.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))

# Encode target
le = LabelEncoder()
y = le.fit_transform(y)
num_classes = len(le.classes_)
print(f"   ✅ {num_classes} classes")

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)
print(f"📊 Train: {len(X_train):,}, Test: {len(X_test):,}")

# ==================== TRAIN MODELS ====================

results = {}
models_path = '/home/eroz/Documents/black_veil/models'

# 1. RandomForest
print("\n🧠 RandomForest...", end='', flush=True)
start = time.time()
rf = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
elapsed = time.time() - start
print(f" ✅ Acc: {acc:.4f}, F1: {f1:.4f} ({elapsed:.1f}s)")
joblib.dump(rf, f"{models_path}/CICIDS_RandomForest.pkl")
results['RandomForest'] = {'accuracy': acc, 'f1_score': f1}

# 2. LogisticRegression
print("   LogisticRegression...", end='', flush=True)
start = time.time()
lr = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
lr.fit(X_train, y_train)
y_pred = lr.predict(X_test)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
elapsed = time.time() - start
print(f" ✅ Acc: {acc:.4f}, F1: {f1:.4f} ({elapsed:.1f}s)")
joblib.dump(lr, f"{models_path}/CICIDS_LogisticRegression.pkl")
results['LogisticRegression'] = {'accuracy': acc, 'f1_score': f1}

# 3. MLPClassifier
print("   MLPClassifier...", end='', flush=True)
start = time.time()
mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=100, random_state=42, early_stopping=True)
mlp.fit(X_train, y_train)
y_pred = mlp.predict(X_test)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
elapsed = time.time() - start
print(f" ✅ Acc: {acc:.4f}, F1: {f1:.4f} ({elapsed:.1f}s)")
joblib.dump(mlp, f"{models_path}/CICIDS_MLP.pkl")
results['MLP'] = {'accuracy': acc, 'f1_score': f1}

# 4. PyTorch GPU
print("   PyTorch GPU...", end='', flush=True)
start = time.time()

X_train_t = torch.FloatTensor(X_train).to(device)
y_train_t = torch.LongTensor(y_train).to(device)
X_test_t = torch.FloatTensor(X_test).to(device)
y_test_t = torch.LongTensor(y_test).to(device)

class FastNN(torch.nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(input_dim, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, num_classes)
        )
    def forward(self, x):
        return self.net(x)

model = FastNN(X_train.shape[1], num_classes).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
criterion = torch.nn.CrossEntropyLoss()

for epoch in range(30):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_t)
    loss = criterion(outputs, y_train_t)
    loss.backward()
    optimizer.step()

model.eval()
with torch.no_grad():
    outputs = model(X_test_t)
    _, pred = torch.max(outputs, 1)
    acc = (pred == y_test_t).float().mean().item()
    f1 = f1_score(y_test_t.cpu().numpy(), pred.cpu().numpy(), average='weighted', zero_division=0)

elapsed = time.time() - start
print(f" ✅ Acc: {acc:.4f}, F1: {f1:.4f} ({elapsed:.1f}s)")
torch.save(model.state_dict(), f"{models_path}/CICIDS_PyTorch.pt")
results['PyTorch'] = {'accuracy': acc, 'f1_score': f1}

# Save preprocessors
joblib.dump({'scaler': scaler, 'target_encoder': le}, f"{models_path}/CICIDS_preprocessors.pkl")

print("\n" + "="*60)
print("✅ CICIDS TRAINING COMPLETE!")
print("="*60)
for name, metrics in results.items():
    print(f"   {name}: {metrics['accuracy']:.4f} (F1: {metrics['f1_score']:.4f})")
print(f"\n📁 Models saved to: {models_path}")
