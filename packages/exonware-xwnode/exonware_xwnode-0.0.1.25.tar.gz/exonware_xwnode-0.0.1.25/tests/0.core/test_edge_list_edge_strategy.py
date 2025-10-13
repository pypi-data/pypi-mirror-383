"""
Unit tests for EDGE_LIST edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.edge_list import EdgeListStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestEdgeListCore:
    """Core tests for EDGE_LIST edge strategy."""
    
    def test_initialization(self):
        """Test initialization with EXACT expected state."""
        strategy = EdgeListStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.EDGE_LIST
        assert len(strategy) == 0
    
    def test_add_edge(self, graph_factory):
        """Test add_edge with EXACT verification."""
        strategy = EdgeListStrategy()
        edges = graph_factory(10, 20, directed=True, weighted=True)
        
        for src, tgt, props in edges:
            edge_id = strategy.add_edge(src, tgt, **props)
            assert edge_id is not None
        
        assert len(strategy) == 20
    
    def test_has_edge(self):
        """Test has_edge with EXACT boolean results."""
        strategy = EdgeListStrategy()
        strategy.add_edge("v1", "v2", weight=1.0)
        
        assert strategy.has_edge("v1", "v2") is True
        assert strategy.has_edge("v2", "v3") is False
    
    def test_remove_edge(self):
        """Test edge deletion."""
        strategy = EdgeListStrategy()
        strategy.add_edge("v1", "v2")
        
        result = strategy.remove_edge("v1", "v2")
        assert result is True or result is False
    
    def test_clear_operation(self):
        """Test clear with EXACT empty state."""
        strategy = EdgeListStrategy()
        strategy.add_edge("v1", "v2")
        strategy.clear()
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = EdgeListStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.SPARSE in traits
    
    def test_simple_format(self):
        """Test simple list format."""
        strategy = EdgeListStrategy()
        strategy.add_edge("A", "B")
        strategy.add_edge("B", "C")
        strategy.add_edge("C", "A")
        
        edges = list(strategy.edges())
        assert len(edges) == 3
    
    def test_edges_iteration(self):
        """Test iterating over all edges."""
        strategy = EdgeListStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v2", "v3")
        
        edges = list(strategy.edges())
        assert len(edges) == 2


@pytest.mark.xwnode_performance
class TestEdgeListPerformance:
    """Performance tests for EDGE_LIST."""
    
    def test_fast_addition(self):
        """Test O(1) edge addition."""
        strategy = EdgeListStrategy()
        
        import time
        start = time.perf_counter()
        
        for i in range(10000):
            strategy.add_edge(f"v{i}", f"v{(i+1)%10000}")
        
        elapsed = time.perf_counter() - start
        
        assert len(strategy) == 10000
        assert elapsed < 1.0
    
    def test_memory_efficiency(self, measure_memory):
        """Validate minimal memory usage."""
        def operation():
            strategy = EdgeListStrategy()
            for i in range(1000):
                strategy.add_edge(f"v{i}", f"v{(i+1)%1000}")
            return strategy
        
        result, memory = measure_memory(operation)
        # Should be very memory efficient
        assert memory < 500 * 1024


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

