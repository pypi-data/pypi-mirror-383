"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/adjacency_list.py

Adjacency List Strategy Implementation

Production-grade graph representation using adjacency lists.

Best Practices Implemented:
- Dictionary of lists for O(1) neighbor access
- Support for directed and undirected graphs
- Weighted edges with efficient storage
- Industry-standard graph algorithms (DFS, BFS, topological sort)
- Proper graph semantics following CLRS and NetworkX patterns

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.24
Generation Date: October 12, 2025
"""

from typing import Any, Iterator, List, Optional, Dict, Set, Tuple, Callable
from collections import defaultdict, deque
from .base import ANodeGraphStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class AdjacencyListStrategy(ANodeGraphStrategy):
    """
    Production-grade Adjacency List graph strategy.
    
    Optimized for:
    - Social networks (followers, friends, connections)
    - Web graphs (links, citations, dependencies)
    - Routing algorithms (Dijkstra, A*, Bellman-Ford)
    - Dependency graphs (build systems, package managers)
    - Recommendation systems (user-item graphs)
    - Network analysis (PageRank, community detection)
    
    Format: Dictionary of Lists
    - Best for: Sparse graphs, dynamic graphs
    - Storage: node -> list of (neighbor, weight) tuples
    - Space: O(V + E) where V=vertices, E=edges
    - Operations: O(degree) neighbor queries
    
    Performance:
    - Add vertex: O(1)
    - Add edge: O(1)
    - Remove edge: O(degree)
    - Get neighbors: O(1) to O(degree)
    - DFS: O(V + E)
    - BFS: O(V + E)
    - Topological sort: O(V + E)
    
    Security:
    - Vertex existence validation
    - Cycle detection for safety
    - Safe edge weight handling
    
    Follows eXonware Priorities:
    1. Security: Input validation, safe traversal
    2. Usability: Standard graph operations interface
    3. Maintainability: Clean adjacency list implementation
    4. Performance: O(V + E) algorithms, O(1) neighbor access
    5. Extensibility: Easy to add custom graph algorithms
    """
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.GRAPH
    
    __slots__ = ('_adj_list', '_nodes', '_is_directed', '_edge_count')
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize an empty adjacency list.
        
        Args:
            traits: Additional node traits
            **options:
                is_directed: True for directed graph, False for undirected
                initial_vertices: Optional list of initial vertices
                initial_edges: Optional list of (from, to, weight) tuples
        """
        super().__init__(
            NodeMode.ADJACENCY_LIST,
            traits | NodeTrait.GRAPH | NodeTrait.SPARSE | NodeTrait.FAST_NEIGHBORS,
            **options
        )
        
        self._is_directed: bool = options.get('is_directed', True)
        self._adj_list: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self._nodes: Dict[str, Any] = {}
        self._edge_count = 0
        
        # Initialize vertices if provided
        for vertex in options.get('initial_vertices', []):
            self.add_vertex(vertex)
        
        # Initialize edges if provided
        for edge in options.get('initial_edges', []):
            if len(edge) == 2:
                self.add_edge(edge[0], edge[1])
            elif len(edge) == 3:
                self.add_edge(edge[0], edge[1], edge[2])
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the adjacency list strategy."""
        return NodeTrait.GRAPH | NodeTrait.SPARSE | NodeTrait.FAST_NEIGHBORS
    
    # ============================================================================
    # CORE GRAPH OPERATIONS (Industry Standard)
    # ============================================================================
    
    def add_vertex(self, vertex: str, data: Any = None) -> None:
        """
        Add a vertex to the graph.
        
        Time: O(1)
        Space: O(1)
        """
        if vertex not in self._nodes:
            self._nodes[vertex] = data
            if vertex not in self._adj_list:
                self._adj_list[vertex] = []
    
    def add_edge(self, from_vertex: str, to_vertex: str, weight: float = 1.0) -> None:
        """
        Add an edge between two vertices.
        
        Time: O(1) amortized
        Space: O(1)
        
        Note: Automatically creates vertices if they don't exist
        """
        # Ensure vertices exist
        self.add_vertex(from_vertex)
        self.add_vertex(to_vertex)
        
        # Check if edge already exists (avoid duplicates)
        neighbors = self._adj_list[from_vertex]
        for i, (neighbor, _) in enumerate(neighbors):
            if neighbor == to_vertex:
                # Update existing edge weight
                neighbors[i] = (to_vertex, weight)
                return
        
        # Add new edge
        neighbors.append((to_vertex, weight))
        self._edge_count += 1
        
        # For undirected graphs, add reverse edge
        if not self._is_directed:
            reverse_neighbors = self._adj_list[to_vertex]
            # Check if reverse edge exists
            found = False
            for i, (neighbor, _) in enumerate(reverse_neighbors):
                if neighbor == from_vertex:
                    reverse_neighbors[i] = (from_vertex, weight)
                    found = True
                    break
            if not found:
                reverse_neighbors.append((from_vertex, weight))
    
    def remove_edge(self, from_vertex: str, to_vertex: str) -> bool:
        """
        Remove an edge between two vertices.
        
        Time: O(degree(from_vertex))
        
        Returns:
            True if edge was removed, False if not found
        """
        if from_vertex not in self._adj_list:
            return False
        
        neighbors = self._adj_list[from_vertex]
        for i, (neighbor, _) in enumerate(neighbors):
            if neighbor == to_vertex:
                neighbors.pop(i)
                self._edge_count -= 1
                
                # For undirected graphs, remove reverse edge
                if not self._is_directed:
                    reverse_neighbors = self._adj_list.get(to_vertex, [])
                    for j, (n, _) in enumerate(reverse_neighbors):
                        if n == from_vertex:
                            reverse_neighbors.pop(j)
                            break
                
                return True
        
        return False
    
    def remove_vertex(self, vertex: str) -> bool:
        """
        Remove a vertex and all its edges.
        
        Time: O(V + E) worst case
        
        Returns:
            True if vertex was removed, False if not found
        """
        if vertex not in self._nodes:
            return False
        
        # Remove vertex data
        del self._nodes[vertex]
        
        # Count edges to be removed
        edges_removed = len(self._adj_list.get(vertex, []))
        
        # Remove all edges TO this vertex
        for node in list(self._adj_list.keys()):
            if node == vertex:
                continue
            self._adj_list[node] = [
                (neighbor, weight) 
                for neighbor, weight in self._adj_list[node] 
                if neighbor != vertex
            ]
        
        # Remove vertex's adjacency list
        if vertex in self._adj_list:
            del self._adj_list[vertex]
        
        self._edge_count -= edges_removed
        
        return True
    
    def get_neighbors(self, vertex: str) -> List[str]:
        """
        Get all neighbors of a vertex.
        
        Time: O(1) to O(degree)
        
        Returns:
            List of neighbor vertices
        """
        if vertex not in self._adj_list:
            return []
        return [neighbor for neighbor, _ in self._adj_list[vertex]]
    
    def get_neighbors_with_weights(self, vertex: str) -> List[Tuple[str, float]]:
        """
        Get all neighbors with edge weights.
        
        Time: O(degree)
        
        Returns:
            List of (neighbor, weight) tuples
        """
        if vertex not in self._adj_list:
            return []
        return self._adj_list[vertex].copy()
    
    def has_edge(self, from_vertex: str, to_vertex: str) -> bool:
        """
        Check if an edge exists.
        
        Time: O(degree(from_vertex))
        """
        if from_vertex not in self._adj_list:
            return False
        
        for neighbor, _ in self._adj_list[from_vertex]:
            if neighbor == to_vertex:
                return True
        return False
    
    def get_edge_weight(self, from_vertex: str, to_vertex: str) -> Optional[float]:
        """
        Get the weight of an edge.
        
        Time: O(degree(from_vertex))
        
        Returns:
            Edge weight or None if edge doesn't exist
        """
        if from_vertex not in self._adj_list:
            return None
        
        for neighbor, weight in self._adj_list[from_vertex]:
            if neighbor == to_vertex:
                return weight
        
        return None
    
    # ============================================================================
    # GRAPH ANALYSIS METHODS
    # ============================================================================
    
    def degree(self, vertex: str) -> int:
        """Get the degree of a vertex (out-degree for directed graphs)."""
        if vertex not in self._adj_list:
            return 0
        return len(self._adj_list[vertex])
    
    def in_degree(self, vertex: str) -> int:
        """
        Get the in-degree of a vertex.
        
        Time: O(E) - must scan all edges
        """
        if vertex not in self._nodes:
            return 0
        
        count = 0
        for neighbors in self._adj_list.values():
            for neighbor, _ in neighbors:
                if neighbor == vertex:
                    count += 1
        return count
    
    def out_degree(self, vertex: str) -> int:
        """Get the out-degree of a vertex (same as degree for directed graphs)."""
        return self.degree(vertex)
    
    # ============================================================================
    # GRAPH TRAVERSAL ALGORITHMS (Production-Grade)
    # ============================================================================
    
    def dfs(self, start: str, visit_fn: Optional[Callable[[str], None]] = None) -> List[str]:
        """
        Depth-First Search from start vertex.
        
        Time: O(V + E)
        Space: O(V) for recursion stack
        
        Args:
            start: Starting vertex
            visit_fn: Optional callback for each visited vertex
            
        Returns:
            List of visited vertices in DFS order
        """
        if start not in self._nodes:
            return []
        
        visited = set()
        result = []
        
        def dfs_recursive(vertex: str) -> None:
            visited.add(vertex)
            result.append(vertex)
            if visit_fn:
                visit_fn(vertex)
            
            for neighbor, _ in self._adj_list.get(vertex, []):
                if neighbor not in visited:
                    dfs_recursive(neighbor)
        
        dfs_recursive(start)
        return result
    
    def bfs(self, start: str, visit_fn: Optional[Callable[[str], None]] = None) -> List[str]:
        """
        Breadth-First Search from start vertex.
        
        Time: O(V + E)
        Space: O(V) for queue
        
        Args:
            start: Starting vertex
            visit_fn: Optional callback for each visited vertex
            
        Returns:
            List of visited vertices in BFS order
        """
        if start not in self._nodes:
            return []
        
        visited = set([start])
        result = [start]
        queue = deque([start])  # Use deque for O(1) operations
        
        if visit_fn:
            visit_fn(start)
        
        while queue:
            vertex = queue.popleft()  # O(1) with deque
            
            for neighbor, _ in self._adj_list.get(vertex, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    result.append(neighbor)
                    queue.append(neighbor)
                    if visit_fn:
                        visit_fn(neighbor)
        
        return result
    
    def find_path(self, start: str, end: str) -> List[str]:
        """
        Find path between two vertices using BFS.
        
        Time: O(V + E)
        Space: O(V)
        
        Returns:
            List representing path from start to end, or empty list if no path
        """
        if start not in self._nodes or end not in self._nodes:
            return []
        
        if start == end:
            return [start]
        
        visited = set([start])
        queue = deque([(start, [start])])
        
        while queue:
            vertex, path = queue.popleft()
            
            for neighbor, _ in self._adj_list.get(vertex, []):
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No path found
    
    def has_cycle(self) -> bool:
        """
        Check if the graph contains a cycle.
        
        Time: O(V + E)
        Space: O(V)
        
        Returns:
            True if graph has a cycle, False otherwise
        """
        if not self._is_directed:
            # Undirected graph cycle detection
            visited = set()
            
            def has_cycle_undirected(vertex: str, parent: Optional[str]) -> bool:
                visited.add(vertex)
                
                for neighbor, _ in self._adj_list.get(vertex, []):
                    if neighbor not in visited:
                        if has_cycle_undirected(neighbor, vertex):
                            return True
                    elif neighbor != parent:
                        return True
                
                return False
            
            for vertex in self._nodes:
                if vertex not in visited:
                    if has_cycle_undirected(vertex, None):
                        return True
            
            return False
        else:
            # Directed graph cycle detection (using DFS with colors)
            WHITE, GRAY, BLACK = 0, 1, 2
            color = {v: WHITE for v in self._nodes}
            
            def has_cycle_directed(vertex: str) -> bool:
                color[vertex] = GRAY
                
                for neighbor, _ in self._adj_list.get(vertex, []):
                    if color[neighbor] == GRAY:  # Back edge found
                        return True
                    if color[neighbor] == WHITE:
                        if has_cycle_directed(neighbor):
                            return True
                
                color[vertex] = BLACK
                return False
            
            for vertex in self._nodes:
                if color[vertex] == WHITE:
                    if has_cycle_directed(vertex):
                        return True
            
            return False
    
    def topological_sort(self) -> Optional[List[str]]:
        """
        Perform topological sort on the graph.
        
        Time: O(V + E)
        Space: O(V)
        
        Returns:
            List of vertices in topological order, or None if graph has cycle
            
        Note: Only works on directed acyclic graphs (DAGs)
        """
        if not self._is_directed:
            return None  # Topological sort only for directed graphs
        
        if self.has_cycle():
            return None  # Cannot topologically sort cyclic graphs
        
        visited = set()
        stack = []
        
        def dfs_topological(vertex: str) -> None:
            visited.add(vertex)
            
            for neighbor, _ in self._adj_list.get(vertex, []):
                if neighbor not in visited:
                    dfs_topological(neighbor)
            
            stack.append(vertex)
        
        for vertex in self._nodes:
            if vertex not in visited:
                dfs_topological(vertex)
        
        return list(reversed(stack))
    
    def get_connected_components(self) -> List[Set[str]]:
        """
        Get all connected components in the graph.
        
        Time: O(V + E)
        Space: O(V)
        
        Returns:
            List of sets, each containing vertices in a connected component
        """
        visited = set()
        components = []
        
        for start_vertex in self._nodes:
            if start_vertex not in visited:
                # BFS to find component
                component = set()
                queue = deque([start_vertex])
                visited.add(start_vertex)
                
                while queue:
                    vertex = queue.popleft()
                    component.add(vertex)
                    
                    for neighbor, _ in self._adj_list.get(vertex, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                    
                    # For undirected graphs, also check incoming edges
                    if not self._is_directed:
                        for other_vertex in self._nodes:
                            if other_vertex not in visited:
                                for n, _ in self._adj_list.get(other_vertex, []):
                                    if n == vertex:
                                        visited.add(other_vertex)
                                        queue.append(other_vertex)
                                        break
                
                components.append(component)
        
        return components
    
    def is_connected(self, from_vertex: str, to_vertex: str) -> bool:
        """
        Check if there's a path between two vertices.
        
        Time: O(V + E)
        
        Returns:
            True if vertices are connected, False otherwise
        """
        return len(self.find_path(from_vertex, to_vertex)) > 0
    
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (from ANodeStrategy)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store vertex with data."""
        self.add_vertex(str(key), value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get vertex data."""
        return self._nodes.get(str(key), default)
    
    def has(self, key: Any) -> bool:
        """Check if vertex exists."""
        return str(key) in self._nodes
    
    def delete(self, key: Any) -> bool:
        """Delete a vertex and all its edges."""
        return self.remove_vertex(str(key))
    
    def keys(self) -> Iterator[Any]:
        """Get all vertex IDs."""
        return iter(self._nodes.keys())
    
    def values(self) -> Iterator[Any]:
        """Get all vertex data."""
        return iter(self._nodes.values())
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get all vertices as (id, data) pairs."""
        return iter(self._nodes.items())
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def size(self) -> int:
        """Get the number of vertices."""
        return len(self._nodes)
    
    def is_empty(self) -> bool:
        """Check if graph has no vertices."""
        return len(self._nodes) == 0
    
    def clear(self) -> None:
        """Clear all vertices and edges."""
        self._nodes.clear()
        self._adj_list.clear()
        self._edge_count = 0
    
    def vertex_count(self) -> int:
        """Get the number of vertices."""
        return len(self._nodes)
    
    def edge_count(self) -> int:
        """Get the number of edges."""
        return self._edge_count
    
    def vertices(self) -> List[str]:
        """Get all vertices."""
        return list(self._nodes.keys())
    
    def edges(self) -> List[Tuple[str, str, float]]:
        """Get all edges as (from, to, weight) tuples."""
        result = []
        for from_vertex, neighbors in self._adj_list.items():
            for to_vertex, weight in neighbors:
                result.append((from_vertex, to_vertex, weight))
        return result
    
    def to_native(self) -> Dict[str, Any]:
        """Convert graph to native dictionary format."""
        return {
            'vertices': self._nodes,
            'edges': {
                vertex: [(neighbor, weight) for neighbor, weight in neighbors]
                for vertex, neighbors in self._adj_list.items()
                if neighbors
            },
            'is_directed': self._is_directed,
            'vertex_count': self.vertex_count(),
            'edge_count': self.edge_count()
        }
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load graph from native dictionary format."""
        self._nodes.clear()
        self._adj_list.clear()
        self._edge_count = 0
        
        # Load vertices
        for vertex, vertex_data in data.get('vertices', {}).items():
            self._nodes[vertex] = vertex_data
        
        # Load edges
        self._is_directed = data.get('is_directed', True)
        for vertex, neighbors in data.get('edges', {}).items():
            for neighbor, weight in neighbors:
                self.add_edge(vertex, neighbor, weight)
    
    
    # ============================================================================
    # PYTHON SPECIAL METHODS
    # ============================================================================
    
    def __len__(self) -> int:
        """Return the number of vertices."""
        return len(self._nodes)
    
    def __bool__(self) -> bool:
        """Return True if graph has vertices."""
        return bool(self._nodes)
    
    def __contains__(self, vertex: str) -> bool:
        """Check if vertex exists in graph."""
        return vertex in self._nodes
    
    def __iter__(self) -> Iterator[str]:
        """Iterate through all vertices."""
        return iter(self._nodes.keys())
    
    def __repr__(self) -> str:
        """Professional string representation."""
        graph_type = "directed" if self._is_directed else "undirected"
        return f"AdjacencyListStrategy(vertices={self.vertex_count()}, edges={self.edge_count()}, {graph_type})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Graph[V={self.vertex_count()}, E={self.edge_count()}]"
    
    # ============================================================================
    # PERFORMANCE METADATA
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'ADJACENCY_LIST',
            'backend': 'dict of lists (defaultdict)',
            'graph_type': 'directed' if self._is_directed else 'undirected',
            'complexity': {
                'add_vertex': 'O(1)',
                'add_edge': 'O(1)',
                'remove_vertex': 'O(V + E)',
                'remove_edge': 'O(degree)',
                'get_neighbors': 'O(1)',
                'has_edge': 'O(degree)',
                'dfs': 'O(V + E)',
                'bfs': 'O(V + E)',
                'space': 'O(V + E)'
            },
            'best_for': 'sparse graphs, dynamic graphs, neighbor queries',
            'thread_safe': False
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        avg_degree = self.edge_count() / self.vertex_count() if self.vertex_count() > 0 else 0
        max_edges = self.vertex_count() * (self.vertex_count() - 1)
        if not self._is_directed:
            max_edges //= 2
        
        sparsity = 1 - (self.edge_count() / max_edges) if max_edges > 0 else 1.0
        
        return {
            'vertices': self.vertex_count(),
            'edges': self.edge_count(),
            'avg_degree': f"{avg_degree:.2f}",
            'sparsity': f"{sparsity:.2%}",
            'is_directed': self._is_directed,
            'memory_usage': f"{(self.vertex_count() * 8 + self.edge_count() * 16)} bytes (estimated)"
        }
