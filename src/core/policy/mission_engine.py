"""
Mission Policy Engine - Aligns security decisions with business priorities
BLACK VEIL - Ensures security responses respect mission-critical constraints

Core Principle:
Security is not one-size-fits-all. A hospital prioritizes availability,
a bank prioritizes integrity, a research lab prioritizes confidentiality.

Maps business mission profiles to security response priorities.
"""
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MissionPriority(Enum):
    """Mission priority types"""
    AVAILABILITY = "availability"
    CONFIDENTIALITY = "confidentiality"
    INTEGRITY = "integrity"
    PERFORMANCE = "performance"
    SAFETY = "safety"


class MissionContext:
    """Context for a business mission"""
    def __init__(
        self,
        mission_id: str,
        priority: MissionPriority,
        assets: List[str],
        criticality: float,
        sla: Optional[Dict[str, float]] = None,
    ):
        self.mission_id = mission_id
        self.priority = priority
        self.assets = assets
        self.criticality = min(1.0, max(0.0, criticality))
        self.sla = sla or {}
        self.created_at = None


class MissionPolicyEngine:
    """
    Ensures security responses align with business missions.

    Provides response priority weights based on mission profile:
    - Hospital:  Availability > Confidentiality
    - Bank:       Integrity > Availability
    - Research:   Confidentiality > Availability
    - Military:   Safety > All

    Usage:
        engine = MissionPolicyEngine()
        weights = engine.get_response_weights('hospital', 'isolate')
        # Returns: {'availability_impact': 0.9, 'security_impact': 0.3, ...}
    """

    def __init__(self):
        self._missions: Dict[str, MissionContext] = {}
        self._load_default_missions()
        self._active_mission: Optional[str] = None
        logger.info("MissionPolicyEngine initialized")

    def _load_default_missions(self) -> None:
        """Load default mission profiles"""
        self.register_mission(MissionContext(
            mission_id='hospital',
            priority=MissionPriority.AVAILABILITY,
            assets=['patient_records', 'life_support', 'monitoring_systems',
                    'ehr_systems', 'pharmacy'],
            criticality=0.95,
            sla={'max_downtime_seconds': 300, 'response_time_seconds': 30},
        ))

        self.register_mission(MissionContext(
            mission_id='bank',
            priority=MissionPriority.INTEGRITY,
            assets=['transactions', 'accounts', 'audit_logs',
                    'ledger', 'payment_systems'],
            criticality=0.95,
            sla={'max_data_loss': 0.0, 'settlement_time_minutes': 5},
        ))

        self.register_mission(MissionContext(
            mission_id='research',
            priority=MissionPriority.CONFIDENTIALITY,
            assets=['ip', 'patents', 'research_data',
                    'source_code', 'experimental_results'],
            criticality=0.9,
            sla={'classification_level': 'top_secret'},
        ))

        self.register_mission(MissionContext(
            mission_id='military',
            priority=MissionPriority.SAFETY,
            assets=['command_control', 'communication', 'surveillance',
                    'weapons_systems', 'personnel_data'],
            criticality=1.0,
            sla={'max_latency_ms': 10, 'availability': 0.9999},
        ))

        self.register_mission(MissionContext(
            mission_id='ecommerce',
            priority=MissionPriority.AVAILABILITY,
            assets=['product_catalog', 'cart', 'payment', 'user_accounts',
                    'inventory'],
            criticality=0.85,
            sla={'uptime': 0.995, 'max_response_time_ms': 200},
        ))

    def register_mission(self, mission: MissionContext) -> None:
        """Register a mission profile"""
        self._missions[mission.mission_id] = mission
        logger.info(f"Mission registered: {mission.mission_id} "
                    f"(priority={mission.priority.value}, "
                    f"criticality={mission.criticality})")

    def set_active_mission(self, mission_id: str) -> bool:
        """Set the currently active mission profile"""
        if mission_id in self._missions:
            self._active_mission = mission_id
            logger.info(f"Active mission set: {mission_id}")
            return True
        logger.warning(f"Mission not found: {mission_id}")
        return False

    def get_response_weights(self, mission_id: Optional[str] = None,
                             response_type: Optional[str] = None) -> Dict[str, float]:
        """
        Get response priority weights based on mission.

        Args:
            mission_id: Mission profile to use (uses active if not specified)
            response_type: Type of response (for type-specific adjustments)

        Returns:
            Dict with weights for: availability_impact, security_impact,
            cost_impact, speed_required, autonomy_level
        """
        mid = mission_id or self._active_mission
        mission = self._missions.get(mid) if mid else None

        if not mission:
            return self._default_weights()

        # Base weights by priority type
        if mission.priority == MissionPriority.AVAILABILITY:
            weights = {
                'availability_impact': 0.9,
                'security_impact': 0.3,
                'cost_impact': 0.2,
                'speed_required': 0.9,
                'autonomy_level': 0.8,
            }
        elif mission.priority == MissionPriority.CONFIDENTIALITY:
            weights = {
                'availability_impact': 0.2,
                'security_impact': 0.9,
                'cost_impact': 0.3,
                'speed_required': 0.5,
                'autonomy_level': 0.6,
            }
        elif mission.priority == MissionPriority.INTEGRITY:
            weights = {
                'availability_impact': 0.4,
                'security_impact': 0.9,
                'cost_impact': 0.4,
                'speed_required': 0.6,
                'autonomy_level': 0.7,
            }
        elif mission.priority == MissionPriority.SAFETY:
            weights = {
                'availability_impact': 0.8,
                'security_impact': 0.7,
                'cost_impact': 0.1,
                'speed_required': 1.0,
                'autonomy_level': 0.9,
            }
        elif mission.priority == MissionPriority.PERFORMANCE:
            weights = {
                'availability_impact': 0.6,
                'security_impact': 0.5,
                'cost_impact': 0.5,
                'speed_required': 0.3,
                'autonomy_level': 0.5,
            }
        else:
            weights = self._default_weights()

        # Adjust for response type
        if response_type:
            weights = self._adjust_for_response(weights, response_type, mission)

        # Scale by criticality
        for k in weights:
            weights[k] = round(weights[k] * mission.criticality, 4)

        return weights

    def _adjust_for_response(self, weights: Dict[str, float],
                              response_type: str,
                              mission: MissionContext) -> Dict[str, float]:
        """Adjust weights for specific response types"""
        adjusted = weights.copy()

        # Responses that impact availability
        if response_type in ('isolate', 'block', 'shutdown'):
            if mission.priority == MissionPriority.AVAILABILITY:
                adjusted['availability_impact'] = min(1.0, adjusted['availability_impact'] * 1.2)
                adjusted['security_impact'] *= 0.8

        # Responses that impact data
        if response_type in ('rotate', 'revoke', 'encrypt'):
            if mission.priority == MissionPriority.INTEGRITY:
                adjusted['security_impact'] = min(1.0, adjusted['security_impact'] * 1.1)

        # Monitoring responses
        if response_type in ('monitor', 'deceive'):
            adjusted['availability_impact'] *= 0.3  # Low availability impact

        return adjusted

    def get_mission_impact(self, response_type: str,
                           mission_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the impact assessment of a response on the mission.

        Returns:
            {
                'mission_id': str,
                'priority': str,
                'availability_risk': float,
                'security_benefit': float,
                'critical_asset_risk': float,
                'sla_violation_risk': float,
                'recommendation': str
            }
        """
        weights = self.get_response_weights(mission_id, response_type)
        mission = self._missions.get(mission_id or self._active_mission)

        if not mission:
            return {
                'mission_id': mission_id or 'unknown',
                'priority': 'unknown',
                'availability_risk': 0.5,
                'security_benefit': 0.5,
                'recommendation': 'No mission profile',
            }

        # Calculate risks based on response type
        disruptive_actions = ('isolate', 'shutdown', 'block', 'revoke')
        safe_actions = ('monitor', 'deceive', 'notify', 'log')

        availability_risk = weights['availability_impact'] * (
            1.0 if response_type in disruptive_actions else
            0.2 if response_type in safe_actions else 0.5
        )

        security_benefit = weights['security_impact'] * (
            1.0 if response_type in ('block', 'isolate') else
            0.8 if response_type in ('rotate', 'revoke') else
            0.5
        )

        # Check if critical assets are at risk
        critical_risk = min(1.0, availability_risk * 0.5 + (1 - security_benefit) * 0.5)

        return {
            'mission_id': mission.mission_id,
            'priority': mission.priority.value,
            'availability_risk': round(availability_risk, 4),
            'security_benefit': round(security_benefit, 4),
            'critical_asset_risk': round(critical_risk, 4),
            'recommendation': (
                'Proceed' if security_benefit > availability_risk * 1.5
                else 'Proceed with caution' if security_benefit > availability_risk
                else 'Seek alternative'
            ),
        }

    def list_missions(self) -> List[Dict[str, Any]]:
        """List all registered mission profiles"""
        return [
            {
                'mission_id': m.mission_id,
                'priority': m.priority.value,
                'assets': m.assets,
                'criticality': m.criticality,
            }
            for m in self._missions.values()
        ]

    def _default_weights(self) -> Dict[str, float]:
        """Default weights when no mission is defined"""
        return {
            'availability_impact': 0.5,
            'security_impact': 0.5,
            'cost_impact': 0.3,
            'speed_required': 0.5,
            'autonomy_level': 0.6,
        }

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of mission policy engine state"""
        return {
            'missions_registered': len(self._missions),
            'active_mission': self._active_mission,
            'mission_profiles': [
                f"{m.mission_id} ({m.priority.value})"
                for m in self._missions.values()
            ],
            'active_mission_profile': (
                self._missions[self._active_mission].priority.value
                if self._active_mission and self._active_mission in self._missions
                else None
            ),
        }

