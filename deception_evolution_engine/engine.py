"""
BLACK VEIL V5 — Adaptive Cyber Deception Model (ACDM)
IEEE Research Contribution 2: Evolutionary game theory-based deception strategy selection

Mathematical Model:
    D*(t) = argmaxₖ [Eₖ(t) · (1 - P̂_detectₖ(t)) / Cₖ(t)]
    Eₖ(t+1) = Eₖ(t) + η · [Rₖ(t) - Eₖ(t) · P̂_detectₖ(t)]

Key Novelty: First application of evolutionary game theory to cyber deception selection
where deception strategies evolve over multiple deployment cycles based on attacker interaction feedback.
"""
import math
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


# ── Deception Strategy Templates ──────────────────────────────

DECEPTION_STRATEGIES: dict[str, dict[str, Any]] = {
    "ssh_honeypot": {
        "name": "SSH Honeypot",
        "type": "HONEYPOT",
        "subtype": "SSH",
        "port": 22,
        "realism": 0.85,
        "luring": 0.80,
        "cost": 0.3,
        "detection_risk": 0.2,
        "description": "Fake SSH server that mimics OpenSSH",
    },
    "web_honeypot": {
        "name": "Web Application Honeypot",
        "type": "HONEYPOT",
        "subtype": "HTTP",
        "port": 80,
        "realism": 0.90,
        "luring": 0.85,
        "cost": 0.5,
        "detection_risk": 0.25,
        "description": "Fake web application with realistic content",
    },
    "database_honeypot": {
        "name": "Database Honeypot",
        "type": "HONEYPOT",
        "subtype": "MYSQL",
        "port": 3306,
        "realism": 0.80,
        "luring": 0.75,
        "cost": 0.4,
        "detection_risk": 0.3,
        "description": "Fake MySQL database with fake records",
    },
    "api_honeypot": {
        "name": "API Honeypot",
        "type": "HONEYPOT",
        "subtype": "REST_API",
        "port": 8080,
        "realism": 0.88,
        "luring": 0.82,
        "cost": 0.45,
        "detection_risk": 0.22,
        "description": "Fake REST API with realistic endpoints",
    },
    "fake_credential_db": {
        "name": "Fake Credential Database",
        "type": "FAKE_CREDENTIAL",
        "subtype": "DATABASE",
        "port": 0,
        "realism": 0.92,
        "luring": 0.90,
        "cost": 0.2,
        "detection_risk": 0.15,
        "description": "Fake credentials planted in accessible locations",
    },
    "fake_credential_api": {
        "name": "Fake API Credentials",
        "type": "FAKE_CREDENTIAL",
        "subtype": "API_KEY",
        "port": 0,
        "realism": 0.88,
        "luring": 0.85,
        "cost": 0.15,
        "detection_risk": 0.18,
        "description": "Fake API keys exposed in configuration files",
    },
    "decoy_service": {
        "name": "Decoy Network Service",
        "type": "DECOY_SERVICE",
        "subtype": "NETWORK",
        "port": 0,
        "realism": 0.82,
        "luring": 0.70,
        "cost": 0.35,
        "detection_risk": 0.28,
        "description": "Decoy service mimicking internal applications",
    },
    "network_deception": {
        "name": "Network Traffic Deception",
        "type": "NETWORK_DECEPTION",
        "subtype": "TRAFFIC",
        "port": 0,
        "realism": 0.78,
        "luring": 0.65,
        "cost": 0.25,
        "detection_risk": 0.35,
        "description": "Fake network traffic patterns to confuse attackers",
    },
}


@dataclass
class DeceptionStrategy:
    """A single deception strategy with evolutionary state"""
    strategy_id: str
    name: str
    strategy_type: str
    subtype: str
    port: int
    realism: float          # How realistic the deception appears
    luring: float           # How attractive to attackers
    cost: float             # Normalized deployment cost
    detection_risk: float   # P̂_detect — Estimated detection probability
    effectiveness: float    # Eₖ(t) — Current effectiveness score
    generation: int         # Evolution generation
    reward_history: list[float] = field(default_factory=list)
    interaction_count: int = 0
    total_dwell_time: float = 0.0
    description: str = ""


