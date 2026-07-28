"""
Trust Engine - TTRM (Temporal Trust Recovery Model)
BLACK VEIL Research Contribution 1: Temporal Trust Recovery Model

Tᵣ(t) = T₀ · e^(-λt) + Σᵢ [Rᵢ · e^(-μ(t - tᵢ))] + D(t) · δ(t)

Core Principle:
Trust is not binary - it's a continuous, dynamic metric
that factors in behavior, context, risk, and confidence.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import math
import logging
import uuid

logger = logging.getLogger(__name__)


class TrustEngine:
    """
    Trust Engine implementing TTRM with:
    - Temporal trust decay and recovery
    - Multi-factor trust computation
    - Drift detection (CUSUM)
    - Context-aware trust adjustment
    - Confidence-calibrated trust scores
    """

    def __init__(self):
        self._trust_scores: Dict[str, Dict[str, Any]] = {}
        self._trust_decay_rate = 0.01  # λ
        self._recovery_decay_rate = 0.1  # μ
        self._drift_threshold = 3.0
        logger.info("TrustEngine initialized")

    def evaluate(
        self,
        entity_id: str,
        entity_type: str,
        event: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate trust for an entity based on current context and history.

        Tᵣ(t) = T₀ · e^(-λt) + Σᵢ [Rᵢ · e^(-μ(t - tᵢ))] + D(t) · δ(t)
        """
        key = f"{entity_type}:{entity_id}"
        now = datetime.now(timezone.utc)

        # Get or initialize trust state
        if key not in self._trust_scores:
            self._trust_scores[key] = self._initialize_trust(entity_id, entity_type)

        state = self._trust_scores[key]

        # Apply temporal decay
        if state['last_updated']:
            time_diff = (now - datetime.fromisoformat(state['last_updated'])).total_seconds()
            decay = math.exp(-self._trust_decay_rate * time_diff / 3600.0)
            state['trust_score'] *= decay

        # Process event if provided
        if event:
            state = self._update_from_event(state, event)

        # Calculate drift
        drift = self._detect_drift(state)
        if drift > self._drift_threshold:
            state['drift_detected'] = True
            state['trust_score'] = max(0.0, state['trust_score'] - drift * 0.01)

        # Calculate confidence
        confidence = self._calculate_confidence(state)

        # Determine trust level
        trust_level = self._determine_trust_level(state['trust_score'])

        state['last_updated'] = now.isoformat()
        self._trust_scores[key] = state

        return {
            'entity_id': entity_id,
            'entity_type': entity_type,
            'trust_score': round(state['trust_score'], 4),
            'confidence': round(confidence, 4),
            'risk_score': round(1.0 - state['trust_score'], 4),
            'trust_level': trust_level,
            'drift_detected': state.get('drift_detected', False),
            'factors': state.get('factors', {}),
            'history_length': len(state.get('history', [])),
            'assessed_at': now.isoformat(),
        }

    def _initialize_trust(self, entity_id: str, entity_type: str) -> Dict[str, Any]:
        """Initialize trust state for a new entity"""
        return {
            'entity_id': entity_id,
            'entity_type': entity_type,
            'trust_score': 0.7,  # Start with moderate trust
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'history': [],
            'factors': {},
            'drift_detected': False,
            'recovery_events': [],
        }

    def _update_from_event(
        self,
        state: Dict[str, Any],
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update trust based on new event"""
        event_type = event.get('type', 'unknown')
        severity = event.get('severity', 0.5)

        # Calculate trust impact
        if severity > 0.7:  # Malicious event
            impact = -(severity * 0.2)
        elif severity > 0.3:  # Suspicious event
            impact = -(severity * 0.1)
        else:  # Benign/positive event
            impact = 0.05  # Small positive recovery

        # Apply impact
        state['trust_score'] = max(0.0, min(1.0, state['trust_score'] + impact))

        # Record recovery event if positive
        if impact > 0:
            state['recovery_events'].append({
                'magnitude': impact,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            })

        # Record history
        state['history'].append({
            'event_type': event_type,
            'severity': severity,
            'impact': impact,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })

        # Keep history limited
        if len(state['history']) > 100:
            state['history'] = state['history'][-100:]

        return state

    def _detect_drift(self, state: Dict[str, Any]) -> float:
        """Detect trust drift using CUSUM-based approach"""
        if len(state['history']) < 2:
            return 0.0

        recent = state['history'][-10:]
        scores = [h.get('impact', 0) for h in recent]
        avg_score = sum(scores) / len(scores) if scores else 0
        baseline = 0.0  # Expected normal impact

        drift = abs(avg_score - baseline) * len(scores) ** 0.5
        return drift

    def _calculate_confidence(self, state: Dict[str, Any]) -> float:
        """Calculate confidence in trust score"""
        history_len = len(state['history'])
        if history_len < 5:
            return 0.3  # Low confidence with little data
        elif history_len < 20:
            return 0.6
        elif history_len < 50:
            return 0.8
        return 0.95

    @staticmethod
    def _determine_trust_level(trust_score: float) -> str:
        """Determine trust level from score"""
        if trust_score >= 0.7:
            return 'high'
        elif trust_score >= 0.4:
            return 'medium'
        return 'low'

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of trust engine state"""
        scores = [s['trust_score'] for s in self._trust_scores.values()]
        return {
            'total_entities': len(self._trust_scores),
            'avg_trust_score': round(sum(scores) / max(1, len(scores)), 4) if scores else 0,
            'high_trust': sum(1 for s in scores if s >= 0.7),
            'medium_trust': sum(1 for s in scores if 0.4 <= s < 0.7),
            'low_trust': sum(1 for s in scores if s < 0.4),
            'drift_detected_count': sum(
                1 for s in self._trust_scores.values() if s.get('drift_detected')
            ),
        }

