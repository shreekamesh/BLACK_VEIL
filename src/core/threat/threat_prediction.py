"""
Threat Prediction Engine - Predict next attacker moves
BLACK VEIL - Predictive security capability

Instead of waiting for attacks to happen, predict the attacker's
next objective based on current behavior patterns and kill chain progression.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class ThreatPredictionEngine:
    """
    Predicts attacker's next likely objectives and actions.

    Capabilities:
    - Next objective prediction (credential theft, lateral movement, etc.)
    - Time-to-compromise estimation
    - Most likely attack path forecasting
    - Early warning generation
    """

    def __init__(self):
        self._predictions: List[Dict[str, Any]] = []
        logger.info("ThreatPredictionEngine initialized")

    def predict_next_objective(
        self,
        current_events: List[Dict[str, Any]],
        attacker_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Predict attacker's next objective based on current behavior.

        Returns:
            {
                'predicted_objective': str,
                'confidence': float,
                'timeframe': str,
                'indicators_to_watch': List[str],
                'recommended_preventions': List[str],
            }
        """
        # Analyze current behavior patterns
        techniques = self._extract_techniques(current_events)
        current_objective = self._infer_current_objective(techniques)

        # Predict next step based on kill chain
        next_objective = self._predict_next_in_kill_chain(current_objective)
        confidence = self._calculate_prediction_confidence(
            current_events, next_objective
        )

        # Generate watch indicators
        watch_indicators = self._get_watch_indicators(next_objective)

        # Recommend preventions
        preventions = self._get_recommended_preventions(next_objective)

        prediction = {
            'prediction_id': str(uuid.uuid4())[:8],
            'predicted_objective': next_objective,
            'confidence': round(confidence, 4),
            'timeframe': self._estimate_timeframe(current_objective, next_objective),
            'current_phase': current_objective,
            'indicators_to_watch': watch_indicators,
            'recommended_preventions': preventions,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        self._predictions.append(prediction)
        logger.info(
            f"Next objective prediction: {next_objective} "
            f"(confidence={confidence:.3f})"
        )
        return prediction

    def _extract_techniques(self, events: List[Dict[str, Any]]) -> List[str]:
        """Extract MITRE technique IDs from events"""
        techniques = []
        for event in events:
            if 'technique_id' in event:
                techniques.append(event['technique_id'])
            if 'techniques' in event:
                techniques.extend(event['techniques'])
        return list(set(techniques))

    def _infer_current_objective(self, techniques: List[str]) -> str:
        """Infer current attacker objective from techniques"""
        objective_map = {
            'credential': ['T1003', 'T1110', 'T1552', 'T1056'],
            'reconnaissance': ['T1046', 'T1082', 'T1518', 'T1595'],
            'lateral_movement': ['T1021', 'T1550', 'T1210'],
            'persistence': ['T1547', 'T1543', 'T1136', 'T1098'],
            'exfiltration': ['T1048', 'T1567', 'T1020'],
            'impact': ['T1486', 'T1490', 'T1485'],
        }

        for objective, techs in objective_map.items():
            if any(t in techs for t in techniques):
                return objective

        return 'reconnaissance'

    def _predict_next_in_kill_chain(self, current: str) -> str:
        """Predict next step based on kill chain progression"""
        kill_chain = [
            'reconnaissance',
            'initial_access',
            'execution',
            'persistence',
            'privilege_escalation',
            'defense_evasion',
            'credential_access',
            'discovery',
            'lateral_movement',
            'collection',
            'exfiltration',
            'impact',
        ]

        if current in kill_chain:
            idx = kill_chain.index(current)
            if idx < len(kill_chain) - 1:
                return kill_chain[idx + 1]

        return 'unknown'

    def _calculate_prediction_confidence(
        self,
        events: List[Dict[str, Any]],
        next_objective: str,
    ) -> float:
        """Calculate confidence in prediction"""
        base = 0.6
        if len(events) > 10:
            base += 0.2
        if next_objective != 'unknown':
            base += 0.1
        return min(1.0, base)

    def _estimate_timeframe(
        self,
        current: str,
        next_objective: str,
    ) -> str:
        """Estimate when next objective will be attempted"""
        objective_times = {
            'credential_access': 'immediate',
            'lateral_movement': 'short_term',
            'exfiltration': 'medium_term',
            'impact': 'long_term',
        }
        return objective_times.get(next_objective, 'unknown')

    def _get_watch_indicators(self, objective: str) -> List[str]:
        """Get indicators to watch for predicted objective"""
        indicators = {
            'credential_access': ['Multiple failed logins', 'Unusual credential dumping tools',
                                  'Suspicious PowerShell execution'],
            'lateral_movement': ['Internal port scanning', 'Remote service connections',
                                 'Unusual file transfers'],
            'exfiltration': ['Large outbound data transfers', 'Unusual DNS queries',
                             'Connections to unknown external IPs'],
            'impact': ['Ransomware indicators', 'Backup deletion attempts',
                       'System restore point removal'],
        }
        return indicators.get(objective, ['Monitor for anomalous activity'])

    def _get_recommended_preventions(self, objective: str) -> List[str]:
        """Get recommended prevention actions"""
        preventions = {
            'credential_access': ['Enforce MFA', 'Monitor credential dumping tools',
                                  'Restrict PowerShell execution'],
            'lateral_movement': ['Network segmentation', 'Restrict RDP access',
                                 'Monitor lateral connections'],
            'exfiltration': ['DLP policies', 'Egress filtering', 'Anomaly-based outbound detection'],
            'impact': ['Immutable backups', 'Ransomware-specific detection rules',
                       'Incident response plan activation'],
        }
        return preventions.get(objective, ['General security monitoring'])

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of prediction engine state"""
        return {
            'total_predictions': len(self._predictions),
            'recent_predictions': [
                {
                    'predicted_objective': p['predicted_objective'],
                    'confidence': p['confidence'],
                    'timeframe': p['timeframe'],
                }
                for p in self._predictions[-10:]
            ],
        }

