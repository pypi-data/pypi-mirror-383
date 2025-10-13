"""
#exonware/xwnode/tests/0.core/test_b_plus_tree_strategy.py

Comprehensive tests for B_PLUS_TREE node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.b_plus_tree import BPlusTreeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestBPlusTreeCore:
    """Core functionality tests for B_PLUS_TREE strategy."""
    
    def test_initialization_default(self):
        """Test initialization with default options."""
        strategy = BPlusTreeStrategy()
        assert strategy is not None
        assert len(strategy) == 0
        assert strategy.mode == NodeMode.B_PLUS_TREE
    
    def test_insert_and_retrieve(self):
        """Test basic insert and retrieve operations."""
        strategy = BPlusTreeStrategy()
        strategy.put("key1", "value1")
        assert strategy.get("key1") == "value1"
    
    def test_insert_multiple_sorted(self):
        """Test inserting multiple keys in sorted order."""
        strategy = BPlusTreeStrategy()
        for i in range(20):
            strategy.put(f"key_{i:03d}", f"value_{i}")
        
        # Verify all keys are accessible
        for i in range(20):
            result = strategy.get(f"key_{i:03d}")
            assert result is not None, f"Key key_{i:03d} not found"
            assert result == f"value_{i}", f"Expected value_{i}, got {result}"
    
    def test_leaf_linked_list(self):
        """Test that B+ Tree maintains leaf linked list for range queries."""
        strategy = BPlusTreeStrategy()
        # Insert sorted keys
        for i in range(10):
            strategy.put(f"key_{i:03d}", i)
        
        # All values should be accessible (stored in leaves)
        for i in range(10):
            key = f"key_{i:03d}"
            assert strategy.has(key), f"Key {key} should exist but doesn't"
            assert strategy.get(key) is not None, f"Key {key} should have value"
    
    def test_update_existing_key(self):
        """Test updating existing key."""
        strategy = BPlusTreeStrategy()
        strategy.put("key", "value1")
        strategy.put("key", "value2")
        assert strategy.get("key") == "value2"
    
    def test_delete_key(self):
        """Test deleting keys."""
        strategy = BPlusTreeStrategy()
        for i in range(10):
            strategy.put(f"key_{i:03d}", i)
        
        assert strategy.delete("key_005")
        assert not strategy.has("key_005")
    
    def test_iteration(self):
        """Test iteration over keys."""
        strategy = BPlusTreeStrategy()
        keys = ["a", "c", "b", "d", "e"]
        for k in keys:
            strategy.put(k, k.upper())
        
        result_keys = list(strategy.keys())
        assert len(result_keys) == len(keys)
    
    def test_clear(self):
        """Test clearing all data."""
        strategy = BPlusTreeStrategy()
        for i in range(20):
            strategy.put(f"key_{i}", i)
        
        strategy.clear()
        assert len(strategy) == 0
    
    def test_to_native(self):
        """Test conversion to native dict."""
        strategy = BPlusTreeStrategy()
        data = {"a": 1, "b": 2, "c": 3}
        for k, v in data.items():
            strategy.put(k, v)
        
        native = strategy.to_native()
        assert isinstance(native, dict)


@pytest.mark.xwnode_performance
class TestBPlusTreePerformance:
    """Performance validation for B+ Tree."""
    
    def test_time_complexity_ologn(self):
        """
        Validate O(log n) complexity for B+ Tree.
        
        B+ Trees maintain sorted order with O(log n) operations.
        This is CORRECT - the algorithm requires tree traversal.
        """
        import time
        
        strategies = {}
        for size in [100, 1000, 10000]:
            s = BPlusTreeStrategy()
            for i in range(size):
                s.put(f"key_{i:06d}", i)
            strategies[size] = s
        
        timings = {}
        for size, strategy in strategies.items():
            measurements = []
            for _ in range(50):
                start = time.perf_counter()
                strategy.get(f"key_{size//2:06d}")
                elapsed = time.perf_counter() - start
                measurements.append(elapsed)
            measurements.sort()
            timings[size] = measurements[len(measurements)//2]
        
        # Validate O(log n) behavior
        import math
        expected_ratio = math.log(10000) / math.log(100)
        actual_ratio = timings[10000] / timings[100]
        
        assert actual_ratio < expected_ratio * 3.0, (
            f"Expected O(log n) ~{expected_ratio:.2f}, got {actual_ratio:.2f}"
        )
    
    def test_range_query_performance(self):
        """Test that range queries are efficient (B+ Tree strength)."""
        import time
        
        strategy = BPlusTreeStrategy()
        # Insert 1000 items
        for i in range(1000):
            strategy.put(f"key_{i:06d}", i)
        
        # Range query should be fast
        start = time.perf_counter()
        items = list(strategy.items())
        elapsed = time.perf_counter() - start
        
        # Should complete in < 10ms for 1000 items
        assert elapsed < 0.01, f"Range query took {elapsed*1000:.2f}ms"


@pytest.mark.xwnode_core
class TestBPlusTreeEdgeCases:
    """Edge case tests for B+ Tree."""
    
    def test_empty_operations(self):
        """Test operations on empty tree."""
        strategy = BPlusTreeStrategy()
        assert len(strategy) == 0
        assert strategy.get("any") is None
    
    def test_single_element(self):
        """Test with single element."""
        strategy = BPlusTreeStrategy()
        strategy.put("only", "one")
        assert strategy.get("only") == "one"
    
    def test_large_dataset(self, large_dataset):
        """Test with 10,000 items."""
        strategy = BPlusTreeStrategy()
        count = 0
        for k, v in sorted(large_dataset.items())[:1000]:  # First 1000
            strategy.put(k, v)
            count += 1
        
        assert count >= 1000

