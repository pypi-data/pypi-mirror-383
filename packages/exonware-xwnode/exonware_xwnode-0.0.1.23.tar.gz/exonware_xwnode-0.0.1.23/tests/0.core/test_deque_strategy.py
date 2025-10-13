"""
#exonware/xwnode/tests/0.core/test_deque_strategy.py

Test Deque Strategy Implementation

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

import pytest
from exonware.xwnode.nodes.strategies.deque import DequeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


def test_deque_initialization():
    """Test deque strategy initialization"""
    dq = DequeStrategy()
    assert len(dq) == 0
    assert dq.is_empty()
    assert NodeTrait.DOUBLE_ENDED in dq.get_supported_traits()


def test_deque_append_pop():
    """Test append and pop operations (right end)"""
    dq = DequeStrategy()
    
    dq.append("value1")
    dq.append("value2")
    dq.append("value3")
    
    assert dq.pop() == "value3"
    assert dq.pop() == "value2"
    assert dq.pop() == "value1"
    
    with pytest.raises(IndexError):
        dq.pop()  # Empty deque should raise


def test_deque_appendleft_popleft():
    """Test appendleft and popleft operations (left end)"""
    dq = DequeStrategy()
    
    dq.appendleft("value1")
    dq.appendleft("value2")
    dq.appendleft("value3")
    
    assert dq.popleft() == "value3"
    assert dq.popleft() == "value2"
    assert dq.popleft() == "value1"
    
    with pytest.raises(IndexError):
        dq.popleft()  # Empty deque should raise


def test_deque_mixed_operations():
    """Test mixed front and back operations"""
    dq = DequeStrategy()
    
    dq.append("value1")      # Right: [value1]
    dq.appendleft("value2")  # Left:  [value2, value1]
    dq.append("value3")      # Right: [value2, value1, value3]
    dq.appendleft("value4")  # Left:  [value4, value2, value1, value3]
    
    assert dq.popleft() == "value4"
    assert dq.pop() == "value3"
    assert dq.popleft() == "value2"
    assert dq.pop() == "value1"


def test_deque_rotate():
    """Test rotate operation"""
    dq = DequeStrategy()
    
    dq.extend([1, 2, 3, 4, 5])
    
    dq.rotate(2)  # Rotate right by 2
    assert list(dq) == [4, 5, 1, 2, 3]
    
    dq.rotate(-1)  # Rotate left by 1
    assert list(dq) == [5, 1, 2, 3, 4]


def test_deque_reverse():
    """Test reverse operation"""
    dq = DequeStrategy()
    
    dq.extend([1, 2, 3, 4, 5])
    dq.reverse()
    
    assert list(dq) == [5, 4, 3, 2, 1]


def test_deque_extend():
    """Test extend and extendleft operations"""
    dq = DequeStrategy()
    
    dq.extend([1, 2, 3])
    assert list(dq) == [1, 2, 3]
    
    dq.extendleft([4, 5, 6])
    assert list(dq) == [6, 5, 4, 1, 2, 3]  # Note: extendleft reverses


def test_deque_max_size():
    """Test max_size with automatic eviction"""
    dq = DequeStrategy(max_size=3)
    
    dq.append(1)
    dq.append(2)
    dq.append(3)
    dq.append(4)  # Evicts 1 (leftmost)
    
    assert list(dq) == [2, 3, 4]
    assert len(dq) == 3


def test_deque_peek():
    """Test peek_left and peek_right operations"""
    dq = DequeStrategy()
    
    dq.extend([1, 2, 3])
    
    assert dq.peek_left() == 1
    assert dq.peek_right() == 3
    assert len(dq) == 3  # Unchanged


def test_deque_supported_traits():
    """Test that deque supports correct traits"""
    dq = DequeStrategy()
    traits = dq.get_supported_traits()
    
    assert NodeTrait.DOUBLE_ENDED in traits
    assert NodeTrait.FAST_INSERT in traits
    assert NodeTrait.FAST_DELETE in traits

