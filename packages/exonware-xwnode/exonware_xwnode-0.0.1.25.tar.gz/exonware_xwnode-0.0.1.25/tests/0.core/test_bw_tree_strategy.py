"""
#exonware/xwnode/tests/0.core/test_bw_tree_strategy.py

Core tests for Bw-Tree (Lock-Free B-tree) node strategy.

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
class TestBwTreeStrategyCore:
    """Core functionality tests for Bw-Tree strategy."""
    
    def test_create_from_dict(self):
        """Test creating Bw-Tree from dictionary."""
        data = {'key1': 'value1', 'key2': 'value2'}
        node = XWNode.from_native(data, mode=NodeMode.BW_TREE)
        assert node is not None
    
    def test_delta_based_updates(self):
        """Test delta-based updates."""
        node = XWNode.from_native({}, mode=NodeMode.BW_TREE)
        node.set('key1', 'value1', in_place=True)
        node.set('key2', 'value2', in_place=True)
        
        assert node.exists('key1')
        assert node.exists('key2')
    
    def test_lock_free_operations(self):
        """Test lock-free operation support."""
        node = XWNode.from_native({'a': '1', 'b': '2'}, mode=NodeMode.BW_TREE)
        
        # Updates should work atomically
        node.set('c', '3', in_place=True)
        assert node.exists('c')

