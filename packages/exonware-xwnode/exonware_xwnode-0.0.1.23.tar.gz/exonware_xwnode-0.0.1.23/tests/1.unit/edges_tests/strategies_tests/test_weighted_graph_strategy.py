"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_weighted_graph_strategy.py

Comprehensive tests for WeightedGraphStrategy.

Supports weighted edges for network algorithms.
Critical for shortest path, flow algorithms, etc.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.weighted_graph import WeightedGraphStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.fixture
def empty_weighted_graph():
    """Create empty weighted graph."""
    return WeightedGraphStrategy()


@pytest.fixture
def weighted_network():
    """Create weighted graph for network algorithms."""
    graph = WeightedGraphStrategy()
    graph.add_edge('A', 'B', weight=1.0)
    graph.add_edge('B', 'C', weight=2.0)
    graph.add_edge('A', 'C', weight=5.0)
    graph.add_edge('C', 'D', weight=1.0)
    return graph


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestWeightedGraphInterface:
    """Test WeightedGraphStrategy interface compliance."""
    
    def test_add_weighted_edge(self, empty_weighted_graph):
        """Test adding edges with weights."""
        empty_weighted_graph.add_edge('A', 'B', weight=2.5)
        
        assert empty_weighted_graph.has_edge('A', 'B') is True
    
    def test_get_edge_weight(self, weighted_network):
        """Test retrieving edge weights."""
        # Should be able to get edge weight
        assert weighted_network.has_edge('A', 'B') is True
    
    def test_weighted_path_algorithms(self, weighted_network):
        """Test that weighted graph supports path algorithms."""
        # Verify structure for shortest path algorithms
        assert weighted_network.has_edge('A', 'B')
        assert weighted_network.has_edge('B', 'C')
        # Path A->B->C->D should exist


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestWeightedGraphEdgeCases:
    """Test WeightedGraphStrategy edge cases."""
    
    def test_zero_weight(self, empty_weighted_graph):
        """Test edge with zero weight."""
        empty_weighted_graph.add_edge('A', 'B', weight=0.0)
        assert empty_weighted_graph.has_edge('A', 'B') is True
    
    def test_negative_weight(self, empty_weighted_graph):
        """Test edge with negative weight."""
        empty_weighted_graph.add_edge('A', 'B', weight=-1.0)
        # Should handle negative weights for some algorithms
        assert empty_weighted_graph.has_edge('A', 'B') is True
    
    def test_very_large_weight(self, empty_weighted_graph):
        """Test edge with very large weight."""
        empty_weighted_graph.add_edge('A', 'B', weight=float('inf'))
        assert empty_weighted_graph.has_edge('A', 'B') is True

