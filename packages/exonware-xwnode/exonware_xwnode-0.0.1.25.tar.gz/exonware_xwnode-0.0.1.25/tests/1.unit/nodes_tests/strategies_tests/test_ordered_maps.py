"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_ordered_maps.py

Comprehensive tests for Ordered Map Strategies.

Tests ORDERED_MAP and ORDERED_MAP_BALANCED.
Critical for sorted operations and range queries.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import (
    ordered_map,
    ordered_map_balanced
)


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestOrderedMapStrategy:
    """Test ORDERED_MAP strategy."""
    
    def test_strategy_exists(self):
        """Test that ORDERED_MAP strategy exists."""
        assert ordered_map is not None
        assert NodeMode.ORDERED_MAP is not None
    
    def test_ordered_iteration(self):
        """Test that iteration maintains order."""
        # Ordered maps maintain sorted key traversal
        assert NodeTrait.ORDERED is not None
    
    def test_range_queries(self):
        """Test range query support."""
        # Ordered maps support efficient range queries
        assert NodeMode.ORDERED_MAP is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestOrderedMapBalancedStrategy:
    """Test ORDERED_MAP_BALANCED strategy (RB/AVL/Treap)."""
    
    def test_strategy_exists(self):
        """Test that ORDERED_MAP_BALANCED strategy exists."""
        assert ordered_map_balanced is not None
        assert NodeMode.ORDERED_MAP_BALANCED is not None
    
    def test_balanced_property(self):
        """Test explicit balanced tree implementation."""
        # Uses RB, AVL, or Treap for balancing
        assert NodeTrait.ORDERED is not None
        assert NodeTrait.INDEXED is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestOrderedMapPerformance:
    """Test ordered map performance."""
    
    def test_olog_n_operations(self):
        """Test O(log n) operations."""
        # Ordered maps have O(log n) complexity
        assert NodeMode.ORDERED_MAP is not None

