"""
Policy Engine - Central policy management
BLACK VEIL - Dynamic security policy enforcement

Separates policy configuration from execution:
- Rotation Rules
- Access Rules
- Response Rules
- Trust Rules
- Deception Rules
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class PolicyEngine:
    """
    Central policy engine that manages and enforces security policies.
    Policies evolve dynamically based on threat landscape and learning.
    """

    def __init__(self):
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._violations: List[Dict[str, Any]] = []
        self._init_default_policies()
        logger.info("PolicyEngine initialized")

    def _init_default_policies(self):
        """Initialize default security policies"""
        self._policies['rotation'] = {
            'type': 'rotation',
            'rules': {
                'credential_lifetime': 86400,  # 24h
                'min_entropy': 3.5,
                'max_age_before_rotation': 43200,  # 12h
            },
            'enabled': True,
        }
        self._policies['access'] = {
            'type': 'access',
            'rules': {
                'max_failed_attempts': 5,
                'lockout_duration': 900,  # 15min
                'require_mfa': True,
                'allowed_hours': [0, 24],  # 24/7
            },
            'enabled': True,
        }
        self._policies['response'] = {
            'type': 'response',
            'rules': {
                'auto_block_threshold': 0.8,
                'auto_isolate_threshold': 0.9,
                'max_auto_actions_per_hour': 10,
                'require_human_approval_for': ['isolate', 'escalate'],
            },
            'enabled': True,
        }
        self._policies['trust'] = {
            'type': 'trust',
            'rules': {
                'initial_trust': 0.7,
                'decay_rate': 0.01,
                'recovery_rate': 0.05,
                'min_trust_for_access': 0.3,
            },
            'enabled': True,
        }
        self._policies['deception'] = {
            'type': 'deception',
            'rules': {
                'max_active_deceptions': 100,
                'min_deception_lifetime': 3600,  # 1h
                'max_deception_lifetime': 259200,  # 72h
                'require_ethical_review': True,
            },
            'enabled': True,
        }

    def check_policy(self, policy_type: str, action: str,
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if an action violates any policy"""
        policy = self._policies.get(policy_type)
        if not policy:
            return {'allowed': True, 'violations': []}

        violations = []
        rules = policy.get('rules', {})

        for rule, value in rules.items():
            # Check specific rule violations
            if rule == 'credential_lifetime' and action == 'rotate':
                age = context.get('credential_age', 0)
                if age < value * 0.9:
                    violations.append(f"credential_age_below_minimum")
            elif rule == 'max_failed_attempts':
                attempts = context.get('failed_attempts', 0)
                if attempts >= value:
                    violations.append(f"max_failed_attempts_exceeded")

        if violations:
            self._violations.append({
                'policy_type': policy_type,
                'action': action,
                'violations': violations,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            })

        return {
            'allowed': len(violations) == 0,
            'violations': violations,
            'policy_type': policy_type,
        }

    def update_policy(self, policy_type: str, updates: Dict[str, Any]) -> bool:
        """Update a policy's rules"""
        if policy_type in self._policies:
            self._policies[policy_type]['rules'].update(updates)
            logger.info(f"Policy updated: {policy_type}")
            return True
        return False

    def get_policy(self, policy_type: str) -> Optional[Dict[str, Any]]:
        """Get a policy by type"""
        return self._policies.get(policy_type)

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of policy engine state"""
        return {
            'active_policies': list(self._policies.keys()),
            'total_violations': len(self._violations),
        }

