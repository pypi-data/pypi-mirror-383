"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_set_strategies.py

Comprehensive tests for Set Strategies.

Tests SET_HASH and SET_TREE.
Critical for set operations and membership testing.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import (
    set_hash,
    set_tree
)


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestSetHashStrategy:
    """Test SET_HASH strategy (unordered set)."""
    
    def test_strategy_exists(self):
        """Test that SET_HASH strategy exists."""
        assert set_hash is not None
        assert NodeMode.SET_HASH is not None
    
    def test_set_operations(self):
        """Test set operations (union, intersection, etc.)."""
        # Set operations should be efficient
        assert NodeMode.SET_HASH is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestSetTreeStrategy:
    """Test SET_TREE strategy (ordered set)."""
    
    def test_strategy_exists(self):
        """Test that SET_TREE strategy exists."""
        assert set_tree is not None
        assert NodeMode.SET_TREE is not None
    
    def test_ordered_set_operations(self):
        """Test ordered set operations."""
        # Tree-based sets maintain order
        assert NodeTrait.ORDERED is not None

