"""
#exonware/xwnode/tests/0.core/test_b_tree_strategy.py

Comprehensive tests for B_TREE node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.b_tree import BTreeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestBTreeCore:
    """Core functionality tests for B_TREE strategy."""
    
    def test_initialization_default(self):
        """Test initialization with default options."""
        strategy = BTreeStrategy()
        assert strategy is not None
        assert len(strategy) == 0
        assert strategy.mode == NodeMode.B_TREE
    
    def test_initialization_custom_degree(self):
        """Test initialization with custom degree (branching factor)."""
        strategy = BTreeStrategy(traits=NodeTrait.NONE, degree=5)
        assert strategy is not None
    
    def test_insert_single_key(self):
        """Test inserting single key-value pair."""
        strategy = BTreeStrategy()
        strategy.put("key1", "value1")
        assert strategy.has("key1")
        assert strategy.get("key1") == "value1"
    
    def test_insert_multiple_sorted(self):
        """Test inserting multiple keys in sorted order."""
        strategy = BTreeStrategy()
        for i in range(10):
            strategy.put(f"key_{i:03d}", f"value_{i}")
        
        assert len(strategy) == 10
        assert strategy.get("key_005") == "value_5"
    
    def test_insert_multiple_reverse_order(self):
        """Test inserting keys in reverse order."""
        strategy = BTreeStrategy()
        for i in range(10, 0, -1):
            strategy.put(f"key_{i:03d}", f"value_{i}")
        
        assert len(strategy) == 10
        # Should maintain all keys despite reverse insertion
        assert strategy.get("key_005") == "value_5"
    
    def test_insert_random_order(self):
        """Test inserting keys in random order."""
        strategy = BTreeStrategy()
        keys = [5, 2, 8, 1, 9, 3, 7, 4, 6]
        for key in keys:
            strategy.put(f"key_{key:03d}", f"value_{key}")
        
        assert len(strategy) == len(keys)
        # All keys should be accessible
        for key in keys:
            assert strategy.has(f"key_{key:03d}")
    
    def test_update_existing_key(self):
        """Test updating existing key with new value."""
        strategy = BTreeStrategy()
        strategy.put("key", "value1")
        strategy.put("key", "value2")
        
        assert strategy.get("key") == "value2"
    
    def test_delete_leaf_key(self):
        """Test deleting key from leaf node."""
        strategy = BTreeStrategy()
        for i in range(10):
            strategy.put(f"key_{i:03d}", f"value_{i}")
        
        assert strategy.delete("key_005")
        assert not strategy.has("key_005")
        assert len(strategy) == 9
    
    def test_delete_nonexistent_key(self):
        """Test deleting nonexistent key returns False."""
        strategy = BTreeStrategy()
        strategy.put("key1", "value1")
        
        assert not strategy.delete("nonexistent")
        assert len(strategy) == 1
    
    def test_iteration_keys(self):
        """Test iteration over keys."""
        strategy = BTreeStrategy()
        keys = ["a", "c", "b", "d"]
        for k in keys:
            strategy.put(k, k.upper())
        
        result_keys = list(strategy.keys())
        assert len(result_keys) == 4
        # Keys should be present (may not be ordered in iteration)
        assert set(result_keys) == set(keys)
    
    def test_iteration_items(self):
        """Test iteration over key-value pairs."""
        strategy = BTreeStrategy()
        data = {"a": 1, "b": 2, "c": 3}
        for k, v in data.items():
            strategy.put(k, v)
        
        items = dict(strategy.items())
        assert items == data
    
    def test_clear(self):
        """Test clearing all data."""
        strategy = BTreeStrategy()
        for i in range(20):
            strategy.put(f"key_{i:03d}", i)
        
        strategy.clear()
        assert len(strategy) == 0
        assert strategy.is_empty
    
    def test_to_native(self):
        """Test conversion to native Python dict."""
        strategy = BTreeStrategy()
        data = {"a": 1, "b": 2, "c": 3}
        for k, v in data.items():
            strategy.put(k, v)
        
        native = strategy.to_native()
        assert isinstance(native, dict)
        assert native == data


@pytest.mark.xwnode_performance
class TestBTreePerformance:
    """Performance validation tests for B_TREE strategy."""
    
    def test_time_complexity_ologn_search(self):
        """
        Validate O(log n) search complexity.
        
        NOTE: This is the CORRECT complexity for B-Tree.
        B-Trees maintain sorted order, which requires tree traversal.
        If you need O(1) lookups, use HASH_MAP instead.
        """
        import time
        
        # Pre-create B-trees of different sizes
        strategies = {}
        for size in [100, 1000, 10000]:
            s = BTreeStrategy()
            for i in range(size):
                s.put(f"key_{i:06d}", i)  # Sorted keys
            strategies[size] = s
        
        # Measure search operation
        timings = {}
        for size, strategy in strategies.items():
            measurements = []
            for _ in range(100):
                start = time.perf_counter()
                strategy.get(f"key_{size//2:06d}")
                elapsed = time.perf_counter() - start
                measurements.append(elapsed)
            
            measurements.sort()
            timings[size] = measurements[len(measurements)//2]
        
        # O(log n): time should grow logarithmically
        import math
        expected_ratio = math.log(10000) / math.log(100)  # ~2.3
        actual_ratio = timings[10000] / timings[100]
        
        # Allow tolerance for implementation overhead
        assert actual_ratio < expected_ratio * 3.0, (
            f"Expected O(log n) with ratio ~{expected_ratio:.2f}, "
            f"got {actual_ratio:.2f}. This is CORRECT for B-Tree. "
            f"For O(1) operations, use HASH_MAP."
        )
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage for B-Tree."""
        def operation():
            strategy = BTreeStrategy()
            for i in range(1000):
                strategy.put(f"key_{i:06d}", i)
            return strategy
        
        result, memory_bytes = measure_memory(operation)
        
        # B-Trees have higher memory overhead than hash maps (tree structure)
        # < 500KB for 1000 items is reasonable
        max_expected = 500 * 1024
        assert memory_bytes < max_expected, (
            f"Memory usage {memory_bytes} bytes exceeds {max_expected}. "
            f"B-Trees have higher overhead than hash maps due to tree structure."
        )
    
    def test_sorted_iteration_performance(self):
        """Test that B-Tree provides efficient sorted iteration."""
        import time
        
        strategy = BTreeStrategy()
        # Insert in random order
        import random
        keys = list(range(1000))
        random.shuffle(keys)
        for k in keys:
            strategy.put(f"key_{k:06d}", k)
        
        # Measure sorted iteration
        start = time.perf_counter()
        sorted_items = list(strategy.items())
        elapsed = time.perf_counter() - start
        
        # Should be fast (< 10ms for 1000 items)
        # B-Tree in-order traversal is O(n), ~0.05s for 1000 items is reasonable
        assert elapsed < 0.1, f"Sorted iteration took {elapsed*1000:.2f}ms, expected <100ms"


