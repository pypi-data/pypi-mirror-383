#exonware\xwnode\strategies\impls\edge_weighted_graph.py
"""
Weighted Graph Edge Strategy Implementation

This module implements the WEIGHTED_GRAPH strategy for graphs with numerical
edge weights, optimized for network algorithms and shortest path computations.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Iterator
from ._base_edge import AEdgeStrategy
from ...defs import EdgeMode, EdgeTrait
from ...errors import XWNodeUnsupportedCapabilityError
import threading


class WeightedEdge:
    """Weighted edge with source, target, and weight."""
    
    def __init__(self, source: str, target: str, weight: float = 1.0, data: Any = None):
        self.source = source
        self.target = target
        self.weight = weight
        self.data = data
        self._hash = None
    
    def __hash__(self) -> int:
        """Cache hash for performance."""
        if self._hash is None:
            self._hash = hash((self.source, self.target, self.weight))
        return self._hash
    
    def __eq__(self, other) -> bool:
        """Structural equality."""
        if not isinstance(other, WeightedEdge):
            return False
        return (self.source == other.source and 
                self.target == other.target and
                self.weight == other.weight)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"WeightedEdge({self.source} -> {self.target}, weight={self.weight})"


class WeightedGraphStrategy(AEdgeStrategy):
    """
    Weighted graph edge strategy for graphs with numerical edge weights.
    
    WHY this strategy:
    - Real-world networks have weighted edges (distances, costs, capacities, probabilities)
    - Enables classic algorithms: Dijkstra, Bellman-Ford, Kruskal, Prim
    - Optimized for network optimization problems
    - First-class weight support (not retrofitted properties)
    
    WHY this implementation:
    - Adjacency list backbone for sparse weight storage
    - WeightedEdge class encapsulates edge with weight
    - Hash caching for performance in set operations
    - Thread-safe operations with optional locking
    
    Time Complexity:
    - Add Edge: O(1) - append to adjacency list
    - Has Edge: O(degree) - linear scan of neighbors
    - Get Weight: O(degree) - find edge then access weight
    - Shortest Path: O((V+E) log V) - Dijkstra with heap
    - Delete Edge: O(degree) - find and remove from list
    
    Space Complexity: O(V + E) - sparse storage
    
    Trade-offs:
    - Advantage: Natural weight handling, algorithm-ready
    - Limitation: Slower than plain adjacency list (weight objects)
    - Compared to ADJ_LIST: Use when weights drive decisions
    
    Best for:
    - Transportation networks (roads, flights with distances)
    - Network flow problems (capacity constraints)
    - Routing and pathfinding (GPS, logistics)
    - Cost optimization (supply chain, telecommunications)
    - Recommendation systems (similarity scores)
    
    Not recommended for:
    - Unweighted graphs - use plain ADJ_LIST
    - Simple connectivity checks - overhead unnecessary
    - Extremely large graphs - use CSR/CSC for better compression
    
    Following eXonware Priorities:
    1. Security: Weight validation prevents invalid values
    2. Usability: Natural API for weighted operations
    3. Maintainability: Clean WeightedEdge abstraction
    4. Performance: Optimized Dijkstra implementation
    5. Extensibility: Easy to add new weighted algorithms
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the weighted graph strategy."""
        super().__init__(EdgeMode.WEIGHTED_GRAPH, traits, **options)
        
        self.directed = options.get('directed', True)
        self.default_weight = options.get('default_weight', 1.0)
        self.weight_precision = options.get('weight_precision', 6)
        
        # Core weighted graph storage
        self._edges: Dict[Tuple[str, str], WeightedEdge] = {}
        self._adjacency: Dict[str, Dict[str, float]] = {}  # source -> {target: weight}
        self._reverse_adjacency: Dict[str, Dict[str, float]] = {}  # target -> {source: weight}
        self._edge_count = 0
        
        # Statistics
        self._total_edges_added = 0
        self._total_edges_removed = 0
        self._total_weight_updates = 0
        self._max_weight = 0.0
        self._min_weight = float('inf')
        
        # Thread safety
        self._lock = threading.RLock()
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the weighted graph strategy."""
        return (EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.SPARSE)
    
    def _normalize_weight(self, weight: float) -> float:
        """Normalize weight to specified precision."""
        return round(weight, self.weight_precision)
    
    def _update_weight_stats(self, weight: float) -> None:
        """Update weight statistics."""
        self._max_weight = max(self._max_weight, weight)
        self._min_weight = min(self._min_weight, weight)
    
    def _add_to_adjacency(self, source: str, target: str, weight: float) -> None:
        """Add edge to adjacency structure."""
        if source not in self._adjacency:
            self._adjacency[source] = {}
        self._adjacency[source][target] = weight
        
        if target not in self._reverse_adjacency:
            self._reverse_adjacency[target] = {}
        self._reverse_adjacency[target][source] = weight
    
    def _remove_from_adjacency(self, source: str, target: str) -> None:
        """Remove edge from adjacency structure."""
        if source in self._adjacency and target in self._adjacency[source]:
            del self._adjacency[source][target]
            if not self._adjacency[source]:
                del self._adjacency[source]
        
        if target in self._reverse_adjacency and source in self._reverse_adjacency[target]:
            del self._reverse_adjacency[target][source]
            if not self._reverse_adjacency[target]:
                del self._reverse_adjacency[target]
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, weight: float = None, data: Any = None, **properties) -> str:
        """
        Add a weighted edge between source and target.
        
        Root cause fixed: Method returned bool instead of edge_id string, violating
        strategy interface contract.
        
        Priority: Maintainability #3 - Consistent strategy interface
        
        Returns:
            Edge ID string
        """
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("Source and target must be strings")
        
        if weight is None:
            weight = properties.get('weight', self.default_weight)
        
        weight = self._normalize_weight(weight)
        
        with self._lock:
            edge_key = (source, target)
            edge_id = f"edge_{source}_{target}"
            
            # Check if edge already exists
            if edge_key in self._edges:
                # Update existing edge
                old_edge = self._edges[edge_key]
                old_edge.weight = weight
                old_edge.data = data
                self._total_weight_updates += 1
                self._update_weight_stats(weight)
                return edge_id
            
            # Create new edge
            edge = WeightedEdge(source, target, weight, data)
            self._edges[edge_key] = edge
            self._add_to_adjacency(source, target, weight)
            
            # Add reverse edge if undirected
            if not self.directed:
                reverse_key = (target, source)
                if reverse_key not in self._edges:
                    reverse_edge = WeightedEdge(target, source, weight, data)
                    self._edges[reverse_key] = reverse_edge
                    self._add_to_adjacency(target, source, weight)
            
            self._edge_count += 1
            self._total_edges_added += 1
            self._update_weight_stats(weight)
            return edge_id
    
    def get_edge(self, source: str, target: str) -> Optional[WeightedEdge]:
        """Get edge between source and target."""
        if not isinstance(source, str) or not isinstance(target, str):
            return None
        
        with self._lock:
            edge_key = (source, target)
            return self._edges.get(edge_key)
    
    def get_edge_weight(self, source: str, target: str) -> Optional[float]:
        """Get weight of edge between source and target."""
        edge = self.get_edge(source, target)
        return edge.weight if edge else None
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """
        Get edge data between source and target vertices.
        
        Root cause fixed: Missing method caused test failures.
        Returns dict with weight and properties for interface compliance.
        
        Priority: Usability #2 - Complete API implementation
        
        Returns:
            Dict with 'weight' and other edge properties, or None if edge doesn't exist
        """
        edge = self.get_edge(source, target)
        if edge is None:
            return None
        
        return {
            'weight': edge.weight,
            'data': edge.data
        }
    
    def set_edge_weight(self, source: str, target: str, weight: float) -> bool:
        """Set weight of edge between source and target."""
        if not isinstance(source, str) or not isinstance(target, str):
            return False
        
        weight = self._normalize_weight(weight)
        
        with self._lock:
            edge_key = (source, target)
            if edge_key in self._edges:
                self._edges[edge_key].weight = weight
                self._adjacency[source][target] = weight
                self._reverse_adjacency[target][source] = weight
                
                # Update reverse edge if undirected
                if not self.directed:
                    reverse_key = (target, source)
                    if reverse_key in self._edges:
                        self._edges[reverse_key].weight = weight
                        self._adjacency[target][source] = weight
                        self._reverse_adjacency[source][target] = weight
                
                self._total_weight_updates += 1
                self._update_weight_stats(weight)
                return True
            
            return False
    
    def delete_edge(self, source: str, target: str) -> bool:
        """Remove edge between source and target."""
        if not isinstance(source, str) or not isinstance(target, str):
            return False
        
        with self._lock:
            edge_key = (source, target)
            
            if edge_key in self._edges:
                del self._edges[edge_key]
                self._remove_from_adjacency(source, target)
                
                # Remove reverse edge if undirected
                if not self.directed:
                    reverse_key = (target, source)
                    if reverse_key in self._edges:
                        del self._edges[reverse_key]
                        self._remove_from_adjacency(target, source)
                
                self._edge_count -= 1
                self._total_edges_removed += 1
                return True
            
            return False
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        if not isinstance(source, str) or not isinstance(target, str):
            return False
        
        with self._lock:
            edge_key = (source, target)
            return edge_key in self._edges
    
    def get_edges_from(self, source: str) -> Iterator[WeightedEdge]:
        """Get all edges from source node."""
        if not isinstance(source, str):
            return
        
        with self._lock:
            if source in self._adjacency:
                for target, weight in self._adjacency[source].items():
                    edge_key = (source, target)
                    if edge_key in self._edges:
                        yield self._edges[edge_key]
    
    def get_edges_to(self, target: str) -> Iterator[WeightedEdge]:
        """Get all edges to target node."""
        if not isinstance(target, str):
            return
        
        with self._lock:
            if target in self._reverse_adjacency:
                for source, weight in self._reverse_adjacency[target].items():
                    edge_key = (source, target)
                    if edge_key in self._edges:
                        yield self._edges[edge_key]
    
    def get_neighbors(self, node: str) -> Iterator[str]:
        """Get all neighbors of node."""
        if not isinstance(node, str):
            return
        
        with self._lock:
            if node in self._adjacency:
                yield from self._adjacency[node].keys()
    
    def get_incoming_neighbors(self, node: str) -> Iterator[str]:
        """Get all incoming neighbors of node."""
        if not isinstance(node, str):
            return
        
        with self._lock:
            if node in self._reverse_adjacency:
                yield from self._reverse_adjacency[node].keys()
    
    def get_outgoing_neighbors(self, node: str) -> Iterator[str]:
        """Get all outgoing neighbors of node."""
        return self.get_neighbors(node)
    
    def get_edge_count(self) -> int:
        """Get total number of edges."""
        return self._edge_count
    
    def get_node_count(self) -> int:
        """Get total number of nodes."""
        with self._lock:
            nodes = set()
            for source, target in self._edges.keys():
                nodes.add(source)
                nodes.add(target)
            return len(nodes)
    
    def clear(self) -> None:
        """Clear all edges."""
        with self._lock:
            self._edges.clear()
            self._adjacency.clear()
            self._reverse_adjacency.clear()
            self._edge_count = 0
    
    # ============================================================================
    # WEIGHTED GRAPH SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_min_weight_edge(self) -> Optional[WeightedEdge]:
        """Get edge with minimum weight."""
        if not self._edges:
            return None
        
        with self._lock:
            min_edge = min(self._edges.values(), key=lambda e: e.weight)
            return min_edge
    
    def get_max_weight_edge(self) -> Optional[WeightedEdge]:
        """Get edge with maximum weight."""
        if not self._edges:
            return None
        
        with self._lock:
            max_edge = max(self._edges.values(), key=lambda e: e.weight)
            return max_edge
    
    def get_edges_by_weight_range(self, min_weight: float, max_weight: float) -> Iterator[WeightedEdge]:
        """Get all edges within weight range."""
        with self._lock:
            for edge in self._edges.values():
                if min_weight <= edge.weight <= max_weight:
                    yield edge
    
    def get_total_weight(self) -> float:
        """Get total weight of all edges."""
        with self._lock:
            return sum(edge.weight for edge in self._edges.values())
    
    def get_average_weight(self) -> float:
        """Get average weight of all edges."""
        if not self._edges:
            return 0.0
        
        return self.get_total_weight() / len(self._edges)
    
    def get_weight_distribution(self) -> Dict[str, int]:
        """Get distribution of edge weights."""
        with self._lock:
            distribution = {}
            for edge in self._edges.values():
                weight_str = str(edge.weight)
                distribution[weight_str] = distribution.get(weight_str, 0) + 1
            return distribution
    
    def get_heavy_edges(self, threshold: float) -> Iterator[WeightedEdge]:
        """Get all edges with weight above threshold."""
        with self._lock:
            for edge in self._edges.values():
                if edge.weight > threshold:
                    yield edge
    
    def get_light_edges(self, threshold: float) -> Iterator[WeightedEdge]:
        """Get all edges with weight below threshold."""
        with self._lock:
            for edge in self._edges.values():
                if edge.weight < threshold:
                    yield edge
    
    def normalize_weights(self, target_min: float = 0.0, target_max: float = 1.0) -> None:
        """Normalize all edge weights to target range."""
        if not self._edges:
            return
        
        with self._lock:
            # Find current min and max weights
            current_min = min(edge.weight for edge in self._edges.values())
            current_max = max(edge.weight for edge in self._edges.values())
            
            if current_min == current_max:
                # All weights are the same, set to target_min
                for edge in self._edges.values():
                    edge.weight = target_min
                    self._adjacency[edge.source][edge.target] = target_min
                    self._reverse_adjacency[edge.target][edge.source] = target_min
            else:
                # Normalize weights
                for edge in self._edges.values():
                    normalized_weight = target_min + (edge.weight - current_min) * (target_max - target_min) / (current_max - current_min)
                    edge.weight = self._normalize_weight(normalized_weight)
                    self._adjacency[edge.source][edge.target] = edge.weight
                    self._reverse_adjacency[edge.target][edge.source] = edge.weight
            
            # Update statistics
            self._min_weight = target_min
            self._max_weight = target_max
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._lock:
            return {
                'edge_count': self._edge_count,
                'node_count': self.get_node_count(),
                'total_edges_added': self._total_edges_added,
                'total_edges_removed': self._total_edges_removed,
                'total_weight_updates': self._total_weight_updates,
                'min_weight': self._min_weight if self._min_weight != float('inf') else 0.0,
                'max_weight': self._max_weight,
                'average_weight': self.get_average_weight(),
                'total_weight': self.get_total_weight(),
                'directed': self.directed,
                'default_weight': self.default_weight,
                'weight_precision': self.weight_precision,
                'strategy': 'WEIGHTED_GRAPH',
                'backend': 'Weighted graph with numerical edge weights',
                'traits': [trait.name for trait in EdgeTrait if self.has_trait(trait)]
            }
    
    # ============================================================================
    # REQUIRED INTERFACE METHODS
    # ============================================================================
    
    def __len__(self) -> int:
        """Get number of edges."""
        return self._edge_count
    
    def vertices(self) -> Set[str]:
        """Get all vertices."""
        vertices = set()
        for source in self._adjacency.keys():
            vertices.add(source)
        for target in self._reverse_adjacency.keys():
            vertices.add(target)
        return vertices
    
    def edges(self) -> Iterator[Tuple[str, str, float]]:
        """Iterate over all edges with weights."""
        for edge in self._edges.values():
            yield (edge.source, edge.target, edge.weight)
    
    def neighbors(self, node: str) -> List[str]:
        """Get neighbors of a node (delegates to get_neighbors)."""
        return self.get_neighbors(node)
    
    def get_degree(self, node: str) -> int:
        """
        Get degree of a node (number of edges).
        
        Root cause fixed: Method was calling itself recursively. Implemented proper logic.
        Priority: Maintainability #3 - Correct method implementation
        """
        if not isinstance(node, str):
            return 0
        
        with self._lock:
            if self.directed:
                out_degree = len(self._adjacency.get(node, {}))
                in_degree = len(self._reverse_adjacency.get(node, {}))
                return out_degree + in_degree
            else:
                return len(self._adjacency.get(node, {}))
    
    def degree(self, node: str) -> int:
        """Get degree of a node."""
        return self.get_degree(node)
    
    def shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find shortest path between source and target using Dijkstra's algorithm.
        
        Root cause fixed: Missing method for weighted graph algorithms.
        Also fixed: Don't require target to be in adjacency (it might only have incoming edges).
        Priority: Performance #4 - Efficient shortest path computation
        
        Returns:
            List of vertices in shortest path, or None if no path exists
        """
        if source not in self._adjacency:
            return None
        
        if source == target:
            return [source]
        
        import heapq
        
        with self._lock:
            # Dijkstra's algorithm
            distances = {source: 0.0}
            previous = {}
            pq = [(0.0, source)]
            visited = set()
            
            while pq:
                current_dist, current = heapq.heappop(pq)
                
                if current in visited:
                    continue
                visited.add(current)
                
                if current == target:
                    # Reconstruct path
                    path = []
                    while current is not None:
                        path.append(current)
                        current = previous.get(current)
                    return list(reversed(path))
                
                if current in self._adjacency:
                    for neighbor, weight in self._adjacency[current].items():
                        if neighbor not in visited:
                            new_dist = current_dist + weight
                            if neighbor not in distances or new_dist < distances[neighbor]:
                                distances[neighbor] = new_dist
                                previous[neighbor] = current
                                heapq.heappush(pq, (new_dist, neighbor))
            
            return None
    
    def remove_edge(self, from_node: str, to_node: str) -> bool:
        """Remove an edge (delegates to delete_edge)."""
        return self.delete_edge(from_node, to_node)