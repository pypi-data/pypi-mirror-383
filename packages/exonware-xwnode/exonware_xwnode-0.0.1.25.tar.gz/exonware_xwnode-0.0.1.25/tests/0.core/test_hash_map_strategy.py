"""
#exonware/xwnode/tests/0.core/test_hash_map_strategy.py

Comprehensive tests for HASH_MAP node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeValueError


@pytest.mark.xwnode_core
class TestHashMapCore:
    """Core functionality tests for HASH_MAP strategy."""
    
    def test_initialization_default(self):
        """Test initialization with default options."""
        strategy = HashMapStrategy()
        assert strategy is not None
        assert len(strategy) == 0
        assert strategy.mode == NodeMode.HASH_MAP
        assert strategy.is_empty
    
    def test_initialization_with_options(self):
        """Test initialization with custom options."""
        strategy = HashMapStrategy(traits=NodeTrait.INDEXED)
        assert strategy.traits == NodeTrait.INDEXED
    
    def test_basic_put_get(self):
        """Test basic put and get operations."""
        strategy = HashMapStrategy()
        strategy.put("key1", "value1")
        assert strategy.get("key1") == "value1"
    
    def test_basic_has(self):
        """Test has/contains operations."""
        strategy = HashMapStrategy()
        strategy.put("key1", "value1")
        assert strategy.has("key1")
        assert not strategy.has("nonexistent")
        assert "key1" in strategy  # __contains__
    
    def test_basic_delete(self):
        """Test delete operation."""
        strategy = HashMapStrategy()
        strategy.put("key1", "value1")
        assert strategy.delete("key1")
        assert not strategy.has("key1")
        assert not strategy.delete("nonexistent")
    
    def test_multiple_keys(self):
        """Test storing multiple key-value pairs."""
        strategy = HashMapStrategy()
        for i in range(100):
            strategy.put(f"key_{i}", f"value_{i}")
        
        assert len(strategy) == 100
        assert strategy.get("key_50") == "value_50"
    
    def test_update_existing_key(self):
        """Test updating existing key with new value."""
        strategy = HashMapStrategy()
        strategy.put("key", "value1")
        strategy.put("key", "value2")
        
        assert strategy.get("key") == "value2"
        assert len(strategy) == 1  # No duplicate keys
    
    def test_get_with_default(self):
        """Test get with default value for missing keys."""
        strategy = HashMapStrategy()
        assert strategy.get("nonexistent", "default") == "default"
        assert strategy.get("nonexistent") is None
    
    def test_iteration_keys(self):
        """Test iteration over keys."""
        strategy = HashMapStrategy()
        data = {"a": 1, "b": 2, "c": 3}
        for k, v in data.items():
            strategy.put(k, v)
        
        keys = list(strategy.keys())
        assert len(keys) == 3
        assert set(keys) == {"a", "b", "c"}
    
    def test_iteration_values(self):
        """Test iteration over values."""
        strategy = HashMapStrategy()
        data = {"a": 1, "b": 2, "c": 3}
        for k, v in data.items():
            strategy.put(k, v)
        
        values = list(strategy.values())
        assert len(values) == 3
        assert set(values) == {1, 2, 3}
    
    def test_iteration_items(self):
        """Test iteration over key-value pairs."""
        strategy = HashMapStrategy()
        data = {"a": 1, "b": 2, "c": 3}
        for k, v in data.items():
            strategy.put(k, v)
        
        items = list(strategy.items())
        assert len(items) == 3
        assert dict(items) == data
    
    def test_clear(self):
        """Test clearing all data."""
        strategy = HashMapStrategy()
        for i in range(10):
            strategy.put(f"key_{i}", i)
        
        strategy.clear()
        assert len(strategy) == 0
        assert strategy.is_empty
    
    def test_to_native(self):
        """Test conversion to native Python dict."""
        strategy = HashMapStrategy()
        data = {"a": 1, "b": "two", "c": [3, 4]}
        for k, v in data.items():
            strategy.put(k, v)
        
        native = strategy.to_native()
        assert isinstance(native, dict)
        assert native == data
    
    def test_special_methods_getitem(self):
        """Test __getitem__ protocol."""
        strategy = HashMapStrategy()
        strategy.put("key", "value")
        assert strategy["key"] == "value"
    
    def test_special_methods_setitem(self):
        """Test __setitem__ protocol."""
        strategy = HashMapStrategy()
        strategy["key"] = "value"
        assert strategy.get("key") == "value"
    
    def test_special_methods_delitem(self):
        """Test __delitem__ protocol."""
        strategy = HashMapStrategy()
        strategy.put("key", "value")
        del strategy["key"]
        assert not strategy.has("key")
    
    def test_special_methods_delitem_missing_raises(self):
        """Test __delitem__ raises KeyError for missing keys."""
        strategy = HashMapStrategy()
        with pytest.raises(KeyError):
            del strategy["nonexistent"]
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = HashMapStrategy()
        supported = strategy.get_supported_traits()
        assert NodeTrait.NONE in supported or supported == NodeTrait.NONE


@pytest.mark.xwnode_performance
class TestHashMapPerformance:
    """Performance validation tests for HASH_MAP strategy."""
    
    def test_time_complexity_o1_get(self):
        """Validate O(1) average-case get operation."""
        import time
        
        # Pre-create strategies of different sizes
        strategies = {}
        for size in [100, 1000, 10000]:
            s = HashMapStrategy()
            for i in range(size):
                s.put(f"key_{i}", i)
            strategies[size] = s
        
        # Measure ONLY the get operation
        timings = {}
        for size, strategy in strategies.items():
            measurements = []
            for _ in range(100):  # Multiple iterations for accuracy
                start = time.perf_counter()
                strategy.get(f"key_{size//2}")
                elapsed = time.perf_counter() - start
                measurements.append(elapsed)
            
            measurements.sort()
            timings[size] = measurements[len(measurements)//2]  # Median
        
        # O(1): time should be roughly constant regardless of size
        ratio = timings[10000] / timings[100]
        assert ratio < 3.0, (
            f"Expected O(1) get operation, but ratio {ratio:.2f} indicates non-constant time. "
            f"Timings: {timings}"
        )
    
    def test_time_complexity_o1_put(self):
        """Validate O(1) average-case put operation."""
        import time
        
        # Pre-create strategies of different sizes
        timings = {}
        for size in [100, 1000, 10000]:
            strategy = HashMapStrategy()
            # Pre-fill to size
            for i in range(size):
                strategy.put(f"key_{i}", i)
            
            # Measure ONLY a single put operation (amortized O(1))
            measurements = []
            for j in range(100):  # Multiple iterations
                start = time.perf_counter()
                strategy.put(f"new_key_{j}", j)
                elapsed = time.perf_counter() - start
                measurements.append(elapsed)
            
            measurements.sort()
            timings[size] = measurements[len(measurements)//2]  # Median
        
        # O(1): time should be roughly constant
        ratio = timings[10000] / timings[100]
        assert ratio < 3.0, f"Expected O(1) put, got ratio {ratio:.2f}"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage is reasonable for hash map."""
        def operation():
            strategy = HashMapStrategy()
            for i in range(1000):
                strategy.put(f"key_{i}", i)
            return strategy
        
        result, memory_bytes = measure_memory(operation)
        
        # Hash maps have overhead, but should be reasonable
        # < 300KB for 1000 items is acceptable
        max_expected = 300 * 1024
        assert memory_bytes < max_expected, (
            f"Memory usage {memory_bytes} bytes exceeds {max_expected}. "
            f"This indicates potential memory inefficiency."
        )
    
    def test_performance_vs_stdlib_dict(self, benchmark_vs_stdlib):
        """Compare against Python's built-in dict."""
        def strategy_op(size):
            strategy = HashMapStrategy()
            for i in range(size):
                strategy.put(f"k{i}", i)
        
        def stdlib_op(size):
            data = {}
            for i in range(size):
                data[f"k{i}"] = i
        
        results = benchmark_vs_stdlib(strategy_op, stdlib_op, 1000)
        
        # Strategy should be within 10x of stdlib (reasonable overhead for abstraction)
        assert results['ratio'] < 10.0, (
            f"Hash Map is {results['ratio']:.2f}x slower than stdlib dict. "
            f"Expected < 10.0x. {results['message']}"
        )


