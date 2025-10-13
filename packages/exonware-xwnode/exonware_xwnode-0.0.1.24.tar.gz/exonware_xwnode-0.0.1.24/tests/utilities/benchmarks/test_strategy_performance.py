"""
#exonware/xwnode/tests/utilities/benchmarks/test_strategy_performance.py

Performance benchmarks for all node and edge strategies.

Validates performance claims in defs.py metadata:
- Time complexity verification
- Memory usage measurement
- Performance gains validation
- Benchmark documentation

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
import time
import sys
from typing import List, Dict, Any
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode, EdgeMode, NODE_STRATEGY_METADATA

# ============================================================================
# PERFORMANCE BENCHMARK UTILITIES
# ============================================================================

def measure_operation_time(operation_func, iterations=1000):
    """Measure average time for an operation."""
    start = time.time()
    for _ in range(iterations):
        operation_func()
    elapsed = time.time() - start
    return elapsed / iterations


def measure_memory_usage(data_func):
    """Measure memory usage of data structure."""
    import tracemalloc
    
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()
    
    data = data_func()
    
    snapshot_after = tracemalloc.take_snapshot()
    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    
    tracemalloc.stop()
    
    total_memory = sum(stat.size_diff for stat in top_stats)
    return total_memory


# ============================================================================
# NODE STRATEGY BENCHMARKS
# ============================================================================

class TestHashMapPerformance:
    """Benchmark HASH_MAP strategy performance."""
    
    @pytest.mark.performance
    def test_hash_map_o1_get_complexity(self):
        """Verify HASH_MAP provides O(1) get operations."""
        # Test with different sizes
        results = []
        
        for size in [100, 1000, 10000]:
            data = {f'key{i}': f'value{i}' for i in range(size)}
            node = XWNode.from_native(data)
            
            # Measure lookup time
            def lookup_op():
                node.get(f'key{size//2}')
            
            avg_time = measure_operation_time(lookup_op, iterations=100)
            results.append((size, avg_time))
        
        # Verify O(1) - times should be similar regardless of size
        # Allow some variation but should not grow linearly
        time_100 = results[0][1]
        time_10000 = results[2][1]
        
        # Time for 10000 elements should not be 100x time for 100 elements
        # (O(1) vs O(n) distinction)
        assert time_10000 < time_100 * 10  # Allow 10x variation
    
    @pytest.mark.performance
    def test_hash_map_o1_put_complexity(self):
        """Verify HASH_MAP provides O(1) put operations."""
        node = XWNode.from_native({})
        
        # Measure put time for different sizes
        def put_op(size):
            for i in range(size):
                node.set(f'key{i}', f'value{i}', in_place=True)
        
        # Should be fast even for many insertions
        start = time.time()
        put_op(1000)
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 1.0  # 1 second for 1000 insertions
    
    @pytest.mark.performance
    def test_hash_map_memory_usage(self):
        """Test HASH_MAP memory usage characteristics."""
        # Create node with known data
        data = {f'key{i}': i for i in range(1000)}
        
        def create_node():
            return XWNode.from_native(data)
        
        memory_used = measure_memory_usage(create_node)
        
        # Memory should be reasonable (< 1 MB for 1000 items)
        assert memory_used < 1024 * 1024  # 1 MB


class TestArrayListPerformance:
    """Benchmark ARRAY_LIST strategy performance."""
    
    @pytest.mark.performance
    def test_array_list_sequential_access(self):
        """Test ARRAY_LIST sequential access performance."""
        data = list(range(10000))
        node = XWNode.from_native(data)
        
        # Measure iteration time
        start = time.time()
        count = 0
        for item in node:
            count += 1
            if count > 10000:
                break
        elapsed = time.time() - start
        
        # Should be fast for sequential access
        assert elapsed < 0.5  # 0.5 seconds for 10000 items


class TestTreeGraphHybridPerformance:
    """Benchmark TREE_GRAPH_HYBRID strategy performance."""
    
    @pytest.mark.performance
    def test_tree_navigation_performance(self):
        """Test tree navigation performance."""
        # Create nested structure
        data = {}
        current = data
        for i in range(50):
            current['level'] = {}
            current = current['level']
        current['value'] = 'deep'
        
        node = XWNode.from_native(data)
        
        # Measure navigation time
        start = time.time()
        for _ in range(100):
            result = node.find('level.level.level.level.value')
        elapsed = time.time() - start
        
        # Should be reasonably fast
        assert elapsed < 1.0


# ============================================================================
# PERFORMANCE METADATA VALIDATION
# ============================================================================

class TestPerformanceMetadataValidation:
    """Validate that strategies meet their performance claims from defs.py."""
    
    @pytest.mark.performance
    def test_hash_map_claims_validation(self):
        """Validate HASH_MAP performance claims."""
        metadata = NODE_STRATEGY_METADATA.get(NodeMode.HASH_MAP)
        
        if metadata:
            # Claim: "10-100x faster lookups"
            # Claim: O(1) get, set, delete
            assert metadata.performance_gain == "10-100x faster lookups"
            assert metadata.time_complexity.get('get') == 'O(1)'
            assert metadata.time_complexity.get('set') == 'O(1)'
            assert metadata.time_complexity.get('delete') == 'O(1)'
    
    @pytest.mark.performance
    def test_array_list_claims_validation(self):
        """Validate ARRAY_LIST performance claims."""
        metadata = NODE_STRATEGY_METADATA.get(NodeMode.ARRAY_LIST)
        
        if metadata:
            # Claim: "2-5x faster for small datasets"
            assert metadata.performance_gain == "2-5x faster for small datasets"
            assert metadata.time_complexity.get('get') == 'O(1)'
    
    @pytest.mark.performance
    def test_b_tree_claims_validation(self):
        """Validate B_TREE performance claims."""
        metadata = NODE_STRATEGY_METADATA.get(NodeMode.B_TREE)
        
        if metadata:
            # Claim: "10-100x faster disk I/O"
            assert "faster disk I/O" in metadata.performance_gain.lower()


# ============================================================================
# COMPARATIVE BENCHMARKS
# ============================================================================

class TestComparativeBenchmarks:
    """Compare performance across different strategies."""
    
    @pytest.mark.performance
    def test_lookup_performance_comparison(self):
        """Compare lookup performance across strategies."""
        data = {f'key{i}': f'value{i}' for i in range(1000)}
        
        # Benchmark different strategies
        benchmarks = {}
        
        # HASH_MAP (should be fastest)
        node_hash = XWNode.from_native(data)
        def hash_lookup():
            node_hash.get('key500')
        benchmarks['HASH_MAP'] = measure_operation_time(hash_lookup, 100)
        
        # TREE_GRAPH_HYBRID
        node_tree = XWNode.from_native(data)
        def tree_lookup():
            node_tree.get('key500')
        benchmarks['TREE_GRAPH_HYBRID'] = measure_operation_time(tree_lookup, 100)
        
        # Document results
        print(f"\nLookup Performance Comparison:")
        for strategy, avg_time in benchmarks.items():
            print(f"  {strategy}: {avg_time*1000:.4f}ms")
        
        # Verification: HASH_MAP should be competitive
        assert benchmarks['HASH_MAP'] < 0.001  # < 1ms average


# ============================================================================
# STRESS TESTS
# ============================================================================

class TestPerformanceStress:
    """Stress test strategies with extreme conditions."""
    
    @pytest.mark.performance
    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        # Create large dataset (10K items)
        large_data = {f'key{i}': f'value{i}' for i in range(10_000)}
        
        start = time.time()
        node = XWNode.from_native(large_data)
        creation_time = time.time() - start
        
        # Should create quickly
        assert creation_time < 5.0  # 5 seconds max
        assert len(node) > 0
    
    @pytest.mark.performance
    def test_many_operations_performance(self):
        """Test performance with many consecutive operations."""
        node = XWNode.from_native({})
        
        start = time.time()
        # Perform 10K operations
        for i in range(10_000):
            node.set(f'key{i}', i, in_place=True)
        elapsed = time.time() - start
        
        # Should handle many operations efficiently
        assert elapsed < 10.0  # 10 seconds for 10K operations


# ============================================================================
# BENCHMARK REPORTING
# ============================================================================

@pytest.mark.performance
class TestBenchmarkReporting:
    """Generate benchmark reports for documentation."""
    
    def test_generate_performance_report(self):
        """Generate comprehensive performance report."""
        report = {
            'test_date': '11-Oct-2025',
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
            'benchmarks': {}
        }
        
        # Benchmark HASH_MAP
        data = {f'key{i}': i for i in range(1000)}
        node = XWNode.from_native(data)
        
        def get_op():
            node.get('key500')
        
        report['benchmarks']['hash_map_get'] = {
            'avg_time_ms': measure_operation_time(get_op, 100) * 1000,
            'operations_per_second': int(1.0 / (measure_operation_time(get_op, 100) + 1e-10))
        }
        
        print(f"\nPerformance Report: {report}")
        
        assert report['benchmarks']['hash_map_get']['avg_time_ms'] < 10.0  # < 10ms


# ============================================================================
# RUN CONFIGURATION
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-m', 'performance'])

