"""
Unit tests for Segment Tree strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.segment_tree import SegmentTreeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestSegmentTreeCore:
    """Core tests for Segment Tree strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = SegmentTreeStrategy()
        assert strategy is not None
        assert strategy.mode == NodeMode.SEGMENT_TREE
    
    def test_basic_operations(self):
        """Test basic operations."""
        strategy = SegmentTreeStrategy()
        strategy.put("0", 5)
        assert strategy.get("0") == 5
    
    def test_range_sum(self):
        """Test range sum query with EXACT expected values."""
        strategy = SegmentTreeStrategy(initial_size=5, operation='sum')
        strategy.update(0, 1)
        strategy.update(1, 2)
        strategy.update(2, 3)
        strategy.update(3, 4)
        strategy.update(4, 5)
        
        # Test specific ranges with EXACT expected values
        result = strategy.range_query(0, 2)
        assert result == 6, f"Expected 1+2+3=6, got {result}"
        
        result_all = strategy.range_query(0, 4)
        assert result_all == 15, f"Expected 1+2+3+4+5=15, got {result_all}"
    
    def test_range_min(self):
        """Test range min query with EXACT expected values."""
        strategy = SegmentTreeStrategy(initial_size=4, operation='min')
        strategy.update(0, 5)
        strategy.update(1, 2)
        strategy.update(2, 8)
        strategy.update(3, 1)
        
        result = strategy.range_query(0, 3)
        assert result == 1, f"Expected min([5,2,8,1])=1, got {result}"
        
        result_partial = strategy.range_query(0, 2)
        assert result_partial == 2, f"Expected min([5,2,8])=2, got {result_partial}"
    
    def test_range_max(self):
        """Test range max query with EXACT expected values."""
        strategy = SegmentTreeStrategy(initial_size=4, operation='max')
        strategy.update(0, 5)
        strategy.update(1, 2)
        strategy.update(2, 8)
        strategy.update(3, 1)
        
        result = strategy.range_query(0, 3)
        assert result == 8, f"Expected max([5,2,8,1])=8, got {result}"
        
        result_partial = strategy.range_query(1, 3)
        assert result_partial == 8, f"Expected max([2,8,1])=8, got {result_partial}"
    
    def test_update_operation(self):
        """Test update operation with EXACT expected values."""
        strategy = SegmentTreeStrategy(initial_size=3, operation='sum')
        strategy.update(0, 1)
        strategy.update(1, 2)
        strategy.update(2, 3)
        
        # Initial sum: 1+2+3 = 6
        result = strategy.range_query(0, 2)
        assert result == 6, f"Expected initial sum 1+2+3=6, got {result}"
        
        # Update index 1: 1+5+3 = 9
        strategy.update(1, 5)
        result = strategy.range_query(0, 2)
        assert result == 9, f"Expected updated sum 1+5+3=9, got {result}"
    
    def test_single_element_range(self):
        """Test single element range query with EXACT expected value."""
        strategy = SegmentTreeStrategy(initial_size=5, operation='sum')
        strategy.update(0, 10)
        strategy.update(2, 20)
        
        result = strategy.range_query(0, 0)
        assert result == 10, f"Expected single element [0]=10, got {result}"
        
        result2 = strategy.range_query(2, 2)
        assert result2 == 20, f"Expected single element [2]=20, got {result2}"
    
    def test_clear_operation(self):
        """Test clear operation."""
        strategy = SegmentTreeStrategy()
        strategy.put("0", 1)
        strategy.clear()
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = SegmentTreeStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.INDEXED in traits
        assert NodeTrait.HIERARCHICAL in traits


@pytest.mark.xwnode_core
class TestSegmentTreeSpecificFeatures:
    """Tests for Segment Tree specific features."""
    
    def test_different_operations_with_validation(self):
        """Test different operations with EXACT expected values."""
        # Sum operation
        sum_strategy = SegmentTreeStrategy(initial_size=5, operation='sum')
        for i in range(5):
            sum_strategy.update(i, i + 1)  # 1,2,3,4,5
        assert sum_strategy.range_query(0, 4) == 15
        
        # Min operation
        min_strategy = SegmentTreeStrategy(initial_size=4, operation='min')
        min_strategy.update(0, 10)
        min_strategy.update(1, 5)
        min_strategy.update(2, 20)
        min_strategy.update(3, 3)
        assert min_strategy.range_query(0, 3) == 3
        
        # Max operation
        max_strategy = SegmentTreeStrategy(initial_size=4, operation='max')
        max_strategy.update(0, 10)
        max_strategy.update(1, 5)
        max_strategy.update(2, 20)
        max_strategy.update(3, 3)
        assert max_strategy.range_query(0, 3) == 20
    
    def test_partial_range_with_exact_values(self):
        """Test partial range queries with EXACT expected values."""
        strategy = SegmentTreeStrategy(initial_size=10, operation='sum')
        for i in range(10):
            strategy.update(i, i)  # 0,1,2,3,4,5,6,7,8,9
        
        # Range [2,5] = 2+3+4+5 = 14
        result = strategy.range_query(2, 5)
        assert result == 14, f"Expected 2+3+4+5=14, got {result}"
        
        # Range [5,8] = 5+6+7+8 = 26
        result2 = strategy.range_query(5, 8)
        assert result2 == 26, f"Expected 5+6+7+8=26, got {result2}"
    
    def test_multiple_updates_exact_values(self):
        """Test multiple updates with EXACT expected values."""
        strategy = SegmentTreeStrategy(initial_size=3, operation='sum')
        strategy.update(0, 1)
        strategy.update(1, 2)
        strategy.update(2, 3)
        
        # Initial: 1+2+3 = 6
        assert strategy.range_query(0, 2) == 6
        
        # Update index 0: 10+2+3 = 15
        strategy.update(0, 10)
        assert strategy.range_query(0, 2) == 15
        
        # Update index 2: 10+2+30 = 42
        strategy.update(2, 30)
        assert strategy.range_query(0, 2) == 42


@pytest.mark.xwnode_performance
class TestSegmentTreePerformance:
    """Performance tests for Segment Tree strategy."""
    
    def test_performance(self):
        """Validate O(log n) query performance."""
        import time
        strategy = SegmentTreeStrategy(initial_size=1000, operation='sum')
        
        # Build tree with 1000 elements
        for i in range(1000):
            strategy.update(i, i)
        
        # Query should be fast (O(log n))
        start = time.perf_counter()
        for _ in range(100):
            result = strategy.range_query(0, 500)
        elapsed = time.perf_counter() - start
        
        # 100 range queries should complete quickly
        assert elapsed < 0.1, f"Range queries too slow: {elapsed}s for 100 queries"
        
        # Verify correctness: sum of 0..500 = 500*501/2 = 125250
        final_result = strategy.range_query(0, 500)
        expected = sum(range(501))
        assert final_result == expected, f"Expected {expected}, got {final_result}"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage."""
        def operation():
            strategy = SegmentTreeStrategy(initial_size=100)
            for i in range(100):
                strategy.update(i, i)
            return strategy
        
        result, memory = measure_memory(operation)
        # Segment tree uses 4n space
        assert memory < 500 * 1024  # 500KB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
