"""
Unit tests for TEMPORAL_EDGESET edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.temporal_edgeset import TemporalEdgeSetStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestTemporalEdgeSetCore:
    """Core tests for TEMPORAL_EDGESET edge strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = TemporalEdgeSetStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.TEMPORAL_EDGESET
        assert len(strategy) == 0
    
    def test_add_temporal_edge(self, temporal_dataset):
        """Test adding edges with timestamps."""
        strategy = TemporalEdgeSetStrategy()
        edges = temporal_dataset(num_edges=20)
        
        for src, tgt, props in edges:
            edge_id = strategy.add_edge(src, tgt, **props)
            assert edge_id is not None
        
        assert len(strategy) == 20
    
    def test_time_range_query(self):
        """Test temporal range queries."""
        strategy = TemporalEdgeSetStrategy()
        strategy.add_edge("v1", "v2", timestamp=100.0)
        strategy.add_edge("v2", "v3", timestamp=200.0)
        strategy.add_edge("v3", "v4", timestamp=300.0)
        
        # Query edges in time range
        edges = list(strategy.range_query_time(150.0, 250.0))
        assert len(edges) >= 1
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = TemporalEdgeSetStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.TEMPORAL in traits


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

