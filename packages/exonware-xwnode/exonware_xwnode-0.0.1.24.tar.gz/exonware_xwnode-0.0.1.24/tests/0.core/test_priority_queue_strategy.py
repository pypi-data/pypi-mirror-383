"""
#exonware/xwnode/tests/0.core/test_priority_queue_strategy.py

Test Priority Queue Strategy Implementation

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

import pytest
from exonware.xwnode.nodes.strategies.priority_queue import PriorityQueueStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


def test_priority_queue_initialization():
    """Test priority queue strategy initialization"""
    pq = PriorityQueueStrategy()
    assert len(pq) == 0
    assert pq.is_empty()
    assert NodeTrait.PRIORITY in pq.get_supported_traits()


def test_priority_queue_min_heap():
    """Test min-heap operations (default)"""
    pq = PriorityQueueStrategy()
    
    pq.push("Low priority task", 10.0)
    pq.push("High priority task", 1.0)
    pq.push("Medium priority task", 5.0)
    
    # Min-heap: lowest priority number = highest priority
    assert pq.pop() == "High priority task"
    assert pq.pop() == "Medium priority task"
    assert pq.pop() == "Low priority task"


def test_priority_queue_max_heap():
    """Test max-heap operations"""
    pq = PriorityQueueStrategy(is_max_heap=True)
    
    pq.push("Low priority task", 1.0)
    pq.push("High priority task", 10.0)
    pq.push("Medium priority task", 5.0)
    
    # Max-heap: highest priority number = highest priority
    assert pq.pop() == "High priority task"
    assert pq.pop() == "Medium priority task"
    assert pq.pop() == "Low priority task"


def test_priority_queue_peek():
    """Test peek operation"""
    pq = PriorityQueueStrategy()
    
    with pytest.raises(IndexError):
        pq.peek()  # Empty queue should raise
    
    pq.push("value1", 10.0)
    pq.push("value2", 5.0)
    
    assert pq.peek() == "value2"  # Lowest priority
    assert pq.peek() == "value2"  # Peek doesn't remove
    assert len(pq) == 2


def test_priority_queue_peek_with_priority():
    """Test peek_with_priority operation"""
    pq = PriorityQueueStrategy()
    
    pq.push("task1", 5.0)
    pq.push("task2", 3.0)
    
    priority, value = pq.peek_with_priority()
    assert priority == 3.0
    assert value == "task2"


def test_priority_queue_pushpop():
    """Test efficient pushpop operation"""
    pq = PriorityQueueStrategy()
    
    pq.push("value1", 5.0)
    result = pq.pushpop("value2", 3.0)
    
    # Should pop value2 (lower priority)
    assert result == "value2"
    assert len(pq) == 1
    assert pq.peek() == "value1"


def test_priority_queue_stable_sort():
    """Test that equal priorities maintain insertion order"""
    pq = PriorityQueueStrategy()
    
    pq.push("first", 5.0)
    pq.push("second", 5.0)
    pq.push("third", 5.0)
    
    assert pq.pop() == "first"
    assert pq.pop() == "second"
    assert pq.pop() == "third"


def test_priority_queue_max_size():
    """Test max_size enforcement"""
    pq = PriorityQueueStrategy(max_size=3)
    
    pq.push("value1", 1.0)
    pq.push("value2", 2.0)
    pq.push("value3", 3.0)
    
    assert pq.is_full()
    
    with pytest.raises(OverflowError):
        pq.push("value4", 4.0)


def test_priority_queue_supported_traits():
    """Test that priority queue supports correct traits"""
    pq = PriorityQueueStrategy()
    traits = pq.get_supported_traits()
    
    assert NodeTrait.PRIORITY in traits
    assert NodeTrait.HEAP_OPERATIONS in traits