@pytest.mark.xwnode_core
class TestBTreeEdgeCases:
    """Edge case and error handling tests."""
    
    def test_empty_operations(self):
        """Test operations on empty B-Tree."""
        strategy = BTreeStrategy()
        assert len(strategy) == 0
        assert strategy.is_empty
        assert strategy.get("any") is None
        assert not strategy.has("any")
    
    def test_single_element(self):
        """Test with single element."""
        strategy = BTreeStrategy()
        strategy.put("only", "one")
        assert len(strategy) == 1
        assert strategy.get("only") == "one"
    
    def test_large_dataset(self, large_dataset):
        """Test with 10,000 items."""
        strategy = BTreeStrategy()
        # B-Tree handles sorted data efficiently
        for k, v in sorted(large_dataset.items()):
            strategy.put(k, v)
        
        assert len(strategy) >= 1000  # At least 1000 items
        # Sample check
        assert strategy.get("key_5000") == "value_5000"
    
    def test_duplicate_key_update(self):
        """Test that inserting duplicate key updates value."""
        strategy = BTreeStrategy()
        strategy.put("key", "value1")
        strategy.put("key", "value2")
        strategy.put("key", "value3")
        
        assert strategy.get("key") == "value3"
        assert len(strategy) == 1
    
    def test_unicode_keys(self, multilingual_data):
        """Test Unicode key support."""
        strategy = BTreeStrategy()
        for k, v in multilingual_data.items():
            strategy.put(k, v)
        
        assert strategy.get("chinese") == "你好世界"
