"""
#exonware/xwnode/tests/0.core/test_queue_strategy.py

Test Queue Strategy Implementation

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

import pytest
from exonware.xwnode.nodes.strategies.queue import QueueStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


def test_queue_initialization():
    """Test queue strategy initialization"""
    queue = QueueStrategy()
    assert len(queue) == 0
    assert queue.is_empty()
    assert NodeTrait.FIFO in queue.get_supported_traits()


def test_queue_enqueue_dequeue():
    """Test enqueue and dequeue operations (FIFO semantics)"""
    queue = QueueStrategy()
    
    queue.enqueue("value1")
    queue.enqueue("value2")
    queue.enqueue("value3")
    
    assert queue.dequeue() == "value1"  # FIFO: first in, first out
    assert queue.dequeue() == "value2"
    assert queue.dequeue() == "value3"
    
    with pytest.raises(IndexError):
        queue.dequeue()  # Empty queue should raise


def test_queue_front_rear():
    """Test front and rear operations"""
    queue = QueueStrategy()
    
    with pytest.raises(IndexError):
        queue.front()  # Empty queue should raise
    
    queue.enqueue("value1")
    queue.enqueue("value2")
    queue.enqueue("value3")
    
    assert queue.front() == "value1"  # First added
    assert queue.rear() == "value3"   # Last added
    assert len(queue) == 3  # Size unchanged


def test_queue_is_empty():
    """Test is_empty and bool operations"""
    queue = QueueStrategy()
    
    assert queue.is_empty() is True
    assert not queue
    
    queue.enqueue("value1")
    assert queue.is_empty() is False
    assert bool(queue)
    
    queue.dequeue()
    assert queue.is_empty() is True


def test_queue_size():
    """Test size tracking via __len__"""
    queue = QueueStrategy()
    
    assert len(queue) == 0
    
    queue.enqueue("value1")
    queue.enqueue("value2")
    assert len(queue) == 2
    
    queue.dequeue()
    assert len(queue) == 1


def test_queue_clear():
    """Test clear operation"""
    queue = QueueStrategy()
    
    queue.enqueue("value1")
    queue.enqueue("value2")
    queue.enqueue("value3")
    
    queue.clear()
    assert len(queue) == 0
    assert queue.is_empty()


def test_queue_max_size():
    """Test max_size enforcement"""
    queue = QueueStrategy(max_size=3)
    
    queue.enqueue("value1")
    queue.enqueue("value2")
    queue.enqueue("value3")
    
    assert queue.is_full()
    
    with pytest.raises(OverflowError):
        queue.enqueue("value4")


def test_queue_supported_traits():
    """Test that queue supports correct traits"""
    queue = QueueStrategy()
    traits = queue.get_supported_traits()
    
    assert NodeTrait.FIFO in traits
    assert NodeTrait.FAST_INSERT in traits
    assert NodeTrait.FAST_DELETE in traits

