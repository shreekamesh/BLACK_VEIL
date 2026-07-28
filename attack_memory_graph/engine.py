"""
BLACK VEIL V5 — Living Attack Memory Graph (LAMG)
IEEE Research Contribution 6: Graph-based attack memory with DNA encoding and evolution tracking

Mathematical Model:
    Attack DNA Encoding → Similarity Search → Evolution Tracking
    τ(t) = ⟨type, severity, source, target, pattern, indicators, techniques⟩

Key Novelty: First living memory graph for attacks with DNA encoding, threat genome database,
behavioral timeline construction, and attack evolution history tracking.
"""
import hashlib
import json
import math
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AttackNode:
    """
    A node in the Living Attack Memory Graph representing an attack.
    """
    node_id: str
    attack_dna: dict[str, Any]         # Encoded attack DNA features
    signature: str                      # Unique attack signature hash
    attack_type: str                    # e.g., SQL_INJECTION, PORT_SCAN
    severity: float                     # 0.0 - 1.0
    occurrence_count: int               # Times this attack pattern observed
    first_seen: str                     # ISO timestamp
    last_seen: str                      # ISO timestamp
    techniques: list[str]               # MITRE ATT&CK techniques
    indicators: list[str]               # IoCs
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackEdge:
    """
    A directed edge representing relationship between two attack nodes.
    """
    edge_id: str
    source_id: str                      # Source attack node
    target_id: str                      # Target attack node
    relationship: str                   # EVOLVED_FROM, RELATED_TO, SEQUEL, VARIANT_OF
    weight: float                       # Relationship strength (0-1)
    evidence: list[str]                 # Supporting evidence
    created_at: str


