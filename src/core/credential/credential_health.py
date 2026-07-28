"""
Credential Health Engine - Monitor credential strength and exposure
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CredentialHealthEngine:
    """Monitors credential health metrics including exposure, entropy, and age"""

    def __init__(self):
        self._health_records: Dict[str, Dict[str, Any]] = {}
        logger.info("CredentialHealthEngine initialized")

    def check_health(self, credential_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of a credential"""
        credential_id = credential_data.get('credential_id', 'unknown')
        entropy = credential_data.get('entropy', 0.0)
        age = credential_data.get('age', 0)
        exposed = credential_data.get('exposed', False)

        score = 1.0
        issues = []

        if entropy < 3.0:
            score -= 0.3
            issues.append('low_entropy')
        if age > 86400:  # Older than 24h
            score -= 0.2
            issues.append('expired_age')
        if exposed:
            score -= 0.5
            issues.append('exposed')

        health = {
            'credential_id': credential_id,
            'health_score': round(max(0.0, score), 4),
            'issues': issues,
            'status': 'healthy' if score > 0.6 else 'unhealthy',
        }

        self._health_records[credential_id] = health
        return health

    def get_state_summary(self) -> Dict[str, Any]:
        return {'total_checked': len(self._health_records)}

