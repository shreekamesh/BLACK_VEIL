"""
Threat Genome - Attack pattern encoding and matching
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import hashlib
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class ThreatGenome:
    """
    Threat Genome Database - Encodes attack patterns as genomes
    for similarity matching, evolution tracking, and prediction.
    """

    def __init__(self):
        self._genomes: Dict[str, Dict[str, Any]] = {}
        self._type_index: Dict[str, List[str]] = {}
        self._technique_index: Dict[str, List[str]] = {}
        logger.info("ThreatGenome initialized")

    def register_genome(
        self,
        attack_type: str,
        techniques: Optional[List[str]] = None,
        indicators: Optional[List[str]] = None,
        severity: float = 0.5,
    ) -> str:
        """Register a new threat genome"""
        genome_id = str(uuid.uuid4())
        sig = self._compute_signature(attack_type, techniques or [], indicators or [])

        genome = {
            'genome_id': genome_id,
            'attack_type': attack_type,
            'techniques': techniques or [],
            'indicators': indicators or [],
            'severity': min(1.0, max(0.0, severity)),
            'signature': sig,
            'frequency': 1,
            'first_seen': datetime.now(timezone.utc).isoformat(),
            'last_seen': datetime.now(timezone.utc).isoformat(),
        }

        self._genomes[genome_id] = genome
        self._type_index.setdefault(attack_type, []).append(genome_id)
        for t in techniques or []:
            self._technique_index.setdefault(t, []).append(genome_id)

        logger.info(f"Genome registered: {genome_id[:8]} type={attack_type}")
        return genome_id

    def find_similar(self, genome_id: str) -> List[Dict[str, Any]]:
        """Find similar genomes"""
        if genome_id not in self._genomes:
            return []
        genome = self._genomes[genome_id]
        results = []

        for gid, g in self._genomes.items():
            if gid == genome_id:
                continue
            similarity = self._compute_similarity(genome, g)
            if similarity > 0.5:
                results.append({'genome_id': gid, 'similarity': similarity})

        return sorted(results, key=lambda x: x['similarity'], reverse=True)[:5]

    def get_most_frequent(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently observed threat genomes"""
        return sorted(
            self._genomes.values(),
            key=lambda g: g['frequency'],
            reverse=True,
        )[:top_k]

    def _compute_signature(self, attack_type: str, techniques: List[str],
                           indicators: List[str]) -> str:
        """Compute unique signature for a threat pattern"""
        data = {
            'type': attack_type,
            'techniques': sorted(techniques),
            'indicators': sorted(indicators)[:5],
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def _compute_similarity(g1: Dict[str, Any], g2: Dict[str, Any]) -> float:
        """Compute similarity between two genomes"""
        techs1 = set(g1.get('techniques', []))
        techs2 = set(g2.get('techniques', []))
        union = len(techs1 | techs2)
        jaccard = len(techs1 & techs2) / max(1, union)

        type_match = 1.0 if g1['attack_type'] == g2['attack_type'] else 0.0
        severity_sim = 1.0 - abs(g1['severity'] - g2['severity'])

        return jaccard * 0.5 + type_match * 0.3 + severity_sim * 0.2

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of threat genome state"""
        return {
            'total_genomes': len(self._genomes),
            'unique_types': len(self._type_index),
            'unique_techniques': len(self._technique_index),
            'most_common_type': max(self._type_index, key=lambda k: len(self._type_index[k]))
            if self._type_index else 'none',
        }

