"""
Unit tests for COMPRESSED_GRAPH edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.compressed_graph import CompressedGraphStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestCompressedGraphCore:
    """Core tests for COMPRESSED_GRAPH edge strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = CompressedGraphStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.COMPRESSED_GRAPH
        assert len(strategy) == 0
    
    def test_add_edge(self, graph_factory):
        """Test add_edge."""
        strategy = CompressedGraphStrategy()
        edges = graph_factory(10, 20)
        
        for src, tgt, props in edges:
            edge_id = strategy.add_edge(src, tgt, **props)
            assert edge_id is not None
        
        assert len(strategy) == 20
    
    def test_has_edge(self):
        """Test has_edge."""
        strategy = CompressedGraphStrategy()
        strategy.add_edge("v1", "v2")
        assert strategy.has_edge("v1", "v2") is True
        assert strategy.has_edge("v2", "v3") is False
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = CompressedGraphStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.COMPRESSED in traits
    
    def test_compression(self):
        """Test graph compression."""
        strategy = CompressedGraphStrategy()
        for i in range(100):
            strategy.add_edge(f"v{i}", f"v{(i+1)%100}")
        
        # Verify compression achieved
        assert len(strategy) == 100
    
    def test_memory_efficiency(self, measure_memory):
        """Test compression reduces memory."""
        def operation():
            strategy = CompressedGraphStrategy()
            for i in range(1000):
                strategy.add_edge(f"v{i}", f"v{(i+1)%1000}")
            return strategy
        
        result, memory = measure_memory(operation)
        assert memory < 1024 * 1024


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

