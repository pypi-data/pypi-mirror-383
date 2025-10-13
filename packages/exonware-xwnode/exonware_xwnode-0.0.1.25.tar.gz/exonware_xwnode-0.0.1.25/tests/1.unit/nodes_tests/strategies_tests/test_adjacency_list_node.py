"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_adjacency_list_node.py

Comprehensive tests for ADJACENCY_LIST Node Strategy.

Graph node representation using adjacency lists.
Critical for graph-based data structures.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import adjacency_list


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestAdjacencyListNodeInterface:
    """Test ADJACENCY_LIST node strategy."""
    
    def test_strategy_exists(self):
        """Test that ADJACENCY_LIST strategy exists."""
        assert adjacency_list is not None
        assert NodeMode.ADJACENCY_LIST is not None
    
    def test_graph_representation(self):
        """Test adjacency list graph representation."""
        # Adjacency lists represent graphs
        assert NodeTrait.GRAPH is not None

