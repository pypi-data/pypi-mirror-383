"""
#exonware/xwnode/src/exonware/xwnode/edges/strategies/edge_edge_list.py

Edge List Edge Strategy Implementation

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
Generation Date: 11-Oct-2025
"""

from typing import Any, Iterator, Dict, List, Set, Optional
from ._base_edge import AEdgeStrategy
from ...defs import EdgeMode, EdgeTrait


class EdgeListStrategy(AEdgeStrategy):
    """
    Edge List - Simple list of (source, target) pairs.
    
    WHY this strategy:
    - Simplest possible graph representation
    - Universal file format (SNAP datasets, NetworkX, GraphML)
    - Minimal memory overhead - just edge tuples
    - Trivial serialization/deserialization
    
    WHY this implementation:
    - Python list of edge dicts for simplicity
    - Linear storage matches file format exactly
    - Node set tracking for vertex iteration
    - No indexing overhead - pure sequential storage
    
    Time Complexity:
    - Add Edge: O(1) - append to list
    - Has Edge: O(E) - linear scan
    - Get Neighbors: O(E) - scan all edges
    - Remove Edge: O(E) - linear search and remove
    - Iteration: O(E) - direct list iteration
    
    Space Complexity: O(E) - minimal overhead
    
    Trade-offs:
    - Advantage: Simplest format, minimal memory, fast I/O
    - Limitation: Slow for all queries except iteration
    - Compared to ADJ_LIST: Use only for storage/transport
    
    Best for:
    - Graph file I/O (reading/writing edge lists)
    - Data interchange (network datasets, graph databases)
    - Initial graph loading (convert to better format after)
    - Minimal memory scenarios
    - Streaming edge data collection
    
    Not recommended for:
    - Any graph algorithms - convert first
    - Production queries - too slow
    - Interactive applications - needs indexing
    
    Following eXonware Priorities:
    1. Security: Simple format reduces attack surface
    2. Usability: Trivial to understand and use
    3. Maintainability: Minimal code, no complex logic
    4. Performance: Fast sequential access, slow queries
    5. Extensibility: Easy to add filters, transformations
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        super().__init__(EdgeMode.EDGE_LIST, traits, **options)
        self._edges: List[Dict[str, Any]] = []
        self._nodes: Set[str] = set()
        self._edge_id_counter = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        return EdgeTrait.SPARSE | EdgeTrait.DIRECTED
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add edge to list."""
        edge_id = f"edge_{self._edge_id_counter}"
        self._edge_id_counter += 1
        
        edge_data = {
            'id': edge_id,
            'source': source,
            'target': target,
            'properties': properties.copy()
        }
        
        self._edges.append(edge_data)
        self._nodes.add(source)
        self._nodes.add(target)
        self._edge_count += 1
        
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove edge from list (O(n) operation)."""
        removed = False
        
        if edge_id:
            self._edges = [e for e in self._edges if e['id'] != edge_id]
            removed = True
        else:
            original_len = len(self._edges)
            self._edges = [e for e in self._edges 
                          if not (e['source'] == source and e['target'] == target)]
            removed = len(self._edges) < original_len
        
        if removed:
            self._edge_count = len(self._edges)
        
        return removed
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists."""
        return any(e['source'] == source and e['target'] == target for e in self._edges)
    
    def neighbors(self, node: str) -> Iterator[Any]:
        """Get neighbors of node (required by base class)."""
        return iter(self.get_neighbors(node, "outgoing"))
    
    def get_neighbors(self, node: str, direction: str = "outgoing") -> List[str]:
        """Get neighbors (O(m) where m = total edges)."""
        neighbors = set()
        
        for edge in self._edges:
            if direction == "outgoing" and edge['source'] == node:
                neighbors.add(edge['target'])
            elif direction == "incoming" and edge['target'] == node:
                neighbors.add(edge['source'])
            elif direction == "both":
                if edge['source'] == node:
                    neighbors.add(edge['target'])
                elif edge['target'] == node:
                    neighbors.add(edge['source'])
        
        return list(neighbors)
    
    def degree(self, node: str) -> int:
        """Get degree of node."""
        return len(self.get_neighbors(node, "both"))
    
    def edges(self) -> Iterator[tuple[Any, Any, Dict[str, Any]]]:
        """Iterator over edges."""
        for edge in self._edges:
            yield (edge['source'], edge['target'], edge['properties'])
    
    def vertices(self) -> Iterator[Any]:
        """Iterator over vertices."""
        return iter(self._nodes)
    
    def __len__(self) -> int:
        """Get number of edges."""
        return len(self._edges)
    
    def to_native(self) -> List[tuple[str, str]]:
        """Convert to simple edge list format."""
        return [(e['source'], e['target']) for e in self._edges]
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend info."""
        return {
            'strategy': 'Edge List',
            'description': 'Simple edge list format',
            'total_edges': len(self._edges),
            'total_nodes': len(self._nodes)
        }

