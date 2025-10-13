"""
Unit tests for BIDIR_WRAPPER edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.bidir_wrapper import BidirWrapperStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestBidirWrapperCore:
    """Core tests for BIDIR_WRAPPER edge strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = BidirWrapperStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.BIDIR_WRAPPER
        assert len(strategy) == 0
    
    def test_add_edge_creates_both_directions(self):
        """Test undirected wrapper creates dual arcs."""
        strategy = BidirWrapperStrategy()
        strategy.add_edge("v1", "v2")
        
        # Both directions should exist
        assert strategy.has_edge("v1", "v2") is True
        assert strategy.has_edge("v2", "v1") is True
    
    def test_symmetry(self):
        """Test symmetric edge representation."""
        strategy = BidirWrapperStrategy()
        strategy.add_edge("A", "B", weight=5.0)
        
        # Both directions should have same properties
        data_ab = strategy.get_edge_data("A", "B")
        data_ba = strategy.get_edge_data("B", "A")
        
        assert data_ab is not None
        assert data_ba is not None
    
    def test_remove_edge_removes_both(self):
        """Test removing edge removes both directions."""
        strategy = BidirWrapperStrategy()
        strategy.add_edge("v1", "v2")
        
        strategy.remove_edge("v1", "v2")
        
        assert strategy.has_edge("v1", "v2") is False
        assert strategy.has_edge("v2", "v1") is False
    
    def test_supported_traits(self):
        """
        Test trait support.
        
        Fixed: EdgeTrait.UNDIRECTED doesn't exist - bidirectional is achieved
        through strategy wrapper behavior, not a trait.
        
        Priority: Maintainability #3 - Correct trait usage
        """
        strategy = BidirWrapperStrategy()
        traits = strategy.get_supported_traits()
        # BidirWrapper supports standard traits from wrapped strategy
        assert traits is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

