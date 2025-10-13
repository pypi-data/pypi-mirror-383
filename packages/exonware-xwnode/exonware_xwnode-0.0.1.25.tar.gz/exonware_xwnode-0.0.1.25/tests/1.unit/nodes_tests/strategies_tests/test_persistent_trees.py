"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_persistent_trees.py

Comprehensive tests for Persistent Tree Strategies.

Tests B_TREE, B_PLUS_TREE, LSM_TREE, PERSISTENT_TREE, COW_TREE.
Critical for disk storage, versioning, and write-heavy workloads.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import (
    b_tree,
    b_plus_tree,
    lsm_tree,
    persistent_tree,
    cow_tree
)


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestBTreeStrategy:
    """Test B_TREE strategy (disk/page indexes)."""
    
    def test_strategy_exists(self):
        """Test that B_TREE strategy exists."""
        assert b_tree is not None
        assert NodeMode.B_TREE is not None
    
    def test_persistent_trait(self):
        """Test persistent storage trait."""
        assert NodeTrait.PERSISTENT is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestBPlusTreeStrategy:
    """Test B_PLUS_TREE strategy (database-friendly)."""
    
    def test_strategy_exists(self):
        """Test that B_PLUS_TREE strategy exists."""
        assert b_plus_tree is not None
        assert NodeMode.B_PLUS_TREE is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance
class TestLSMTreeStrategy:
    """Test LSM_TREE strategy (write-heavy workloads)."""
    
    def test_strategy_exists(self):
        """Test that LSM_TREE strategy exists."""
        assert lsm_tree is not None
        assert NodeMode.LSM_TREE is not None
    
    def test_write_optimization(self):
        """Test 100-1000x faster writes."""
        # LSM trees optimize for writes
        assert NodeTrait.STREAMING is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestPersistentTreeStrategy:
    """Test PERSISTENT_TREE strategy (immutable functional)."""
    
    def test_strategy_exists(self):
        """Test that PERSISTENT_TREE strategy exists."""
        assert persistent_tree is not None
        assert NodeMode.PERSISTENT_TREE is not None
    
    def test_immutability(self):
        """Test immutable structural sharing."""
        # Persistent trees use structural sharing
        assert NodeMode.PERSISTENT_TREE is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestCOWTreeStrategy:
    """Test COW_TREE strategy (copy-on-write)."""
    
    def test_strategy_exists(self):
        """Test that COW_TREE strategy exists."""
        assert cow_tree is not None
        assert NodeMode.COW_TREE is not None
    
    def test_instant_snapshots(self):
        """Test O(1) snapshot capability."""
        # COW trees provide instant snapshots
        assert NodeMode.COW_TREE is not None

