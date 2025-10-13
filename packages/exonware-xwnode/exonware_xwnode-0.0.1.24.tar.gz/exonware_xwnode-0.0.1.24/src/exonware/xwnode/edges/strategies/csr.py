"""
Compressed Sparse Row (CSR) Edge Strategy Implementation

This module implements the CSR strategy for memory-efficient sparse graph
representation with fast row-wise operations.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple, Union
import bisect
from ._base_edge import AEdgeStrategy
from ...defs import EdgeMode, EdgeTrait


class CSRStrategy(AEdgeStrategy):
    """
    Compressed Sparse Row (CSR) edge strategy for memory-efficient sparse graphs.
    
    WHY this strategy:
    - Industry-standard format for sparse matrix operations (NumPy/SciPy compatible)
    - 3-10x memory reduction vs adjacency list for large graphs  
    - Cache-friendly contiguous storage for matrix operations
    - Optimal for read-heavy workloads (ML, graph algorithms)
    
    WHY this implementation:
    - Three-array format (row_ptr, col_indices, values) standard in HPC
    - Binary search in sorted columns for O(log degree) lookups
    - Build cache for batched edge additions before compression
    - Lazy rebuild minimizes compression overhead
    
    Time Complexity:
    - Add Edge: O(1) amortized (cached), O(E) worst case (rebuild)
    - Has Edge: O(log degree) - binary search in row
    - Get Neighbors (out): O(degree) - contiguous row access
    - Get Neighbors (in): O(E) - must scan all edges
    - Delete Edge: O(E) - requires rebuild
    
    Space Complexity: O(V + E) - three arrays totaling 2E + V elements
    
    Trade-offs:
    - Advantage: Minimal memory, fast SpMV operations, cache-friendly
    - Limitation: Expensive modifications (rebuilds required)
    - Compared to ADJ_LIST: Better for static graphs, ML pipelines
    
    Best for:
    - Machine learning (sparse feature matrices, embeddings)
    - PageRank and similar iterative algorithms  
    - Read-heavy analytics workloads
    - Interop with NumPy/SciPy/scikit-learn
    
    Not recommended for:
    - Frequently changing graphs - use DYNAMIC_ADJ_LIST
    - Incoming neighbor queries - use CSC or bidirectional
    - Small graphs (<1000 vertices) - overhead not worth it
    
    Following eXonware Priorities:
    1. Security: Array bounds validation prevents buffer overflows
    2. Usability: Standard format familiar to ML/scientific community
    3. Maintainability: Well-documented CSR format, industry standard
    4. Performance: Optimal for SpMV, matrix operations, large graphs
    5. Extensibility: Compatible with numerical libraries, easy to extend
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the CSR strategy."""
        super().__init__(EdgeMode.CSR, traits, **options)
        
        self.is_directed = options.get('directed', True)
        self.allow_self_loops = options.get('self_loops', True)
        
        # CSR storage format
        self._row_ptr: List[int] = [0]  # Pointers to start of each row
        self._col_indices: List[int] = []  # Column indices of non-zero elements
        self._values: List[Dict[str, Any]] = []  # Edge data for each non-zero element
        
        # Vertex management
        self._vertex_to_index: Dict[str, int] = {}
        self._index_to_vertex: Dict[int, str] = {}
        self._vertex_count = 0
        self._edge_count = 0
        self._edge_id_counter = 0
        
        # Build cache
        self._needs_rebuild = False
        self._build_cache: List[Tuple[str, str, Dict[str, Any]]] = []
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the CSR strategy."""
        return (EdgeTrait.SPARSE | EdgeTrait.COMPRESSED | EdgeTrait.CACHE_FRIENDLY | EdgeTrait.COLUMNAR)
    
    # ============================================================================
    # VERTEX MANAGEMENT
    # ============================================================================
    
    def _get_vertex_index(self, vertex: str) -> int:
        """Get or create index for vertex."""
        if vertex in self._vertex_to_index:
            return self._vertex_to_index[vertex]
        
        # Add new vertex
        index = self._vertex_count
        self._vertex_to_index[vertex] = index
        self._index_to_vertex[index] = vertex
        self._vertex_count += 1
        self._needs_rebuild = True
        
        return index
    
    def _rebuild_csr(self) -> None:
        """Rebuild CSR format from edge cache."""
        if not self._needs_rebuild:
            return
        
        # Sort edges by source vertex index
        edges_by_source = {}
        for source, target, edge_data in self._build_cache:
            source_idx = self._vertex_to_index[source]
            target_idx = self._vertex_to_index[target]
            
            if source_idx not in edges_by_source:
                edges_by_source[source_idx] = []
            edges_by_source[source_idx].append((target_idx, edge_data))
        
        # Sort edges within each source by target index
        for source_idx in edges_by_source:
            edges_by_source[source_idx].sort(key=lambda x: x[0])
        
        # Rebuild CSR arrays
        self._row_ptr = [0]
        self._col_indices = []
        self._values = []
        
        for source_idx in range(self._vertex_count):
            if source_idx in edges_by_source:
                for target_idx, edge_data in edges_by_source[source_idx]:
                    self._col_indices.append(target_idx)
                    self._values.append(edge_data)
            
            self._row_ptr.append(len(self._col_indices))
        
        self._build_cache.clear()
        self._needs_rebuild = False
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add an edge between source and target vertices."""
        # Validate self-loops
        if source == target and not self.allow_self_loops:
            raise ValueError(f"Self-loops not allowed: {source} -> {target}")
        
        # Get vertex indices (creates vertices if needed)
        source_idx = self._get_vertex_index(source)
        target_idx = self._get_vertex_index(target)
        
        # Generate edge ID
        edge_id = f"edge_{self._edge_id_counter}"
        self._edge_id_counter += 1
        
        # Create edge data
        edge_data = {
            'id': edge_id,
            'source': source,
            'target': target,
            'weight': properties.get('weight', 1.0),
            'properties': properties.copy()
        }
        
        # Add to build cache
        self._build_cache.append((source, target, edge_data))
        
        # For undirected graphs, add reverse edge
        if not self.is_directed and source != target:
            reverse_edge_data = edge_data.copy()
            reverse_edge_data['source'] = target
            reverse_edge_data['target'] = source
            self._build_cache.append((target, source, reverse_edge_data))
        
        self._edge_count += 1
        self._needs_rebuild = True
        
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """
        Remove edge between source and target.
        
        Root cause fixed: Previously only removed from build cache, missing edges
        already in CSR structure. Now checks both locations.
        
        Priority: Maintainability #3 - Correct edge removal logic
        """
        if source not in self._vertex_to_index or target not in self._vertex_to_index:
            return False
        
        # First check if edge exists (either in cache or CSR structure)
        edge_exists = False
        
        # Check build cache
        original_cache_size = len(self._build_cache)
        if edge_id:
            self._build_cache = [
                (s, t, data) for s, t, data in self._build_cache
                if not (s == source and t == target and data['id'] == edge_id)
            ]
        else:
            self._build_cache = [
                (s, t, data) for s, t, data in self._build_cache
                if not (s == source and t == target)
            ]
        
        cache_removed = len(self._build_cache) < original_cache_size
        
        # If not in cache, might be in rebuilt CSR structure
        if not cache_removed and not self._needs_rebuild:
            # Need to remove from CSR - rebuild entire structure without this edge
            # Mark for rebuild by checking all existing edges
            self._rebuild_csr()
            
            # Collect all edges from CSR structure back to cache
            for source_idx in range(self._vertex_count):
                start = self._row_ptr[source_idx]
                end = self._row_ptr[source_idx + 1]
                
                source_vertex = self._index_to_vertex[source_idx]
                
                for i in range(start, end):
                    target_idx = self._col_indices[i]
                    target_vertex = self._index_to_vertex[target_idx]
                    edge_data = self._values[i]
                    
                    # Skip the edge we're removing
                    skip = False
                    if edge_id:
                        skip = (source_vertex == source and target_vertex == target and edge_data['id'] == edge_id)
                    else:
                        skip = (source_vertex == source and target_vertex == target)
                    
                    if not skip:
                        self._build_cache.append((source_vertex, target_vertex, edge_data))
                    else:
                        edge_exists = True
            
            if edge_exists:
                self._edge_count -= 1
                self._needs_rebuild = True
        elif cache_removed:
            edge_exists = True
            self._edge_count -= (original_cache_size - len(self._build_cache))
            self._needs_rebuild = True
        
        return edge_exists
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        if source not in self._vertex_to_index or target not in self._vertex_to_index:
            return False
        
        # Rebuild if needed
        self._rebuild_csr()
        
        source_idx = self._vertex_to_index[source]
        target_idx = self._vertex_to_index[target]
        
        # Binary search in the row
        start = self._row_ptr[source_idx]
        end = self._row_ptr[source_idx + 1]
        
        # Use binary search to find target
        pos = bisect.bisect_left(self._col_indices[start:end], target_idx)
        return (pos < end - start and 
                self._col_indices[start + pos] == target_idx)
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data between source and target."""
        if source not in self._vertex_to_index or target not in self._vertex_to_index:
            return None
        
        # Rebuild if needed
        self._rebuild_csr()
        
        source_idx = self._vertex_to_index[source]
        target_idx = self._vertex_to_index[target]
        
        # Binary search in the row
        start = self._row_ptr[source_idx]
        end = self._row_ptr[source_idx + 1]
        
        pos = bisect.bisect_left(self._col_indices[start:end], target_idx)
        if pos < end - start and self._col_indices[start + pos] == target_idx:
            return self._values[start + pos]
        
        return None
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get neighbors of a vertex."""
        if vertex not in self._vertex_to_index:
            return
        
        # Rebuild if needed
        self._rebuild_csr()
        
        vertex_idx = self._vertex_to_index[vertex]
        
        if direction == 'out':
            # Outgoing neighbors (direct from CSR)
            start = self._row_ptr[vertex_idx]
            end = self._row_ptr[vertex_idx + 1]
            
            for i in range(start, end):
                target_idx = self._col_indices[i]
                yield self._index_to_vertex[target_idx]
        
        elif direction == 'in':
            # Incoming neighbors (scan all rows)
            for source_idx in range(self._vertex_count):
                start = self._row_ptr[source_idx]
                end = self._row_ptr[source_idx + 1]
                
                for i in range(start, end):
                    if self._col_indices[i] == vertex_idx:
                        yield self._index_to_vertex[source_idx]
                        break
        
        elif direction == 'both':
            # All neighbors
            seen = set()
            for neighbor in self.neighbors(vertex, 'out'):
                if neighbor not in seen:
                    seen.add(neighbor)
                    yield neighbor
            for neighbor in self.neighbors(vertex, 'in'):
                if neighbor not in seen:
                    seen.add(neighbor)
                    yield neighbor
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree of a vertex."""
        if vertex not in self._vertex_to_index:
            return 0
        
        # Rebuild if needed
        self._rebuild_csr()
        
        vertex_idx = self._vertex_to_index[vertex]
        
        if direction == 'out':
            # Out-degree from row pointer difference
            return self._row_ptr[vertex_idx + 1] - self._row_ptr[vertex_idx]
        
        elif direction == 'in':
            # In-degree by scanning columns
            count = 0
            for i in range(len(self._col_indices)):
                if self._col_indices[i] == vertex_idx:
                    count += 1
            return count
        
        elif direction == 'both':
            out_degree = self.degree(vertex, 'out')
            in_degree = self.degree(vertex, 'in')
            return out_degree if not self.is_directed else out_degree + in_degree
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all edges in the graph."""
        # Rebuild if needed
        self._rebuild_csr()
        
        for source_idx in range(self._vertex_count):
            start = self._row_ptr[source_idx]
            end = self._row_ptr[source_idx + 1]
            
            source = self._index_to_vertex[source_idx]
            
            for i in range(start, end):
                target_idx = self._col_indices[i]
                target = self._index_to_vertex[target_idx]
                
                # For undirected graphs, avoid returning duplicate edges
                if not self.is_directed and source > target:
                    continue
                
                if data:
                    yield (source, target, self._values[i])
                else:
                    yield (source, target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices in the graph."""
        return iter(self._vertex_to_index.keys())
    
    def __len__(self) -> int:
        """Get the number of edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get the number of vertices."""
        return self._vertex_count
    
    def clear(self) -> None:
        """Clear all edges and vertices."""
        self._row_ptr = [0]
        self._col_indices.clear()
        self._values.clear()
        self._vertex_to_index.clear()
        self._index_to_vertex.clear()
        self._vertex_count = 0
        self._edge_count = 0
        self._edge_id_counter = 0
        self._build_cache.clear()
        self._needs_rebuild = False
    
    def add_vertex(self, vertex: str) -> None:
        """Add a vertex to the graph."""
        if vertex not in self._vertex_to_index:
            self._get_vertex_index(vertex)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove a vertex and all its edges."""
        if vertex not in self._vertex_to_index:
            return False
        
        # Remove all edges involving this vertex from cache
        original_cache_size = len(self._build_cache)
        self._build_cache = [
            (s, t, data) for s, t, data in self._build_cache
            if s != vertex and t != vertex
        ]
        
        edges_removed = original_cache_size - len(self._build_cache)
        self._edge_count -= edges_removed
        
        # Remove vertex from mappings
        vertex_idx = self._vertex_to_index[vertex]
        del self._vertex_to_index[vertex]
        del self._index_to_vertex[vertex_idx]
        
        # Compact indices (expensive operation)
        self._compact_indices()
        
        self._needs_rebuild = True
        return True
    
    def _compact_indices(self) -> None:
        """Compact vertex indices after vertex removal."""
        # Create new mapping with compacted indices
        old_to_new = {}
        new_vertex_to_index = {}
        new_index_to_vertex = {}
        
        new_index = 0
        for old_index in sorted(self._index_to_vertex.keys()):
            vertex = self._index_to_vertex[old_index]
            old_to_new[old_index] = new_index
            new_vertex_to_index[vertex] = new_index
            new_index_to_vertex[new_index] = vertex
            new_index += 1
        
        # Update mappings
        self._vertex_to_index = new_vertex_to_index
        self._index_to_vertex = new_index_to_vertex
        self._vertex_count = len(new_vertex_to_index)
        
        # Update build cache with new indices
        updated_cache = []
        for source, target, edge_data in self._build_cache:
            if source in self._vertex_to_index and target in self._vertex_to_index:
                updated_cache.append((source, target, edge_data))
        
        self._build_cache = updated_cache
    
    # ============================================================================
    # CSR-SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_csr_arrays(self) -> Tuple[List[int], List[int], List[float]]:
        """Get the raw CSR arrays (row_ptr, col_indices, weights)."""
        self._rebuild_csr()
        
        weights = [edge_data.get('weight', 1.0) for edge_data in self._values]
        return self._row_ptr.copy(), self._col_indices.copy(), weights
    
    def from_csr_arrays(self, row_ptr: List[int], col_indices: List[int], 
                       weights: List[float], vertices: List[str]) -> None:
        """Build graph from CSR arrays."""
        if len(row_ptr) != len(vertices) + 1:
            raise ValueError("row_ptr length must be vertices + 1")
        if len(col_indices) != len(weights):
            raise ValueError("col_indices and weights must have same length")
        
        # Clear existing data
        self.clear()
        
        # Add vertices
        for vertex in vertices:
            self.add_vertex(vertex)
        
        # Add edges from CSR format
        for source_idx, vertex in enumerate(vertices):
            start = row_ptr[source_idx]
            end = row_ptr[source_idx + 1]
            
            for i in range(start, end):
                target_idx = col_indices[i]
                weight = weights[i]
                target = vertices[target_idx]
                
                self.add_edge(vertex, target, weight=weight)
    
    def multiply_vector(self, vector: List[float]) -> List[float]:
        """Multiply the adjacency matrix by a vector (SpMV operation)."""
        if len(vector) != self._vertex_count:
            raise ValueError(f"Vector length {len(vector)} must match vertex count {self._vertex_count}")
        
        # Rebuild if needed
        self._rebuild_csr()
        
        result = [0.0] * self._vertex_count
        
        for source_idx in range(self._vertex_count):
            start = self._row_ptr[source_idx]
            end = self._row_ptr[source_idx + 1]
            
            for i in range(start, end):
                target_idx = self._col_indices[i]
                weight = self._values[i].get('weight', 1.0)
                result[source_idx] += weight * vector[target_idx]
        
        return result
    
    def get_compression_ratio(self) -> float:
        """Get the compression ratio compared to dense matrix."""
        dense_size = self._vertex_count * self._vertex_count
        sparse_size = len(self._col_indices) + len(self._row_ptr) + len(self._values)
        return sparse_size / max(1, dense_size)
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'CSR',
            'backend': 'Compressed Sparse Row format',
            'directed': self.is_directed,
            'compression': True,
            'complexity': {
                'add_edge': 'O(1) amortized',
                'remove_edge': 'O(E) worst case',
                'has_edge': 'O(log degree)',
                'neighbors_out': 'O(degree)',
                'neighbors_in': 'O(E)',
                'space': 'O(V + E)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        compression_ratio = self.get_compression_ratio()
        avg_degree = self._edge_count / max(1, self._vertex_count) if self._vertex_count else 0
        
        return {
            'vertices': self._vertex_count,
            'edges': self._edge_count,
            'compression_ratio': round(compression_ratio, 4),
            'average_degree': round(avg_degree, 2),
            'memory_usage': f"{len(self._col_indices) * 12 + len(self._row_ptr) * 4} bytes (estimated)",
            'cache_size': len(self._build_cache),
            'needs_rebuild': self._needs_rebuild
        }
