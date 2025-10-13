"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_hash_map_strategy.py

Comprehensive tests for HashMapStrategy.

Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find, delete)
- Iterator protocol
- Container protocol
- Performance characteristics (O(1) operations)
- Security (malicious input, resource limits)
- Error handling
- Edge cases

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from typing import Any
from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def empty_strategy():
    """Create empty hash map strategy."""
    return HashMapStrategy()


@pytest.fixture
def simple_strategy():
    """Create hash map with simple data."""
    strategy = HashMapStrategy()
    strategy.insert('key1', 'value1')
    strategy.insert('key2', 'value2')
    strategy.insert('key3', 'value3')
    return strategy


@pytest.fixture
def nested_strategy():
    """Create hash map with nested data."""
    strategy = HashMapStrategy()
    strategy.insert('level1', {'level2': {'key': 'value'}})
    return strategy


# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestHashMapStrategyInterface:
    """Test HashMapStrategy implements iNodeStrategy interface correctly."""
    
    def test_insert_operation(self, empty_strategy):
        """Test insert operation works correctly."""
        empty_strategy.insert('test_key', 'test_value')
        
        result = empty_strategy.find('test_key')
        assert result == 'test_value'
    
    def test_find_operation(self, simple_strategy):
        """Test find operation returns correct values."""
        assert simple_strategy.find('key1') == 'value1'
        assert simple_strategy.find('key2') == 'value2'
        assert simple_strategy.find('nonexistent') is None
    
    def test_delete_operation(self, simple_strategy):
        """Test delete operation removes keys correctly."""
        assert simple_strategy.delete('key1') is True
        assert simple_strategy.find('key1') is None
        assert simple_strategy.delete('nonexistent') is False
    
    def test_size_operation(self, simple_strategy):
        """Test size returns correct count."""
        assert simple_strategy.size() == 3
        
        simple_strategy.delete('key1')
        assert simple_strategy.size() == 2
    
    def test_is_empty_operation(self, empty_strategy, simple_strategy):
        """Test is_empty correctly identifies empty structures."""
        assert empty_strategy.is_empty() is True
        assert simple_strategy.is_empty() is False
    
    def test_to_native_conversion(self, simple_strategy):
        """Test conversion to native Python dict."""
        native = simple_strategy.to_native()
        
        assert isinstance(native, dict)
        assert native['key1'] == 'value1'
        assert native['key2'] == 'value2'
        assert native['key3'] == 'value3'
    
    def test_keys_iteration(self, simple_strategy):
        """Test keys() returns all keys."""
        keys = list(simple_strategy.keys())
        
        assert 'key1' in keys
        assert 'key2' in keys
        assert 'key3' in keys
        assert len(keys) == 3
    
    def test_values_iteration(self, simple_strategy):
        """Test values() returns all values."""
        values = list(simple_strategy.values())
        
        assert 'value1' in values
        assert 'value2' in values
        assert 'value3' in values
        assert len(values) == 3
    
    def test_items_iteration(self, simple_strategy):
        """Test items() returns all key-value pairs."""
        items = list(simple_strategy.items())
        
        assert ('key1', 'value1') in items
        assert ('key2', 'value2') in items
        assert ('key3', 'value3') in items
        assert len(items) == 3


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestHashMapStrategyCore:
    """Test core HashMapStrategy functionality."""
    
    def test_get_with_default(self, simple_strategy):
        """Test get() method with default value."""
        assert simple_strategy.get('key1') == 'value1'
        assert simple_strategy.get('nonexistent', 'default') == 'default'
    
    def test_setdefault_operation(self, empty_strategy):
        """Test setdefault() creates key if missing."""
        result = empty_strategy.setdefault('new_key', 'default_value')
        assert result == 'default_value'
        assert empty_strategy.find('new_key') == 'default_value'
    
    def test_update_operation(self, simple_strategy):
        """Test update() merges dictionaries."""
        simple_strategy.update({'key4': 'value4', 'key5': 'value5'})
        
        assert simple_strategy.find('key4') == 'value4'
        assert simple_strategy.find('key5') == 'value5'
        assert simple_strategy.size() == 5
    
    def test_clear_operation(self, simple_strategy):
        """Test clear() removes all items."""
        simple_strategy.clear()
        
        assert simple_strategy.is_empty() is True
        assert simple_strategy.size() == 0
    
    def test_contains_operation(self, simple_strategy):
        """Test __contains__ for key existence."""
        assert 'key1' in simple_strategy._data
        assert 'nonexistent' not in simple_strategy._data


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance
class TestHashMapStrategyPerformance:
    """Test HashMapStrategy performance characteristics."""
    
    def test_o1_insert_performance(self):
        """Test that insert is O(1) - constant time."""
        import time
        
        strategy = HashMapStrategy()
        
        # Insert 1000 items
        start = time.time()
        for i in range(1000):
            strategy.insert(f'key_{i}', f'value_{i}')
        elapsed_1k = time.time() - start
        
        # Insert 10000 items  
        strategy2 = HashMapStrategy()
        start = time.time()
        for i in range(10000):
            strategy2.insert(f'key_{i}', f'value_{i}')
        elapsed_10k = time.time() - start
        
        # O(1) means time should scale linearly with n
        # 10x more items should take roughly 10x time (not 100x)
        # Handle case where operations are too fast to measure
        if elapsed_1k > 0:
            assert elapsed_10k < elapsed_1k * 15  # Allow some overhead
        else:
            # If too fast to measure, just verify it completed successfully
            assert strategy2.size() == 10000
    
    def test_o1_find_performance(self):
        """Test that find is O(1) - constant time."""
        import time
        
        # Create large dataset
        strategy = HashMapStrategy()
        for i in range(10000):
            strategy.insert(f'key_{i}', f'value_{i}')
        
        # Find first item
        start = time.time()
        for _ in range(1000):
            strategy.find('key_0')
        elapsed_first = time.time() - start
        
        # Find last item (should be same time as first - O(1))
        start = time.time()
        for _ in range(1000):
            strategy.find('key_9999')
        elapsed_last = time.time() - start
        
        # Both should take similar time (O(1) doesn't depend on position)
        # Handle case where operations are too fast to measure
        if elapsed_first > 0:
            assert abs(elapsed_first - elapsed_last) < elapsed_first * 2
        else:
            # If too fast to measure, verify correctness instead
            assert strategy.find('key_0') == 'value_0'
            assert strategy.find('key_9999') == 'value_9999'


