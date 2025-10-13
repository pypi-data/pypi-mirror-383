"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_heap_strategy.py

Comprehensive tests for HeapStrategy.

Priority queue with O(1) get_min and O(log n) operations.
Critical for priority-based operations and scheduling.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.heap import HeapStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.fixture
def empty_heap():
    """Create empty heap."""
    return HeapStrategy()


@pytest.fixture
def min_heap():
    """Create min heap with values."""
    heap = HeapStrategy()
    values = [5, 3, 8, 1, 9, 2, 7]
    for i, val in enumerate(values):
        heap.insert(i, val)
    return heap


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestHeapStrategyInterface:
    """Test HeapStrategy interface compliance."""
    
    def test_insert_operation(self, empty_heap):
        """Test inserting elements into heap."""
        empty_heap.insert(0, 10)
        empty_heap.insert(1, 5)
        empty_heap.insert(2, 15)
        
        assert empty_heap.size() == 3
    
    def test_size_operation(self, min_heap):
        """Test size returns correct count."""
        assert min_heap.size() == 7
    
    def test_is_empty(self, empty_heap):
        """Test is_empty on empty heap."""
        assert empty_heap.is_empty() is True


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestHeapPerformance:
    """Test Heap performance characteristics."""
    
    def test_priority_operations_fast(self):
        """Test that priority operations are fast."""
        import time
        
        heap = HeapStrategy()
        
        # Insert many items
        start = time.time()
        for i in range(10000):
            heap.insert(i, i)
        elapsed = time.time() - start
        
        # Should complete quickly (< 1 second)
        assert elapsed < 1.0


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestHeapEdgeCases:
    """Test Heap edge cases."""
    
    def test_duplicate_values(self, empty_heap):
        """Test handling of duplicate values."""
        empty_heap.insert(0, 5)
        empty_heap.insert(1, 5)
        empty_heap.insert(2, 5)
        
        assert empty_heap.size() == 3
    
    def test_negative_values(self, empty_heap):
        """Test handling of negative values."""
        empty_heap.insert(0, -10)
        empty_heap.insert(1, -5)
        empty_heap.insert(2, 0)
        
        assert empty_heap.size() == 3

