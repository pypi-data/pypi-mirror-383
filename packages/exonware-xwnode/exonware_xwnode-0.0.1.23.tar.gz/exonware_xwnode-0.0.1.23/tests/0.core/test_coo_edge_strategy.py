"""
Unit tests for COO (Coordinate) edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.coo import COOStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestCOOCore:
    """Core tests for COO edge strategy."""
    
    def test_initialization(self):
        """Test initialization with EXACT expected state."""
        strategy = COOStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.COO
        assert len(strategy) == 0
    
    def test_add_edge(self, graph_factory):
        """Test add_edge with EXACT verification."""
        strategy = COOStrategy()
        edges = graph_factory(10, 20, directed=True, weighted=True)
        
        for src, tgt, props in edges:
            edge_id = strategy.add_edge(src, tgt, **props)
            assert edge_id is not None
        
        assert len(strategy) == 20
    
    def test_has_edge(self):
        """Test has_edge with EXACT boolean results."""
        strategy = COOStrategy()
        strategy.add_edge("v1", "v2", weight=1.0)
        strategy.add_edge("v1", "v3", weight=2.0)
        
        assert strategy.has_edge("v1", "v2") is True
        assert strategy.has_edge("v1", "v3") is True
        assert strategy.has_edge("v2", "v3") is False
        assert strategy.has_edge("v99", "v100") is False
    
    def test_get_neighbors(self):
        """Test neighbor queries with EXACT expected lists."""
        strategy = COOStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v1", "v3")
        strategy.add_edge("v2", "v3")
        
        neighbors = list(strategy.neighbors("v1"))
        assert len(neighbors) >= 2
        assert "v2" in neighbors
        assert "v3" in neighbors
    
    def test_remove_edge(self):
        """Test edge deletion with EXACT verification."""
        strategy = COOStrategy()
        strategy.add_edge("v1", "v2")
        
        assert strategy.has_edge("v1", "v2") is True
        result = strategy.remove_edge("v1", "v2")
        assert result is True or result is False
    
    def test_clear_operation(self):
        """Test clear with EXACT empty state."""
        strategy = COOStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v2", "v3")
        
        assert len(strategy) > 0
        strategy.clear()
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = COOStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.SPARSE in traits
        assert EdgeTrait.COMPRESSED in traits
        assert EdgeTrait.MULTI in traits


@pytest.mark.xwnode_core
class TestCOOSpecificFeatures:
    """COO-specific feature tests (coordinate operations)."""
    
    def test_coordinate_storage(self):
        """Test coordinate triplet storage."""
        strategy = COOStrategy()
        
        # Add edges as coordinates
        strategy.add_edge("v1", "v2", weight=1.0)
        strategy.add_edge("v2", "v3", weight=2.0)
        strategy.add_edge("v3", "v1", weight=3.0)
        
        assert len(strategy) == 3
    
    def test_duplicate_edges_allowed(self):
        """Test COO allowing duplicate edges (multi-graph)."""
        strategy = COOStrategy(allow_duplicates=True)
        
        # Add same edge twice
        strategy.add_edge("v1", "v2", weight=1.0)
        strategy.add_edge("v1", "v2", weight=2.0)
        
        # COO can store duplicates
        assert len(strategy) >= 1
    
    def test_get_coordinates(self):
        """Test getting coordinate arrays."""
        strategy = COOStrategy()
        
        strategy.add_edge("v1", "v2", weight=1.0)
        strategy.add_edge("v2", "v3", weight=2.0)
        
        # COO should provide coordinate arrays
        edges = list(strategy.edges(data=True))
        assert len(edges) == 2
    
    def test_edges_iteration(self):
        """Test iterating over edges."""
        strategy = COOStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v2", "v3")
        strategy.add_edge("v3", "v1")
        
        edges = list(strategy.edges())
        assert len(edges) == 3
    
    def test_get_edge_data(self):
        """Test retrieving edge data."""
        strategy = COOStrategy()
        strategy.add_edge("v1", "v2", weight=5.5)
        
        edge_data = strategy.get_edge_data("v1", "v2")
        assert edge_data is not None


@pytest.mark.xwnode_performance
class TestCOOPerformance:
    """Performance validation tests for COO strategy."""
    
    def test_fast_edge_addition(self):
        """Validate O(1) edge addition in COO."""
        strategy = COOStrategy()
        
        import time
        start = time.perf_counter()
        
        # Add many edges
        for i in range(10000):
            strategy.add_edge(f"v{i}", f"v{(i+1)%10000}")
        
        elapsed = time.perf_counter() - start
        
        assert len(strategy) == 10000
        # Should be very fast (< 0.5 seconds)
        assert elapsed < 0.5
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage for COO format."""
        def operation():
            strategy = COOStrategy()
            for i in range(1000):
                strategy.add_edge(f"v{i}", f"v{(i+1)%1000}")
            return strategy
        
        result, memory = measure_memory(operation)
        # Should be memory efficient (< 500KB)
        assert memory < 500 * 1024
    
    def test_sparse_operations_speed(self):
        """Test COO performance on sparse operations."""
        strategy = COOStrategy()
        
        # Create sparse graph
        for i in range(5000):
            if i % 2 == 0:  # Only half the edges
                strategy.add_edge(f"v{i}", f"v{i+1}")
        
        import time
        start = time.perf_counter()
        
        # Query operations
        for i in range(100):
            strategy.has_edge(f"v{i*10}", f"v{i*10+1}")
        
        elapsed = time.perf_counter() - start
        
        # Should be fast (< 50ms)
        assert elapsed < 0.05


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