@dataclass
class DeceptionInstance:
    """A deployed deception instance"""
    instance_id: str
    strategy_id: str
    target_asset: Optional[str]
    status: str  # ACTIVE, TRIGGERED, EXPIRED, EVOLVED
    deployed_at: str
    expires_at: str
    interactions: list[dict[str, Any]] = field(default_factory=list)
    attacker_intel: dict[str, Any] = field(default_factory=dict)


class ACDMEngine:
    """
    Adaptive Cyber Deception Model Engine (Algorithm 8).
    
    Implements:
    - Strategy selection using multi-criteria optimization
    - Evolutionary update with reward-based learning
    - Detection probability estimation
    - Honeypot/digital twin deployment
    - Attacker interaction tracking
    - Intelligence gathering from deception interactions
    
    Configuration (from config.settings.acdm):
        honeypot_count: Number of honeypot instances (default: 10)
        deception_duration: Default deception lifetime in seconds (default: 3600)
        learning_rate: η — Evolution learning rate (default: 0.1)
        realism_threshold: Minimum realism score (default: 0.8)
        evolution_generations: Max evolution generations (default: 100)
        mutation_rate: Strategy mutation rate (default: 0.1)
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self._learning_rate = float(self.config.get("learning_rate", 0.1))
        self._deception_duration = int(self.config.get("deception_duration", 3600))
        self._realism_threshold = float(self.config.get("realism_threshold", 0.8))
        self._mutation_rate = float(self.config.get("mutation_rate", 0.1))
        self._max_interactions = int(self.config.get("max_interactions", 1000))

        # Strategy population
        self._strategies: dict[str, DeceptionStrategy] = {}
        self._instances: dict[str, DeceptionInstance] = {}
        self._attacker_profiles: dict[str, dict[str, Any]] = {}

        # Initialize strategy population from templates
        self._initialize_strategies()

        logger.info(
            "ACDM Engine initialized",
            extra={
                "extra": {
                    "strategies": len(self._strategies),
                    "learning_rate": self._learning_rate,
                    "mutation_rate": self._mutation_rate,
                }
            },
        )

    def _initialize_strategies(self) -> None:
        """Initialize strategy population from predefined templates"""
        for sid, template in DECEPTION_STRATEGIES.items():
            strategy = DeceptionStrategy(
                strategy_id=sid,
                name=template["name"],
                strategy_type=template["type"],
                subtype=template["subtype"],
                port=template["port"],
                realism=template["realism"],
                luring=template["luring"],
                cost=template["cost"],
                detection_risk=template["detection_risk"],
                effectiveness=0.5,  # Initial effectiveness (neutral)
                generation=0,
                description=template["description"],
            )
            self._strategies[sid] = strategy

    # ── Strategy Selection ───────────────────────────────────

    def select_optimal_strategy(
        self,
        attacker_profile: Optional[dict[str, Any]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> DeceptionStrategy:
        """
        Select optimal deception strategy using multi-criteria decision analysis.
        
        D*(t) = argmaxₖ [Eₖ(t) · (1 - P̂_detectₖ(t)) / Cₖ(t)]
        
        Args:
            attacker_profile: Known attacker behavior profile
            context: Situational context
            
        Returns:
            Selected DeceptionStrategy with highest score
        """
        best_strategy = None
        best_score = float("-inf")

        for strategy in self._strategies.values():
            # Base score from evolutionary state
            score = self._calculate_strategy_score(strategy, attacker_profile, context)

            if score > best_score:
                best_score = score
                best_strategy = strategy

        logger.info(
            f"Optimal strategy selected: {best_strategy.name} (score={best_score:.4f})",
            extra={
                "extra": {
                    "strategy": best_strategy.strategy_id,
                    "score": round(best_score, 4),
                    "generation": best_strategy.generation,
                }
            },
        )

        return best_strategy

    def select_deception_strategies(
        self,
        count: int = 3,
        attacker_profile: Optional[dict[str, Any]] = None,
    ) -> list[DeceptionStrategy]:
        """
        Select top-K deception strategies ranked by score.
        
        Args:
            count: Number of strategies to select
            attacker_profile: Known attacker behavior profile
            
        Returns:
            List of top-K DeceptionStrategy objects
        """
        scored = []
        for strategy in self._strategies.values():
            score = self._calculate_strategy_score(strategy, attacker_profile)
            scored.append((score, strategy))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:count]]

    def _calculate_strategy_score(
        self,
        strategy: DeceptionStrategy,
        attacker_profile: Optional[dict[str, Any]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Calculate strategy score considering effectiveness, detection risk, and cost.
        
        Score = Eₖ · (1 - P̂_detect) / Cₖ · Attractor
        """
        effectiveness = max(0.01, strategy.effectiveness)
        detection_risk = max(0.01, strategy.detection_risk)
        cost = max(0.01, strategy.cost)

        # Base score
        score = effectiveness * (1.0 - detection_risk) / cost

        # Attacker-specific adjustment
        if attacker_profile:
            attractor = self._calculate_attractor_score(strategy, attacker_profile)
            score *= attractor

        # Context adjustment
        if context:
            context_modifier = self._calculate_context_modifier(strategy, context)
            score *= context_modifier

        return score

    def _calculate_attractor_score(
        self,
        strategy: DeceptionStrategy,
        attacker_profile: dict[str, Any],
    ) -> float:
        """Calculate how attractive this strategy is to a specific attacker"""
        preferred_types = attacker_profile.get("targeted_services", [])
        skill_level = attacker_profile.get("skill_level", "medium")

        if strategy.subtype.lower() in [t.lower() for t in preferred_types]:
            return 1.5
        if skill_level == "low":
            return strategy.realism * 1.2  # Less skilled attackers more easily fooled
        elif skill_level == "high":
            return strategy.luring * 0.8  # Skilled attackers harder to deceive
        return 1.0

    def _calculate_context_modifier(
        self,
        strategy: DeceptionStrategy,
        context: dict[str, Any],
    ) -> float:
        """Calculate context-based score modifier"""
        modifier = 1.0

        # Time-based modification
        hour = context.get("hour", 12)
        if 0 <= hour <= 6:
            modifier *= 1.2  # Night time — more effective

        # Threat level modification
        threat_level = context.get("threat_level", "LOW")
        if threat_level == "CRITICAL":
            modifier *= 1.5
        elif threat_level == "HIGH":
            modifier *= 1.3

        return modifier

    # ── Deployment ───────────────────────────────────────────

    def deploy_strategy(
        self,
        strategy_id: str,
        target_asset: Optional[str] = None,
        duration: Optional[int] = None,
    ) -> DeceptionInstance:
        """
        Deploy a deception strategy as an active instance.
        
        Args:
            strategy_id: Strategy to deploy
            target_asset: Optional target asset to mimic
            duration: Custom lifetime in seconds
            
        Returns:
            Deployed DeceptionInstance
        """
        if strategy_id not in self._strategies:
            raise ValueError(f"Unknown strategy: {strategy_id}")

        strategy = self._strategies[strategy_id]
        now = datetime.now(timezone.utc)
        lifetime = duration or self._deception_duration

        instance = DeceptionInstance(
            instance_id=str(uuid.uuid4()),
            strategy_id=strategy_id,
            target_asset=target_asset,
            status="ACTIVE",
            deployed_at=now.isoformat(),
            expires_at=(now.timestamp() + lifetime).isoformat(),
        )

        self._instances[instance.instance_id] = instance

        logger.info(
            f"Deception deployed: {strategy.name} (instance={instance.instance_id})",
            extra={
                "extra": {
                    "instance_id": instance.instance_id,
                    "strategy": strategy.name,
                    "duration": lifetime,
                    "target": target_asset,
                }
            },
        )

        return instance

    def record_interaction(
        self,
        instance_id: str,
        interaction_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Record an attacker interaction with a deception instance.
        
        Args:
            instance_id: Deception instance ID
            interaction_data: Interaction details including dwell time
            
        Returns:
            Intelligence extracted from the interaction
        """
        if instance_id not in self._instances:
            logger.warning(f"Unknown deception instance: {instance_id}")
            return {}

        instance = self._instances[instance_id]
        strategy_id = instance.strategy_id

        # Record interaction
        interaction = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": interaction_data,
            "intelligence": {},
        }
        instance.interactions.append(interaction)

        # Extract attacker intelligence
        intelligence = self._extract_intelligence(interaction_data)
        interaction["intelligence"] = intelligence
        instance.attacker_intel.update(intelligence)

        # Update strategy with reward
        dwell_time = interaction_data.get("dwell_time", 0)
        interaction_depth = interaction_data.get("depth", 0)
        intel_gathered = len(intelligence)

        reward = self._calculate_reward(dwell_time, interaction_depth, intel_gathered)
        self._update_strategy(strategy_id, reward, interaction_data)

        # Update attacker profile
        attacker_id = interaction_data.get("attacker_id", "unknown")
        self._update_attacker_profile(attacker_id, interaction_data)

        logger.info(
            f"Interaction recorded for instance {instance_id}: dwell={dwell_time}s, reward={reward:.3f}",
            extra={
                "extra": {
                    "instance_id": instance_id,
                    "dwell_time": dwell_time,
                    "reward": round(reward, 4),
                    "intel_count": len(intelligence),
                }
            },
        )

        return intelligence

    def expire_instance(self, instance_id: str) -> None:
        """Mark a deception instance as expired"""
        if instance_id in self._instances:
            self._instances[instance_id].status = "EXPIRED"
            logger.info(f"Deception instance expired: {instance_id}")

    # ── Evolutionary Update ──────────────────────────────────

    def evolve_strategies(self) -> dict[str, float]:
        """
        Evolve all strategies one generation.
        
        Eₖ(t+1) = Eₖ(t) + η · [Rₖ(t) - Eₖ(t) · P̂_detectₖ(t)]
        
        Returns:
            Dict mapping strategy_id to new effectiveness score
        """
        updates = {}
        for sid, strategy in self._strategies.items():
            if not strategy.reward_history:
                continue

            avg_reward = sum(strategy.reward_history[-10:]) / max(1, len(strategy.reward_history[-10:]))

            new_effectiveness = strategy.effectiveness + self._learning_rate * (
                avg_reward - strategy.effectiveness * strategy.detection_risk
            )

            # Clamp to [0, 1]
            new_effectiveness = max(0.0, min(1.0, new_effectiveness))

            strategy.effectiveness = new_effectiveness
            strategy.generation += 1
            updates[sid] = new_effectiveness

            # Mutate detection risk
            if random.random() < self._mutation_rate:
                strategy.detection_risk = max(
                    0.01, min(0.99, strategy.detection_risk + random.uniform(-0.05, 0.05))
                )

        logger.info(
            f"Strategies evolved: {len(updates)} updated",
            extra={"extra": {"generation_updates": updates}},
        )

        return updates

    def get_evolution_summary(self) -> dict[str, Any]:
        """Get summary of strategy evolution state"""
        return {
            strategy_id: {
                "name": s.name,
                "effectiveness": round(s.effectiveness, 4),
                "detection_risk": round(s.detection_risk, 4),
                "generation": s.generation,
                "interactions": s.interaction_count,
                "avg_reward": round(
                    sum(s.reward_history[-20:]) / max(1, len(s.reward_history[-20:])), 4
                ) if s.reward_history else 0.0,
            }
            for strategy_id, s in self._strategies.items()
        }

    # ── Internal: Reward & Update ────────────────────────────

    def _calculate_reward(
        self,
        dwell_time: float,
        interaction_depth: float,
        intel_gathered: int,
    ) -> float:
        """
        Calculate reward from an interaction.
        
        Rₖ(t) = α · DwellTimeₖ(t) + β · InteractionDepthₖ(t) + γ · IntelGatheredₖ(t)
        """
        alpha, beta, gamma = 0.5, 0.3, 0.2

        normalized_dwell = min(1.0, dwell_time / 3600.0)  # Normalize to 1 hour
        normalized_depth = min(1.0, interaction_depth / 10.0)
        normalized_intel = min(1.0, intel_gathered / 20.0)

        return (
            alpha * normalized_dwell
            + beta * normalized_depth
            + gamma * normalized_intel
        )

    def _update_strategy(
        self,
        strategy_id: str,
        reward: float,
        interaction_data: dict[str, Any],
    ) -> None:
        """Update strategy state with interaction feedback"""
        if strategy_id not in self._strategies:
            return

        strategy = self._strategies[strategy_id]
        strategy.reward_history.append(reward)
        strategy.interaction_count += 1

        dwell_time = interaction_data.get("dwell_time", 0)
        strategy.total_dwell_time += dwell_time

        # Update detection probability using Bayesian-like update
        detected = interaction_data.get("detected", False)
        if detected:
            strategy.detection_risk = min(
                0.99, strategy.detection_risk + self._learning_rate * 0.1
            )
        else:
            strategy.detection_risk = max(
                0.01, strategy.detection_risk - self._learning_rate * 0.05
            )

    def _update_attacker_profile(
        self,
        attacker_id: str,
        interaction_data: dict[str, Any],
    ) -> None:
        """Update or create attacker profile from interaction data"""
        if attacker_id not in self._attacker_profiles:
            self._attacker_profiles[attacker_id] = {
                "first_seen": datetime.now(timezone.utc).isoformat(),
                "techniques": set(),
                "tools": set(),
                "interaction_count": 0,
            }

        profile = self._attacker_profiles[attacker_id]
        profile["interaction_count"] += 1

        technique = interaction_data.get("technique")
        if technique:
            profile["techniques"].add(technique)

        tool = interaction_data.get("tool")
        if tool:
            profile["tools"].add(tool)

    def _extract_intelligence(self, interaction: dict[str, Any]) -> dict[str, Any]:
        """Extract intelligence from attacker interaction"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_ip": interaction.get("source_ip"),
            "attack_type": interaction.get("type"),
            "tools_used": interaction.get("tools", []),
            "techniques": interaction.get("techniques", []),
            "data_accessed": interaction.get("data_accessed", []),
            "behavior_pattern": self._analyze_behavior(interaction),
        }

    @staticmethod
    def _analyze_behavior(interaction: dict[str, Any]) -> str:
        """Analyze attacker behavior pattern"""
        attack_type = interaction.get("type", "unknown")
        if attack_type in ("scan", "probe"):
            return "reconnaissance"
        elif attack_type in ("exploit", "attack"):
            return "aggressive"
        elif attack_type == "exfiltrate":
            return "stealthy"
        return "exploratory"

    def _mutate_strategies(self) -> None:
        """Apply random mutations to strategy parameters"""
        for strategy in self._strategies.values():
            if random.random() < self._mutation_rate:
                strategy.realism = max(0.1, min(1.0, strategy.realism + random.uniform(-0.1, 0.1)))
                strategy.luring = max(0.1, min(1.0, strategy.luring + random.uniform(-0.1, 0.1)))

    # ── State Management ─────────────────────────────────────

    def get_active_instances(self) -> list[DeceptionInstance]:
        """Get all active deception instances"""
        return [i for i in self._instances.values() if i.status == "ACTIVE"]

    def get_instance(self, instance_id: str) -> Optional[DeceptionInstance]:
        """Get a specific deception instance"""
        return self._instances.get(instance_id)

    def get_strategy(self, strategy_id: str) -> Optional[DeceptionStrategy]:
        """Get a specific strategy"""
        return self._strategies.get(strategy_id)

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of current ACDM state"""
        return {
            "strategies": len(self._strategies),
            "active_instances": len(self.get_active_instances()),
            "total_interactions": sum(s.interaction_count for s in self._strategies.values()),
            "attacker_profiles": len(self._attacker_profiles),
            "config": {
                "learning_rate": self._learning_rate,
                "deception_duration": self._deception_duration,
                "realism_threshold": self._realism_threshold,
                "mutation_rate": self._mutation_rate,
            },
        }

