"""
Intent Reasoning Engine - Infer attacker goals and predict next moves
BLACK VEIL Research Contribution: Adaptive Trust Cognitive Network (ATCN)

Core Principle:
Instead of asking "What attack is this?"
Ask: "What does the attacker want?" and "What will they do next?"

Maps observed techniques to strategic goals using MITRE ATT&CK,
predicts attacker's next steps based on kill chain progression.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class AttackerGoal(Enum):
    """Possible attacker strategic goals"""
    RECONNAISSANCE = "reconnaissance"
    RESOURCE_DEVELOPMENT = "resource_development"
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    COMMAND_AND_CONTROL = "command_and_control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"


class AttackerProfile:
    """Profile of detected attacker based on observed behavior"""
    def __init__(self):
        self.profile_id = str(uuid.uuid4())[:8]
        self.observed_techniques: List[str] = []
        self.inferred_goals: List[Dict[str, float]] = []
        self.capability_level: float = 0.0  # 0-1
        self.sophistication: float = 0.0  # 0-1
        self.persistent_level: float = 0.0  # 0-1
        self.aggressiveness: float = 0.0  # 0-1
        self.known_tactics: List[str] = []
        self.timeline: List[Dict[str, Any]] = []
        self.first_seen: Optional[str] = None
        self.last_seen: Optional[str] = None


class IntentReasoningEngine:
    """
    Infers attacker intent from observed behavior and predicts next moves.

    Capabilities:
    - Goal inference from observed techniques
    - Attacker profiling (sophistication, persistence, capability)
    - Next-step prediction using kill chain progression
    - Alternative goal analysis with confidence scoring
    """

    def __init__(self):
        # MITRE ATT&CK technique-to-goal mapping
        self._technique_to_goal: Dict[str, AttackerGoal] = self._init_technique_mapping()
        # Kill chain progression sequences
        self._kill_chains: List[List[AttackerGoal]] = self._init_kill_chains()
        # Attacker profiles
        self._profiles: Dict[str, AttackerProfile] = {}
        logger.info("IntentReasoningEngine initialized")

    def _init_technique_mapping(self) -> Dict[str, AttackerGoal]:
        """Map MITRE ATT&CK techniques to strategic goals"""
        return {
            # Reconnaissance
            'T1046': AttackerGoal.RECONNAISSANCE,  # Network Service Scanning
            'T1595': AttackerGoal.RECONNAISSANCE,  # Active Scanning
            'T1592': AttackerGoal.RECONNAISSANCE,  # Gather Victim Host Info
            'T1590': AttackerGoal.RECONNAISSANCE,  # Gather Victim Network Info
            'T1082': AttackerGoal.RECONNAISSANCE,  # System Information Discovery
            'T1518': AttackerGoal.RECONNAISSANCE,  # Software Discovery
            # Initial Access
            'T1190': AttackerGoal.INITIAL_ACCESS,  # Exploit Public-Facing App
            'T1133': AttackerGoal.INITIAL_ACCESS,  # External Remote Services
            'T1566': AttackerGoal.INITIAL_ACCESS,  # Phishing
            'T1078': AttackerGoal.INITIAL_ACCESS,  # Valid Accounts
            # Credential Access
            'T1003': AttackerGoal.CREDENTIAL_ACCESS,  # OS Credential Dumping
            'T1110': AttackerGoal.CREDENTIAL_ACCESS,  # Brute Force
            'T1552': AttackerGoal.CREDENTIAL_ACCESS,  # Unsecured Credentials
            'T1056': AttackerGoal.CREDENTIAL_ACCESS,  # Input Capture
            # Persistence
            'T1547': AttackerGoal.PERSISTENCE,  # Boot or Logon Autostart
            'T1543': AttackerGoal.PERSISTENCE,  # Create/Modify System Process
            'T1136': AttackerGoal.PERSISTENCE,  # Create Account
            'T1098': AttackerGoal.PERSISTENCE,  # Account Manipulation
            # Privilege Escalation
            'T1548': AttackerGoal.PRIVILEGE_ESCALATION,  # Abuse Elevation Control
            'T1574': AttackerGoal.PRIVILEGE_ESCALATION,  # Hijack Execution Flow
            'T1068': AttackerGoal.PRIVILEGE_ESCALATION,  # Exploitation for Priv Esc
            # Defense Evasion
            'T1562': AttackerGoal.DEFENSE_EVASION,  # Impair Defenses
            'T1070': AttackerGoal.DEFENSE_EVASION,  # Indicator Removal
            'T1036': AttackerGoal.DEFENSE_EVASION,  # Masquerading
            # Lateral Movement
            'T1021': AttackerGoal.LATERAL_MOVEMENT,  # Remote Services
            'T1550': AttackerGoal.LATERAL_MOVEMENT,  # Use Alternate Auth Material
            'T1210': AttackerGoal.LATERAL_MOVEMENT,  # Exploitation for Client Exec
            # Collection
            'T1005': AttackerGoal.COLLECTION,  # Data from Local System
            'T1114': AttackerGoal.COLLECTION,  # Email Collection
            'T1057': AttackerGoal.COLLECTION,  # Process Discovery
            # Command and Control
            'T1071': AttackerGoal.COMMAND_AND_CONTROL,  # App Layer Protocol
            'T1573': AttackerGoal.COMMAND_AND_CONTROL,  # Encrypted Channel
            'T1090': AttackerGoal.COMMAND_AND_CONTROL,  # Proxy
            # Exfiltration
            'T1048': AttackerGoal.EXFILTRATION,  # Exfiltration Over Alt Protocol
            'T1567': AttackerGoal.EXFILTRATION,  # Exfiltration Over Web Service
            'T1020': AttackerGoal.EXFILTRATION,  # Automated Exfiltration
            # Impact
            'T1486': AttackerGoal.IMPACT,  # Data Encrypted for Impact
            'T1490': AttackerGoal.IMPACT,  # Inhibit System Recovery
            'T1485': AttackerGoal.IMPACT,  # Data Destruction
        }

    def _init_kill_chains(self) -> List[List[AttackerGoal]]:
        """Initialize known kill chain progressions"""
        return [
            # Standard cyber kill chain
            [
                AttackerGoal.RECONNAISSANCE,
                AttackerGoal.RESOURCE_DEVELOPMENT,
                AttackerGoal.INITIAL_ACCESS,
                AttackerGoal.EXECUTION,
                AttackerGoal.PERSISTENCE,
                AttackerGoal.PRIVILEGE_ESCALATION,
                AttackerGoal.DEFENSE_EVASION,
                AttackerGoal.CREDENTIAL_ACCESS,
                AttackerGoal.DISCOVERY,
                AttackerGoal.LATERAL_MOVEMENT,
                AttackerGoal.COLLECTION,
                AttackerGoal.EXFILTRATION,
                AttackerGoal.IMPACT,
            ],
            # Ransomware kill chain
            [
                AttackerGoal.INITIAL_ACCESS,
                AttackerGoal.PERSISTENCE,
                AttackerGoal.PRIVILEGE_ESCALATION,
                AttackerGoal.DEFENSE_EVASION,
                AttackerGoal.IMPACT,
            ],
            # Data breach kill chain
            [
                AttackerGoal.RECONNAISSANCE,
                AttackerGoal.INITIAL_ACCESS,
                AttackerGoal.CREDENTIAL_ACCESS,
                AttackerGoal.LATERAL_MOVEMENT,
                AttackerGoal.COLLECTION,
                AttackerGoal.EXFILTRATION,
            ],
            # Advanced persistent threat (APT)
            [
                AttackerGoal.INITIAL_ACCESS,
                AttackerGoal.PERSISTENCE,
                AttackerGoal.PRIVILEGE_ESCALATION,
                AttackerGoal.DEFENSE_EVASION,
                AttackerGoal.CREDENTIAL_ACCESS,
                AttackerGoal.DISCOVERY,
                AttackerGoal.LATERAL_MOVEMENT,
                AttackerGoal.COLLECTION,
                AttackerGoal.COMMAND_AND_CONTROL,
                AttackerGoal.EXFILTRATION,
            ],
        ]

    def infer_intent(
        self,
        events: List[Dict[str, Any]],
        attacker_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Infer attacker intent from sequence of events.

        Args:
            events: Chronological list of security events
            attacker_id: Optional identifier for tracking attacker

        Returns:
            {
                'primary_goal': AttackerGoal,
                'confidence': float,
                'alternative_goals': List[Dict],
                'predicted_next_steps': List[Dict],
                'timeline_phase': str,
                'attacker_profile': AttackerProfile,
                'attacker_id': str
            }
        """
        if not events:
            return self._empty_intent()

        # Step 1: Extract techniques from events
        techniques = self._extract_techniques(events)

        # Step 2: Map techniques to goals
        goal_matches = self._match_techniques_to_goals(techniques)

        # Step 3: Identify primary goal
        primary_goal, confidence = self._identify_primary_goal(goal_matches)

        # Step 4: Get or create attacker profile
        profile = self._get_or_create_profile(attacker_id or str(uuid.uuid4()))
        self._update_profile(profile, events, techniques)

        # Step 5: Predict next steps
        next_steps = self._predict_next_steps(primary_goal, techniques, profile)

        # Step 6: Determine timeline phase
        phase = self._determine_timeline_phase(primary_goal, profile)

        logger.info(
            f"Intent inferred: goal={primary_goal.value}, "
            f"confidence={confidence:.3f}, "
            f"next_steps={len(next_steps)}, "
            f"profile_sophistication={profile.sophistication:.2f}"
        )

        return {
            'attacker_id': profile.profile_id,
            'primary_goal': primary_goal.value,
            'confidence': round(confidence, 4),
            'alternative_goals': self._get_alternative_goals(goal_matches),
            'predicted_next_steps': next_steps,
            'timeline_phase': phase,
            'attacker_profile': {
                'sophistication': round(profile.sophistication, 3),
                'capability_level': round(profile.capability_level, 3),
                'persistent_level': round(profile.persistent_level, 3),
                'aggressiveness': round(profile.aggressiveness, 3),
                'observed_techniques': profile.observed_techniques[-20:],
                'inferred_goals': profile.inferred_goals[-10:],
                'event_count': len(profile.timeline),
            },
        }

    def _extract_techniques(self, events: List[Dict[str, Any]]) -> List[str]:
        """Extract MITRE technique IDs from events"""
        techniques = []
        for event in events:
            if 'technique_id' in event:
                techniques.append(event['technique_id'])
            if 'techniques' in event:
                techniques.extend(event['techniques'])
            if 'mitre_technique' in event:
                techniques.append(event['mitre_technique'])
        return list(set(techniques))

    def _match_techniques_to_goals(
        self,
        techniques: List[str],
    ) -> Dict[str, float]:
        """Match observed techniques to possible attacker goals"""
        goal_scores: Dict[str, float] = {}

        for technique in techniques:
            goal = self._technique_to_goal.get(technique)
            if goal:
                goal_name = goal.value
                goal_scores[goal_name] = goal_scores.get(goal_name, 0.0) + 1.0

        # Normalize by total techniques
        total = len(techniques) if techniques else 1
        return {k: min(1.0, v / total * 2) for k, v in goal_scores.items()}

    def _identify_primary_goal(
        self,
        goal_matches: Dict[str, float],
    ) -> tuple[AttackerGoal, float]:
        """Identify the most likely primary goal"""
        if not goal_matches:
            return AttackerGoal.RECONNAISSANCE, 0.1

        top_goal = max(goal_matches, key=goal_matches.get)

        # Map string back to enum
        try:
            primary = AttackerGoal(top_goal)
        except ValueError:
            primary = AttackerGoal.RECONNAISSANCE

        # Calculate confidence
        scores = sorted(goal_matches.values(), reverse=True)
        if len(scores) == 1:
            confidence = min(1.0, scores[0])
        else:
            # Margin-based confidence
            confidence = min(1.0, scores[0] - scores[1] + 0.3)

        return primary, max(0.0, confidence)

    def _predict_next_steps(
        self,
        current_goal: AttackerGoal,
        techniques: List[str],
        profile: AttackerProfile,
    ) -> List[Dict[str, Any]]:
        """Predict attacker's next likely actions"""
        next_steps = []

        # Find best matching kill chain and predict next phase
        for chain in self._kill_chains:
            if current_goal in chain:
                current_idx = chain.index(current_goal)
                remaining = chain[current_idx + 1:current_idx + 4]  # Next 3 steps

                for i, next_goal in enumerate(remaining):
                    # Find techniques associated with this goal
                    associated_techs = [
                        t for t, g in self._technique_to_goal.items()
                        if g == next_goal and t not in techniques
                    ]

                    # Confidence decreases with distance
                    step_confidence = max(0.2, 0.8 - (i * 0.2))

                    next_steps.append({
                        'goal': next_goal.value,
                        'confidence': round(step_confidence, 3),
                        'timeframe': 'immediate' if i == 0 else 'short_term',
                        'predicted_techniques': associated_techs[:3],
                        'detectable': True,
                    })

                break

        return next_steps

    def _determine_timeline_phase(
        self,
        current_goal: AttackerGoal,
        profile: AttackerProfile,
    ) -> str:
        """Determine where in the attack timeline we are"""
        event_count = len(profile.timeline)

        if event_count < 5:
            return 'early'
        elif event_count < 20:
            return 'developing'
        elif event_count < 50:
            return 'mid'
        else:
            return 'late'

    def _get_or_create_profile(self, attacker_id: str) -> AttackerProfile:
        """Get existing profile or create new one"""
        if attacker_id not in self._profiles:
            self._profiles[attacker_id] = AttackerProfile()
            self._profiles[attacker_id].profile_id = attacker_id
        return self._profiles[attacker_id]

    def _update_profile(
        self,
        profile: AttackerProfile,
        events: List[Dict[str, Any]],
        techniques: List[str],
    ) -> None:
        """Update attacker profile with new observations"""
        # Update observed techniques
        profile.observed_techniques = list(set(
            profile.observed_techniques + techniques
        ))

        # Update timeline
        for event in events:
            profile.timeline.append({
                'event_type': event.get('type', 'unknown'),
                'technique_id': event.get('technique_id', ''),
                'timestamp': event.get('timestamp', datetime.now(timezone.utc).isoformat()),
            })

        # Update first/last seen
        now = datetime.now(timezone.utc).isoformat()
        if not profile.first_seen:
            profile.first_seen = now
        profile.last_seen = now

        # Calculate sophistication
        unique_techs = len(set(techniques))
        profile.sophistication = min(1.0, unique_techs / 30)
        profile.capability_level = min(1.0, unique_techs / 25)

        # Calculate persistence
        if profile.first_seen:
            try:
                first = datetime.fromisoformat(profile.first_seen.replace('Z', '+00:00'))
                span = (datetime.now(timezone.utc) - first).total_seconds()
                profile.persistent_level = min(1.0, span / 86400)  # Over days
            except Exception:
                profile.persistent_level = 0.3

        # Calculate aggressiveness
        recent_events = len(profile.timeline[-50:])
        profile.aggressiveness = min(1.0, recent_events / 50)

    def _get_alternative_goals(
        self,
        goal_matches: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Get alternative goals ranked by confidence"""
        sorted_goals = sorted(
            goal_matches.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return [
            {'goal': goal, 'confidence': round(conf, 4)}
            for goal, conf in sorted_goals[1:4]
        ]

    def _empty_intent(self) -> Dict[str, Any]:
        """Return empty/unknown intent response"""
        return {
            'attacker_id': 'unknown',
            'primary_goal': 'unknown',
            'confidence': 0.0,
            'alternative_goals': [],
            'predicted_next_steps': [],
            'timeline_phase': 'unknown',
            'attacker_profile': {},
        }

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of intent reasoning engine state"""
        return {
            'active_profiles': len(self._profiles),
            'techniques_mapped': len(self._technique_to_goal),
            'total_tracked_events': sum(
                len(p.timeline) for p in self._profiles.values()
            ),
            'high_sophistication_attackers': sum(
                1 for p in self._profiles.values()
                if p.sophistication > 0.7
            ),
        }

