"""
#exonware/xwnode/tests/0.core/test_array_list_strategy.py

Comprehensive tests for ARRAY_LIST node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.array_list import ArrayListStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestArrayListCore:
    """Core tests for ARRAY_LIST strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = ArrayListStrategy()
        assert strategy is not None
        assert len(strategy) == 0
    
    def test_insert_and_get(self):
        """Test basic operations."""
        strategy = ArrayListStrategy()
        strategy.insert(0, "value1")
        strategy.insert(1, "value2")
        assert len(strategy) >= 2
    
    def test_push_operations(self):
        """Test push front/back."""
        strategy = ArrayListStrategy()
        strategy.push_back("a")
        strategy.push_back("b")
        strategy.push_front("z")
        assert len(strategy) == 3
    
    def test_pop_operations(self):
        """Test pop front/back."""
        strategy = ArrayListStrategy()
        strategy.push_back("a")
        strategy.push_back("b")
        
        val = strategy.pop_back()
        assert val == "b"
        assert len(strategy) == 1
    
    def test_iteration(self):
        """Test iteration."""
        strategy = ArrayListStrategy()
        for i in range(10):
            strategy.push_back(i)
        values = list(strategy.values())
        assert len(values) >= 10
    
    def test_clear(self):
        """Test clear."""
        strategy = ArrayListStrategy()
        for i in range(10):
            strategy.push_back(i)
        strategy.clear()
        assert len(strategy) == 0


@pytest.mark.xwnode_performance
class TestArrayListPerformance:
    """Performance tests for Array List."""
    
    def test_indexed_access_o1(self):
        """Test O(1) indexed access."""
        import time
        
        strategies = {}
        for size in [100, 1000, 10000]:
            s = ArrayListStrategy()
            for i in range(size):
                s.push_back(i)
            strategies[size] = s
        
        timings = {}
        for size, s in strategies.items():
            measurements = []
            for _ in range(100):
                start = time.perf_counter()
                s.get_at_index(size//2)
                elapsed = time.perf_counter() - start
                measurements.append(elapsed)
            measurements.sort()
            timings[size] = measurements[len(measurements)//2]
        
        ratio = timings[10000] / timings[100]
        assert ratio < 3.0, f"Expected O(1) indexed access, got ratio {ratio:.2f}"


@pytest.mark.xwnode_core
class TestArrayListEdgeCases:
    """Edge cases."""
    
    def test_empty(self):
        """Test empty list."""
        strategy = ArrayListStrategy()
        assert len(strategy) == 0
    
    def test_single_element(self):
        """Test single element."""
        strategy = ArrayListStrategy()
        strategy.push_back("only")
        assert len(strategy) == 1
