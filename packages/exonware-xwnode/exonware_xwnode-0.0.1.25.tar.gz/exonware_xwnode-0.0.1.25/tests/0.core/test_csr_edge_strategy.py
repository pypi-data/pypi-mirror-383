"""
Unit tests for CSR (Compressed Sparse Row) edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.csr import CSRStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestCSRCore:
    """Core tests for CSR edge strategy."""
    
    def test_initialization(self):
        """Test initialization with EXACT expected state."""
        strategy = CSRStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.CSR
        assert len(strategy) == 0
        assert strategy.vertex_count() == 0
    
    def test_add_edge(self, graph_factory):
        """Test add_edge with EXACT verification."""
        strategy = CSRStrategy()
        edges = graph_factory(10, 20, directed=True, weighted=True)
        
        edge_ids = []
        for src, tgt, props in edges:
            edge_id = strategy.add_edge(src, tgt, **props)
            assert edge_id is not None
            assert isinstance(edge_id, str)
            edge_ids.append(edge_id)
        
        # Verify count
        assert len(strategy) == 20
        
        # Verify uniqueness of edge IDs
        assert len(set(edge_ids)) == 20
    
    def test_has_edge(self):
        """Test has_edge with EXACT boolean results."""
        strategy = CSRStrategy()
        strategy.add_edge("v1", "v2", weight=1.0)
        strategy.add_edge("v1", "v3", weight=2.0)
        
        assert strategy.has_edge("v1", "v2") is True
        assert strategy.has_edge("v1", "v3") is True
        assert strategy.has_edge("v2", "v3") is False
        assert strategy.has_edge("v3", "v1") is False
        assert strategy.has_edge("v99", "v100") is False
    
    def test_get_neighbors_out(self):
        """Test outgoing neighbor queries with EXACT expected lists."""
        strategy = CSRStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v1", "v3")
        strategy.add_edge("v1", "v4")
        strategy.add_edge("v2", "v3")
        
        neighbors = list(strategy.neighbors("v1", direction='out'))
        assert len(neighbors) == 3
        assert "v2" in neighbors
        assert "v3" in neighbors
        assert "v4" in neighbors
        
        neighbors_v2 = list(strategy.neighbors("v2", direction='out'))
        assert len(neighbors_v2) == 1
        assert "v3" in neighbors_v2
    
    def test_get_neighbors_empty(self):
        """Test neighbors for non-existent vertex."""
        strategy = CSRStrategy()
        strategy.add_edge("v1", "v2")
        
        neighbors = list(strategy.neighbors("v99"))
        assert len(neighbors) == 0
    
    def test_remove_edge(self):
        """Test edge deletion with EXACT verification."""
        strategy = CSRStrategy()
        edge_id = strategy.add_edge("v1", "v2")
        
        assert strategy.has_edge("v1", "v2") is True
        result = strategy.remove_edge("v1", "v2")
        assert result is True
        assert strategy.has_edge("v1", "v2") is False
    
    def test_remove_edge_nonexistent(self):
        """Test removing non-existent edge."""
        strategy = CSRStrategy()
        result = strategy.remove_edge("v1", "v2")
        assert result is False
    
    def test_clear_operation(self):
        """Test clear with EXACT empty state."""
        strategy = CSRStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v2", "v3")
        strategy.add_edge("v3", "v4")
        
        assert len(strategy) == 3
        strategy.clear()
        assert len(strategy) == 0
        assert strategy.vertex_count() == 0
        assert strategy.has_edge("v1", "v2") is False
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = CSRStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.SPARSE in traits
        assert EdgeTrait.COMPRESSED in traits
        assert EdgeTrait.CACHE_FRIENDLY in traits
        assert EdgeTrait.COLUMNAR in traits
    
    def test_degree_out(self):
        """Test out-degree calculation."""
        strategy = CSRStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v1", "v3")
        strategy.add_edge("v1", "v4")
        
        assert strategy.degree("v1", direction='out') == 3
        assert strategy.degree("v2", direction='out') == 0
        assert strategy.degree("v99", direction='out') == 0


@pytest.mark.xwnode_core
class TestCSRSpecificFeatures:
    """CSR-specific feature tests."""
    
    def test_csr_rebuild(self):
        """Test CSR array rebuild after modifications."""
        strategy = CSRStrategy()
        
        # Add edges
        strategy.add_edge("v0", "v1")
        strategy.add_edge("v0", "v2")
        strategy.add_edge("v1", "v2")
        
        # Force rebuild by checking edge
        assert strategy.has_edge("v0", "v1") is True
        
        # Verify CSR structure is valid
        row_ptr, col_indices, weights = strategy.get_csr_arrays()
        assert len(row_ptr) >= 1
        assert len(col_indices) == 3
        assert len(weights) == 3
    
    def test_sparse_vector_multiply(self):
        """Test sparse matrix-vector multiplication."""
        strategy = CSRStrategy()
        
        # Create simple graph: v0 -> v1, v1 -> v2
        strategy.add_edge("v0", "v1", weight=2.0)
        strategy.add_edge("v1", "v2", weight=3.0)
        strategy.add_edge("v0", "v2", weight=1.0)
        
        # Vector [1, 1, 1]
        vector = [1.0, 1.0, 1.0]
        result = strategy.multiply_vector(vector)
        
        # v0: 2*1 + 1*1 = 3
        # v1: 3*1 = 3
        # v2: 0
        assert len(result) == 3
        assert result[0] == 3.0
        assert result[1] == 3.0
        assert result[2] == 0.0
    
    def test_compression_ratio(self):
        """Test compression ratio calculation."""
        strategy = CSRStrategy()
        
        # Add sparse edges (10 edges in 10 vertices = ~10% density)
        for i in range(10):
            strategy.add_edge(f"v{i}", f"v{(i+1)%10}")
        
        ratio = strategy.get_compression_ratio()
        # Should be much less than 1.0 for sparse graph
        assert 0.0 < ratio < 1.0
    
    def test_get_edge_data(self):
        """Test retrieving edge data with properties."""
        strategy = CSRStrategy()
        strategy.add_edge("v1", "v2", weight=5.5, label="test", color="red")
        
        edge_data = strategy.get_edge_data("v1", "v2")
        assert edge_data is not None
        assert edge_data['weight'] == 5.5
        assert 'properties' in edge_data
        assert edge_data['properties']['label'] == "test"
        assert edge_data['properties']['color'] == "red"
    
    def test_from_csr_arrays(self):
        """
        Test building graph from CSR arrays.
        
        Fixed: CSR format requires row_ptr length = vertices + 1.
        Corrected to valid CSR format: v0 -> v1, v0 -> v2, v1 -> v2 with 3 vertices.
        
        Priority: Maintainability #3 - Correct CSR format specification
        """
        strategy = CSRStrategy()
        
        # CSR arrays for: v0 -> v1, v0 -> v2, v1 -> v2
        # row_ptr[i] to row_ptr[i+1] gives edges for vertex i
        # For 3 vertices, need row_ptr length = 4 (vertices + 1)
        row_ptr = [0, 2, 3, 3]  # v0: edges 0-2, v1: edges 2-3, v2: edges 3-3 (none)
        col_indices = [1, 2, 2]  # v0->v1, v0->v2, v1->v2
        weights = [1.0, 2.0, 3.0]
        vertices = ["v0", "v1", "v2"]
        
        strategy.from_csr_arrays(row_ptr, col_indices, weights, vertices)
        
        assert strategy.vertex_count() == 3
        assert strategy.has_edge("v0", "v1") is True
        assert strategy.has_edge("v0", "v2") is True
        assert strategy.has_edge("v1", "v2") is True


@pytest.mark.xwnode_performance
class TestCSRPerformance:
    """Performance validation tests for CSR strategy."""
    
    def test_time_complexity_add(self, measure_time_complexity):
        """Validate O(1) amortized add edge complexity."""
        def operation(size):
            strategy = CSRStrategy()
            for i in range(size):
                strategy.add_edge(f"v{i}", f"v{i+1}")
        
        measure_time_complexity(operation, [1000, 5000, 10000], 'O(N)')
    
    def test_time_complexity_has_edge(self):
        """Validate O(log degree) has_edge complexity."""
        strategy = CSRStrategy()
        
        # Create vertex with many neighbors
        for i in range(100):
            strategy.add_edge("v0", f"v{i+1}")
        
        # has_edge should use binary search - fast even with many neighbors
        import time
        start = time.perf_counter()
        for _ in range(1000):
            strategy.has_edge("v0", "v50")
        elapsed = time.perf_counter() - start
        
        # Should be very fast (< 10ms for 1000 lookups)
        assert elapsed < 0.01
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage is reasonable for sparse graphs."""
        def operation():
            strategy = CSRStrategy()
            # Add 1000 edges in a sparse graph
            for i in range(1000):
                strategy.add_edge(f"v{i}", f"v{(i+1)%1000}")
            return strategy
        
        result, memory = measure_memory(operation)
        # CSR should be memory efficient: < 500KB for 1000 edges
        assert memory < 500 * 1024
    
    def test_sparse_graph_efficiency(self):
        """Test CSR efficiency on large sparse graphs."""
        strategy = CSRStrategy()
        
        # Create large sparse graph (10,000 vertices, 20,000 edges = 0.02% density)
        import time
        start = time.perf_counter()
        
        for i in range(10000):
            strategy.add_edge(f"v{i}", f"v{(i+1)%10000}")
            strategy.add_edge(f"v{i}", f"v{(i+2)%10000}")
        
        elapsed = time.perf_counter() - start
        
        assert len(strategy) == 20000
        # Should complete in reasonable time (< 1 second)
        assert elapsed < 1.0
        
        # Verify compression is good
        ratio = strategy.get_compression_ratio()
        assert ratio < 0.01  # Should be < 1% of dense matrix


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

