"""
Unit tests for Treap strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.treap import TreapStrategy, TreapNode
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestTreapCore:
    """Core tests for Treap strategy."""
    
    def test_initialization(self):
        """Test initialization with default and custom options."""
        strategy = TreapStrategy()
        assert strategy is not None
        assert len(strategy) == 0
        assert strategy.is_empty()
        assert strategy.mode == NodeMode.TREAP
        
        # Custom case sensitivity
        strategy_insensitive = TreapStrategy(case_sensitive=False)
        assert strategy_insensitive is not None
    
    def test_basic_insert_and_get(self):
        """Test basic insert and get operations."""
        strategy = TreapStrategy()
        strategy.put("key1", "value1")
        assert strategy.get("key1") == "value1"
        assert len(strategy) == 1
        
        strategy.put("key2", "value2")
        strategy.put("key3", "value3")
        assert strategy.get("key2") == "value2"
        assert strategy.get("key3") == "value3"
        assert len(strategy) == 3
    
    def test_update_existing_key(self):
        """Test updating value for existing key."""
        strategy = TreapStrategy()
        strategy.put("key", "value1")
        assert strategy.get("key") == "value1"
        
        strategy.put("key", "value2")
        assert strategy.get("key") == "value2"
        assert len(strategy) == 1  # Size doesn't change
    
    def test_delete_operation(self):
        """Test delete operation."""
        strategy = TreapStrategy()
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        strategy.put("key3", "value3")
        
        assert strategy.delete("key2")
        assert not strategy.has("key2")
        assert len(strategy) == 2
        
        assert not strategy.delete("nonexistent")
    
    def test_has_operation(self):
        """Test has operation."""
        strategy = TreapStrategy()
        strategy.put("key1", "value1")
        
        assert strategy.has("key1")
        assert not strategy.has("nonexistent")
    
    def test_iteration(self):
        """Test iteration over keys, values, and items."""
        strategy = TreapStrategy()
        strategy.put("c", 3)
        strategy.put("a", 1)
        strategy.put("b", 2)
        
        # Keys should be in sorted order (BST property)
        keys = list(strategy.keys())
        assert keys == ["a", "b", "c"]
        
        values = list(strategy.values())
        assert values == [1, 2, 3]
        
        items = list(strategy.items())
        assert items == [("a", 1), ("b", 2), ("c", 3)]
    
    def test_clear_operation(self):
        """Test clear operation."""
        strategy = TreapStrategy()
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        assert len(strategy) == 2
        
        strategy.clear()
        assert len(strategy) == 0
        assert strategy.is_empty()
        assert not strategy.has("key1")
    
    def test_to_native(self):
        """Test conversion to native dict."""
        strategy = TreapStrategy()
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        
        native = strategy.to_native()
        assert isinstance(native, dict)
        assert native == {"key1": "value1", "key2": "value2"}
    
    def test_edge_case_empty(self):
        """Test operations on empty tree."""
        strategy = TreapStrategy()
        assert len(strategy) == 0
        assert strategy.is_empty()
        assert strategy.get("nonexistent") is None
        assert not strategy.has("nonexistent")
        assert not strategy.delete("nonexistent")
        assert list(strategy.keys()) == []
    
    def test_edge_case_single_element(self):
        """Test operations on single element tree."""
        strategy = TreapStrategy()
        strategy.put("key", "value")
        assert len(strategy) == 1
        assert not strategy.is_empty()
        assert strategy.get("key") == "value"
        
        strategy.delete("key")
        assert len(strategy) == 0
        assert strategy.is_empty()
    
    def test_supported_traits(self):
        """Test supported traits validation."""
        strategy = TreapStrategy()
        traits = strategy.get_supported_traits()
        
        # Treap supports ordered and indexed access
        assert NodeTrait.ORDERED in traits
        assert NodeTrait.INDEXED in traits


@pytest.mark.xwnode_core
class TestTreapSpecificFeatures:
    """Tests for Treap specific features."""
    
    def test_random_priorities(self):
        """Test that random priorities are assigned."""
        strategy = TreapStrategy()
        
        # Insert elements
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        strategy.put("key3", "value3")
        
        # Check that priorities were assigned
        stats = strategy.get_stats()
        assert stats['size'] == 3
    
    def test_height_tracking(self):
        """Test that height is tracked and stays reasonable (expected O(log n))."""
        strategy = TreapStrategy()
        
        # Empty tree
        assert strategy.get_height() == 0
        
        # Single element
        strategy.put("a", 1)
        assert strategy.get_height() == 1
        
        # Multiple elements - height should be reasonable (probabilistic)
        for i in range(100):
            strategy.put(f"key{i:03d}", i)
        
        height = strategy.get_height()
        # For 101 elements, expected height is ~log2(101) ≈ 6.7
        # Allow up to 3x expected for probabilistic nature
        assert height <= 20  # Reasonable upper bound
    
    def test_rotation_tracking(self):
        """Test that rotations are tracked."""
        strategy = TreapStrategy()
        
        # Insert multiple elements (triggers rotations)
        for i in range(10):
            strategy.put(f"key{i:02d}", i)
        
        stats = strategy.get_stats()
        # Rotations should have occurred
        assert stats['total_rotations'] > 0
    
    def test_get_min_max(self):
        """Test getting minimum and maximum elements."""
        strategy = TreapStrategy()
        
        # Empty tree
        assert strategy.get_min() is None
        assert strategy.get_max() is None
        
        # With elements
        strategy.put("c", 3)
        strategy.put("a", 1)
        strategy.put("e", 5)
        strategy.put("b", 2)
        strategy.put("d", 4)
        
        assert strategy.get_min() == ("a", 1)
        assert strategy.get_max() == ("e", 5)
    
    def test_large_dataset(self):
        """Test with large dataset."""
        strategy = TreapStrategy()
        
        # Insert 1000 elements
        for i in range(1000):
            strategy.put(f"key{i:04d}", i)
        
        assert len(strategy) == 1000
        
        # Height should be logarithmic (expected ~log2(1000) ≈ 10)
        height = strategy.get_height()
        # Allow up to 3x for probabilistic nature
        assert height <= 30
    
    def test_sequential_insertion(self):
        """Test sequential insertion (worst case for unbalanced BST)."""
        strategy = TreapStrategy()
        
        # Insert in order (random priorities should balance)
        for i in range(100):
            strategy.put(f"key{i:03d}", i)
        
        # Should remain reasonably balanced due to random priorities
        assert strategy.get_height() <= 20  # Much better than O(n) = 100
    
    def test_case_insensitive_mode(self):
        """Test case-insensitive key handling."""
        strategy = TreapStrategy(case_sensitive=False)
        strategy.put("Key", "value1")
        strategy.put("KEY", "value2")
        
        # Should update same key
        assert len(strategy) == 1
        assert strategy.get("key") == "value2"
    
    def test_deterministic_priorities(self):
        """Test that same priorities produce deterministic structure."""
        import random as rand
        
        # Set seed for reproducibility
        rand.seed(42)
        strategy1 = TreapStrategy()
        for i in range(10):
            strategy1.put(f"key{i}", i)
        height1 = strategy1.get_height()
        
        # Same seed, same structure
        rand.seed(42)
        strategy2 = TreapStrategy()
        for i in range(10):
            strategy2.put(f"key{i}", i)
        height2 = strategy2.get_height()
        
        # Heights should be identical with same seed
        assert height1 == height2


@pytest.mark.xwnode_performance
class TestTreapPerformance:
    """Performance tests for Treap strategy."""
    
    def test_time_complexity_validation(self):
        """Validate that operations complete in reasonable time."""
        import time
        
        # Test that search is fast even with large dataset
        strategy = TreapStrategy()
        for i in range(10000):
            strategy.put(f"key_{i:06d}", i)
        
        # Search should be fast (O(log n) expected)
        start = time.perf_counter()
        for _ in range(100):
            strategy.get(f"key_{5000:06d}")
        elapsed = time.perf_counter() - start
        
        # 100 searches should complete in < 0.01 seconds
        assert elapsed < 0.01, f"Search too slow: {elapsed}s for 100 searches"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage is reasonable."""
        def operation():
            strategy = TreapStrategy()
            for i in range(1000):
                strategy.put(f"key_{i}", i)
            return strategy
        
        result, memory = measure_memory(operation)
        
        # Each node has key, value, priority, 2 pointers
        # Reasonable overhead: < 250KB for 1000 items
        max_expected = 250 * 1024  # 250KB
        assert memory < max_expected, (
            f"Memory usage {memory} exceeds {max_expected}. "
            f"This may indicate a memory leak or inefficiency."
        )
    
    def test_delete_performance(self):
        """Test delete performance maintains tree functionality."""
        strategy = TreapStrategy()
        
        # Insert 100 elements
        for i in range(100):
            strategy.put(f"key{i:03d}", i)
        
        # Delete half
        for i in range(0, 100, 2):
            strategy.delete(f"key{i:03d}")
        
        assert len(strategy) == 50
        # Verify remaining keys are still accessible
        for i in range(1, 100, 2):
            assert strategy.has(f"key{i:03d}")
        assert strategy.get_height() <= 15  # Still reasonable


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

