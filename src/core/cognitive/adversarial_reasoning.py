"""
Adversarial Reasoning Engine - Think like an attacker
BLACK VEIL Research Contribution: Adaptive Trust Cognitive Network (ATCN)

Core Principle:
Instead of "What attack is happening?", ask:
  "If I were the attacker, how would I bypass this defense?"

Continuously evaluates defenses from the attacker's perspective to
identify blind spots before they are exploited.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import logging
import math
import uuid

logger = logging.getLogger(__name__)


class DefenseGap:
    """A weakness identified from the attacker's perspective"""
    def __init__(
        self,
        layer: str,
        weakness_score: float,
        description: str,
        exploit_difficulty: float,
        impact_if_exploited: float,
        recommended_action: str,
    ):
        self.gap_id = str(uuid.uuid4())[:8]
        self.layer = layer
        self.weakness_score = weakness_score  # 0-1 (higher = weaker)
        self.description = description
        self.exploit_difficulty = exploit_difficulty  # 0-1 (higher = easier)
        self.impact_if_exploited = impact_if_exploited  # 0-1
        self.recommended_action = recommended_action
        self.identified_at = datetime.now(timezone.utc).isoformat()


class AttackPath:
    """A possible attack path identified through simulation"""
    def __init__(
        self,
        path: List[str],
        likelihood: float,
        impact: float,
        cost: float,
        time_to_execute: float,
    ):
        self.path = path
        self.likelihood = likelihood  # 0-1
        self.impact = impact  # 0-1
        self.cost = cost  # 0-1 (normalized)
        self.time_to_execute = time_to_execute  # seconds
        self.risk_score = likelihood * impact


