"""
Recovery Intelligence Engine - Post-incident learning
BLACK VEIL - Continuous improvement after defensive actions

After each incident:
1. What failed?
2. What worked?
3. What should change?
4. Update policy
"""
from typing import Dict, Any, List
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class RecoveryIntelligenceEngine:
    """
    Learns from incidents to continuously improve defenses.

    Post-incident analysis pipeline:
    1. Collect incident data
    2. Analyze failures
    3. Identify successful defenses
    4. Generate recommendations
    5. Update policies and models
    """

    def __init__(self):
        self._incident_analyses: List[Dict[str, Any]] = []
        logger.info("RecoveryIntelligenceEngine initialized")

    def analyze_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a security incident for post-incident intelligence.

        Args:
            incident: Incident data with detection/response details

        Returns:
            {
                'analysis_id': str,
                'what_failed': List[str],
                'what_worked': List[str],
                'recommendations': List[str],
                'policy_updates': List[str],
            }
        """
        detection_time = incident.get('detection_time', 0)
        response_time = incident.get('response_time', 0)
        attack_type = incident.get('attack_type', 'unknown')
        was_blocked = incident.get('was_blocked', True)

        analysis = {
            'analysis_id': f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            'attack_type': attack_type,
            'detection_latency': detection_time,
            'response_latency': response_time,
            'was_blocked': was_blocked,
            'what_failed': self._analyze_failures(incident),
            'what_worked': self._analyze_successes(incident),
            'recommendations': self._generate_recommendations(incident),
            'policy_updates': self._suggest_policy_updates(incident),
            'analyzed_at': datetime.now(timezone.utc).isoformat(),
        }

        self._incident_analyses.append(analysis)
        logger.info(f"Incident analyzed: {attack_type}")
        return analysis

    def _analyze_failures(self, incident: Dict[str, Any]) -> List[str]:
        """Analyze what failed in the incident response"""
        failures = []
        if incident.get('detection_time', 0) > 60:
            failures.append('Detection latency exceeded 60 seconds')
        if incident.get('response_time', 0) > 300:
            failures.append('Response time exceeded 5 minutes')
        if not incident.get('was_blocked', True):
            failures.append('Attack was not successfully blocked')
        return failures

    def _analyze_successes(self, incident: Dict[str, Any]) -> List[str]:
        """Analyze what worked in the incident response"""
        successes = []
        if incident.get('detection_time', 0) < 10:
            successes.append('Rapid threat detection')
        if incident.get('was_blocked', True):
            successes.append('Attack successfully blocked')
        if incident.get('forensics_collected', False):
            successes.append('Forensic evidence collected')
        return successes

    def _generate_recommendations(self, incident: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on incident analysis"""
        recommendations = []
        attack_type = incident.get('attack_type', 'unknown')

        if 'credential' in attack_type:
            recommendations.append('Implement additional MFA factors')
            recommendations.append('Reduce credential lifetime')
        elif 'ransomware' in attack_type:
            recommendations.append('Enhance backup isolation')
            recommendations.append('Deploy additional endpoint detection')
        elif 'lateral_movement' in attack_type:
            recommendations.append('Strengthen network segmentation')
            recommendations.append('Implement micro-segmentation')

        if incident.get('detection_time', 0) > 30:
            recommendations.append('Optimize detection rule thresholds')

        return recommendations

    def _suggest_policy_updates(self, incident: Dict[str, Any]) -> List[str]:
        """Suggest policy updates based on incident"""
        updates = []
        if incident.get('response_time', 0) > 120:
            updates.append('Reduce auto-response thresholds')
        if not incident.get('was_blocked', True):
            updates.append('Add blocking rule for this attack pattern')
        return updates

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of recovery intelligence state"""
        return {'total_analyses': len(self._incident_analyses)}

