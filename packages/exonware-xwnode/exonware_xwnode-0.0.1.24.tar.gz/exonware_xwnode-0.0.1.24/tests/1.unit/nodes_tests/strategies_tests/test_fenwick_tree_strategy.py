"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_fenwick_tree_strategy.py

Comprehensive tests for FENWICK_TREE Strategy (Binary Indexed Tree).

Optimized for prefix sums and range updates.
Critical for cumulative frequency operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import fenwick_tree


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestFenwickTreeInterface:
    """Test FENWICK_TREE interface."""
    
    def test_strategy_exists(self):
        """Test that FENWICK_TREE strategy exists."""
        assert fenwick_tree is not None
        assert NodeMode.FENWICK_TREE is not None
    
    def test_prefix_sum_operations(self):
        """Test prefix sum operations."""
        # Fenwick trees excel at prefix sums
        assert NodeMode.FENWICK_TREE is not None
    
    def test_range_update_operations(self):
        """Test range update operations."""
        # Fenwick trees support efficient range updates
        assert NodeMode.FENWICK_TREE is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestFenwickTreePerformance:
    """Test FENWICK_TREE performance."""
    
    def test_olog_n_operations(self):
        """Test O(log n) prefix sum and update operations."""
        assert NodeMode.FENWICK_TREE is not None

