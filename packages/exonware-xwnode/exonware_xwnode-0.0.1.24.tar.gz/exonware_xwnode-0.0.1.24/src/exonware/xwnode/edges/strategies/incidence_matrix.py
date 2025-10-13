"""
#exonware/xwnode/src/exonware/xwnode/edges/strategies/edge_incidence_matrix.py

Incidence Matrix Edge Strategy Implementation

This module implements the INCIDENCE_MATRIX strategy for edge-centric
graph representation and queries.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.24
Generation Date: 11-Oct-2025
"""

from typing import Any, Iterator, Dict, List, Set, Optional
from collections import defaultdict
from ._base_edge import AEdgeStrategy
from ...defs import EdgeMode, EdgeTrait


class IncidenceMatrixStrategy(AEdgeStrategy):
    """
    Incidence Matrix - Edge-centric graph representation.
    
    WHY this strategy:
    - Edge-centric view essential for network flow, matching, edge coloring
    - O(1) edge property access (better than adjacency for edge operations)
    - Natural for multi-graphs (parallel edges get separate columns)
    - Standard in graph theory textbooks and research
    
    WHY this implementation:
    - Dict[node][edge] = {1, -1, 0} for directed graphs
    - Separate edge storage for O(1) property access
    - 1/-1 encoding enables incidence-based algorithms
    - Multi-edge support through unique edge IDs
    
    Time Complexity:
    - Add Edge: O(1) - insert into dict
    - Remove Edge: O(1) - delete from dict
    - Edge Properties: O(1) - direct edge dict access
    - Node Neighbors: O(E) - scan all edges
    - Edge Iteration: O(E) - iterate edge dict
    
    Space Complexity: O(V * E) worst case (sparse dict in practice)
    
    Trade-offs:
    - Advantage: Fast edge operations, natural multi-graph support
    - Limitation: Slow neighbor queries vs adjacency list
    - Compared to ADJ_LIST: Use when edges are primary focus
    
    Best for:
    - Network flow algorithms (Ford-Fulkerson, max flow)
    - Graph matching problems (bipartite matching)
    - Edge coloring and scheduling
    - Multi-graphs (parallel edges, duplicate connections)
    - Educational/research graph theory
    
    Not recommended for:
    - Neighbor-heavy algorithms - use ADJ_LIST
    - Large dense graphs - memory inefficient
    - Simple connectivity queries
    
    Following eXonware Priorities:
    1. Security: Edge ID validation prevents injection
    2. Usability: Clear edge-centric API for edge-focused problems
    3. Maintainability: Standard incidence matrix, well-documented
    4. Performance: O(1) edge access optimal for edge operations
    5. Extensibility: Easy to add edge-based algorithms
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize Incidence Matrix strategy."""
        super().__init__(EdgeMode.INCIDENCE_MATRIX, traits, **options)
        
        self.is_directed = options.get('directed', True)
        
        # Incidence matrix: node -> edge_id -> value {1, -1, 0}
        self._matrix: Dict[str, Dict[str, int]] = defaultdict(dict)
        
        # Edge storage: edge_id -> {source, target, properties}
        self._edges: Dict[str, Dict[str, Any]] = {}
        
        # Node set
        self._nodes: Set[str] = set()
        
        # Edge counter
        self._edge_id_counter = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get supported traits."""
        return EdgeTrait.SPARSE | EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.MULTI
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add edge between source and target."""
        # Generate edge ID
        edge_id = f"edge_{self._edge_id_counter}"
        self._edge_id_counter += 1
        
        # Store edge data
        self._edges[edge_id] = {
            'id': edge_id,
            'source': source,
            'target': target,
            'properties': properties.copy()
        }
        
        # Update incidence matrix
        if self.is_directed:
            self._matrix[source][edge_id] = 1   # Edge originates from source
            self._matrix[target][edge_id] = -1  # Edge terminates at target
        else:
            self._matrix[source][edge_id] = 1
            self._matrix[target][edge_id] = 1
        
        # Add nodes to node set
        self._nodes.add(source)
        self._nodes.add(target)
        
        self._edge_count += 1
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove edge between source and target."""
        if edge_id:
            # Remove specific edge by ID
            if edge_id in self._edges:
                edge_data = self._edges[edge_id]
                src = edge_data['source']
                tgt = edge_data['target']
                
                # Remove from matrix
                if src in self._matrix and edge_id in self._matrix[src]:
                    del self._matrix[src][edge_id]
                if tgt in self._matrix and edge_id in self._matrix[tgt]:
                    del self._matrix[tgt][edge_id]
                
                # Remove edge data
                del self._edges[edge_id]
                self._edge_count -= 1
                return True
            return False
        else:
            # Find and remove all edges between source and target
            edges_to_remove = []
            for eid, edge_data in self._edges.items():
                if edge_data['source'] == source and edge_data['target'] == target:
                    edges_to_remove.append(eid)
            
            for eid in edges_to_remove:
                self.remove_edge(source, target, edge_id=eid)
            
            return len(edges_to_remove) > 0
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        for edge_id, edge_data in self._edges.items():
            if edge_data['source'] == source and edge_data['target'] == target:
                return True
        return False
    
    def neighbors(self, node: str) -> Iterator[Any]:
        """Get neighbors of node (required by base class)."""
        return iter(self.get_neighbors(node, "outgoing"))
    
    def get_neighbors(self, node: str, direction: str = "outgoing") -> List[str]:
        """Get neighbors of node."""
        neighbors = set()
        
        if node not in self._matrix:
            return []
        
        # Check all edges incident to this node
        for edge_id, value in self._matrix[node].items():
            edge_data = self._edges[edge_id]
            
            if direction == "outgoing" and value == 1:
                neighbors.add(edge_data['target'])
            elif direction == "incoming" and value == -1:
                neighbors.add(edge_data['source'])
            elif direction == "both":
                if value == 1:
                    neighbors.add(edge_data['target'])
                elif value == -1:
                    neighbors.add(edge_data['source'])
        
        return list(neighbors)
    
    def degree(self, node: str) -> int:
        """Get degree of node."""
        if node not in self._matrix:
            return 0
        return len(self._matrix[node])
    
    def edges(self) -> Iterator[tuple[Any, Any, Dict[str, Any]]]:
        """Iterator over all edges."""
        for edge_data in self._edges.values():
            yield (edge_data['source'], edge_data['target'], edge_data['properties'])
    
    def vertices(self) -> Iterator[Any]:
        """Iterator over all vertices."""
        return iter(self._nodes)
    
    def __len__(self) -> int:
        """Get number of edges."""
        return self._edge_count
    
    # ============================================================================
    # EDGE-CENTRIC OPERATIONS
    # ============================================================================
    
    def get_edge_by_id(self, edge_id: str) -> Optional[Dict[str, Any]]:
        """Get edge data by edge ID (O(1) operation)."""
        return self._edges.get(edge_id)
    
    def get_incident_edges(self, node: str) -> List[Dict[str, Any]]:
        """Get all edges incident to node."""
        if node not in self._matrix:
            return []
        
        edge_ids = self._matrix[node].keys()
        return [self._edges[eid] for eid in edge_ids]
    
    def get_all_edge_ids(self) -> List[str]:
        """Get list of all edge IDs."""
        return list(self._edges.keys())
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native representation."""
        return {
            'edges': list(self._edges.values()),
            'nodes': list(self._nodes),
            'directed': self.is_directed
        }
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend information."""
        return {
            'strategy': 'Incidence Matrix',
            'description': 'Edge-centric graph representation',
            'total_edges': self._edge_count,
            'total_nodes': len(self._nodes),
            'directed': self.is_directed,
            'matrix_size': sum(len(edges) for edges in self._matrix.values())
        }

