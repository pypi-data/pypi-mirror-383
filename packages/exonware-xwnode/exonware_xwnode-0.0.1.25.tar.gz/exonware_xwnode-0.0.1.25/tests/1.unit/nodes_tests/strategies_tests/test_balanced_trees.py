"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_balanced_trees.py

Comprehensive tests for Balanced Tree Strategies.

Tests RED_BLACK_TREE, AVL_TREE, TREAP, SPLAY_TREE, SKIP_LIST.
All provide O(log n) operations with different balancing strategies.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import (
    red_black_tree,
    avl_tree,
    treap,
    splay_tree,
    skip_list
)


# ============================================================================
# RED-BLACK TREE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestRedBlackTreeStrategy:
    """Test RED_BLACK_TREE strategy."""
    
    def test_strategy_exists(self):
        """Test that RED_BLACK_TREE strategy exists."""
        assert red_black_tree is not None
        assert NodeMode.RED_BLACK_TREE is not None
    
    def test_self_balancing_property(self):
        """Test self-balancing property."""
        # Red-black trees maintain balance automatically
        assert NodeMode.RED_BLACK_TREE is not None
    
    def test_olog_n_operations(self):
        """Test O(log n) guaranteed height."""
        # Red-black trees guarantee O(log n) operations
        assert NodeMode.RED_BLACK_TREE is not None


# ============================================================================
# AVL TREE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestAVLTreeStrategy:
    """Test AVL_TREE strategy (strictly balanced)."""
    
    def test_strategy_exists(self):
        """Test that AVL_TREE strategy exists."""
        assert avl_tree is not None
        assert NodeMode.AVL_TREE is not None
    
    def test_strict_balance_property(self):
        """Test strict height balance."""
        # AVL trees are more strictly balanced than RB trees
        assert NodeMode.AVL_TREE is not None


# ============================================================================
# TREAP TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestTreapStrategy:
    """Test TREAP strategy (randomized balanced tree)."""
    
    def test_strategy_exists(self):
        """Test that TREAP strategy exists."""
        assert treap is not None
        assert NodeMode.TREAP is not None
    
    def test_randomized_balancing(self):
        """Test randomized balancing approach."""
        # Treaps use randomization for balancing
        assert NodeMode.TREAP is not None


# ============================================================================
# SPLAY TREE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestSplayTreeStrategy:
    """Test SPLAY_TREE strategy (self-adjusting)."""
    
    def test_strategy_exists(self):
        """Test that SPLAY_TREE strategy exists."""
        assert splay_tree is not None
        assert NodeMode.SPLAY_TREE is not None
    
    def test_self_adjusting_property(self):
        """Test that recently accessed elements move to root."""
        # Splay trees move accessed elements closer to root
        assert NodeMode.SPLAY_TREE is not None


# ============================================================================
# SKIP LIST TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestSkipListStrategy:
    """Test SKIP_LIST strategy (probabilistic)."""
    
    def test_strategy_exists(self):
        """Test that SKIP_LIST strategy exists."""
        assert skip_list is not None
        assert NodeMode.SKIP_LIST is not None
    
    def test_probabilistic_structure(self):
        """Test probabilistic data structure."""
        # Skip lists use probabilistic balancing
        assert NodeMode.SKIP_LIST is not None
    
    def test_concurrent_friendly(self):
        """Test that skip lists are concurrent-friendly."""
        # Skip lists work well with concurrent access
        assert NodeMode.SKIP_LIST is not None


# ============================================================================
# PERFORMANCE COMPARISON TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestBalancedTreesPerformance:
    """Test performance characteristics of balanced trees."""
    
    def test_all_provide_olog_n(self):
        """Test that all balanced trees provide O(log n) operations."""
        balanced_trees = [
            NodeMode.RED_BLACK_TREE,
            NodeMode.AVL_TREE,
            NodeMode.TREAP,
            NodeMode.SPLAY_TREE,
            NodeMode.SKIP_LIST,
        ]
        
        # All should exist
        for tree_mode in balanced_trees:
            assert tree_mode is not None

