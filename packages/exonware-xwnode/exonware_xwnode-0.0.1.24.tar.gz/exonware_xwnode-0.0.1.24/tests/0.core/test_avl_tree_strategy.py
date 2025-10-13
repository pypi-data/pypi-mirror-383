"""
Unit tests for AVL Tree strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.avl_tree import AVLTreeStrategy, AVLTreeNode
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestAVLTreeCore:
    """Core tests for AVL Tree strategy."""
    
    def test_initialization(self):
        """Test initialization with default and custom options."""
        strategy = AVLTreeStrategy()
        assert strategy is not None
        assert len(strategy) == 0
        assert strategy.is_empty()
        assert strategy.mode == NodeMode.AVL_TREE
        
        # Custom case sensitivity
        strategy_insensitive = AVLTreeStrategy(case_sensitive=False)
        assert strategy_insensitive is not None
    
    def test_basic_insert_and_get(self):
        """Test basic insert and get operations."""
        strategy = AVLTreeStrategy()
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
        strategy = AVLTreeStrategy()
        strategy.put("key", "value1")
        assert strategy.get("key") == "value1"
        
        strategy.put("key", "value2")
        assert strategy.get("key") == "value2"
        assert len(strategy) == 1  # Size doesn't change
    
    def test_delete_operation(self):
        """Test delete operation."""
        strategy = AVLTreeStrategy()
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        strategy.put("key3", "value3")
        
        assert strategy.delete("key2")
        assert not strategy.has("key2")
        assert len(strategy) == 2
        
        assert not strategy.delete("nonexistent")
    
    def test_has_operation(self):
        """Test has operation."""
        strategy = AVLTreeStrategy()
        strategy.put("key1", "value1")
        
        assert strategy.has("key1")
        assert not strategy.has("nonexistent")
    
    def test_iteration(self):
        """Test iteration over keys, values, and items."""
        strategy = AVLTreeStrategy()
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
        strategy = AVLTreeStrategy()
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        assert len(strategy) == 2
        
        strategy.clear()
        assert len(strategy) == 0
        assert strategy.is_empty()
        assert not strategy.has("key1")
    
    def test_to_native(self):
        """Test conversion to native dict."""
        strategy = AVLTreeStrategy()
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        
        native = strategy.to_native()
        assert isinstance(native, dict)
        assert native == {"key1": "value1", "key2": "value2"}
    
    def test_edge_case_empty(self):
        """Test operations on empty tree."""
        strategy = AVLTreeStrategy()
        assert len(strategy) == 0
        assert strategy.is_empty()
        assert strategy.get("nonexistent") is None
        assert not strategy.has("nonexistent")
        assert not strategy.delete("nonexistent")
        assert list(strategy.keys()) == []
    
    def test_edge_case_single_element(self):
        """Test operations on single element tree."""
        strategy = AVLTreeStrategy()
        strategy.put("key", "value")
        assert len(strategy) == 1
        assert not strategy.is_empty()
        assert strategy.get("key") == "value"
        
        strategy.delete("key")
        assert len(strategy) == 0
        assert strategy.is_empty()
    
    def test_supported_traits(self):
        """Test supported traits validation."""
        strategy = AVLTreeStrategy()
        traits = strategy.get_supported_traits()
        
        # AVL Tree supports ordered and indexed access
        assert NodeTrait.ORDERED in traits
        assert NodeTrait.INDEXED in traits


@pytest.mark.xwnode_core
class TestAVLTreeSpecificFeatures:
    """Tests for AVL Tree specific features."""
    
    def test_avl_balance_after_insert(self):
        """Test that AVL balance property is maintained after insertions."""
        strategy = AVLTreeStrategy()
        
        # Insert in sequential order (worst case for unbalanced BST)
        for i in range(10):
            strategy.put(f"key{i:02d}", i)
        
        # Verify AVL properties
        assert strategy.is_balanced()
        
        # Height should be logarithmic
        assert strategy.get_height() <= 5  # log2(10) ≈ 3.3, AVL allows +1
    
    def test_avl_balance_after_delete(self):
        """Test that tree remains balanced after deletions."""
        strategy = AVLTreeStrategy()
        
        # Insert and delete
        for i in range(10):
            strategy.put(f"key{i}", i)
        
        strategy.delete("key5")
        strategy.delete("key3")
        strategy.delete("key7")
        
        # Verify tree is still functional and balanced
        assert len(strategy) == 7
        assert not strategy.has("key5")
        assert strategy.is_balanced()
    
    def test_get_min_max(self):
        """Test getting minimum and maximum elements."""
        strategy = AVLTreeStrategy()
        
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
        """Test that height is tracked correctly and stays logarithmic."""
        strategy = AVLTreeStrategy()
        
        # Empty tree
        assert strategy.get_height() == 0
        
        # Single element
        strategy.put("a", 1)
        assert strategy.get_height() == 1
        
        # Multiple elements - height should stay strictly logarithmic
        for i in range(15):
            strategy.put(f"key{i:02d}", i)
        
        height = strategy.get_height()
        # For 16 elements, AVL tree height should be <= log2(16+1) + 1 ≈ 5
        assert height <= 5
    
    def test_rotation_tracking(self):
        """Test that rotations are tracked."""
        strategy = AVLTreeStrategy()
        
        # Insert in order (triggers rotations)
        for i in range(10):
            strategy.put(f"key{i:02d}", i)
        
        stats = strategy.get_stats()
        # Rotations should have occurred
        assert stats['total_rotations'] > 0
    
    def test_balance_factor(self):
        """Test that balance factor is maintained within [-1, 0, 1]."""
        strategy = AVLTreeStrategy()
        
        # Insert many elements
        for i in range(100):
            strategy.put(f"key{i:03d}", i)
        
        # Verify all nodes have valid balance factors
        assert strategy.is_balanced()
    
    def test_large_dataset(self):
        """Test with large dataset."""
        strategy = AVLTreeStrategy()
        
        # Insert 1000 elements
        for i in range(1000):
            strategy.put(f"key{i:04d}", i)
        
        assert len(strategy) == 1000
        assert strategy.is_balanced()
        
        # Height should be strictly logarithmic
        height = strategy.get_height()
        # For 1000 elements, AVL tree height should be <= log2(1000) + 1 ≈ 11
        assert height <= 11
    
    def test_case_insensitive_mode(self):
        """Test case-insensitive key handling."""
        strategy = AVLTreeStrategy(case_sensitive=False)
        strategy.put("Key", "value1")
        strategy.put("KEY", "value2")
        
        # Should update same key
        assert len(strategy) == 1
        assert strategy.get("key") == "value2"


@pytest.mark.xwnode_performance
class TestAVLTreePerformance:
    """Performance tests for AVL Tree strategy."""
    
    def test_time_complexity_validation(self):
        """Validate that operations complete in reasonable time."""
        import time
        
        # Test that search is fast even with large dataset
        strategy = AVLTreeStrategy()
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
            strategy = AVLTreeStrategy()
            for i in range(1000):
                strategy.put(f"key_{i}", i)
            return strategy
        
        result, memory = measure_memory(operation)
        
        # Each node has key, value, height, 2 pointers (left, right)
        # Reasonable overhead: < 250KB for 1000 items
        max_expected = 250 * 1024  # 250KB
        assert memory < max_expected, (
            f"Memory usage {memory} exceeds {max_expected}. "
            f"This may indicate a memory leak or inefficiency."
        )
    
    def test_sequential_insert_performance(self):
        """Test performance of sequential insertions (triggers many rotations)."""
        strategy = AVLTreeStrategy()
        
        # Sequential insertion (worst case)
        for i in range(1000):
            strategy.put(f"key{i:04d}", i)
        
        # Should still maintain logarithmic height
        assert strategy.get_height() <= 11
        assert strategy.is_balanced()
    
    def test_delete_performance(self):
        """Test delete performance maintains AVL tree properties."""
        strategy = AVLTreeStrategy()
        
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
        assert strategy.get_height() <= 7  # Still logarithmic
        assert strategy.is_balanced()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

