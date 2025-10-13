"""
Unit tests for Set Hash strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri  
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.set_hash import SetHashStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestSetHashCore:
    """Core tests for Set Hash strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = SetHashStrategy()
        assert strategy is not None
        assert strategy.mode == NodeMode.SET_HASH
        assert len(strategy) == 0
    
    def test_add_operation(self):
        """Test adding elements with EXACT expected behavior."""
        strategy = SetHashStrategy()
        strategy.add("a")
        strategy.add("b")
        strategy.add("c")
        
        assert len(strategy) == 3
        assert "a" in strategy
        assert "b" in strategy
        assert "c" in strategy
    
    def test_duplicate_handling(self):
        """Test duplicates not added with EXACT count."""
        strategy = SetHashStrategy()
        strategy.add("item")
        strategy.add("item")
        strategy.add("item")
        
        # Set should have exactly 1 item
        assert len(strategy) == 1, "Set should not contain duplicates"
    
    def test_remove_operation(self):
        """Test removing elements."""
        strategy = SetHashStrategy()
        strategy.add("a")
        strategy.add("b")
        
        assert strategy.remove("a")
        assert len(strategy) == 1
        assert "a" not in strategy
        assert not strategy.remove("nonexistent")
    
    def test_set_operations(self):
        """Test set operations with EXACT expected results."""
        set1 = SetHashStrategy()
        set1.add("a")
        set1.add("b")
        set1.add("c")
        
        set2 = SetHashStrategy()
        set2.add("b")
        set2.add("c")
        set2.add("d")
        
        # Union: {a, b, c, d}
        union = set1.union(set2)
        assert len(union) == 4
        
        # Intersection: {b, c}
        intersection = set1.intersection(set2)
        assert len(intersection) == 2
        
        # Difference: {a}
        difference = set1.difference(set2)
        assert len(difference) == 1
    
    def test_clear_operation(self):
        """Test clear."""
        strategy = SetHashStrategy()
        strategy.add("item")
        strategy.clear()
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = SetHashStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.INDEXED in traits


@pytest.mark.xwnode_performance
class TestSetHashPerformance:
    """Performance tests for Set Hash strategy."""
    
    def test_time_complexity(self):
        """Validate O(1) operations."""
        import time
        strategy = SetHashStrategy()
        
        start = time.perf_counter()
        for i in range(1000):
            strategy.add(f"item_{i}")
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.05
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage."""
        def operation():
            strategy = SetHashStrategy()
            for i in range(1000):
                strategy.add(f"item_{i}")
            return strategy
        
        result, memory = measure_memory(operation)
        assert memory < 500 * 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

