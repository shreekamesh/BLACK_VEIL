"""
BLACK VEIL - Complete Training Pipeline
Trains on ALL datasets with multiple models
"""

import pandas as pd
import numpy as np
import joblib
import os
import time
import warnings
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

warnings.filterwarnings('ignore')

class CompleteTrainer:
    def __init__(self):
        self.datasets_path = '/home/eroz/Documents/black_veil/master_dataset'
        self.models_path = '/home/eroz/Documents/black_veil/models'
        self.results = {}
        os.makedirs(self.models_path, exist_ok=True)
        
        # GPU for PyTorch
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🚀 Using device: {self.device}")
    
    def load_encode(self, dataset_name):
        """Load and encode dataset"""
        file_map = {
            'UNSW': 'UNSW_clean.csv',
            'EDGE': 'EDGE_Clean.csv',
            'CICIDS': 'CICIDS2017_Clean.csv'
        }
        
        file_path = os.path.join(self.datasets_path, file_map.get(dataset_name))
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None, None, None
        
        print(f"📊 Loading {dataset_name}...")
        df = pd.read_csv(file_path, low_memory=False)
        print(f"   ✅ {len(df):,} rows, {len(df.columns)} columns")
        
        # Find label
        label_cols = ['label', 'Label', 'attack', 'Attack', 'malicious', 'Malicious']
        label_col = None
        for col in label_cols:
            if col in df.columns:
                label_col = col
                break
        if not label_col:
            label_col = df.columns[-1]
        
        print(f"   ✅ Label: {label_col}")
        
        X = df.drop(columns=[label_col])
        y = df[label_col]
        
        # Sample large datasets
        if dataset_name == 'CICIDS' and len(X) > 50000:
            idx = np.random.choice(len(X), 50000, replace=False)
            X = X.iloc[idx]
            y = y.iloc[idx]
            print(f"   📊 Sampled to {len(X):,} rows")
        elif dataset_name == 'EDGE' and len(X) > 50000:
            idx = np.random.choice(len(X), 50000, replace=False)
            X = X.iloc[idx]
            y = y.iloc[idx]
            print(f"   📊 Sampled to {len(X):,} rows")
        
        # Encode categorical columns
        encoders = {}
        for col in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[col] = X[col].fillna('unknown').astype(str)
            X[col] = le.fit_transform(X[col])
            encoders[col] = le
        
        # Encode target
        if y.dtype == 'object':
            le = LabelEncoder()
            y = le.fit_transform(y)
            encoders['target'] = le
        
        # Scale
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled, y, {'encoders': encoders, 'scaler': scaler, 'columns': X.columns.tolist()}
    
    def train_models(self, X, y, dataset_name):
        """Train all models"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\n🧠 Training on {dataset_name}: {len(X_train):,} train, {len(X_test):,} test, {len(np.unique(y))} classes")
        
        models = {
            'RandomForest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
            'XGBoost': xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, use_label_encoder=False, eval_metric='logloss'),
            'LightGBM': lgb.LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1),
            'CatBoost': cb.CatBoostClassifier(iterations=100, depth=6, learning_rate=0.1, random_state=42, verbose=False),
            'GradientBoosting': GradientBoostingClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
        }
        
        results = {}
        
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
                model_path = os.path.join(self.models_path, f"{dataset_name}_{name}.pkl")
                joblib.dump(model, model_path)
                
            except Exception as e:
                print(f" ❌ Failed: {str(e)[:50]}")
                results[name] = {'error': str(e)}
        
        return results
    
    def train_deep_learning(self, X, y, dataset_name):
        """Train PyTorch model on GPU"""
        print(f"\n🖥️ Training PyTorch on {dataset_name}...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Convert to tensors
        X_train_t = torch.FloatTensor(X_train)
        y_train_t = torch.LongTensor(y_train)
        X_test_t = torch.FloatTensor(X_test)
        y_test_t = torch.LongTensor(y_test)
        
        # Move to GPU
        X_train_t = X_train_t.to(self.device)
        y_train_t = y_train_t.to(self.device)
        X_test_t = X_test_t.to(self.device)
        y_test_t = y_test_t.to(self.device)
        
        # DataLoader
        train_dataset = TensorDataset(X_train_t, y_train_t)
        train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True)
        
        # Model
        class SimpleNN(nn.Module):
            def __init__(self, input_dim, num_classes):
                super().__init__()
                self.net = nn.Sequential(
                    nn.Linear(input_dim, 256),
                    nn.BatchNorm1d(256),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(256, 128),
                    nn.BatchNorm1d(128),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(128, num_classes)
                )
            def forward(self, x):
                return self.net(x)
        
        model = SimpleNN(X.shape[1], len(np.unique(y))).to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        # Train
        print(f"   Training on {self.device}...")
        start = time.time()
        
        for epoch in range(20):
            model.train()
            loss_sum = 0
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                loss_sum += loss.item()
            
            if (epoch + 1) % 5 == 0:
                print(f"      Epoch {epoch+1}/20 - Loss: {loss_sum/len(train_loader):.4f}")
        
        # Evaluate
        model.eval()
        with torch.no_grad():
            outputs = model(X_test_t)
            _, pred = torch.max(outputs, 1)
            acc = (pred == y_test_t).float().mean().item()
            f1 = f1_score(y_test_t.cpu(), pred.cpu(), average='weighted', zero_division=0)
        
        elapsed = time.time() - start
        
        # Save model
        model_path = os.path.join(self.models_path, f"{dataset_name}_PyTorch.pt")
        torch.save({
            'model_state_dict': model.state_dict(),
            'input_dim': X.shape[1],
            'num_classes': len(np.unique(y)),
            'accuracy': acc,
            'f1': f1
        }, model_path)
        
        print(f"   ✅ Acc: {acc:.4f}, F1: {f1:.4f} ({elapsed:.2f}s)")
        
        return {'accuracy': acc, 'f1_score': f1, 'time': elapsed}
    
    def run(self):
        """Run complete training"""
        print("="*60)
        print("🚀 BLACK VEIL COMPLETE TRAINING")
        print("="*60)
        print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        datasets = ['UNSW', 'EDGE', 'CICIDS']
        
        for dataset in datasets:
            print(f"\n{'='*60}")
            print(f"📁 {dataset}")
            print(f"{'='*60}")
            
            X, y, preprocessors = self.load_encode(dataset)
            if X is None:
                continue
            
            # Train traditional models
            results = self.train_models(X, y, dataset)
            
            # Train PyTorch
            dl_results = self.train_deep_learning(X, y, dataset)
            results['PyTorch'] = dl_results
            
            # Save preprocessors
            joblib.dump(preprocessors, os.path.join(self.models_path, f"{dataset}_preprocessors.pkl"))
            
            self.results[dataset] = results
            
            print(f"\n✅ {dataset} complete!")
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 TRAINING SUMMARY")
        print(f"{'='*60}")
        for dataset, results in self.results.items():
            print(f"\n📁 {dataset}:")
            for model, metrics in results.items():
                if isinstance(metrics, dict) and 'accuracy' in metrics:
                    print(f"   {model}: {metrics['accuracy']:.4f} (F1: {metrics['f1_score']:.4f})")
        
        print(f"\n✅ All models saved to: {self.models_path}")
        return self.results

if __name__ == "__main__":
    trainer = CompleteTrainer()
    results = trainer.run()
