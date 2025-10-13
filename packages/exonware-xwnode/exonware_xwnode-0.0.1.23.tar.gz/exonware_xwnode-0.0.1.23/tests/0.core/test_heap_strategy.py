"""
Unit tests for Heap strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.heap import HeapStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestHeapCore:
    """Core tests for Heap strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = HeapStrategy()
        assert strategy is not None
        assert strategy.mode == NodeMode.HEAP
        assert len(strategy) == 0
    
    def test_basic_operations(self):
        """Test basic push/pop with EXACT expected ordering."""
        strategy = HeapStrategy()
        
        # Push items: value first, priority second
        strategy.push("five", 5)
        strategy.push("one", 1)
        strategy.push("three", 3)
        
        # Min heap - should pop in priority order: 1, 3, 5
        assert strategy.pop() == "one", "Should pop min priority (1) first"
        assert strategy.pop() == "three", "Should pop priority 3 second"
        assert strategy.pop() == "five", "Should pop priority 5 last"
    
    def test_max_heap(self):
        """Test max heap mode with EXACT expected ordering."""
        strategy = HeapStrategy(max_heap=True)
        
        strategy.push("five", 5)
        strategy.push("one", 1)
        strategy.push("three", 3)
        
        # Max heap - should pop in reverse priority order: 5, 3, 1
        assert strategy.pop() == "five", "Should pop max priority (5) first"
        assert strategy.pop() == "three", "Should pop priority 3 second"
        assert strategy.pop() == "one", "Should pop priority 1 last"
    
    def test_peek_operation(self):
        """Test peek without removing."""
        strategy = HeapStrategy()
        strategy.push("two", 2)
        strategy.push("one", 1)
        
        # Peek doesn't remove
        assert strategy.peek() == "one", "Peek should return min priority item"
        assert len(strategy) == 2, "Peek should not remove elements"
        assert strategy.pop() == "one", "Pop should return same as peek"
        assert len(strategy) == 1
    
    def test_clear_operation(self):
        """Test clear."""
        strategy = HeapStrategy()
        strategy.push("one", 1)
        strategy.clear()
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = HeapStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.PRIORITY in traits


@pytest.mark.xwnode_performance
class TestHeapPerformance:
    """Performance tests for Heap strategy."""
    
    def test_time_complexity(self):
        """Validate O(log n) operations."""
        import time
        strategy = HeapStrategy()
        
        # Many push operations
        start = time.perf_counter()
        for i in range(1000):
            strategy.push(i, f"value_{i}")
        elapsed = time.perf_counter() - start
        
        # O(log n) per push
        assert elapsed < 0.05, f"Pushes too slow: {elapsed}s for 1000 ops"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage."""
        def operation():
            strategy = HeapStrategy()
            for i in range(1000):
                strategy.push(i, f"value_{i}")
            return strategy
        
        result, memory = measure_memory(operation)
        assert memory < 500 * 1024  # 500KB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

