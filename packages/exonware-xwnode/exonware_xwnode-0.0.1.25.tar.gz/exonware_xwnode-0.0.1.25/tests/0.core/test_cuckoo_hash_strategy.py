"""
Unit tests for Cuckoo Hash strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.cuckoo_hash import CuckooHashStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestCuckooHashCore:
    """Core tests for Cuckoo Hash strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = CuckooHashStrategy()
        assert strategy is not None
        assert strategy.mode == NodeMode.CUCKOO_HASH
        assert len(strategy) == 0
    
    def test_basic_operations(self):
        """Test basic put/get operations with EXACT expected values."""
        strategy = CuckooHashStrategy()
        strategy.put("key1", "value1")
        assert strategy.get("key1") == "value1"
        assert len(strategy) == 1
        
        strategy.put("key2", "value2")
        assert strategy.get("key2") == "value2"
        assert len(strategy) == 2
    
    def test_update_existing_key(self):
        """Test updating existing key with EXACT expected behavior."""
        strategy = CuckooHashStrategy()
        strategy.put("key", "value1")
        assert strategy.get("key") == "value1"
        
        strategy.put("key", "value2")
        assert strategy.get("key") == "value2"
        assert len(strategy) == 1, "Size should not change on update"
    
    def test_delete_operation(self):
        """Test delete with EXACT expected behavior."""
        strategy = CuckooHashStrategy()
        strategy.put("key1", "value1")
        strategy.put("key2", "value2")
        
        assert strategy.delete("key1")
        assert not strategy.has("key1")
        assert strategy.has("key2")
        assert len(strategy) == 1
    
    def test_has_operation(self):
        """Test has operation."""
        strategy = CuckooHashStrategy()
        strategy.put("exists", "value")
        
        assert strategy.has("exists")
        assert not strategy.has("nonexistent")
    
    def test_clear_operation(self):
        """Test clear operation."""
        strategy = CuckooHashStrategy()
        strategy.put("key", "value")
        strategy.clear()
        assert len(strategy) == 0
        assert not strategy.has("key")
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = CuckooHashStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.INDEXED in traits


@pytest.mark.xwnode_core
class TestCuckooHashSpecificFeatures:
    """Tests for Cuckoo Hash specific features."""
    
    def test_collision_handling(self):
        """Test cuckoo hashing handles collisions."""
        strategy = CuckooHashStrategy()
        
        # Add many items to trigger evictions
        for i in range(50):
            strategy.put(f"key_{i}", i)
        
        # All should be retrievable
        for i in range(50):
            assert strategy.get(f"key_{i}") == i, f"Key key_{i} should have value {i}"
    
    def test_rehashing(self):
        """Test rehashing when table is full."""
        strategy = CuckooHashStrategy()
        
        # Add many items
        for i in range(100):
            strategy.put(f"item_{i}", i)
        
        # All items should still be accessible
        assert len(strategy) == 100
        for i in range(100):
            assert strategy.has(f"item_{i}")


@pytest.mark.xwnode_performance
class TestCuckooHashPerformance:
    """Performance tests for Cuckoo Hash strategy."""
    
    def test_time_complexity(self):
        """Validate O(1) expected time operations."""
        import time
        strategy = CuckooHashStrategy()
        
        # Many insertions
        start = time.perf_counter()
        for i in range(1000):
            strategy.put(f"key_{i}", i)
        elapsed = time.perf_counter() - start
        
        # Should be fast (O(1) expected)
        assert elapsed < 0.1, f"Insertions too slow: {elapsed}s for 1000 ops"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage."""
        def operation():
            strategy = CuckooHashStrategy()
            for i in range(1000):
                strategy.put(f"key_{i}", i)
            return strategy
        
        result, memory = measure_memory(operation)
        # Cuckoo hash has overhead for two tables
        assert memory < 500 * 1024  # 500KB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

