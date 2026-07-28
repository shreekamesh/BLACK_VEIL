"""
Threat Analyzer - Central threat analysis and correlation
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class ThreatAnalyzer:
    """
    Central threat analysis engine that correlates signals from
    multiple AI models into unified threat assessments.
    """

    def __init__(self):
        self._analysis_history: List[Dict[str, Any]] = []
        logger.info("ThreatAnalyzer initialized")

    def analyze(
        self,
        event: Dict[str, Any],
        domain_predictions: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a security event and produce threat assessment.

        Args:
            event: Raw security event data
            domain_predictions: Predictions from domain-specific AI models

        Returns:
            {
                'severity': float (0-1),
                'attack_type': str,
                'confidence': float,
                'threat_level': str,
                'indicators': List[str],
                'techniques': List[str],
                'recommended_actions': List[str],
            }
        """
        # Extract features from event
        severity = event.get('severity', 0.5)
        event_type = event.get('type', 'unknown')

        # Correlate with domain predictions if available
        if domain_predictions:
            severity = self._correlate_severity(severity, domain_predictions)
            event_type = self._correlate_attack_type(event_type, domain_predictions)

        # Determine threat level
        threat_level = self._determine_threat_level(severity)

        # Generate indicators
        indicators = self._extract_indicators(event)

        # MITRE techniques
        techniques = event.get('techniques', [])

        # Recommended actions
        actions = self._recommend_actions(threat_level, event_type)

        result = {
            'analysis_id': str(uuid.uuid4())[:8],
            'severity': round(severity, 4),
            'attack_type': event_type,
            'confidence': event.get('confidence', 0.7),
            'threat_level': threat_level,
            'indicators': indicators,
            'techniques': techniques,
            'recommended_actions': actions,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        self._analysis_history.append(result)
        logger.info(f"Threat analyzed: {event_type} (severity={severity:.2f}, level={threat_level})")
        return result

    def _correlate_severity(
        self,
        base_severity: float,
        domain_predictions: Dict[str, Any],
    ) -> float:
        """Correlate severity across multiple domain predictions"""
        severities = [base_severity]
        for domain, pred in domain_predictions.items():
            severities.append(pred.get('severity', 0.5) if isinstance(pred, dict) else 0.5)
        return sum(severities) / len(severities)

    def _correlate_attack_type(
        self,
        base_type: str,
        domain_predictions: Dict[str, Any],
    ) -> str:
        """Correlate attack type across domains"""
        return base_type  # Simplified

    def _determine_threat_level(self, severity: float) -> str:
        """Determine threat level from severity score"""
        if severity >= 0.9:
            return 'CRITICAL'
        elif severity >= 0.7:
            return 'HIGH'
        elif severity >= 0.4:
            return 'MEDIUM'
        elif severity >= 0.2:
            return 'LOW'
        return 'INFO'

    def _extract_indicators(self, event: Dict[str, Any]) -> List[str]:
        """Extract IoCs from event"""
        indicators = []
        if 'source_ip' in event:
            indicators.append(f"IP: {event['source_ip']}")
        if 'source_user' in event:
            indicators.append(f"User: {event['source_user']}")
        if 'file_hash' in event:
            indicators.append(f"Hash: {event['file_hash']}")
        return indicators

    def _recommend_actions(self, threat_level: str, attack_type: str) -> List[str]:
        """Recommend response actions based on threat level"""
        actions = []
        if threat_level in ('CRITICAL', 'HIGH'):
            actions.extend(['block', 'isolate', 'escalate'])
        elif threat_level == 'MEDIUM':
            actions.extend(['monitor', 'investigate'])
        else:
            actions.extend(['log', 'monitor'])

        if 'credential' in attack_type.lower():
            actions.append('rotate_credentials')
        if 'ransomware' in attack_type.lower():
            actions.append('activate_backups')

        return actions

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of threat analyzer state"""
        return {
            'total_analyses': len(self._analysis_history),
            'recent_threat_levels': [
                h['threat_level'] for h in self._analysis_history[-20:]
            ],
        }

