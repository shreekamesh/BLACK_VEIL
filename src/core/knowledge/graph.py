"""
Knowledge Graph - Living Attack Memory Graph
BLACK VEIL - Attack memory with entity correlation

Expands attack memory to correlate:
User → Device → Credential → IP → Application → Alert → Risk → Trust
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """
    Security Knowledge Graph that correlates entities, events,
    and relationships across the entire security domain.
    """

    def __init__(self):
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Dict[str, Any]] = []
        logger.info("KnowledgeGraph initialized")

    def add_entity(self, entity_type: str, entity_id: str,
                   properties: Optional[Dict] = None) -> str:
        """Add an entity node to the graph"""
        node_id = f"{entity_type}:{entity_id}"
        self._nodes[node_id] = {
            'node_id': node_id,
            'type': entity_type,
            'entity_id': entity_id,
            'properties': properties or {},
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        return node_id

    def add_relationship(self, source: str, target: str,
                         relationship: str, properties: Optional[Dict] = None):
        """Add a relationship edge between two nodes"""
        edge = {
            'edge_id': str(uuid.uuid4())[:8],
            'source': source,
            'target': target,
            'relationship': relationship,
            'properties': properties or {},
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        self._edges.append(edge)

    def query(self, node_type: Optional[str] = None,
              relationship: Optional[str] = None) -> List[Dict]:
        """Query the knowledge graph"""
        results = []
        for nid, node in self._nodes.items():
            if node_type and node['type'] != node_type:
                continue

            relationships = []
            for edge in self._edges:
                if edge['source'] == nid or edge['target'] == nid:
                    if relationship and edge['relationship'] != relationship:
                        continue
                    relationships.append(edge)

            results.append({'node': node, 'relationships': relationships})

        return results

    def get_state_summary(self) -> Dict[str, Any]:
        return {
            'total_nodes': len(self._nodes),
            'total_edges': len(self._edges),
            'node_types': list(set(n['type'] for n in self._nodes.values())),
        }

