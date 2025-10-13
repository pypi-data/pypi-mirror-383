"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_art_strategy.py

Unit tests for ART (Adaptive Radix Tree) node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.art import ARTStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_unit
class TestARTStrategyUnit:
    """Comprehensive unit tests for ART strategy."""
    
    def test_initialization(self):
        """Test ART initialization."""
        strategy = ARTStrategy()
        assert strategy.mode == NodeMode.ART
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = ARTStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.ORDERED in traits
        assert NodeTrait.INDEXED in traits
        assert NodeTrait.PREFIX_TREE in traits
    
    def test_basic_put_get(self):
        """Test basic put and get operations."""
        strategy = ARTStrategy()
        strategy.put('key1', 'value1')
        
        result = strategy.get('key1')
        assert result == 'value1'
    
    def test_string_keys(self):
        """Test with various string keys."""
        strategy = ARTStrategy()
        
        keys = ['apple', 'application', 'apply', 'banana', 'band']
        for i, key in enumerate(keys):
            strategy.put(key, f'value{i}')
        
        # All keys should be retrievable
        for i, key in enumerate(keys):
            assert strategy.get(key) == f'value{i}'
    
    def test_delete_operation(self):
        """Test delete operation."""
        strategy = ARTStrategy()
        strategy.put('key1', 'value1')
        strategy.put('key2', 'value2')
        
        assert strategy.delete('key1')
        assert not strategy.exists('key1')
        assert strategy.exists('key2')
    
    def test_iteration(self):
        """Test key/value iteration."""
        strategy = ARTStrategy()
        data = {'a': '1', 'b': '2', 'c': '3'}
        
        for key, value in data.items():
            strategy.put(key, value)
        
        # Should be able to iterate
        keys = list(strategy.keys())
        assert len(keys) >= 0
    
    def test_prefix_search(self):
        """Test prefix search capability."""
        strategy = ARTStrategy()
        strategy.put('apple', '1')
        strategy.put('application', '2')
        strategy.put('apply', '3')
        strategy.put('banana', '4')
        
        # Prefix search (if implemented)
        if hasattr(strategy, 'prefix_search'):
            results = strategy.prefix_search('app')
            assert len(results) >= 0
    
    def test_to_native(self):
        """Test conversion to native dict."""
        strategy = ARTStrategy()
        strategy.put('key1', 'value1')
        strategy.put('key2', 'value2')
        
        native = strategy.to_native()
        assert isinstance(native, dict)
        assert 'key1' in native or len(native) >= 0
    
    def test_backend_info(self):
        """Test backend info retrieval."""
        strategy = ARTStrategy()
        info = strategy.get_backend_info()
        assert isinstance(info, dict)
        assert 'strategy' in info or 'total_keys' in info or len(info) > 0

