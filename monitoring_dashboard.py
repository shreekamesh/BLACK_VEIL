"""
BLACK VEIL - Monitoring Dashboard
"""

import time
import json
import requests
from datetime import datetime
import os

def check_api_health():
    """Check BLACK VEIL API health"""
    try:
        resp = requests.get('http://localhost:8000/health', timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ API Health: {data['status']}")
            print(f"   Models Loaded: {data['models_loaded']}")
            return True
    except:
        pass
    print("❌ API Health: DOWN")
    return False

def get_models():
    """Get list of models"""
    try:
        resp = requests.get('http://localhost:8000/models', timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            print(f"📊 Total Models: {data['total_models']}")
            return data['models']
    except:
        pass
    return []

def test_predictions():
    """Test predictions with sample data"""
    print("\n🧠 Testing Predictions...")
    
    # Test data
    test_cases = [
        ('unsw_rf', 43, 'Threat Detection'),
        ('edge_rf', 21, 'Trust Prediction'),
        ('cicids_rf', 78, 'Credential Risk')
    ]
    
    for model_name, features_count, label in test_cases:
        try:
            features = [0.0] * features_count
            payload = {'model_name': model_name, 'features': features}
            resp = requests.post('http://localhost:8000/predict', json=payload, timeout=2)
            
            if resp.status_code == 200:
                data = resp.json()
                pred = data['prediction']
                conf = data['confidence']
                print(f"   ✅ {label}: {model_name} → {pred} ({conf:.2%})")
            else:
                print(f"   ❌ {label}: {model_name} → Failed ({resp.status_code})")
        except Exception as e:
            print(f"   ❌ {label}: {model_name} → Error: {str(e)[:50]}")

def show_system_info():
    """Show system information"""
    print("\n💻 System Info:")
    print("="*50)
    
    # Memory info
    try:
        import psutil
        mem = psutil.virtual_memory()
        print(f"   Memory: {mem.used/(1024**3):.1f}GB / {mem.total/(1024**3):.1f}GB ({mem.percent}%)")
        print(f"   CPU: {psutil.cpu_percent()}%")
    except:
        pass
    
    # Disk info
    try:
        import shutil
        total, used, free = shutil.disk_usage('/')
        print(f"   Disk: {used/(1024**3):.1f}GB / {total/(1024**3):.1f}GB")
    except:
        pass

def run_dashboard():
    """Run the monitoring dashboard"""
    print("\n" + "="*60)
    print("🛡️  BLACK VEIL MONITORING DASHBOARD")
    print("="*60)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Health check
    print("\n🔍 Health Check:")
    api_healthy = check_api_health()
    
    # Models
    if api_healthy:
        models = get_models()
        if models:
            print(f"\n📊 Models ({len(models)}):")
            for model in models[:5]:  # Show first 5
                print(f"   - {model['name']}: {model['type']} ({model['features']} features)")
            if len(models) > 5:
                print(f"   ... and {len(models)-5} more")
    
    # Test predictions
    if api_healthy:
        test_predictions()
    
    # System info
    show_system_info()
    
    print("\n" + "="*60)
    print("🔄 Update every 10 seconds (Ctrl+C to exit)")
    print("="*60)

def main():
    try:
        while True:
            os.system('clear')
            run_dashboard()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")

if __name__ == "__main__":
    main()
