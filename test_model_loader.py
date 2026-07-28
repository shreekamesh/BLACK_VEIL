"""
BLACK VEIL V2 — Model Loader Verification Test
Tests all existing .pkl models load successfully
"""
from ai_core.model_loader import model_loader

print("=" * 60)
print(" BLACK VEIL V2 — MODEL LOADER TEST")
print("=" * 60)

models = model_loader.list_available_models()
print(f"\nAvailable models ({len(models)}):")
for m in models:
    print(f"  - {m}")

for name in models:
    print(f"\n{'─' * 50}")
    print(f"  Loading: {name}")
    try:
        obj = model_loader.load_model(name)
        print(f"  ✅ Success: {obj is not None}")
        if obj is not None:
            print(f"  Type: {type(obj).__name__}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

print(f"\n{'=' * 60}")
print(" TEST COMPLETE")
print(f"{'=' * 60}")
