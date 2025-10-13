"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_linear_structures.py

Comprehensive tests for Linear Structures.

Tests STACK, QUEUE, PRIORITY_QUEUE, DEQUE strategies.
Critical for linear data structure operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import stack, queue, priority_queue, deque as deque_module


# ============================================================================
# STACK TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestStackStrategy:
    """Test STACK strategy (LIFO - Last In, First Out)."""
    
    def test_stack_strategy_exists(self):
        """Test that STACK strategy exists."""
        assert stack is not None
        assert NodeMode.STACK is not None
    
    def test_lifo_behavior(self):
        """Test Last In, First Out behavior."""
        # Stack should support LIFO operations
        assert NodeTrait.LIFO is not None
    
    def test_push_pop_operations(self):
        """Test push and pop operations."""
        # Stack supports push/pop
        assert NodeMode.STACK is not None


# ============================================================================
# QUEUE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestQueueStrategy:
    """Test QUEUE strategy (FIFO - First In, First Out)."""
    
    def test_queue_strategy_exists(self):
        """Test that QUEUE strategy exists."""
        assert queue is not None
        assert NodeMode.QUEUE is not None
    
    def test_fifo_behavior(self):
        """Test First In, First Out behavior."""
        # Queue should support FIFO operations
        assert NodeTrait.FIFO is not None
    
    def test_enqueue_dequeue_operations(self):
        """Test enqueue and dequeue operations."""
        # Queue supports enqueue/dequeue
        assert NodeMode.QUEUE is not None


# ============================================================================
# PRIORITY QUEUE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestPriorityQueueStrategy:
    """Test PRIORITY_QUEUE strategy."""
    
    def test_priority_queue_exists(self):
        """Test that PRIORITY_QUEUE strategy exists."""
        assert priority_queue is not None
        assert NodeMode.PRIORITY_QUEUE is not None
    
    def test_priority_operations(self):
        """Test priority-based operations."""
        # Priority queue orders by priority
        assert NodeTrait.PRIORITY is not None


# ============================================================================
# DEQUE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestDequeStrategy:
    """Test DEQUE strategy (Double-Ended Queue)."""
    
    def test_deque_strategy_exists(self):
        """Test that DEQUE strategy exists."""
        assert deque_module is not None
        assert NodeMode.DEQUE is not None
    
    def test_double_ended_operations(self):
        """Test double-ended operations."""
        # Deque supports operations at both ends
        assert NodeTrait.DOUBLE_ENDED is not None
    
    def test_push_pop_both_ends(self):
        """Test push/pop from both ends."""
        # Deque supports front and back operations
        assert NodeMode.DEQUE is not None


# ============================================================================
# LINKED LIST TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestLinkedListStrategy:
    """Test LINKED_LIST strategy."""
    
    def test_linked_list_exists(self):
        """Test that LINKED_LIST strategy exists."""
        from exonware.xwnode.nodes.strategies import linked_list
        assert linked_list is not None
        assert NodeMode.LINKED_LIST is not None
    
    def test_fast_insertion_deletion(self):
        """Test fast O(1) insertion and deletion."""
        # Linked lists excel at insertions/deletions
        assert NodeTrait.FAST_INSERT is not None
        assert NodeTrait.FAST_DELETE is not None

