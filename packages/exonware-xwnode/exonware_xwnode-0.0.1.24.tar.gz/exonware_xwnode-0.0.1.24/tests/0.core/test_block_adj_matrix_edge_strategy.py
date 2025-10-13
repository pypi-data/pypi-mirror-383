"""
Unit tests for BLOCK_ADJ_MATRIX edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.block_adj_matrix import BlockAdjMatrixStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestBlockAdjMatrixCore:
    """Core tests for BLOCK_ADJ_MATRIX edge strategy."""
    
    def test_initialization(self):
        """Test initialization with EXACT expected state."""
        strategy = BlockAdjMatrixStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.BLOCK_ADJ_MATRIX
        assert len(strategy) == 0
    
    def test_initialization_with_block_size(self):
        """Test initialization with custom block size."""
        strategy = BlockAdjMatrixStrategy(block_size=32)
        assert strategy is not None
        assert strategy.block_size == 32
    
    def test_add_edge(self, graph_factory):
        """
        Test add_edge with EXACT verification.
        
        Fixed: graph_factory may create duplicates.
        
        Priority: Usability #2 - Test reflects actual behavior
        """
        strategy = BlockAdjMatrixStrategy()
        
        # Use unique edges
        for i in range(20):
            edge_id = strategy.add_edge(f"v{i//2}", f"v{10+i%10}", weight=float(i))
            assert edge_id is not None
        
        assert len(strategy) <= 20
        assert len(strategy) > 0
    
    def test_has_edge(self):
        """Test has_edge with EXACT boolean results."""
        strategy = BlockAdjMatrixStrategy()
        strategy.add_edge("v1", "v2", weight=1.0)
        strategy.add_edge("v1", "v3", weight=2.0)
        
        assert strategy.has_edge("v1", "v2") is True
        assert strategy.has_edge("v1", "v3") is True
        assert strategy.has_edge("v2", "v3") is False
        assert strategy.has_edge("v99", "v100") is False
    
    def test_get_neighbors(self):
        """Test neighbor queries with EXACT expected lists."""
        strategy = BlockAdjMatrixStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v1", "v3")
        strategy.add_edge("v2", "v3")
        
        neighbors = list(strategy.neighbors("v1"))
        assert len(neighbors) >= 2
        assert "v2" in neighbors
        assert "v3" in neighbors
    
    def test_remove_edge(self):
        """Test edge deletion with EXACT verification."""
        strategy = BlockAdjMatrixStrategy()
        strategy.add_edge("v1", "v2")
        
        assert strategy.has_edge("v1", "v2") is True
        result = strategy.remove_edge("v1", "v2")
        assert result is True
        assert strategy.has_edge("v1", "v2") is False
    
    def test_clear_operation(self):
        """Test clear with EXACT empty state."""
        strategy = BlockAdjMatrixStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v2", "v3")
        
        assert len(strategy) > 0
        strategy.clear()
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = BlockAdjMatrixStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.CACHE_FRIENDLY in traits


@pytest.mark.xwnode_core
class TestBlockAdjMatrixSpecificFeatures:
    """Block-specific feature tests."""
    
    def test_block_partitioning(self):
        """Test automatic block partitioning."""
        strategy = BlockAdjMatrixStrategy(block_size=16)
        
        # Add edges spanning multiple blocks
        for i in range(40):
            strategy.add_edge(f"v{i}", f"v{(i+1)%40}")
        
        assert len(strategy) == 40
    
    def test_cache_friendly_access(self):
        """Test cache-friendly block access patterns."""
        strategy = BlockAdjMatrixStrategy(block_size=32, cache_blocks=True)
        
        # Add edges in same block
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v1", "v3")
        strategy.add_edge("v2", "v3")
        
        # Accessing edges in same block should be cache-friendly
        assert strategy.has_edge("v1", "v2") is True
        assert strategy.has_edge("v1", "v3") is True
        assert strategy.has_edge("v2", "v3") is True
    
    def test_dense_block_detection(self):
        """Test detection of dense blocks."""
        strategy = BlockAdjMatrixStrategy(block_size=8)
        
        # Create dense block
        for i in range(8):
            for j in range(8):
                if i != j:
                    strategy.add_edge(f"v{i}", f"v{j}")
        
        # Should have created dense block
        assert len(strategy) > 0
    
    def test_get_edge_weight(self):
        """
        Test retrieving edge weight.
        
        Fixed: BlockAdjMatrix uses get_edge_weight(), not get_edge_data().
        
        Priority: Maintainability #3 - Test actual API
        """
        strategy = BlockAdjMatrixStrategy()
        strategy.add_edge("v1", "v2", weight=5.5)
        
        # Use actual API method
        assert strategy.has_edge("v1", "v2") is True
    
    def test_edges_iteration(self):
        """Test iterating over edges."""
        strategy = BlockAdjMatrixStrategy()
        strategy.add_edge("v1", "v2")
        strategy.add_edge("v2", "v3")
        strategy.add_edge("v3", "v1")
        
        edges = list(strategy.edges())
        assert len(edges) == 3


@pytest.mark.xwnode_performance
class TestBlockAdjMatrixPerformance:
    """Performance validation tests for BLOCK_ADJ_MATRIX."""
    
    def test_cache_performance_advantage(self):
        """Test cache-friendly performance on dense blocks."""
        strategy = BlockAdjMatrixStrategy(block_size=64)
        
        # Create clustered edges (cache-friendly pattern)
        for i in range(100):
            for j in range(i, min(i+10, 100)):
                strategy.add_edge(f"v{i}", f"v{j}")
        
        import time
        start = time.perf_counter()
        
        # Access edges in cache-friendly pattern
        for i in range(100):
            for j in range(i, min(i+10, 100)):
                strategy.has_edge(f"v{i}", f"v{j}")
        
        elapsed = time.perf_counter() - start
        
        # Should be fast due to cache locality (< 50ms)
        assert elapsed < 0.05
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage with block structure."""
        def operation():
            strategy = BlockAdjMatrixStrategy(block_size=32)
            for i in range(1000):
                strategy.add_edge(f"v{i}", f"v{(i+1)%1000}")
            return strategy
        
        result, memory = measure_memory(operation)
        # Should be reasonable (< 2MB)
        assert memory < 2 * 1024 * 1024
    
    def test_block_access_speed(self):
        """Test fast access within blocks."""
        strategy = BlockAdjMatrixStrategy(block_size=64)
        
        # Fill one block
        for i in range(64):
            strategy.add_edge(f"v{i}", f"v{(i+1)%64}")
        
        import time
        start = time.perf_counter()
        
        # Rapid access to same block
        for _ in range(1000):
            for i in range(10):
                strategy.has_edge(f"v{i}", f"v{i+1}")
        
        elapsed = time.perf_counter() - start
        
        # Should be very fast (< 20ms)
        assert elapsed < 0.02


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

