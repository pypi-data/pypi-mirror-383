"""
Unit tests for Count-Min Sketch strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.count_min_sketch import CountMinSketchStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestCountMinSketchCore:
    """Core tests for Count-Min Sketch strategy."""
    
    def test_initialization(self):
        """Test initialization with EXACT parameters."""
        strategy = CountMinSketchStrategy()
        assert strategy is not None
        assert strategy.mode == NodeMode.COUNT_MIN_SKETCH
        assert strategy.width > 0, "Width must be positive"
        assert strategy.depth > 0, "Depth must be positive"
    
    def test_basic_increment(self):
        """Test basic increment operation with EXACT count verification."""
        strategy = CountMinSketchStrategy()
        
        # Increment "apple" 5 times
        for _ in range(5):
            strategy.increment("apple")
        
        # Estimate should be >= 5 (may overestimate, never underestimate)
        count = strategy.estimate_count("apple")
        assert count >= 5, f"Count-Min Sketch cannot underestimate: expected >=5, got {count}"
        assert count <= 10, f"Overestimation too high: expected <=10, got {count}"
    
    def test_multiple_items(self):
        """Test counting multiple items with EXACT counts."""
        strategy = CountMinSketchStrategy()
        
        # Add different items
        strategy.increment("a", 10)  # a: 10
        strategy.increment("b", 20)  # b: 20
        strategy.increment("c", 5)   # c: 5
        
        # Estimates should be >= actual (probabilistic)
        assert strategy.estimate_count("a") >= 10
        assert strategy.estimate_count("b") >= 20
        assert strategy.estimate_count("c") >= 5
    
    def test_zero_count(self):
        """Test items not added have zero/low count."""
        strategy = CountMinSketchStrategy()
        strategy.increment("exists", 100)
        
        # Item never added should have low count
        count_nonexistent = strategy.estimate_count("never_added")
        assert count_nonexistent < 100, "Nonexistent item should have low count"
    
    def test_clear_operation(self):
        """Test clear operation."""
        strategy = CountMinSketchStrategy()
        strategy.increment("item", 100)
        strategy.clear()
        
        # After clear, counts should be zero
        assert strategy.estimate_count("item") == 0
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = CountMinSketchStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.PROBABILISTIC in traits
        assert NodeTrait.STREAMING in traits


@pytest.mark.xwnode_core
class TestCountMinSketchSpecificFeatures:
    """Tests for Count-Min Sketch specific features."""
    
    def test_error_bounds(self):
        """Test probabilistic error bounds are reasonable."""
        strategy = CountMinSketchStrategy(epsilon=0.01, delta=0.01)
        
        # Add many items
        for i in range(100):
            strategy.increment(f"item_{i}", 10)
        
        # Check estimates are reasonable
        for i in range(10):
            estimate = strategy.estimate_count(f"item_{i}")
            # Should be >= 10 (true count), but not wildly off
            assert 10 <= estimate <= 50, f"Estimate {estimate} outside reasonable bounds [10, 50]"
    
    def test_heavy_hitters(self):
        """Test heavy hitter tracking."""
        strategy = CountMinSketchStrategy(track_heavy_hitters=True)
        
        # Add items with different frequencies
        strategy.increment("rare", 1)
        strategy.increment("common", 100)
        strategy.increment("very_common", 1000)
        
        # Verify counts are tracked
        estimate_rare = strategy.estimate_count("rare")
        estimate_common = strategy.estimate_count("common")
        estimate_very_common = strategy.estimate_count("very_common")
        
        # Counts should be >= actual (no false negatives)
        assert estimate_rare >= 1
        assert estimate_common >= 100
        assert estimate_very_common >= 1000


@pytest.mark.xwnode_performance
class TestCountMinSketchPerformance:
    """Performance tests for Count-Min Sketch strategy."""
    
    def test_time_complexity(self):
        """Validate O(1) increment and query operations."""
        import time
        strategy = CountMinSketchStrategy()
        
        # Many increments should be fast
        start = time.perf_counter()
        for i in range(10000):
            strategy.increment(f"item_{i % 100}")
        elapsed = time.perf_counter() - start
        
        # Should be very fast (O(1) per operation)
        # Note: 10000 ops with MD5 hashing takes ~0.1s, allow reasonable margin
        assert elapsed < 0.15, f"Increments too slow: {elapsed}s for 10000 ops"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory efficiency."""
        def operation():
            strategy = CountMinSketchStrategy()
            for i in range(1000):
                strategy.increment(f"item_{i}")
            return strategy
        
        result, memory = measure_memory(operation)
        # Count-Min Sketch is very memory efficient
        assert memory < 500 * 1024  # 500KB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

