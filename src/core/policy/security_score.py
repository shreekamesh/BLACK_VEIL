"""
Security Score Engine - Overall defensive posture measurement
BLACK VEIL - Holistic security scoring

Calculates overall security posture based on:
Trust + Credential Health + Deception Coverage + Attack Surface + Policy Compliance
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SecurityScoreEngine:
    """
    Calculates and tracks overall security posture score.
    Score = f(Trust, CredentialHealth, DeceptionCoverage, AttackSurface, PolicyCompliance)
    """

    def __init__(self):
        self._score_history: list = []
        logger.info("SecurityScoreEngine initialized")

    def calculate_score(
        self,
        trust_score: float,
        credential_health: float,
        deception_coverage: float,
        attack_surface: float,
        policy_compliance: float,
    ) -> Dict[str, Any]:
        """
        Calculate overall security posture score.

        Args:
            trust_score: Average trust score across entities (0-1)
            credential_health: Credential health score (0-1)
            deception_coverage: Deception deployment coverage (0-1)
            attack_surface: Attack surface exposure (0-1, lower=better)
            policy_compliance: Policy compliance rate (0-1)
        """
        # Components
        components = {
            'trust': trust_score * 0.25,
            'credential_health': credential_health * 0.20,
            'deception_coverage': deception_coverage * 0.15,
            'attack_surface': (1.0 - attack_surface) * 0.20,
            'policy_compliance': policy_compliance * 0.20,
        }

        total_score = sum(components.values())

        # Determine level
        if total_score >= 0.8:
            level = 'excellent'
        elif total_score >= 0.6:
            level = 'good'
        elif total_score >= 0.4:
            level = 'fair'
        elif total_score >= 0.2:
            level = 'poor'
        else:
            level = 'critical'

        result = {
            'overall_score': round(total_score, 4),
            'level': level,
            'components': {k: round(v, 4) for k, v in components.items()},
            'max_score': 1.0,
            'min_score': 0.0,
        }

        self._score_history.append(result)
        logger.info(f"Security score: {total_score:.3f} ({level})")
        return result

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of security score engine state"""
        return {'total_scores': len(self._score_history)}

