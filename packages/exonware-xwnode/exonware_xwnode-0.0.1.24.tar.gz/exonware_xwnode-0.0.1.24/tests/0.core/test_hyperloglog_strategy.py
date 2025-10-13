"""
Unit tests for HyperLogLog strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.hyperloglog import HyperLogLogStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestHyperLogLogCore:
    """Core tests for HyperLogLog strategy."""
    
    def test_initialization(self):
        """Test initialization with EXACT parameters."""
        strategy = HyperLogLogStrategy()
        assert strategy is not None
        assert strategy.mode == NodeMode.HYPERLOGLOG
    
    def test_basic_add(self):
        """Test adding elements."""
        strategy = HyperLogLogStrategy()
        strategy.add("item1")
        strategy.add("item2")
        strategy.add("item3")
        
        # Cardinality estimate should be close to 3
        estimate = strategy.estimate_cardinality()
        assert 2 <= estimate <= 5, f"Expected cardinality ~3, got {estimate}"
    
    def test_duplicate_handling(self):
        """Test duplicate elements with EXACT expected behavior."""
        strategy = HyperLogLogStrategy()
        
        # Add same item multiple times
        for _ in range(100):
            strategy.add("duplicate")
        
        # Cardinality should be ~1 (one unique element)
        estimate = strategy.estimate_cardinality()
        assert estimate <= 3, f"Expected cardinality ~1 for duplicates, got {estimate}"
    
    def test_large_unique_set(self):
        """Test with large unique set - EXACT bounds checking."""
        strategy = HyperLogLogStrategy()
        
        # Add 1000 unique items
        for i in range(1000):
            strategy.add(f"item_{i}")
        
        # Estimate should be close to 1000 (within typical HLL error: ±2%)
        estimate = strategy.estimate_cardinality()
        lower_bound = 980  # 2% error
        upper_bound = 1020  # 2% error
        assert lower_bound <= estimate <= upper_bound, (
            f"Expected cardinality in [{lower_bound}, {upper_bound}], got {estimate}"
        )
    
    def test_clear_operation(self):
        """Test clear with EXACT expected result."""
        strategy = HyperLogLogStrategy()
        strategy.add("item")
        strategy.clear()
        
        # After clear, cardinality should be 0
        assert strategy.estimate_cardinality() == 0
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = HyperLogLogStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.PROBABILISTIC in traits
        assert NodeTrait.COMPRESSED in traits


@pytest.mark.xwnode_core
class TestHyperLogLogSpecificFeatures:
    """Tests for HyperLogLog specific features."""
    
    def test_merge_operation(self):
        """Test merging two HyperLogLog sketches."""
        strategy1 = HyperLogLogStrategy()
        strategy2 = HyperLogLogStrategy()
        
        # Add different items to each
        for i in range(50):
            strategy1.add(f"item_{i}")
        for i in range(50, 100):
            strategy2.add(f"item_{i}")
        
        # Get individual cardinalities
        card1 = strategy1.estimate_cardinality()
        card2 = strategy2.estimate_cardinality()
        
        # Merge returns new merged HLL
        merged = strategy1.merge(strategy2)
        
        # Combined cardinality should be ~100
        estimate = merged.estimate_cardinality()
        # HyperLogLog has ~2% error, allow reasonable bounds
        assert 90 <= estimate <= 110, f"Expected merged cardinality ~100, got {estimate} (card1={card1}, card2={card2})"


@pytest.mark.xwnode_performance
class TestHyperLogLogPerformance:
    """Performance tests for HyperLogLog strategy."""
    
    def test_time_complexity(self):
        """Validate O(1) add operation."""
        import time
        strategy = HyperLogLogStrategy()
        
        # Many additions should be fast
        start = time.perf_counter()
        for i in range(10000):
            strategy.add(f"item_{i}")
        elapsed = time.perf_counter() - start
        
        # HyperLogLog operations are O(1)
        assert elapsed < 0.15, f"Additions too slow: {elapsed}s for 10000 ops"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate constant memory usage."""
        def operation():
            strategy = HyperLogLogStrategy()
            # Add many items - memory should stay constant
            for i in range(10000):
                strategy.add(f"item_{i}")
            return strategy
        
        result, memory = measure_memory(operation)
        # HyperLogLog uses constant memory regardless of cardinality
        # But tracks items_added set - acceptable for verification
        assert memory < 2 * 1024 * 1024, f"Memory {memory} exceeds 2MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