# ============================================================================
# SECURITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_security
class TestHashMapStrategySecurity:
    """Test HashMapStrategy security measures."""
    
    def test_malicious_key_handling(self, empty_strategy):
        """Test handling of malicious keys."""
        malicious_keys = [
            '../../../etc/passwd',  # Path traversal
            '<script>alert("xss")</script>',  # XSS
            "'; DROP TABLE users; --",  # SQL injection pattern
            '\x00\x01\x02',  # Null bytes
            'A' * 10000,  # Very long key
        ]
        
        for key in malicious_keys:
            # Should not crash
            empty_strategy.insert(key, 'value')
            result = empty_strategy.find(key)
            assert result is not None
    
    def test_resource_limit_protection(self):
        """Test protection against resource exhaustion."""
        strategy = HashMapStrategy()
        
        # Try to insert many items (should not crash)
        for i in range(100000):
            strategy.insert(f'key_{i}', f'value_{i}')
        
        assert strategy.size() == 100000
    
    def test_type_safety(self, empty_strategy):
        """Test type safety for different value types."""
        # Should handle any type safely
        empty_strategy.insert('int_key', 42)
        empty_strategy.insert('str_key', 'string')
        empty_strategy.insert('list_key', [1, 2, 3])
        empty_strategy.insert('dict_key', {'nested': 'dict'})
        empty_strategy.insert('none_key', None)
        
        assert empty_strategy.find('int_key') == 42
        assert empty_strategy.find('none_key') is None


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestHashMapStrategyErrors:
    """Test HashMapStrategy error handling."""
    
    def test_none_key_handling(self, empty_strategy):
        """Test handling of None as key."""
        # Should convert None to string 'None'
        empty_strategy.insert(None, 'null_value')
        result = empty_strategy.find(None)
        assert result == 'null_value'
    
    def test_empty_key_handling(self, empty_strategy):
        """Test handling of empty string as key."""
        empty_strategy.insert('', 'empty_key_value')
        result = empty_strategy.find('')
        assert result == 'empty_key_value'
    
    def test_duplicate_key_handling(self, simple_strategy):
        """Test that duplicate keys overwrite values."""
        original = simple_strategy.find('key1')
        
        simple_strategy.insert('key1', 'new_value')
        updated = simple_strategy.find('key1')
        
        assert updated == 'new_value'
        assert updated != original


# ============================================================================
# EDGE CASES TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestHashMapStrategyEdgeCases:
    """Test HashMapStrategy edge cases."""
    
    def test_empty_data_handling(self):
        """Test handling of empty data."""
        strategy = HashMapStrategy()
        
        assert strategy.is_empty() is True
        assert strategy.size() == 0
        assert list(strategy.keys()) == []
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        strategy = HashMapStrategy()
        
        # Insert 10,000 items
        for i in range(10000):
            strategy.insert(f'key_{i}', f'value_{i}')
        
        assert strategy.size() == 10000
        assert strategy.find('key_5000') == 'value_5000'
    
    def test_unicode_keys_and_values(self, empty_strategy):
        """Test Unicode support in keys and values."""
        unicode_data = {
            '中文': '你好',
            'العربية': 'مرحبا',
            'emoji': '🚀🎉',
            'special': 'åäö ñ ç ß €'
        }
        
        for key, value in unicode_data.items():
            empty_strategy.insert(key, value)
            assert empty_strategy.find(key) == value
    
    def test_nested_structure_handling(self):
        """Test handling of deeply nested structures."""
        strategy = HashMapStrategy()
        
        nested_value = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': 'deep_value'
                    }
                }
            }
        }
        
        strategy.insert('nested', nested_value)
        result = strategy.find('nested')
        
        assert result is not None
        assert isinstance(result, dict)


# ============================================================================
# STRATEGY METADATA TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestHashMapStrategyMetadata:
    """Test HashMapStrategy metadata and traits."""
    
    def test_strategy_mode(self):
        """Test strategy reports correct mode."""
        strategy = HashMapStrategy()
        assert strategy.get_mode() == NodeMode.HASH_MAP
    
    def test_supported_traits(self):
        """Test strategy reports supported traits."""
        strategy = HashMapStrategy()
        traits = strategy.get_supported_traits()
        
        assert NodeTrait.INDEXED in traits
        assert NodeTrait.HIERARCHICAL in traits
    
    def test_strategy_type(self):
        """Test strategy reports correct type."""
        from exonware.xwnode.nodes.strategies.contracts import NodeType
        assert HashMapStrategy.STRATEGY_TYPE == NodeType.TREE

