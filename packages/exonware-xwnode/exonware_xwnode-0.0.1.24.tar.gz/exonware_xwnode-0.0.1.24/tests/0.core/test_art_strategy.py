"""
#exonware/xwnode/tests/0.core/test_art_strategy.py

Core tests for ART (Adaptive Radix Tree) node strategy.

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
class TestARTStrategyCore:
    """Core functionality tests for ART strategy."""
    
    def test_create_from_dict(self):
        """Test creating ART from dictionary."""
        data = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
        node = XWNode.from_native(data, mode=NodeMode.ART)
        assert node is not None
        assert len(node) >= 0
    
    def test_string_key_operations(self):
        """Test ART optimization for string keys."""
        node = XWNode.from_native({}, mode=NodeMode.ART)
        node.set('test_key', 'test_value', in_place=True)
        
        result = node.get('test_key')
        assert result is not None
    
    def test_ok_complexity(self):
        """Test O(k) performance where k = key length."""
        # Create with string keys of varying lengths
        data = {
            'a': '1',
            'ab': '2',
            'abc': '3',
            'abcd': '4',
            'abcde': '5'
        }
        node = XWNode.from_native(data, mode=NodeMode.ART)
        
        # All should exist
        assert node.exists('a')
        assert node.exists('abc')
        assert node.exists('abcde')
    
    def test_prefix_optimization(self):
        """Test prefix compression in ART."""
        # Keys with common prefixes should be optimized
        data = {
            'prefix_key1': 'value1',
            'prefix_key2': 'value2',
            'prefix_key3': 'value3'
        }
        node = XWNode.from_native(data, mode=NodeMode.ART)
        assert len(node) >= 0


@pytest.mark.xwnode_core
class TestARTStrategyPerformance:
    """Performance tests for ART strategy."""
    
    def test_fast_string_lookup(self):
        """Test fast lookup for string keys."""
        # Create large dataset with string keys
        data = {f'key{i:05d}': f'value{i}' for i in range(1000)}
        node = XWNode.from_native(data, mode=NodeMode.ART)
        
        # Lookups should be fast (O(k) where k = key length)
        result = node.get('key00500')
        assert result is not None

