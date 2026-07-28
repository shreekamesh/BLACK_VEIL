from blackveil_client import BlackVeilClient

class ACDOIntegration:
    def __init__(self):
        self.client = BlackVeilClient()

    def analyze_event(self, event_data):
        """Analyze security event using all models"""
        results = {
            'threat': self.client.predict_threat(event_data.get('features_unsw', [0.0]*43)),
            'trust': self.client.predict_trust(event_data.get('features_edge', [0.0]*21)),
            'credential_risk': self.client.predict_credential_risk(event_data.get('features_cicids', [0.0]*78))
        }

        # Determine overall decision
        threat_score = results['threat']['prediction']
        trust_score = results['trust']['prediction']
        risk_score = results['credential_risk']['prediction']

        if threat_score == 1:
            decision = 'block'
        elif risk_score > 1:
            decision = 'rotate_credentials'
        elif trust_score == 0:
            decision = 'monitor'
        else:
            decision = 'allow'

        return {
            'decision': decision,
            'details': results
        }

# Usage
if __name__ == "__main__":
    integration = ACDOIntegration()
    result = integration.analyze_event({})
    print(f"ACDO Decision: {result['decision']}")
    print(f"Details: {result['details']}")
