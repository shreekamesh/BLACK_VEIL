"""
Reputation Engine - Entity reputation scoring
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ReputationEngine:
    """
    Reputation scoring engine that tracks entity behavior over time
    and provides reputation scores based on historical actions.
    """

    def __init__(self):
        self._reputations: Dict[str, Dict[str, Any]] = {}
        logger.info("ReputationEngine initialized")

    def update_reputation(
        self,
        entity_id: str,
        action_type: str,
        success: bool,
    ) -> float:
        """Update entity reputation based on action outcome"""
        if entity_id not in self._reputations:
            self._reputations[entity_id] = {
                'reputation': 0.5,
                'positive_actions': 0,
                'negative_actions': 0,
                'total_actions': 0,
            }

        state = self._reputations[entity_id]
        state['total_actions'] += 1

        if success:
            state['positive_actions'] += 1
            state['reputation'] = min(1.0, state['reputation'] + 0.05)
        else:
            state['negative_actions'] += 1
            state['reputation'] = max(0.0, state['reputation'] - 0.1)

        return state['reputation']

    def get_reputation(self, entity_id: str) -> Dict[str, Any]:
        """Get reputation for an entity"""
        state = self._reputations.get(entity_id, {
            'reputation': 0.5,
            'positive_actions': 0,
            'negative_actions': 0,
            'total_actions': 0,
        })
        return state

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of reputation engine state"""
        return {
            'total_entities': len(self._reputations),
        }

