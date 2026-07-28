import requests
import json

class BlackVeilClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def predict(self, model_name, features):
        """Make prediction using specified model"""
        response = requests.post(
            f"{self.base_url}/predict",
            json={'model_name': model_name, 'features': features}
        )
        return response.json()

    def get_models(self):
        """Get list of available models"""
        response = requests.get(f"{self.base_url}/models")
        return response.json()

    def health_check(self):
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def predict_threat(self, features):
        """Predict threat using UNSW model"""
        return self.predict('unsw_rf', features)

    def predict_trust(self, features):
        """Predict trust using EDGE model"""
        return self.predict('edge_rf', features)

    def predict_credential_risk(self, features):
        """Predict credential risk using CICIDS model"""
        return self.predict('cicids_rf', features)

# Usage
if __name__ == "__main__":
    client = BlackVeilClient()

    # Health check
    print("Health Check:", client.health_check())

    # Threat detection
    threat = client.predict_threat([0.0] * 43)
    print(f"Threat: {threat['prediction']} ({threat['confidence']:.2%})")

    # Trust prediction
    trust = client.predict_trust([0.0] * 21)
    print(f"Trust: {trust['prediction']} ({trust['confidence']:.2%})")

    # Credential risk
    risk = client.predict_credential_risk([0.0] * 78)
    print(f"Credential Risk: {risk['prediction']} ({risk['confidence']:.2%})")
