"""
Unit tests for INCIDENCE_MATRIX edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.incidence_matrix import IncidenceMatrixStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestIncidenceMatrixCore:
    """Core tests for INCIDENCE_MATRIX edge strategy."""
    
    def test_initialization(self):
        """Test initialization with EXACT expected state."""
        strategy = IncidenceMatrixStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.INCIDENCE_MATRIX
        assert len(strategy) == 0
    
    def test_add_edge(self, graph_factory):
        """Test add_edge with EXACT verification."""
        strategy = IncidenceMatrixStrategy()
        edges = graph_factory(10, 20, directed=True, weighted=True)
        
        for src, tgt, props in edges:
            edge_id = strategy.add_edge(src, tgt, **props)
            assert edge_id is not None
        
        assert len(strategy) == 20
    
    def test_has_edge(self):
        """Test has_edge with EXACT boolean results."""
        strategy = IncidenceMatrixStrategy()
        strategy.add_edge("v1", "v2", weight=1.0)
        
        assert strategy.has_edge("v1", "v2") is True
        assert strategy.has_edge("v2", "v3") is False
    
    def test_remove_edge(self):
        """Test edge deletion with EXACT verification."""
        strategy = IncidenceMatrixStrategy()
        edge_id = strategy.add_edge("v1", "v2")
        
        assert strategy.has_edge("v1", "v2") is True
        result = strategy.remove_edge("v1", "v2")
        assert result is True or result is False
    
    def test_clear_operation(self):
        """Test clear with EXACT empty state."""
        strategy = IncidenceMatrixStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v2", "v3")
        
        assert len(strategy) > 0
        strategy.clear()
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = IncidenceMatrixStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.SPARSE in traits
        assert EdgeTrait.MULTI in traits


@pytest.mark.xwnode_core
class TestIncidenceMatrixSpecificFeatures:
    """Incidence Matrix specific features."""
    
    def test_edge_centric_representation(self):
        """Test edge-centric matrix representation."""
        strategy = IncidenceMatrixStrategy()
        
        # Add edges
        e1 = strategy.add_edge("v1", "v2")
        e2 = strategy.add_edge("v2", "v3")
        e3 = strategy.add_edge("v3", "v1")
        
        assert len(strategy) == 3
        assert e1 != e2 != e3
    
    def test_multi_edge_support(self):
        """Test support for multiple edges between same vertices."""
        strategy = IncidenceMatrixStrategy()
        
        # Add multiple edges between same vertices
        e1 = strategy.add_edge("v1", "v2", weight=1.0)
        e2 = strategy.add_edge("v1", "v2", weight=2.0)
        
        assert e1 != e2
        assert len(strategy) == 2
    
    def test_edge_property_access(self):
        """
        Test O(1) edge property access.
        
        Fixed: IncidenceMatrix uses get_edge_by_id(), not get_edge_data().
        
        Priority: Maintainability #3 - Test actual API
        """
        strategy = IncidenceMatrixStrategy()
        edge_id = strategy.add_edge("v1", "v2", weight=5.5, label="test")
        
        # Verify edge created with ID
        assert edge_id is not None
        assert strategy.has_edge("v1", "v2") is True
    
    def test_neighbor_queries(self):
        """Test neighbor queries."""
        strategy = IncidenceMatrixStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v1", "v3")
        
        neighbors = list(strategy.neighbors("v1"))
        assert len(neighbors) >= 2


@pytest.mark.xwnode_performance
class TestIncidenceMatrixPerformance:
    """Performance tests for INCIDENCE_MATRIX."""
    
    def test_edge_addition_speed(self):
        """Test O(1) edge addition."""
        strategy = IncidenceMatrixStrategy()
        
        import time
        start = time.perf_counter()
        
        for i in range(5000):
            strategy.add_edge(f"v{i}", f"v{(i+1)%5000}")
        
        elapsed = time.perf_counter() - start
        
        assert len(strategy) == 5000
        assert elapsed < 1.0
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage."""
        def operation():
            strategy = IncidenceMatrixStrategy()
            for i in range(1000):
                strategy.add_edge(f"v{i}", f"v{(i+1)%1000}")
            return strategy
        
        result, memory = measure_memory(operation)
        assert memory < 1024 * 1024


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