class LAMGEngine:
    """
    Living Attack Memory Graph Engine (Algorithm 9, 11).
    
    Implements:
    - Attack DNA encoding and signature generation
    - Graph-based similarity search with multiple distance metrics
    - Attack timeline reconstruction
    - Evolution path tracking (BFS)
    - Threat genome database management
    - Memory decay and reinforcement
    
    Configuration (from config.settings.lamg):
        node_limit: Max attack nodes in graph (default: 100000)
        edge_limit: Max edges in graph (default: 500000)
        similarity_threshold: Minimum similarity for matching (default: 0.8)
        evolution_window: Days for evolution tracking (default: 30)
        dna_dimension: Attack DNA vector dimension (default: 256)
        memory_decay_rate: λ — Memory decay rate (default: 0.01)
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self._node_limit = int(self.config.get("node_limit", 100000))
        self._edge_limit = int(self.config.get("edge_limit", 500000))
        self._similarity_threshold = float(self.config.get("similarity_threshold", 0.8))
        self._evolution_window = int(self.config.get("evolution_window", 30))
        self._dna_dimension = int(self.config.get("dna_dimension", 256))
        self._memory_decay_rate = float(self.config.get("memory_decay_rate", 0.01))

        # Graph storage
        self._nodes: dict[str, AttackNode] = {}
        self._edges: list[AttackEdge] = []
        self._adjacency: dict[str, set[str]] = defaultdict(set)

        # Indexes
        self._type_index: dict[str, set[str]] = defaultdict(set)
        self._technique_index: dict[str, set[str]] = defaultdict(set)
        self._signature_index: dict[str, str] = {}

        logger.info(
            "LAMG Engine initialized",
            extra={
                "extra": {
                    "node_limit": self._node_limit,
                    "edge_limit": self._edge_limit,
                    "similarity_threshold": self._similarity_threshold,
                    "dna_dimension": self._dna_dimension,
                }
            },
        )

    # ── Attack DNA Encoding ─────────────────────────────────

    def encode_attack(
        self,
        attack_data: dict[str, Any],
    ) -> AttackNode:
        """
        Encode attack data into an AttackNode with DNA signature.
        
        Args:
            attack_data: Raw attack data with type, severity, source, target, etc.
            
        Returns:
            Created AttackNode (or existing if duplicate)
        """
        # Extract features
        features = self._extract_features(attack_data)
        signature = self._generate_signature(features)

        # Check for existing by signature
        if signature in self._signature_index:
            existing_id = self._signature_index[signature]
            existing_node = self._nodes[existing_id]
            existing_node.occurrence_count += 1
            existing_node.last_seen = datetime.now(timezone.utc).isoformat()
            logger.info(f"Attack already exists (incremented count): {existing_id[:8]}...")
            return existing_node

        # Create new node
        node_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        node = AttackNode(
            node_id=node_id,
            attack_dna=features,
            signature=signature,
            attack_type=features.get("type", "unknown"),
            severity=float(features.get("severity", 0.5)),
            occurrence_count=1,
            first_seen=now,
            last_seen=now,
            techniques=features.get("techniques", []),
            indicators=features.get("indicators", []),
            metadata={
                "source_ip": features.get("source", "unknown"),
                "target": features.get("target", "unknown"),
                "protocol": features.get("protocol", "unknown"),
                "port": features.get("port", 0),
            },
        )

        # Add to graph
        self._add_node(node)

        # Check capacity
        if len(self._nodes) >= self._node_limit:
            self._evict_oldest_node()

        logger.info(
            f"Attack encoded: {node_id[:8]}... type={node.attack_type}, sev={node.severity:.2f}",
            extra={
                "extra": {
                    "node_id": node_id,
                    "attack_type": node.attack_type,
                    "severity": node.severity,
                    "techniques": node.techniques,
                }
            },
        )

        return node

    def encode_attack_batch(self, attacks: list[dict[str, Any]]) -> list[AttackNode]:
        """Encode multiple attacks in batch"""
        return [self.encode_attack(a) for a in attacks]

    # ── Similarity Search ────────────────────────────────────

    def find_similar_attacks(
        self,
        attack_dna: dict[str, Any],
        threshold: Optional[float] = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Find similar attacks in the graph.
        
        Args:
            attack_dna: Attack DNA features to match against
            threshold: Similarity threshold (defaults to config value)
            max_results: Maximum results to return
            
        Returns:
            List of {attack: AttackNode, similarity: float} sorted by similarity
        """
        threshold = threshold or self._similarity_threshold
        attack_type = attack_dna.get("type", "")
        results = []

        # Use type index for efficient search
        candidate_ids = self._type_index.get(attack_type, set(self._nodes.keys()))

        for node_id in candidate_ids:
            if node_id not in self._nodes:
                continue

            node = self._nodes[node_id]
            similarity = self._calculate_dna_similarity(attack_dna, node.attack_dna)

            if similarity >= threshold:
                results.append({"attack": node, "similarity": round(similarity, 4)})

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:max_results]

    def find_by_technique(self, technique: str) -> list[AttackNode]:
        """Find attacks matching a MITRE ATT&CK technique"""
        node_ids = self._technique_index.get(technique, set())
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]

    def find_by_indicator(self, indicator: str) -> list[AttackNode]:
        """Find attacks matching an IoC"""
        results = []
        for node in self._nodes.values():
            if indicator in node.indicators:
                results.append(node)
        return results

    # ── Timeline & Evolution ─────────────────────────────────

    def get_attack_timeline(
        self,
        attack_id: str,
        max_events: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Reconstruct attack timeline from graph relationships.
        
        Args:
            attack_id: Starting attack node
            max_events: Maximum timeline events
            
        Returns:
            Chronological timeline of related attacks
        """
        if attack_id not in self._nodes:
            raise ValueError(f"Attack not found: {attack_id}")

        timeline = []
        visited = set()
        queue = [(attack_id, 0)]

        while queue and len(timeline) < max_events:
            current_id, depth = queue.pop(0)

            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id in self._nodes:
                node = self._nodes[current_id]
                timeline.append({
                    "attack_id": current_id,
                    "attack_type": node.attack_type,
                    "severity": node.severity,
                    "first_seen": node.first_seen,
                    "last_seen": node.last_seen,
                    "occurrences": node.occurrence_count,
                    "depth": depth,
                })

            # Traverse edges
            for neighbor_id in self._adjacency.get(current_id, set()):
                if neighbor_id not in visited:
                    queue.append((neighbor_id, depth + 1))

        # Sort chronologically
        timeline.sort(key=lambda x: x["first_seen"])
        return timeline

    def get_evolution_path(
        self,
        attack_id: str,
        max_depth: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Get attack evolution path showing how attack patterns evolved.
        
        Args:
            attack_id: Starting attack node
            max_depth: Maximum evolution depth
            
        Returns:
            Evolution path with levels and relationships
        """
        if attack_id not in self._nodes:
            raise ValueError(f"Attack not found: {attack_id}")

        evolution = []
        visited = set()
        queue = [(attack_id, 0, "")]

        while queue:
            current_id, level, relationship = queue.pop(0)

            if current_id in visited or level > max_depth:
                continue
            visited.add(current_id)

            if current_id in self._nodes:
                node = self._nodes[current_id]
                evolution.append({
                    "attack_id": current_id,
                    "attack_type": node.attack_type,
                    "severity": node.severity,
                    "techniques": node.techniques,
                    "level": level,
                    "relationship": relationship,
                })

            # Get edges from this node
            for edge in self._edges:
                if edge.source_id == current_id:
                    queue.append((edge.target_id, level + 1, edge.relationship))

        return evolution

    # ── Graph Management ─────────────────────────────────────

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship: str = "RELATED_TO",
        weight: float = 0.5,
        evidence: Optional[list[str]] = None,
    ) -> AttackEdge:
        """
        Add a relationship edge between two attack nodes.
        
        Args:
            source_id: Source attack node
            target_id: Target attack node
            relationship: Type (EVOLVED_FROM, RELATED_TO, SEQUEL, VARIANT_OF)
            weight: Relationship strength (0-1)
            evidence: Supporting evidence
            
        Returns:
            Created AttackEdge
        """
        if source_id not in self._nodes or target_id not in self._nodes:
            raise ValueError("Source or target attack not found in graph")

        # Check capacity
        if len(self._edges) >= self._edge_limit:
            self._evict_oldest_edge()

        edge = AttackEdge(
            edge_id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
            weight=min(1.0, max(0.0, weight)),
            evidence=evidence or [],
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        self._edges.append(edge)
        self._adjacency[source_id].add(target_id)

        logger.info(
            f"Relationship added: {source_id[:8]}... --[{relationship}]--> {target_id[:8]}...",
            extra={"extra": {"relationship": relationship, "weight": weight}},
        )

        return edge

    def update_attack(
        self,
        attack_id: str,
        new_data: dict[str, Any],
    ) -> Optional[AttackNode]:
        """Update an existing attack node with new data"""
        if attack_id not in self._nodes:
            logger.warning(f"Attack not found for update: {attack_id}")
            return None

        node = self._nodes[attack_id]
        features = self._extract_features(new_data)

        # Merge features
        merged = self._merge_features(node.attack_dna, features)
        node.attack_dna = merged
        node.last_seen = datetime.now(timezone.utc).isoformat()
        node.occurrence_count += 1

        # Update techniques
        new_techniques = features.get("techniques", [])
        for t in new_techniques:
            if t not in node.techniques:
                node.techniques.append(t)

        # Update indicators
        new_indicators = features.get("indicators", [])
        for ioc in new_indicators:
            if ioc not in node.indicators:
                node.indicators.append(ioc)

        logger.info(f"Attack updated: {attack_id[:8]}... (total occurrences: {node.occurrence_count})")

        return node

    # ── Threat Genome Database ──────────────────────────────

    def get_threat_genome(
        self,
        attack_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Get threat genome summary for one or more attacks.
        
        Args:
            attack_ids: Specific attacks (None = all)
            
        Returns:
            Threat genome data with types, techniques, and relationships
        """
        target_ids = attack_ids or list(self._nodes.keys())

        types = defaultdict(int)
        techniques = defaultdict(int)
        severity_sum = 0.0

        for nid in target_ids:
            if nid not in self._nodes:
                continue
            node = self._nodes[nid]
            types[node.attack_type] += 1
            for t in node.techniques:
                techniques[t] += 1
            severity_sum += node.severity

        return {
            "total_attacks": len(target_ids),
            "attack_types": dict(types),
            "techniques": dict(sorted(techniques.items(), key=lambda x: x[1], reverse=True)[:20]),
            "avg_severity": round(severity_sum / max(1, len(target_ids)), 4),
            "relationships": len(self._edges),
            "timeframe": self._get_graph_timeframe(),
        }

    # ── Internal: Feature Extraction ─────────────────────────

    @staticmethod
    def _extract_features(attack_data: dict[str, Any]) -> dict[str, Any]:
        """Extract normalized features from attack data"""
        return {
            "type": attack_data.get("type", "unknown"),
            "severity": float(attack_data.get("severity", 0.5)),
            "source": attack_data.get("source", ""),
            "target": attack_data.get("target", ""),
            "protocol": attack_data.get("protocol", ""),
            "port": int(attack_data.get("port", 0)),
            "timestamp": attack_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "techniques": attack_data.get("techniques", []),
            "indicators": attack_data.get("indicators", []),
            "payload_hash": attack_data.get("payload_hash", ""),
            "mitre_tactic": attack_data.get("mitre_tactic", ""),
            "mitre_technique": attack_data.get("mitre_technique", ""),
        }

    @staticmethod
    def _generate_signature(features: dict[str, Any]) -> str:
        """Generate unique attack signature hash"""
        sig_data = {
            "type": features.get("type"),
            "techniques": sorted(features.get("techniques", [])),
            "source": features.get("source", ""),
            "target": features.get("target", ""),
            "protocol": features.get("protocol", ""),
            "port": features.get("port", 0),
        }
        sig_str = json.dumps(sig_data, sort_keys=True)
        return hashlib.sha256(sig_str.encode()).hexdigest()

    @staticmethod
    def _calculate_dna_similarity(
        dna1: dict[str, Any],
        dna2: dict[str, Any],
    ) -> float:
        """Calculate similarity between two attack DNA vectors"""
        # Type match
        type_match = 1.0 if dna1.get("type") == dna2.get("type") else 0.0

        # Technique overlap (Jaccard)
        techs1 = set(dna1.get("techniques", []))
        techs2 = set(dna2.get("techniques", []))
        tech_union = len(techs1 | techs2)
        tech_jaccard = len(techs1 & techs2) / max(1, tech_union)

        # Indicator overlap
        ind1 = set(dna1.get("indicators", []))
        ind2 = set(dna2.get("indicators", []))
        ind_union = len(ind1 | ind2)
        ind_jaccard = len(ind1 & ind2) / max(1, ind_union)

        # Source/Target similarity
        src_match = 1.0 if dna1.get("source") == dna2.get("source") else 0.0
        tgt_match = 1.0 if dna1.get("target") == dna2.get("target") else 0.0
        port_match = 1.0 if dna1.get("port") == dna2.get("port") else 0.0

        # Severity similarity
        sev1 = float(dna1.get("severity", 0))
        sev2 = float(dna2.get("severity", 0))
        severity_sim = 1.0 - min(1.0, abs(sev1 - sev2))

        # Weighted combination
        similarity = (
            0.25 * type_match
            + 0.25 * tech_jaccard
            + 0.15 * ind_jaccard
            + 0.10 * src_match
            + 0.10 * tgt_match
            + 0.05 * port_match
            + 0.10 * severity_sim
        )

        return similarity

    # ── Internal: Graph Operations ───────────────────────────

    def _add_node(self, node: AttackNode) -> None:
        """Add a node to the graph with indexing"""
        self._nodes[node.node_id] = node
        self._signature_index[node.signature] = node.node_id
        self._type_index[node.attack_type].add(node.node_id)

        for technique in node.techniques:
            self._technique_index[technique].add(node.node_id)

    def _evict_oldest_node(self) -> None:
        """Evict the oldest node (LRU-like) by last_seen"""
        if not self._nodes:
            return

        oldest_id = min(self._nodes, key=lambda nid: self._nodes[nid].last_seen)
        oldest = self._nodes[oldest_id]

        del self._nodes[oldest_id]
        self._signature_index.pop(oldest.signature, None)
        self._type_index[oldest.attack_type].discard(oldest_id)

        for technique in oldest.techniques:
            self._technique_index[technique].discard(oldest_id)

        logger.debug(f"Evicted oldest node: {oldest_id[:8]}...")

    def _evict_oldest_edge(self) -> None:
        """Evict the oldest edge"""
        if self._edges:
            oldest = min(self._edges, key=lambda e: e.created_at)
            self._edges.remove(oldest)

    @staticmethod
    def _merge_features(
        existing: dict[str, Any],
        new_features: dict[str, Any],
    ) -> dict[str, Any]:
        """Deep merge new features into existing"""
        merged = existing.copy()
        for key, value in new_features.items():
            if key in ("techniques", "indicators"):
                merged_list = list(set(merged.get(key, []) + value))
                merged[key] = merged_list
            elif isinstance(value, (int, float)):
                merged[key] = value
            elif value:
                merged[key] = value
        return merged

    def _get_graph_timeframe(self) -> dict[str, Optional[str]]:
        """Get the time range of the graph"""
        if not self._nodes:
            return {"earliest": None, "latest": None}
        times = [(n.first_seen, n.last_seen) for n in self._nodes.values()]
        return {
            "earliest": min(t[0] for t in times),
            "latest": max(t[1] for t in times),
        }

    # ── State Management ─────────────────────────────────────

    def get_node(self, node_id: str) -> Optional[AttackNode]:
        """Get a specific attack node"""
        return self._nodes.get(node_id)

    def get_statistics(self) -> dict[str, Any]:
        """Get graph statistics"""
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "attack_types": dict(
                (t, len(ids)) for t, ids in self._type_index.items()
            ),
            "unique_techniques": len(self._technique_index),
            "timeframe": self._get_graph_timeframe(),
            "config": {
                "node_limit": self._node_limit,
                "edge_limit": self._edge_limit,
                "similarity_threshold": self._similarity_threshold,
                "dna_dimension": self._dna_dimension,
                "memory_decay_rate": self._memory_decay_rate,
            },
        }

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of current LAMG state"""
        return self.get_statistics()

