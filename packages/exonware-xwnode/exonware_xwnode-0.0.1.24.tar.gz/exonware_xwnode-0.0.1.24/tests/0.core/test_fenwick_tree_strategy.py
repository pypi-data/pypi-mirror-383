"""
Unit tests for Fenwick Tree strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.fenwick_tree import FenwickTreeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestFenwickTreeCore:
    """Core tests for Fenwick Tree strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = FenwickTreeStrategy()
        assert strategy is not None
        assert strategy.mode == NodeMode.FENWICK_TREE
    
    def test_basic_operations(self):
        """Test basic put/get operations."""
        strategy = FenwickTreeStrategy()
        strategy.put("0", 5)
        assert strategy.get("0") == 5
        assert len(strategy) == 1
    
    def test_prefix_sum(self):
        """Test prefix sum query with EXACT expected values."""
        strategy = FenwickTreeStrategy(initial_size=10)
        
        # Add values: indices 1-5 with values 1-5
        strategy.update(1, 1)
        strategy.update(2, 2)
        strategy.update(3, 3)
        strategy.update(4, 4)
        strategy.update(5, 5)
        
        # Prefix sum [1..3] = 1+2+3 = 6
        result = strategy.prefix_sum(3)
        assert result == 6, f"Expected prefix sum [1..3]=1+2+3=6, got {result}"
        
        # Prefix sum [1..5] = 1+2+3+4+5 = 15
        result_all = strategy.prefix_sum(5)
        assert result_all == 15, f"Expected prefix sum [1..5]=15, got {result_all}"
    
    def test_range_sum(self):
        """Test range sum query with EXACT expected values."""
        strategy = FenwickTreeStrategy(initial_size=10)
        
        # Add values at indices 1-6
        for i in range(1, 7):
            strategy.update(i, i)  # 1,2,3,4,5,6
        
        # Range [2,5] = 2+3+4+5 = 14
        result = strategy.range_sum(2, 5)
        assert result == 14, f"Expected range [2,5]=2+3+4+5=14, got {result}"
        
        # Range [1,3] = 1+2+3 = 6
        result2 = strategy.range_sum(1, 3)
        assert result2 == 6, f"Expected range [1,3]=1+2+3=6, got {result2}"
    
    def test_update_operation(self):
        """Test update operation with EXACT expected values."""
        strategy = FenwickTreeStrategy(initial_size=5)
        strategy.update(1, 10)
        strategy.update(2, 20)
        strategy.update(3, 30)
        
        # Initial prefix sum [1..3] = 10+20+30 = 60
        assert strategy.prefix_sum(3) == 60
        
        # Update index 2 to 50 (delta = +30)
        strategy.update(2, 50)
        
        # New prefix sum [1..3] = 10+50+30 = 90
        result = strategy.prefix_sum(3)
        assert result == 90, f"Expected updated prefix sum 10+50+30=90, got {result}"
    
    def test_single_element(self):
        """Test single element with EXACT expected value."""
        strategy = FenwickTreeStrategy(initial_size=5)
        strategy.update(3, 100)
        
        result = strategy.prefix_sum(3)
        assert result == 100, f"Expected single element sum=100, got {result}"
    
    def test_clear_operation(self):
        """Test clear operation."""
        strategy = FenwickTreeStrategy()
        strategy.put("0", 1)
        strategy.clear()
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = FenwickTreeStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.INDEXED in traits
        assert NodeTrait.ORDERED in traits


@pytest.mark.xwnode_core
class TestFenwickTreeSpecificFeatures:
    """Tests for Fenwick Tree specific features."""
    
    def test_incremental_updates(self):
        """Test incremental updates with EXACT expected values."""
        strategy = FenwickTreeStrategy(initial_size=5)
        
        # Add values incrementally
        strategy.update(1, 5)
        assert strategy.prefix_sum(1) == 5
        
        strategy.update(2, 10)
        assert strategy.prefix_sum(2) == 15  # 5+10
        
        strategy.update(3, 15)
        assert strategy.prefix_sum(3) == 30  # 5+10+15
    
    def test_multiple_range_queries(self):
        """Test multiple range queries with EXACT expected values."""
        strategy = FenwickTreeStrategy(initial_size=10)
        
        for i in range(1, 11):
            strategy.update(i, i)  # 1,2,3,4,5,6,7,8,9,10
        
        # Multiple non-overlapping ranges
        assert strategy.range_sum(1, 3) == 6    # 1+2+3
        assert strategy.range_sum(4, 6) == 15   # 4+5+6
        assert strategy.range_sum(7, 10) == 34  # 7+8+9+10
    
    def test_zero_values(self):
        """Test handling of zero values."""
        strategy = FenwickTreeStrategy(initial_size=5)
        strategy.update(1, 0)
        strategy.update(2, 5)
        strategy.update(3, 0)
        
        # Sum should only count non-zero
        assert strategy.prefix_sum(3) == 5


@pytest.mark.xwnode_performance
class TestFenwickTreePerformance:
    """Performance tests for Fenwick Tree strategy."""
    
    def test_time_complexity(self):
        """Validate O(log n) operations with correctness verification."""
        import time
        strategy = FenwickTreeStrategy(initial_size=1000)
        
        # Build tree
        for i in range(1, 1001):
            strategy.update(i, i)
        
        # Verify correctness: sum [1..100] = 100*101/2 = 5050
        result = strategy.prefix_sum(100)
        assert result == 5050, f"Expected sum[1..100]=5050, got {result}"
        
        # Performance: 1000 queries should be fast
        start = time.perf_counter()
        for i in range(1, 1001):
            _ = strategy.prefix_sum(i)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.1, f"1000 prefix queries too slow: {elapsed}s"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage."""
        def operation():
            strategy = FenwickTreeStrategy(initial_size=1000)
            for i in range(1, 101):
                strategy.update(i, i)
            return strategy
        
        result, memory = measure_memory(operation)
        # Fenwick tree is memory efficient: O(n)
        assert memory < 200 * 1024  # 200KB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

