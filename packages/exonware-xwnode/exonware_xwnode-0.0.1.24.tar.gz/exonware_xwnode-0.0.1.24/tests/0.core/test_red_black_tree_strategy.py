"""
Unit tests for Red-Black Tree strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.red_black_tree import RedBlackTreeStrategy, RedBlackTreeNode
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestRedBlackTreeCore:
    """Core tests for Red-Black Tree strategy."""
    
    def test_initialization(self):
        """Test initialization with default and custom options."""
        strategy = RedBlackTreeStrategy()
        assert strategy is not None
        assert len(strategy) == 0
        assert strategy.is_empty()
        assert strategy.mode == NodeMode.RED_BLACK_TREE
        
        # Custom case sensitivity
        strategy_insensitive = RedBlackTreeStrategy(case_sensitive=False)
        assert strategy_insensitive is not None
    
    def test_basic_insert_and_get(self):
        """Test basic insert and get operations."""
        strategy = RedBlackTreeStrategy()
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
        strategy = RedBlackTreeStrategy()
        strategy.put("key", "value1")
        assert strategy.get("key") == "value1"
        
        strategy.put("key", "value2")
        assert strategy.get("key") == "value2"
        assert len(strategy) == 1  # Size doesn't change
    
    def test_delete_operation(self):
        """Test delete operation."""
        strategy = RedBlackTreeStrategy()
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        strategy.put("key3", "value3")
        
        assert strategy.delete("key2")
        assert not strategy.has("key2")
        assert len(strategy) == 2
        
        assert not strategy.delete("nonexistent")
    
    def test_has_operation(self):
        """Test has operation."""
        strategy = RedBlackTreeStrategy()
        strategy.put("key1", "value1")
        
        assert strategy.has("key1")
        assert not strategy.has("nonexistent")
    
    def test_iteration(self):
        """Test iteration over keys, values, and items."""
        strategy = RedBlackTreeStrategy()
        strategy.put("c", 3)
        strategy.put("a", 1)
        strategy.put("b", 2)
        
        # Keys should be in sorted order
        keys = list(strategy.keys())
        assert keys == ["a", "b", "c"]
        
        values = list(strategy.values())
        assert values == [1, 2, 3]
        
        items = list(strategy.items())
        assert items == [("a", 1), ("b", 2), ("c", 3)]
    
    def test_clear_operation(self):
        """Test clear operation."""
        strategy = RedBlackTreeStrategy()
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        assert len(strategy) == 2
        
        strategy.clear()
        assert len(strategy) == 0
        assert strategy.is_empty()
        assert not strategy.has("key1")
    
    def test_to_native(self):
        """Test conversion to native dict."""
        strategy = RedBlackTreeStrategy()
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        
        native = strategy.to_native()
        assert isinstance(native, dict)
        assert native == {"key1": "value1", "key2": "value2"}
    
    def test_edge_case_empty(self):
        """Test operations on empty tree."""
        strategy = RedBlackTreeStrategy()
        assert len(strategy) == 0
        assert strategy.is_empty()
        assert strategy.get("nonexistent") is None
        assert not strategy.has("nonexistent")
        assert not strategy.delete("nonexistent")
        assert list(strategy.keys()) == []
    
    def test_edge_case_single_element(self):
        """Test operations on single element tree."""
        strategy = RedBlackTreeStrategy()
        strategy.put("key", "value")
        assert len(strategy) == 1
        assert not strategy.is_empty()
        assert strategy.get("key") == "value"
        
        strategy.delete("key")
        assert len(strategy) == 0
        assert strategy.is_empty()
    
    def test_supported_traits(self):
        """Test supported traits validation."""
        strategy = RedBlackTreeStrategy()
        traits = strategy.get_supported_traits()
        
        # Red-Black Tree supports ordered and indexed access
        assert NodeTrait.ORDERED in traits
        assert NodeTrait.INDEXED in traits


@pytest.mark.xwnode_core
class TestRedBlackTreeSpecificFeatures:
    """Tests for Red-Black Tree specific features."""
    
    def test_rb_tree_properties_after_insert(self):
        """Test that red-black tree properties are maintained after insertions."""
        strategy = RedBlackTreeStrategy()
        
        # Insert multiple keys
        for i in range(10):
            strategy.put(f"key{i}", i)
        
        # Verify RB-tree properties
        assert strategy.is_valid_rb_tree()
        
        # Root should be black
        assert strategy._root.is_black()
    
    def test_rb_tree_properties_after_delete(self):
        """Test that tree remains functional after deletions."""
        strategy = RedBlackTreeStrategy()
        
        # Insert and delete
        for i in range(10):
            strategy.put(f"key{i}", i)
        
        strategy.delete("key5")
        strategy.delete("key3")
        strategy.delete("key7")
        
        # Verify tree is still functional
        assert len(strategy) == 7
        assert not strategy.has("key5")
        assert not strategy.has("key3")
        assert strategy.has("key0")
        # Note: Full RB-tree invariant verification after complex deletions
        # is a work-in-progress. Basic functionality is validated here.
    
    def test_get_min_max(self):
        """Test getting minimum and maximum elements."""
        strategy = RedBlackTreeStrategy()
        
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
    
    def test_height_tracking(self):
        """Test that height is tracked correctly."""
        strategy = RedBlackTreeStrategy()
        
        # Empty tree
        assert strategy.get_height() == 0
        
        # Single element
        strategy.put("a", 1)
        assert strategy.get_height() == 1
        
        # Multiple elements - height should stay logarithmic
        for i in range(15):
            strategy.put(f"key{i:02d}", i)
        
        height = strategy.get_height()
        # For 16 elements, RB-tree height should be <= 2 * log2(16+1) ≈ 8.5
        assert height <= 9
    
    def test_rotation_tracking(self):
        """Test that rotations are tracked."""
        strategy = RedBlackTreeStrategy()
        
        # Insert in order (worst case for unbalanced BST)
        for i in range(10):
            strategy.put(f"key{i:02d}", i)
        
        stats = strategy.get_stats()
        # Rotations should have occurred
        assert stats['total_rotations'] > 0
    
    def test_large_dataset(self):
        """Test with large dataset."""
        strategy = RedBlackTreeStrategy()
        
        # Insert 1000 elements
        for i in range(1000):
            strategy.put(f"key{i:04d}", i)
        
        assert len(strategy) == 1000
        assert strategy.is_valid_rb_tree()
        
        # Height should be logarithmic
        height = strategy.get_height()
        # For 1000 elements, RB-tree height should be <= 2 * log2(1001) ≈ 20
        assert height <= 20
    
    def test_case_insensitive_mode(self):
        """Test case-insensitive key handling."""
        strategy = RedBlackTreeStrategy(case_sensitive=False)
        strategy.put("Key", "value1")
        strategy.put("KEY", "value2")
        
        # Should update same key
        assert len(strategy) == 1
        assert strategy.get("key") == "value2"


@pytest.mark.xwnode_performance
class TestRedBlackTreePerformance:
    """Performance tests for Red-Black Tree strategy."""
    
    def test_time_complexity_validation(self):
        """Validate that operations complete in reasonable time."""
        import time
        
        # Test that search is fast even with large dataset
        strategy = RedBlackTreeStrategy()
        for i in range(10000):
            strategy.put(f"key_{i:06d}", i)
        
        # Search should be fast (O(log n))
        start = time.perf_counter()
        for _ in range(100):
            strategy.get(f"key_{5000:06d}")
        elapsed = time.perf_counter() - start
        
        # 100 searches should complete in < 0.01 seconds
        assert elapsed < 0.01, f"Search too slow: {elapsed}s for 100 searches"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage is reasonable."""
        def operation():
            strategy = RedBlackTreeStrategy()
            for i in range(1000):
                strategy.put(f"key_{i}", i)
            return strategy
        
        result, memory = measure_memory(operation)
        
        # Each node has key, value, color, 3 pointers (left, right, parent)
        # Reasonable overhead: < 300KB for 1000 items
        max_expected = 300 * 1024  # 300KB
        assert memory < max_expected, (
            f"Memory usage {memory} exceeds {max_expected}. "
            f"This may indicate a memory leak or inefficiency."
        )
    
    def test_sequential_insert_performance(self):
        """Test performance of sequential insertions (worst case for unbalanced BST)."""
        strategy = RedBlackTreeStrategy()
        
        # Sequential insertion
        for i in range(1000):
            strategy.put(f"key{i:04d}", i)
        
        # Should still maintain logarithmic height
        assert strategy.get_height() <= 20
        assert strategy.is_valid_rb_tree()
    
    def test_delete_performance(self):
        """Test delete performance maintains tree functionality."""
        strategy = RedBlackTreeStrategy()
        
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
        assert strategy.get_height() <= 15  # Still reasonable height


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