@pytest.mark.xwnode_core
class TestHashMapEdgeCases:
    """Edge case and error handling tests."""
    
    def test_empty_strategy_operations(self):
        """Test operations on empty strategy."""
        strategy = HashMapStrategy()
        assert len(strategy) == 0
        assert strategy.is_empty
        assert strategy.get("any") is None
        assert not strategy.has("any")
        assert not strategy.delete("any")
    
    def test_single_item_operations(self):
        """Test with single item."""
        strategy = HashMapStrategy()
        strategy.put("only", "one")
        assert len(strategy) == 1
        assert strategy.get("only") == "one"
        strategy.delete("only")
        assert strategy.is_empty
    
    def test_large_dataset_10k(self, large_dataset):
        """Test with 10,000 items."""
        strategy = HashMapStrategy()
        for k, v in large_dataset.items():
            strategy.put(k, v)
        
        assert len(strategy) == 10000
        assert strategy.get("key_5000") == "value_5000"
    
    def test_unicode_keys(self, multilingual_data):
        """Test Unicode and emoji keys."""
        strategy = HashMapStrategy()
        for k, v in multilingual_data.items():
            strategy.put(k, v)
        
        assert strategy.get("chinese") == "你好世界"
        assert strategy.get("emoji") == "🌍🌎🌏 Hello 👋"
    
    def test_mixed_type_values(self, mixed_type_data):
        """Test with mixed value types."""
        strategy = HashMapStrategy()
        for k, v in mixed_type_data.items():
            strategy.put(k, v)
        
        assert strategy.get("string") == "hello"
        assert strategy.get("integer") == 42
        assert strategy.get("boolean") is True
        assert strategy.get("list") == [1, 2, 3]
    
    def test_collision_handling(self):
        """Test that collisions are handled correctly."""
        strategy = HashMapStrategy()
        # Add many keys to potentially trigger collisions
        for i in range(1000):
            strategy.put(f"key_{i}", i)
        
        # Verify all keys are accessible
        for i in range(1000):
            assert strategy.get(f"key_{i}") == i
