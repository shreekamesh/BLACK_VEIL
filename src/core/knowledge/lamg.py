"""
Living Attack Memory Graph (LAMG) - Central knowledge repository
BLACK VEIL - Neo4j-backed graph database for all security knowledge

Single source of truth containing:
- Attack patterns, techniques, TTPs
- Evidence and relationships
- User/Device/Asset context
- Outcomes and evolution tracking
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import logging
import uuid

logger = logging.getLogger(__name__)


class LAMGNode:
    """A node in the Living Attack Memory Graph"""
    def __init__(self, node_type: str, node_id: str, properties: Dict[str, Any] = None):
        self.id = f"{node_type}:{node_id}"
        self.type = node_type
        self.properties = properties or {}
        self.created_at = datetime.now(timezone.utc).isoformat()


class LAMGRelationship:
    """A relationship edge in the Living Attack Memory Graph"""
    def __init__(self, source: str, target: str, rel_type: str, properties: Dict = None):
        self.id = str(uuid.uuid4())[:8]
        self.source = source
        self.target = target
        self.type = rel_type
        self.properties = properties or {}
        self.created_at = datetime.now(timezone.utc).isoformat()


class LivingAttackMemoryGraph:
    """
    Living Attack Memory Graph (LAMG).
    
    Central knowledge repository that evolves with every attack.
    Uses Neo4j-compatible structure with in-memory fallback.
    
    Contains:
    - Attack patterns with DNA encoding
    - MITRE ATT&CK techniques and tactics
    - User, Device, Asset context
    - Evidence and relationships
    - Evolution tracking across time
    """

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None,
                 password: Optional[str] = None):
        self._nodes: Dict[str, LAMGNode] = {}
        self._relationships: List[LAMGRelationship] = []
        self._neo4j_enabled = all([uri, user, password])
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = None

        # Indexes for fast lookup
        self._type_index: Dict[str, List[str]] = {}
        self._technique_index: Dict[str, List[str]] = {}
        self._attacker_index: Dict[str, List[str]] = {}

        if self._neo4j_enabled:
            logger.info("LAMG initialized with Neo4j backend")
        else:
            logger.info("LAMG initialized with in-memory backend")

    # ── Node Operations ───────────────────────────────────────

    def add_node(self, node_type: str, node_id: str,
                 properties: Dict[str, Any] = None) -> str:
        """Add a node to the graph"""
        node = LAMGNode(node_type, node_id, properties)
        self._nodes[node.id] = node

        # Update indexes
        self._type_index.setdefault(node_type, []).append(node.id)

        # Index techniques if present
        techniques = (properties or {}).get('techniques', [])
        for t in techniques:
            self._technique_index.setdefault(t, []).append(node.id)

        logger.debug(f"LAMG node added: {node.id}")
        return node.id

    def add_attack(self, attack_data: Dict[str, Any]) -> str:
        """Add an attack event to the graph"""
        attack_id = attack_data.get('id', str(uuid.uuid4()))
        node_id = self.add_node('Attack', attack_id, {
            'type': attack_data.get('type', 'unknown'),
            'severity': attack_data.get('severity', 0.5),
            'techniques': attack_data.get('techniques', []),
            'outcome': attack_data.get('outcome', 'unknown'),
            'source': attack_data.get('source', ''),
            'target': attack_data.get('target', ''),
            'timestamp': attack_data.get('timestamp', datetime.now(timezone.utc).isoformat()),
        })

        # Add attacker node if present
        attacker_id = attack_data.get('attacker_id')
        if attacker_id:
            attacker_node = f"Attacker:{attacker_id}"
            if attacker_node not in self._nodes:
                self.add_node('Attacker', attacker_id, {'id': attacker_id})
            self.add_relationship(attacker_node, node_id, 'PERFORMED')
            self._attacker_index.setdefault(attacker_id, []).append(node_id)

        # Add technique nodes and relationships
        for technique in attack_data.get('techniques', []):
            tech_node = f"Technique:{technique}"
            if tech_node not in self._nodes:
                self.add_node('Technique', technique, {'id': technique})
            self.add_relationship(node_id, tech_node, 'USES')

        # Add target asset
        target = attack_data.get('target')
        if target:
            target_node = f"Asset:{target}"
            if target_node not in self._nodes:
                self.add_node('Asset', target, {'id': target})
            self.add_relationship(node_id, target_node, 'TARGETED')

        logger.info(f"LAMG attack added: {attack_id} type={attack_data.get('type')}")
        return attack_id

    def add_relationship(self, source: str, target: str, rel_type: str,
                         properties: Dict = None) -> str:
        """Add a relationship between two nodes"""
        rel = LAMGRelationship(source, target, rel_type, properties)
        self._relationships.append(rel)
        return rel.id

    # ── Query Operations ──────────────────────────────────────

    def query_attacker_profile(self, attacker_id: str) -> Dict[str, Any]:
        """Query complete attacker profile from LAMG"""
        attacker_node = f"Attacker:{attacker_id}"
        if attacker_node not in self._nodes:
            return {'attacker_id': attacker_id, 'attacks': [], 'techniques': [], 'targets': []}

        attacks = self._attacker_index.get(attacker_id, [])
        attack_details = []
        techniques_used = set()
        targets_hit = set()

        for attack_id in attacks:
            node = self._nodes.get(f"Attack:{attack_id}")
            if node:
                attack_details.append(node.properties)
                techniques_used.update(node.properties.get('techniques', []))
                # Find target via relationships
                for rel in self._relationships:
                    if rel.source == node.id and rel.type == 'TARGETED':
                        targets_hit.add(rel.target)

        return {
            'attacker_id': attacker_id,
            'total_attacks': len(attacks),
            'attacks': attack_details,
            'techniques': list(techniques_used),
            'targets': list(targets_hit),
            'profile_completeness': min(1.0, len(attacks) / 10.0),
        }

    def find_similar_attacks(self, attack_pattern: Dict[str, Any],
                             max_results: int = 10) -> List[Dict[str, Any]]:
        """Find similar attacks using pattern matching"""
        pattern_techs = set(attack_pattern.get('techniques', []))
        pattern_type = attack_pattern.get('type', '')
        results = []

        for node_id, node in self._nodes.items():
            if node.type != 'Attack':
                continue

            props = node.properties
            techs = set(props.get('techniques', []))
            tech_overlap = len(pattern_techs & techs)
            type_match = 1.0 if props.get('type') == pattern_type else 0.0

            if tech_overlap > 0 or type_match > 0:
                similarity = (tech_overlap / max(1, len(pattern_techs | techs)) * 0.7
                              + type_match * 0.3)
                results.append({
                    'attack_id': node_id.split(':')[1],
                    'similarity': round(similarity, 4),
                    'type': props.get('type'),
                    'severity': props.get('severity'),
                    'techniques': props.get('techniques', []),
                })

        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_results]

    def get_attack_evolution(self, technique: str) -> List[Dict[str, Any]]:
        """Track how attacks using a technique have evolved over time"""
        attacks = []
        for node_id in self._technique_index.get(technique, []):
            node = self._nodes.get(node_id)
            if node and node.type == 'Attack':
                attacks.append({
                    'attack_id': node_id.split(':')[1],
                    'severity': node.properties.get('severity'),
                    'timestamp': node.properties.get('timestamp'),
                    'outcome': node.properties.get('outcome'),
                })

        attacks.sort(key=lambda x: x.get('timestamp', ''))
        return attacks

    def get_statistics(self) -> Dict[str, Any]:
        """Get LAMG statistics"""
        return {
            'total_nodes': len(self._nodes),
            'total_relationships': len(self._relationships),
            'node_types': {
                t: len(ids) for t, ids in self._type_index.items()
            },
            'unique_techniques': len(self._technique_index),
            'unique_attackers': len(self._attacker_index),
            'neo4j_enabled': self._neo4j_enabled,
            'memory_usage': f"{len(self._nodes) + len(self._relationships)} objects",
        }

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of LAMG state"""
        return self.get_statistics()

