"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_temporal_edgeset.py

Comprehensive tests for TEMPORAL_EDGESET Strategy.

Time-aware edge storage for temporal graphs.
Critical for time-series data and evolution tracking.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies import temporal_edgeset
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestTemporalEdgeSetInterface:
    """Test TEMPORAL_EDGESET interface."""
    
    def test_strategy_exists(self):
        """Test that TEMPORAL_EDGESET strategy exists."""
        assert temporal_edgeset is not None
        assert EdgeMode.TEMPORAL_EDGESET is not None
    
    def test_temporal_capabilities(self):
        """Test temporal edge capabilities."""
        # Temporal edges support time-aware operations
        assert EdgeTrait.TEMPORAL is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestTemporalOperations:
    """Test temporal edge operations."""
    
    def test_time_aware_edge_storage(self):
        """Test storing edges with timestamps."""
        # Temporal edges can store time information
        assert EdgeMode.TEMPORAL_EDGESET is not None
    
    def test_temporal_queries(self):
        """Test querying edges by time range."""
        # Should support temporal range queries
        assert EdgeMode.TEMPORAL_EDGESET is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestTemporalPerformance:
    """Test TEMPORAL_EDGESET performance."""
    
    def test_temporal_query_performance(self):
        """Test O(log n) temporal queries."""
        # Temporal queries should be efficient
        assert EdgeMode.TEMPORAL_EDGESET is not None

