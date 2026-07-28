import joblib
import numpy as np

print("🧪 Testing BLACK VEIL Models")
print("="*50)

# Load models
models = {
    'UNSW': joblib.load('/home/eroz/Documents/black_veil/models/UNSW_RandomForest.pkl'),
    'EDGE': joblib.load('/home/eroz/Documents/black_veil/models/EDGE_RandomForest.pkl'),
    'CICIDS': joblib.load('/home/eroz/Documents/black_veil/models/CICIDS_RandomForest.pkl')
}

# Test with random features (matching model expectations)
for name, model in models.items():
    n_features = model.n_features_in_
    test_data = np.random.randn(10, n_features)
    
    predictions = model.predict(test_data)
    classes = model.n_classes_
    
    print(f"\n{name}:")
    print(f"  Features: {n_features}")
    print(f"  Classes: {classes}")
    print(f"  Sample Predictions: {predictions[:5]}")
    print(f"  Status: ✅ Working")

print("\n✅ All models tested successfully!")
