"""
Unit tests for HYPEREDGE_SET edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.hyperedge_set import HyperEdgeSetStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestHyperEdgeSetCore:
    """Core tests for HYPEREDGE_SET edge strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = HyperEdgeSetStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.HYPEREDGE_SET
        assert len(strategy) == 0
    
    def test_add_hyperedge(self):
        """Test adding hyperedge connecting multiple vertices."""
        strategy = HyperEdgeSetStrategy()
        # Hyperedge connecting 3 vertices
        edge_id = strategy.add_hyperedge(["v1", "v2", "v3"], weight=1.0)
        assert edge_id is not None
        assert len(strategy) == 1
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = HyperEdgeSetStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.HYPER in traits


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

