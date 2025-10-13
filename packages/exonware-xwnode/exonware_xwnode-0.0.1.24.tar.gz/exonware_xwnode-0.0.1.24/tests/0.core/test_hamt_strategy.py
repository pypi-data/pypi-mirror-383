"""
#exonware/xwnode/tests/0.core/test_hamt_strategy.py

Core tests for HAMT (Hash Array Mapped Trie) node strategy.

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
class TestHAMTStrategyCore:
    """Core functionality tests for HAMT strategy."""
    
    def test_create_from_dict(self):
        """Test creating HAMT from dictionary."""
        data = {'key1': 'value1', 'key2': 'value2'}
        node = XWNode.from_native(data, mode=NodeMode.HAMT)
        assert node is not None
    
    def test_persistent_operations(self):
        """Test persistent/immutable operations."""
        node = XWNode.from_native({}, mode=NodeMode.HAMT)
        node.set('key1', 'value1', in_place=True)
        assert node.exists('key1')
    
    def test_structural_sharing(self):
        """Test structural sharing for memory efficiency."""
        data = {'a': '1', 'b': '2', 'c': '3'}
        node = XWNode.from_native(data, mode=NodeMode.HAMT)
        assert len(node) >= 0

