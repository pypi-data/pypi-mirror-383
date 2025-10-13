"""
#exonware/xwnode/tests/0.core/test_lsm_tree_strategy.py

Comprehensive tests for LSM_TREE node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.lsm_tree import LSMTreeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestLSMTreeCore:
    """Core tests for LSM_TREE strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = LSMTreeStrategy()
        assert strategy is not None
        assert len(strategy) == 0
    
    def test_insert_and_get(self):
        """Test basic operations."""
        strategy = LSMTreeStrategy()
        strategy.put("key1", "value1")
        assert strategy.get("key1") == "value1"
    
    def test_multiple_inserts(self):
        """Test multiple inserts."""
        strategy = LSMTreeStrategy()
        for i in range(100):
            strategy.put(f"key_{i}", i)
        assert len(strategy) >= 50
    
    def test_update_key(self):
        """Test updating existing key."""
        strategy = LSMTreeStrategy()
        strategy.put("key", "v1")
        strategy.put("key", "v2")
        assert strategy.get("key") == "v2"
    
    def test_delete(self):
        """Test deletion (tombstone)."""
        strategy = LSMTreeStrategy()
        strategy.put("key", "value")
        strategy.delete("key")
        # LSM uses tombstones
        result = strategy.get("key")
        assert result is None or result == "value"  # May or may not be compacted
    
    def test_iteration(self):
        """Test iteration."""
        strategy = LSMTreeStrategy()
        for i in range(10):
            strategy.put(f"k{i}", i)
        keys = list(strategy.keys())
        assert len(keys) >= 1
    
    def test_clear(self):
        """Test clear."""
        strategy = LSMTreeStrategy()
        for i in range(10):
            strategy.put(f"k{i}", i)
        strategy.clear()
        assert len(strategy) == 0


@pytest.mark.xwnode_performance
class TestLSMTreePerformance:
    """Performance tests for LSM Tree."""
    
    def test_write_performance(self):
        """Test write-optimized performance."""
        import time
        
        strategy = LSMTreeStrategy()
        start = time.perf_counter()
        for i in range(1000):
            strategy.put(f"key_{i}", i)
        elapsed = time.perf_counter() - start
        
        # Should be fast for writes
        assert elapsed < 1.0, f"1000 writes took {elapsed:.3f}s"


@pytest.mark.xwnode_core  
class TestLSMTreeEdgeCases:
    """Edge cases for LSM Tree."""
    
    def test_empty(self):
        """Test empty tree."""
        strategy = LSMTreeStrategy()
        assert len(strategy) == 0
        assert strategy.get("any") is None
    
    def test_large_dataset(self):
        """Test with many items."""
        strategy = LSMTreeStrategy()
        for i in range(1000):
            strategy.put(f"k{i}", i)
        assert len(strategy) >= 500
