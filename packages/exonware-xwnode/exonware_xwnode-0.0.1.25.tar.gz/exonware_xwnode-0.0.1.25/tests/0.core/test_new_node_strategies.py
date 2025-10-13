"""
#exonware/xwnode/tests/0.core/test_new_node_strategies.py

Core tests for new node strategies (Masstree, Extendible Hash, Linear Hash, T-Tree, Learned Index).

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode


@pytest.mark.xwnode_core
class TestMasstreeStrategyCore:
    """Core tests for Masstree strategy."""
    
    def test_create_and_operations(self):
        """Test Masstree creation and basic operations."""
        data = {'key1': 'value1', 'key2': 'value2'}
        node = XWNode.from_native(data, mode=NodeMode.MASSTREE)
        assert node is not None
        assert node.exists('key1')


@pytest.mark.xwnode_core
class TestExtendibleHashStrategyCore:
    """Core tests for Extendible Hash strategy."""
    
    def test_create_and_operations(self):
        """Test Extendible Hash creation and operations."""
        node = XWNode.from_native({}, mode=NodeMode.EXTENDIBLE_HASH)
        node.set('key1', 'value1', in_place=True)
        assert node.exists('key1')


@pytest.mark.xwnode_core
class TestLinearHashStrategyCore:
    """Core tests for Linear Hash strategy."""
    
    def test_create_and_operations(self):
        """Test Linear Hash creation and operations."""
        data = {'key1': 'value1'}
        node = XWNode.from_native(data, mode=NodeMode.LINEAR_HASH)
        assert node is not None


@pytest.mark.xwnode_core
class TestTTreeStrategyCore:
    """Core tests for T-Tree strategy."""
    
    def test_create_and_operations(self):
        """Test T-Tree creation and operations."""
        node = XWNode.from_native({'a': '1', 'b': '2'}, mode=NodeMode.T_TREE)
        assert node.exists('a')


@pytest.mark.xwnode_core
class TestLearnedIndexStrategyCore:
    """Core tests for Learned Index strategy (placeholder)."""
    
    def test_create_with_placeholder(self):
        """Test Learned Index creates successfully (delegates to ORDERED_MAP)."""
        data = {'key1': 'value1', 'key2': 'value2'}
        node = XWNode.from_native(data, mode=NodeMode.LEARNED_INDEX)
        assert node is not None
    
    def test_placeholder_delegation(self):
        """Test that operations work via delegation."""
        node = XWNode.from_native({}, mode=NodeMode.LEARNED_INDEX)
        node.set('test', 'value', in_place=True)
        assert node.exists('test')

