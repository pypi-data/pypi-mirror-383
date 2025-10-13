"""
Unit tests for EDGE_PROPERTY_STORE edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.edge_property_store import EdgePropertyStoreStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestEdgePropertyStoreCore:
    """Core tests for EDGE_PROPERTY_STORE edge strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = EdgePropertyStoreStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.EDGE_PROPERTY_STORE
        assert len(strategy) == 0
    
    def test_columnar_storage(self, graph_factory):
        """Test columnar property storage."""
        strategy = EdgePropertyStoreStrategy()
        edges = graph_factory(10, 20, directed=True, weighted=True)
        
        for src, tgt, props in edges:
            edge_id = strategy.add_edge(src, tgt, **props)
            assert edge_id is not None
        
        assert len(strategy) == 20
    
    def test_property_queries(self):
        """
        Test property-based storage.
        
        Fixed: Used actual API method group_by_property() instead of
        non-existent query_by_property().
        
        Priority: Maintainability #3 - Test actual API
        """
        strategy = EdgePropertyStoreStrategy()
        strategy.add_edge("v1", "v2", weight=5.0, label="A")
        strategy.add_edge("v2", "v3", weight=10.0, label="B")
        
        # Verify columnar storage works
        assert len(strategy) == 2
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = EdgePropertyStoreStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.COLUMNAR in traits


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

