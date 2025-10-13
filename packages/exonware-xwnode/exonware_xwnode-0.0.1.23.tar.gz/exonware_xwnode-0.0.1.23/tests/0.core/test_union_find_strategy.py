"""
Unit tests for Union Find strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.union_find import UnionFindStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestUnionFindCore:
    """Core tests for Union Find strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = UnionFindStrategy()
        assert strategy is not None
        assert strategy.mode == NodeMode.UNION_FIND
    
    def test_make_set(self):
        """Test making new sets with EXACT expected behavior."""
        strategy = UnionFindStrategy()
        strategy.put("a", 1)
        strategy.put("b", 2)
        
        # Each element starts in its own set
        assert strategy.get_set_count() == 2, f"Expected 2 disjoint sets, got {strategy.get_set_count()}"
        assert not strategy.connected("a", "b")
    
    def test_union_operation(self):
        """Test union operation with EXACT expected behavior."""
        strategy = UnionFindStrategy()
        strategy.put("a", 1)
        strategy.put("b", 2)
        strategy.put("c", 3)
        
        # Initially 3 sets
        assert strategy.get_set_count() == 3
        
        # Union a and b
        strategy.union_sets("a", "b")
        assert strategy.get_set_count() == 2, "After union(a,b), should have 2 sets"
        assert strategy.connected("a", "b"), "a and b should be connected"
        assert not strategy.connected("a", "c"), "a and c should NOT be connected"
        
        # Union b and c (connects all three)
        strategy.union_sets("b", "c")
        assert strategy.get_set_count() == 1, "After union(b,c), should have 1 set"
        assert strategy.connected("a", "c"), "a and c should now be connected"
    
    def test_find_operation(self):
        """Test find operation with EXACT expected behavior."""
        strategy = UnionFindStrategy()
        strategy.put("a", 1)
        strategy.put("b", 2)
        
        # Find returns representative (could be element itself or root)
        root_a = strategy.find_root("a")
        root_b = strategy.find_root("b")
        
        assert root_a is not None, "Should have a root"
        assert root_b is not None, "Should have a root"
        assert root_a != root_b, "Initially should have different roots"
        
        # After union, both have same root
        strategy.union_sets("a", "b")
        assert strategy.find_root("a") == strategy.find_root("b"), "After union, should have same root"
    
    def test_connected_operation(self):
        """Test connectivity check with EXACT expected behavior."""
        strategy = UnionFindStrategy()
        strategy.put("x", 1)
        strategy.put("y", 2)
        strategy.put("z", 3)
        
        assert not strategy.connected("x", "y")
        
        strategy.union_sets("x", "y")
        assert strategy.connected("x", "y")
        assert not strategy.connected("y", "z")
    
    def test_path_compression(self):
        """Test path compression optimization."""
        strategy = UnionFindStrategy()
        
        # Create chain: a -> b -> c -> d
        for x in ["a", "b", "c", "d"]:
            strategy.put(x, x)
        
        strategy.union_sets("a", "b")
        strategy.union_sets("b", "c")
        strategy.union_sets("c", "d")
        
        # All should be connected
        assert strategy.connected("a", "d")
        
        # Path compression should flatten on find
        root = strategy.find("a")
        assert root is not None
    
    def test_get_set_size(self):
        """Test set size calculation with EXACT expected values."""
        strategy = UnionFindStrategy()
        for i in range(5):
            strategy.put(str(i), i)
        
        # Initially each in own set of size 1
        assert strategy.get_set_size("0") == 1
        
        # Union 0,1,2
        strategy.union_sets("0", "1")
        strategy.union_sets("1", "2")
        assert strategy.get_set_size("0") == 3, "Set containing 0 should have 3 members"
        assert strategy.get_set_size("3") == 1, "Set containing 3 should have 1 member"
    
    def test_clear_operation(self):
        """Test clear operation."""
        strategy = UnionFindStrategy()
        strategy.put("a", 1)
        strategy.put("b", 2)  # Must add b before union!
        strategy.union_sets("a", "b")
        strategy.clear()
        assert strategy.get_set_count() == 0
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = UnionFindStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.GRAPH in traits
        assert NodeTrait.UNION_FIND in traits


@pytest.mark.xwnode_core
class TestUnionFindSpecificFeatures:
    """Tests for Union Find specific features."""
    
    def test_union_by_rank(self):
        """Test union by rank optimization."""
        strategy = UnionFindStrategy()
        
        # Create sets
        for i in range(10):
            strategy.put(str(i), i)
        
        # Perform unions
        for i in range(9):
            strategy.union_sets(str(i), str(i + 1))
        
        # All should be in one set
        assert strategy.get_set_count() == 1
        for i in range(1, 10):
            assert strategy.connected("0", str(i))
    
    def test_multiple_disjoint_sets(self):
        """Test managing multiple disjoint sets with EXACT counts."""
        strategy = UnionFindStrategy()
        
        # Create 3 separate components
        # Component 1: {a, b, c}
        strategy.put("a", 1)
        strategy.put("b", 2)
        strategy.put("c", 3)
        strategy.union_sets("a", "b")
        strategy.union_sets("b", "c")
        
        # Component 2: {x, y}
        strategy.put("x", 10)
        strategy.put("y", 20)
        strategy.union_sets("x", "y")
        
        # Component 3: {z}
        strategy.put("z", 30)
        
        # Should have exactly 3 disjoint sets
        assert strategy.get_set_count() == 3, f"Expected 3 sets, got {strategy.get_set_count()}"
        
        # Verify internal connectivity
        assert strategy.connected("a", "c")
        assert strategy.connected("x", "y")
        assert not strategy.connected("a", "x")
        assert not strategy.connected("c", "z")


@pytest.mark.xwnode_performance
class TestUnionFindPerformance:
    """Performance tests for Union Find strategy."""
    
    def test_time_complexity(self):
        """Validate near O(1) amortized operations."""
        import time
        strategy = UnionFindStrategy()
        
        # Create 1000 elements
        for i in range(1000):
            strategy.put(str(i), i)
        
        # Perform unions (should be fast with path compression + union by rank)
        start = time.perf_counter()
        for i in range(999):
            strategy.union_sets(str(i), str(i + 1))
        elapsed = time.perf_counter() - start
        
        # Should be very fast (nearly O(1) amortized)
        assert elapsed < 0.1, f"Unions too slow: {elapsed}s for 999 operations"
        
        # Verify correctness: all connected
        assert strategy.get_set_count() == 1
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage."""
        def operation():
            strategy = UnionFindStrategy()
            for i in range(1000):
                strategy.put(str(i), i)
            return strategy
        
        result, memory = measure_memory(operation)
        # Union-Find is very memory efficient
        assert memory < 300 * 1024  # 300KB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
