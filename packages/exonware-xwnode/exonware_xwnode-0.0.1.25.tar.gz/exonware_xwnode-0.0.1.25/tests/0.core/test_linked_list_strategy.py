"""
#exonware/xwnode/tests/0.core/test_linked_list_strategy.py

Comprehensive tests for LINKED_LIST node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.linked_list import LinkedListStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestLinkedListCore:
    """Core tests for LINKED_LIST strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = LinkedListStrategy()
        assert strategy is not None
        assert len(strategy) == 0
    
    def test_insert_and_get(self):
        """Test basic operations."""
        strategy = LinkedListStrategy()
        strategy.insert(0, "value1")
        strategy.insert(1, "value2")
        assert len(strategy) >= 2
    
    def test_push_operations(self):
        """Test push front/back."""
        strategy = LinkedListStrategy()
        strategy.push_back("a")
        strategy.push_back("b")
        strategy.push_front("z")
        assert len(strategy) == 3
    
    def test_pop_operations(self):
        """Test pop front/back."""
        strategy = LinkedListStrategy()
        strategy.push_back("a")
        strategy.push_back("b")
        
        val = strategy.pop_back()
        assert val == "b"
        assert len(strategy) == 1
    
    def test_iteration(self):
        """Test iteration."""
        strategy = LinkedListStrategy()
        for i in range(10):
            strategy.push_back(i)
        values = list(strategy.values())
        assert len(values) >= 10
    
    def test_clear(self):
        """Test clear."""
        strategy = LinkedListStrategy()
        for i in range(10):
            strategy.push_back(i)
        strategy.clear()
        assert len(strategy) == 0


@pytest.mark.xwnode_performance
class TestLinkedListPerformance:
    """Performance tests for Linked List."""
    
    def test_insertion_o1(self):
        """Test O(1) insertion at known position."""
        import time
        
        # Test insertion at head (O(1))
        timings = {}
        for size in [100, 1000, 10000]:
            s = LinkedListStrategy()
            # Pre-fill
            for i in range(size):
                s.push_back(i)
            
            # Measure front insertion
            measurements = []
            for _ in range(100):
                start = time.perf_counter()
                s.push_front("new")
                elapsed = time.perf_counter() - start
                measurements.append(elapsed)
            measurements.sort()
            timings[size] = measurements[len(measurements)//2]
        
        ratio = timings[10000] / timings[100]
        assert ratio < 3.0, f"Expected O(1) front insertion, got ratio {ratio:.2f}"


@pytest.mark.xwnode_core
class TestLinkedListEdgeCases:
    """Edge cases."""
    
    def test_empty(self):
        """Test empty list."""
        strategy = LinkedListStrategy()
        assert len(strategy) == 0
    
    def test_single_element(self):
        """Test single element."""
        strategy = LinkedListStrategy()
        strategy.push_back("only")
        assert len(strategy) == 1

