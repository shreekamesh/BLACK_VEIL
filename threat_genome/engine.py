"""
BLACK VEIL V5 — Threat Genome Database
Attack pattern storage, relationship mapping, and pattern matching using genome-style encoding
"""
import hashlib
import json
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ThreatGenome:
    """A threat genome encoding attack patterns and relationships"""
    genome_id: str
    attack_type: str
    signature_hash: str
    techniques: list[str]
    tactics: list[str]
    indicators: list[str]
    severity: float
    frequency: int
    first_seen: str
    last_seen: str
    related_genomes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ThreatGenomeEngine:
    """
    Threat Genome Database Engine.
    
    Stores and manages threat genomes as structured records with:
    - Genome encoding from attack signatures
    - Relationship mapping between related threats
    - Pattern matching for new threat identification
    - Frequency and evolution tracking
    """

    def __init__(self):
        self._genomes: dict[str, ThreatGenome] = {}
        self._type_index: dict[str, set[str]] = defaultdict(set)
        self._technique_index: dict[str, set[str]] = defaultdict(set)
        self._tactic_index: dict[str, set[str]] = defaultdict(set)

        logger.info("Threat Genome Engine initialized")

    def register_genome(
        self,
        attack_type: str,
        techniques: Optional[list[str]] = None,
        tactics: Optional[list[str]] = None,
        indicators: Optional[list[str]] = None,
        severity: float = 0.5,
    ) -> ThreatGenome:
        """
        Register a new threat genome from attack data.
        
        Args:
            attack_type: Classification (e.g., SQL_INJECTION, RANSOMWARE)
            techniques: MITRE ATT&CK technique IDs
            tactics: MITRE ATT&CK tactic categories
            indicators: Observable IoCs
            severity: Impact severity (0-1)
            
        Returns:
            Created or updated ThreatGenome
        """
        techniques = techniques or []
        tactics = tactics or []
        indicators = indicators or []

        sig_hash = self._compute_signature(attack_type, techniques, indicators)

        # Check for existing
        for existing in self._genomes.values():
            if existing.signature_hash == sig_hash:
                existing.frequency += 1
                existing.last_seen = datetime.now(timezone.utc).isoformat()
                logger.info(f"Genome updated (frequency++): {existing.genome_id[:8]}...")
                return existing

        genome_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        genome = ThreatGenome(
            genome_id=genome_id,
            attack_type=attack_type,
            signature_hash=sig_hash,
            techniques=techniques,
            tactics=tactics,
            indicators=indicators,
            severity=min(1.0, max(0.0, severity)),
            frequency=1,
            first_seen=now,
            last_seen=now,
        )

        self._genomes[genome_id] = genome
        self._type_index[attack_type].add(genome_id)
        for t in techniques:
            self._technique_index[t].add(genome_id)
        for t in tactics:
            self._tactic_index[t].add(genome_id)

        logger.info(
            f"Genome registered: {genome_id[:8]}... type={attack_type}",
            extra={"extra": {"genome_id": genome_id, "attack_type": attack_type, "techniques": techniques}},
        )

        return genome

    def relate_genomes(self, source_id: str, target_id: str) -> None:
        """Create a relationship between two threat genomes"""
        if source_id in self._genomes and target_id in self._genomes:
            if target_id not in self._genomes[source_id].related_genomes:
                self._genomes[source_id].related_genomes.append(target_id)
                logger.info(f"Relationship created: {source_id[:8]}... <-> {target_id[:8]}...")

    def find_matching_genomes(
        self,
        attack_type: Optional[str] = None,
        technique: Optional[str] = None,
        tactic: Optional[str] = None,
        indicator: Optional[str] = None,
    ) -> list[ThreatGenome]:
        """Find genomes matching given criteria"""
        results = set()

        if attack_type:
            results.update(self._type_index.get(attack_type, set()))
        if technique:
            results.update(self._technique_index.get(technique, set()))
        if tactic:
            results.update(self._tactic_index.get(tactic, set()))
        if indicator:
            for g in self._genomes.values():
                if indicator in g.indicators:
                    results.add(g.genome_id)

        return [self._genomes[gid] for gid in results if gid in self._genomes]

    def get_most_frequent(self, top_k: int = 10) -> list[ThreatGenome]:
        """Get the most frequently observed threat genomes"""
        sorted_genomes = sorted(
            self._genomes.values(), key=lambda g: g.frequency, reverse=True
        )
        return sorted_genomes[:top_k]

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of Threat Genome state"""
        return {
            "total_genomes": len(self._genomes),
            "attack_types": dict((t, len(ids)) for t, ids in self._type_index.items()),
            "unique_techniques": len(self._technique_index),
            "unique_tactics": len(self._tactic_index),
        }

    @staticmethod
    def _compute_signature(attack_type: str, techniques: list[str], indicators: list[str]) -> str:
        """Compute a unique hash signature for a threat pattern"""
        data = {
            "type": attack_type,
            "techniques": sorted(techniques),
            "indicators": sorted(indicators)[:10],
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