class AdversarialReasoningEngine:
    """
    Continuously evaluates the system from an attacker's perspective.

    Capabilities:
    - Defense gap analysis: Identify weakest defense layer
    - Attack path simulation: Model possible attack routes
    - Weakest asset identification: Most attractive targets
    - Adversarial blind spot detection: What defenses miss
    - Bypass strategy generation: How an attacker would bypass
    """

    def __init__(self):
        self._defense_layers: Dict[str, float] = {
            'firewall': 0.85,
            'credential': 0.75,
            'trust': 0.70,
            'deception': 0.65,
            'api_security': 0.80,
            'identity': 0.75,
            'monitoring': 0.70,
            'encryption': 0.90,
            'network_segmentation': 0.75,
            'endpoint_protection': 0.70,
        }
        self._known_attack_vectors: List[Dict[str, Any]] = []
        self._defense_gaps: List[DefenseGap] = []
        self._analysis_history: List[Dict[str, Any]] = []
        logger.info("AdversarialReasoningEngine initialized")

    def analyze_defenses(
        self,
        threat_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive adversarial analysis of current defenses.

        Returns:
        {
            'weakest_layer': str,
            'defense_gaps': List[DefenseGap],
            'attack_paths': List[AttackPath],
            'most_attractive_targets': List[Dict],
            'bypass_strategies': List[str],
            'overall_adversarial_score': float
        }
        """
        # 1. Analyze each defense layer
        gaps = self._identify_defense_gaps(threat_context)

        # 2. Simulate attack paths
        attack_paths = self._simulate_attack_paths(threat_context)

        # 3. Identify most attractive targets
        targets = self._identify_attractive_targets(threat_context)

        # 4. Generate bypass strategies
        bypasses = self._generate_bypass_strategies(gaps)

        # 5. Overall adversarial score (0=secure, 1=compromised)
        adversarial_score = self._calculate_adversarial_score(gaps, attack_paths)

        result = {
            'weakest_layer': min(gaps, key=lambda g: g.weakness_score).layer if gaps else 'unknown',
            'defense_gaps': [
                {
                    'layer': g.layer,
                    'weakness_score': g.weakness_score,
                    'description': g.description,
                    'exploit_difficulty': g.exploit_difficulty,
                    'impact': g.impact_if_exploited,
                    'recommended_action': g.recommended_action,
                }
                for g in gaps
            ],
            'attack_paths': [
                {
                    'path': p.path,
                    'likelihood': p.likelihood,
                    'impact': p.impact,
                    'cost': p.cost,
                    'time_to_execute': p.time_to_execute,
                    'risk_score': p.risk_score,
                }
                for p in attack_paths
            ],
            'most_attractive_targets': targets,
            'bypass_strategies': bypasses,
            'overall_adversarial_score': round(adversarial_score, 4),
            'analysis_id': str(uuid.uuid4())[:8],
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        self._analysis_history.append(result)
        self._defense_gaps = gaps

        logger.info(
            f"Adversarial analysis: weakest={result['weakest_layer']}, "
            f"score={adversarial_score:.3f}, "
            f"gaps={len(gaps)}, paths={len(attack_paths)}"
        )
        return result

    def _identify_defense_gaps(
        self,
        threat_context: Optional[Dict[str, Any]] = None,
    ) -> List[DefenseGap]:
        """
        Identify weaknesses in each defense layer.

        For each layer, asks:
        "If I'm an attacker, how easy is it to bypass this layer?"
        """
        gaps = []

        # Adjust defense scores based on threat context
        adjusted = self._adjust_defense_scores(threat_context)

        for layer, score in adjusted.items():
            weakness = 1.0 - score
            exploit_difficulty = weakness  # Higher weakness = easier to exploit

            gap = DefenseGap(
                layer=layer,
                weakness_score=weakness,
                description=self._get_gap_description(layer, weakness),
                exploit_difficulty=exploit_difficulty,
                impact_if_exploited=self._get_impact(layer),
                recommended_action=self._get_recommendation(layer, weakness),
            )
            gaps.append(gap)

        # Sort by weakness (highest first)
        gaps.sort(key=lambda g: g.weakness_score, reverse=True)
        return gaps

    def _adjust_defense_scores(
        self,
        threat_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, float]:
        """Adjust defense scores based on current threat context"""
        if not threat_context:
            return self._defense_layers.copy()

        adjusted = self._defense_layers.copy()
        threat_type = threat_context.get('attack_type', '').lower()
        threat_severity = threat_context.get('severity', 0.5)

        # Known threat-specific weaknesses
        if 'sql' in threat_type or 'injection' in threat_type:
            adjusted['api_security'] *= 0.8
            adjusted['firewall'] *= 0.9
        elif 'credential' in threat_type or 'brute' in threat_type:
            adjusted['credential'] *= 0.7
            adjusted['identity'] *= 0.85
        elif 'ransomware' in threat_type or 'malware' in threat_type:
            adjusted['endpoint_protection'] *= 0.75
            adjusted['network_segmentation'] *= 0.85
        elif 'ddos' in threat_type or 'dos' in threat_type:
            adjusted['firewall'] *= 0.7
            adjusted['monitoring'] *= 0.8

        # Scale by severity
        if threat_severity > 0.8:
            for k in adjusted:
                adjusted[k] *= 0.9  # High severity reduces confidence in all defenses

        return adjusted

    def _simulate_attack_paths(
        self,
        threat_context: Optional[Dict[str, Any]] = None,
    ) -> List[AttackPath]:
        """
        Simulate possible attack paths through the system.

        Models paths like:
        Internet → Web Server → API → Database → Privilege Escalation → Sensitive Asset
        """
        paths = []

        # Common attack paths
        path_templates = [
            {
                'path': ['internet', 'web_server', 'api', 'database', 'sensitive_data'],
                'base_likelihood': 0.4,
                'base_impact': 0.9,
            },
            {
                'path': ['internet', 'vpn', 'internal_network', 'credential_server', 'domain_admin'],
                'base_likelihood': 0.3,
                'base_impact': 1.0,
            },
            {
                'path': ['internet', 'web_server', 'file_upload', 'webshell', 'persistence'],
                'base_likelihood': 0.35,
                'base_impact': 0.8,
            },
            {
                'path': ['insider', 'internal_app', 'database', 'data_exfiltration'],
                'base_likelihood': 0.2,
                'base_impact': 0.95,
            },
            {
                'path': ['internet', 'email', 'phishing', 'credential_theft', 'lateral_movement'],
                'base_likelihood': 0.5,
                'base_impact': 0.85,
            },
        ]

        for template in path_templates:
            # Adjust likelihood based on defense gaps
            gap_adjustment = self._calculate_path_gap_factor(template['path'])
            likelihood = min(1.0, template['base_likelihood'] * (1 + gap_adjustment))

            # Adjust based on threat context
            if threat_context:
                if 'phishing' in template['path'] and threat_context.get('attack_type') == 'phishing':
                    likelihood *= 1.5
                elif 'credential' in template['path'] and 'credential' in str(threat_context):
                    likelihood *= 1.3

            # Calculate path metrics
            cost = (1.0 - likelihood) * 0.5 + 0.2  # Harder paths cost more
            time_to_execute = (1.0 - likelihood) * 3600 + 300  # 5min to 1hr

            path = AttackPath(
                path=template['path'],
                likelihood=min(1.0, likelihood),
                impact=template['base_impact'],
                cost=min(1.0, cost),
                time_to_execute=time_to_execute,
            )
            paths.append(path)

        # Sort by risk score (highest first)
        paths.sort(key=lambda p: p.risk_score, reverse=True)
        return paths

    def _calculate_path_gap_factor(self, path: List[str]) -> float:
        """Calculate how much defense gaps increase path likelihood"""
        gap_factor = 0.0
        for step in path:
            for gap in self._defense_gaps:
                if gap.layer in step:
                    gap_factor += gap.weakness_score * 0.2
        return min(1.0, gap_factor)

    def _identify_attractive_targets(
        self,
        threat_context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Identify most attractive targets from attacker's perspective"""
        targets = [
            {
                'asset': 'Primary Database',
                'attractiveness': 0.95,
                'exposure': 0.6,
                'value': 'Customer data, credentials, financial records',
                'weakest_access_path': 'api_security',
            },
            {
                'asset': 'Credential Vault',
                'attractiveness': 0.9,
                'exposure': 0.4,
                'value': 'All user credentials, service accounts',
                'weakest_access_path': 'credential',
            },
            {
                'asset': 'Admin Panel',
                'attractiveness': 0.85,
                'exposure': 0.5,
                'value': 'Full system control',
                'weakest_access_path': 'identity',
            },
            {
                'asset': 'API Gateway',
                'attractiveness': 0.8,
                'exposure': 0.7,
                'value': 'Access to all microservices',
                'weakest_access_path': 'api_security',
            },
            {
                'asset': 'CI/CD Pipeline',
                'attractiveness': 0.75,
                'exposure': 0.3,
                'value': 'Code access, deployment control',
                'weakest_access_path': 'credential',
            },
        ]

        # Adjust attractiveness based on current gaps
        for target in targets:
            for gap in self._defense_gaps:
                if gap.layer == target['weakest_access_path']:
                    target['attractiveness'] = min(1.0, target['attractiveness'] + gap.weakness_score * 0.2)

        targets.sort(key=lambda t: t['attractiveness'], reverse=True)
        return targets

    def _generate_bypass_strategies(self, gaps: List[DefenseGap]) -> List[str]:
        """Generate strategies an attacker would use to bypass defenses"""
        if not gaps:
            return ["No bypass strategies identified — all defenses strong"]

        strategies = []
        for gap in gaps[:3]:  # Top 3 weakest
            if gap.weakness_score > 0.4:
                strategy = (
                    f"Bypass {gap.layer} by exploiting {gap.description}. "
                    f"Difficulty: {gap.exploit_difficulty:.1f}, "
                    f"Impact: {gap.impact_if_exploited:.1f}. "
                    f"Recommendation: {gap.recommended_action}"
                )
                strategies.append(strategy)

        return strategies

    def _calculate_adversarial_score(
        self,
        gaps: List[DefenseGap],
        paths: List[AttackPath],
    ) -> float:
        """Calculate overall adversarial vulnerability score (0=secure, 1=compromised)"""
        if not gaps:
            return 0.0

        # Average weakness across all layers
        avg_weakness = sum(g.weakness_score for g in gaps) / len(gaps)

        # Average risk from attack paths
        avg_risk = sum(p.risk_score for p in paths) / max(1, len(paths))

        # Combined score
        score = avg_weakness * 0.5 + avg_risk * 0.5
        return min(1.0, max(0.0, score))

    @staticmethod
    def _get_gap_description(layer: str, weakness: float) -> str:
        """Get human-readable description of a defense gap"""
        descriptions = {
            'firewall': 'Potential misconfiguration or rule gap',
            'credential': 'Weak password policy or credential exposure',
            'trust': 'Trust scoring may not detect sophisticated attacks',
            'deception': 'Deception coverage may have blind spots',
            'api_security': 'API endpoint may have insufficient validation',
            'identity': 'Identity verification may be bypassable',
            'monitoring': 'Monitoring may miss slow, low-and-slow attacks',
            'encryption': 'Encryption implementation may have side channels',
            'network_segmentation': 'Network segmentation may have gaps',
            'endpoint_protection': 'Endpoint protection may miss zero-days',
        }
        desc = descriptions.get(layer, f'Unknown layer: {layer}')
        if weakness > 0.6:
            desc = f"CRITICAL: {desc}"
        elif weakness > 0.3:
            desc = f"MODERATE: {desc}"
        else:
            desc = f"MINOR: {desc}"
        return desc

    @staticmethod
    def _get_impact(layer: str) -> float:
        """Get potential impact if this layer is breached"""
        impacts = {
            'firewall': 0.6,
            'credential': 0.9,
            'trust': 0.7,
            'deception': 0.5,
            'api_security': 0.8,
            'identity': 0.85,
            'monitoring': 0.4,
            'encryption': 0.7,
            'network_segmentation': 0.65,
            'endpoint_protection': 0.75,
        }
        return impacts.get(layer, 0.5)

    @staticmethod
    def _get_recommendation(layer: str, weakness: float) -> str:
        """Get recommended action to address gap"""
        recommendations = {
            'firewall': 'Review firewall rules, add geo-blocking, enable IPS',
            'credential': 'Enforce MFA, rotate credentials, check for exposures',
            'trust': 'Update trust models, add behavioral baselines',
            'deception': 'Expand deception coverage, add honeytokens',
            'api_security': 'Add input validation, rate limiting, API gateway',
            'identity': 'Strengthen identity verification, add device fingerprinting',
            'monitoring': 'Enhance monitoring rules, add anomaly detection',
            'encryption': 'Audit encryption implementation, update protocols',
            'network_segmentation': 'Review segment boundaries, add micro-segmentation',
            'endpoint_protection': 'Update EDR rules, add behavioral detection',
        }
        base = recommendations.get(layer, 'Review and strengthen layer')
        if weakness > 0.6:
            return f"URGENT: {base}"
        return base

    def update_defense_score(self, layer: str, score: float) -> None:
        """Update the effectiveness score for a defense layer"""
        if layer in self._defense_layers:
            self._defense_layers[layer] = max(0.0, min(1.0, score))
            logger.info(f"Defense score updated: {layer} = {score:.3f}")

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of adversarial reasoning state"""
        return {
            'defense_layers': self._defense_layers.copy(),
            'total_analyses': len(self._analysis_history),
            'current_gaps': len(self._defense_gaps),
            'weakest_layer': min(self._defense_layers, key=self._defense_layers.get)
            if self._defense_layers else 'unknown',
            'overall_defense_strength': round(
                sum(self._defense_layers.values()) / len(self._defense_layers), 3
            ) if self._defense_layers else 0.0,
        }

