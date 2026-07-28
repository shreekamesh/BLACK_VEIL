"""
BLACK VEIL V5 — Knowledge Engine
Threat intelligence knowledge base with MITRE ATT&CK, CAPEC, CVE, Sigma/YARA rules,
evidence graph reasoning, and forward/backward chaining inference
"""
import json
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EvidenceNode:
    """A node in the evidence graph"""
    node_id: str
    node_type: str                    # event, indicator, technique, tactic
    label: str
    properties: dict[str, Any]
    timestamp: str
    confidence: float = 1.0


@dataclass
class EvidenceEdge:
    """An edge/relationship in the evidence graph"""
    source_id: str
    target_id: str
    relationship: str                 # correlates, causes, precedes, indicates
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


class KnowledgeEngine:
    """
    Knowledge Engine with reasoning capabilities.
    
    Implements:
    - Structured threat intelligence (MITRE ATT&CK, CAPEC, CVE, Sigma, YARA)
    - Evidence graph for correlation and causality
    - Forward/backward chaining inference (Algorithm 24)
    - Causal reasoning and root cause analysis
    """

    def __init__(self):
        # Knowledge base
        self._knowledge_base: dict[str, dict[str, Any]] = {
            "mitre_techniques": {},
            "capec_patterns": {},
            "cve_entries": {},
            "sigma_rules": {},
            "yara_rules": {},
        }

        # Evidence graph
        self._nodes: dict[str, EvidenceNode] = {}
        self._edges: list[EvidenceEdge] = []
        self._node_index: dict[str, set[str]] = defaultdict(set)  # type -> node_ids

        logger.info("Knowledge Engine initialized")

    def register_mitre_technique(
        self, technique_id: str, name: str, tactic: str, description: str
    ) -> None:
        """Register a MITRE ATT&CK technique"""
        self._knowledge_base["mitre_techniques"][technique_id] = {
            "id": technique_id,
            "name": name,
            "tactic": tactic,
            "description": description,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"MITRE technique registered: {technique_id} - {name}")

    def register_sigma_rule(self, rule_id: str, title: str, logsource: dict,
                             detection: dict, level: str = "medium") -> None:
        """Register a Sigma detection rule"""
        self._knowledge_base["sigma_rules"][rule_id] = {
            "id": rule_id,
            "title": title,
            "logsource": logsource,
            "detection": detection,
            "level": level,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"Sigma rule registered: {rule_id}")

    def add_evidence_node(
        self,
        node_type: str,
        label: str,
        properties: Optional[dict[str, Any]] = None,
        confidence: float = 1.0,
    ) -> EvidenceNode:
        """Add a node to the evidence graph"""
        node = EvidenceNode(
            node_id=str(uuid.uuid4()),
            node_type=node_type,
            label=label,
            properties=properties or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=min(1.0, max(0.0, confidence)),
        )
        self._nodes[node.node_id] = node
        self._node_index[node_type].add(node.node_id)
        return node

    def add_evidence_edge(
        self,
        source_id: str,
        target_id: str,
        relationship: str,
        weight: float = 1.0,
    ) -> None:
        """Add a relationship edge between two evidence nodes"""
        if source_id not in self._nodes or target_id not in self._nodes:
            raise ValueError("Both source and target nodes must exist")

        edge = EvidenceEdge(
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
            weight=weight,
        )
        self._edges.append(edge)

    def forward_chain(
        self, evidence_ids: list[str]
    ) -> list[dict[str, Any]]:
        """
        Forward chaining: given evidence, infer potential TTPs.
        
        IF [Sigma match] AND [MITRE TTP] THEN [confidence += 0.3]
        """
        inferences = []
        context_nodes = [self._nodes[nid] for nid in evidence_ids if nid in self._nodes]

        for node in context_nodes:
            # Check Sigma rules
            for rule_id, rule in self._knowledge_base["sigma_rules"].items():
                logsource = rule.get("logsource", {})
                detection = rule.get("detection", {})

                # Simple matching: check if event properties match rule conditions
                match_score = self._match_sigma_rule(node.properties, logsource, detection)
                if match_score > 0.5:
                    inferences.append({
                        "rule_type": "sigma",
                        "rule_id": rule_id,
                        "title": rule.get("title", ""),
                        "confidence": match_score,
                        "description": f"Event matches Sigma rule: {rule.get('title', rule_id)}",
                    })

            # Check MITRE techniques
            for tech_id, tech in self._knowledge_base["mitre_techniques"].items():
                if tech.get("name", "").lower() in node.label.lower():
                    inferences.append({
                        "rule_type": "mitre",
                        "technique_id": tech_id,
                        "name": tech.get("name", ""),
                        "tactic": tech.get("tactic", ""),
                        "confidence": 0.7,
                        "description": f"Event associated with MITRE technique: {tech.get('name', tech_id)}",
                    })

        return inferences

    def backward_chain(
        self, technique_id: str
    ) -> list[dict[str, Any]]:
        """
        Backward chaining: given a TTP, find required evidence.
        """
        tech = self._knowledge_base["mitre_techniques"].get(technique_id)
        if not tech:
            return []

        required_evidence = []

        # Find correlated Sigma rules
        for rule_id, rule in self._knowledge_base["sigma_rules"].items():
            required_evidence.append({
                "evidence_type": "sigma_rule",
                "id": rule_id,
                "title": rule.get("title", ""),
                "relevance": 0.8,
            })

        # Find nodes in evidence graph related to this technique
        for node in self._nodes.values():
            if tech["name"].lower() in node.label.lower():
                required_evidence.append({
                    "evidence_type": "graph_node",
                    "id": node.node_id,
                    "label": node.label,
                    "relevance": 0.9,
                })

        return required_evidence

    def causal_reasoning(
        self, event_node_id: str, max_depth: int = 3
    ) -> list[dict[str, Any]]:
        """Perform causal reasoning to find root causes"""
        visited = set()
        causal_chain = []

        def traverse(node_id: str, depth: int):
            if depth > max_depth or node_id in visited:
                return
            visited.add(node_id)

            node = self._nodes.get(node_id)
            if not node:
                return

            causal_chain.append({
                "node_id": node_id,
                "label": node.label,
                "type": node.node_type,
                "depth": depth,
            })

            for edge in self._edges:
                if edge.source_id == node_id and edge.relationship == "causes":
                    traverse(edge.target_id, depth + 1)

        traverse(event_node_id, 0)
        return causal_chain

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of Knowledge Engine state"""
        return {
            "knowledge_base": {
                "mitre_techniques": len(self._knowledge_base["mitre_techniques"]),
                "capec_patterns": len(self._knowledge_base["capec_patterns"]),
                "cve_entries": len(self._knowledge_base["cve_entries"]),
                "sigma_rules": len(self._knowledge_base["sigma_rules"]),
                "yara_rules": len(self._knowledge_base["yara_rules"]),
            },
            "evidence_graph": {
                "total_nodes": len(self._nodes),
                "total_edges": len(self._edges),
                "node_types": dict(
                    (t, len(ids)) for t, ids in self._node_index.items()
                ),
            },
        }

    @staticmethod
    def _match_sigma_rule(
        properties: dict[str, Any],
        logsource: dict[str, Any],
        detection: dict[str, Any],
    ) -> float:
        """Match event properties against a Sigma rule condition"""
        if not properties or not detection:
            return 0.0

        matches = 0
        total = 0

        # Check logsource match
        for key, value in logsource.items():
            total += 1
            if properties.get(key) == value:
                matches += 1

        # Check detection conditions
        for key, condition in detection.items():
            if isinstance(condition, dict):
                for field, expected in condition.items():
                    total += 1
                    actual = properties.get(field)
                    if actual == expected:
                        matches += 1
                    elif isinstance(expected, str) and expected.startswith(">"):
                        try:
                            if float(actual) > float(expected[1:]):
                                matches += 1
                        except (ValueError, TypeError):
                            pass

        return matches / max(1, total)

