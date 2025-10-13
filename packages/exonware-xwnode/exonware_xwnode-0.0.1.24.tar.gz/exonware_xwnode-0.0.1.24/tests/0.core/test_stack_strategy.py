"""
#exonware/xwnode/tests/0.core/test_stack_strategy.py

Test Stack Strategy Implementation

Company: eXonware.com
Author: Eng. Muhammad AlShehri  
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

import pytest
from exonware.xwnode.nodes.strategies.stack import StackStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


def test_stack_initialization():
    """Test stack strategy initialization"""
    stack = StackStrategy()
    assert len(stack) == 0
    assert stack.is_empty()
    assert NodeTrait.LIFO in stack.get_supported_traits()


def test_stack_push_pop():
    """Test push and pop operations (LIFO semantics)"""
    stack = StackStrategy()
    
    stack.push("value1")
    stack.push("value2")
    stack.push("value3")
    
    assert stack.pop() == "value3"  # LIFO: last in, first out
    assert stack.pop() == "value2"
    assert stack.pop() == "value1"
    
    with pytest.raises(IndexError):
        stack.pop()  # Empty stack should raise


def test_stack_peek():
    """Test peek operation"""
    stack = StackStrategy()
    
    with pytest.raises(IndexError):
        stack.peek()  # Empty stack should raise
    
    stack.push("value1")
    stack.push("value2")
    
    assert stack.peek() == "value2"
    assert stack.peek() == "value2"  # Peek doesn't remove
    assert len(stack) == 2  # Size unchanged


def test_stack_is_empty():
    """Test is_empty and bool operations"""
    stack = StackStrategy()
    
    assert stack.is_empty() is True
    assert not stack  # __bool__ returns False
    
    stack.push("value1")
    assert stack.is_empty() is False
    assert bool(stack)  # __bool__ returns True
    
    stack.pop()
    assert stack.is_empty() is True


def test_stack_size():
    """Test size tracking via __len__"""
    stack = StackStrategy()
    
    assert len(stack) == 0
    
    stack.push("value1")
    stack.push("value2")
    assert len(stack) == 2
    
    stack.pop()
    assert len(stack) == 1


def test_stack_clear():
    """Test clear operation"""
    stack = StackStrategy()
    
    stack.push("value1")
    stack.push("value2")
    stack.push("value3")
    
    stack.clear()
    assert len(stack) == 0
    assert stack.is_empty()


def test_stack_max_size():
    """Test max_size enforcement"""
    stack = StackStrategy(max_size=3)
    
    stack.push("value1")
    stack.push("value2")
    stack.push("value3")
    
    assert stack.is_full()
    
    with pytest.raises(OverflowError):
        stack.push("value4")


def test_stack_iteration():
    """Test iteration (top to bottom)"""
    stack = StackStrategy()
    
    stack.push(1)
    stack.push(2)
    stack.push(3)
    
    items = list(stack)
    assert items == [3, 2, 1]  # Top to bottom


def test_stack_supported_traits():
    """Test that stack supports correct traits"""
    stack = StackStrategy()
    traits = stack.get_supported_traits()
    
    assert NodeTrait.LIFO in traits
    assert NodeTrait.FAST_INSERT in traits
    assert NodeTrait.FAST_DELETE in traits

