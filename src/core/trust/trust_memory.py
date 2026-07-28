"""
Trust Memory - Historical trust score storage and recall
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class TrustMemory:
    """
    Stores and manages historical trust scores for temporal analysis.
    Supports pattern detection, trend analysis, and trust recovery.
    """

    def __init__(self, max_history: int = 1000):
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        self._max_history = max_history
        logger.info("TrustMemory initialized")

    def record(self, entity_id: str, trust_score: float, context: Optional[Dict] = None):
        """Record a trust score for an entity"""
        if entity_id not in self._history:
            self._history[entity_id] = []

        self._history[entity_id].append({
            'trust_score': trust_score,
            'context': context or {},
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })

        # Trim history
        if len(self._history[entity_id]) > self._max_history:
            self._history[entity_id] = self._history[entity_id][-self._max_history:]

    def get_history(self, entity_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trust score history for an entity"""
        return self._history.get(entity_id, [])[-limit:]

    def get_trend(self, entity_id: str, window: int = 10) -> str:
        """Get trust score trend"""
        history = self.get_history(entity_id, window)
        if len(history) < 2:
            return 'stable'

        recent = [h['trust_score'] for h in history]
        avg_old = sum(recent[:len(recent)//2]) / max(1, len(recent)//2)
        avg_new = sum(recent[len(recent)//2:]) / max(1, len(recent) - len(recent)//2)

        if avg_new > avg_old + 0.05:
            return 'improving'
        elif avg_new < avg_old - 0.05:
            return 'declining'
        return 'stable'

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of trust memory state"""
        return {
            'total_entities': len(self._history),
            'total_records': sum(len(h) for h in self._history.values()),
        }

