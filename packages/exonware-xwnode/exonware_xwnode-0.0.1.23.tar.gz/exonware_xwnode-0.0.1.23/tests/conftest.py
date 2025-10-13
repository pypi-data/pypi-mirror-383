"""
#exonware/xwnode/tests/conftest.py

Pytest configuration and fixtures for xwnode tests.
Provides reusable test data and setup utilities.

Following GUIDELINES_TEST.md for reusable, production-grade test infrastructure.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from pathlib import Path
import sys
import time
import tracemalloc
import math
from typing import Callable, Any, Tuple, Dict

# Ensure src is in path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# ============================================================================
# STANDARD FIXTURES (Per GUIDELINES_TEST.md)
# ============================================================================

@pytest.fixture
def simple_data():
    """Simple data for basic tests."""
    return {
        'name': 'Alice',
        'age': 30,
        'city': 'New York',
        'active': True
    }


@pytest.fixture
def simple_dict_data():
    """Simple dictionary test data (alias for simple_data)."""
    return {
        'name': 'Alice',
        'age': 30,
        'city': 'New York',
        'active': True
    }


@pytest.fixture
def complex_data():
    """Complex nested data for comprehensive testing."""
    return {
        'users': [
            {
                'id': 1,
                'name': 'Alice',
                'age': 30,
                'profile': {
                    'email': 'alice@example.com',
                    'preferences': {
                        'theme': 'dark',
                        'notifications': True
                    }
                },
                'roles': ['admin', 'user']
            },
            {
                'id': 2,
                'name': 'Bob',
                'age': 25,
                'profile': {
                    'email': 'bob@example.com',
                    'preferences': {
                        'theme': 'light',
                        'notifications': False
                    }
                },
                'roles': ['user']
            }
        ],
        'metadata': {
            'version': 1.0,
            'created': '2024-01-01',
            'tags': ['test', 'sample', 'data']
        }
    }


@pytest.fixture
def nested_data():
    """Complex nested hierarchical test data (alias for complex_data)."""
    return {
        'users': [
            {
                'id': 1,
                'name': 'Alice',
                'profile': {
                    'email': 'alice@example.com',
                    'preferences': {'theme': 'dark'}
                }
            }
        ],
        'metadata': {
            'version': 1.0,
            'created': '2024-01-01'
        }
    }


@pytest.fixture
def simple_list_data():
    """Simple list test data."""
    return ['apple', 'banana', 'cherry']


@pytest.fixture
def large_dataset():
    """Large dataset for performance testing (10,000 items)."""
    return {f'key_{i}': f'value_{i}' for i in range(10000)}


@pytest.fixture
def edge_cases():
    """Edge case data (empty, None, etc.)."""
    return {
        'empty_dict': {},
        'empty_list': [],
        'null_value': None,
        'empty_string': '',
        'zero': 0,
        'false': False
    }


@pytest.fixture
def multilingual_data():
    """Unicode and emoji data for multilingual testing."""
    return {
        'english': 'Hello World',
        'arabic': 'مرحبا بالعالم',
        'chinese': '你好世界',
        'russian': 'Привет мир',
        'japanese': 'こんにちは世界',
        'emoji': '🌍🌎🌏 Hello 👋',
        'mixed': 'Hello مرحبا 你好 🎉'
    }


@pytest.fixture
def test_data_dir():
    """Get the test data directory."""
    return Path(__file__).parent / "0.core" / "data"


@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary directory for test files."""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return test_dir


# ============================================================================
# XWNODE-SPECIFIC FIXTURES
# ============================================================================

@pytest.fixture
def simple_node(simple_dict_data):
    """XWNode instance from simple dictionary."""
    from exonware.xwnode import XWNode
    return XWNode.from_native(simple_dict_data)


@pytest.fixture
def list_node(simple_list_data):
    """XWNode instance from simple list."""
    from exonware.xwnode import XWNode
    return XWNode.from_native(simple_list_data)


@pytest.fixture
def nested_node(nested_data):
    """XWNode instance from nested data."""
    from exonware.xwnode import XWNode
    return XWNode.from_native(nested_data)


@pytest.fixture
def leaf_node():
    """Simple leaf node."""
    from exonware.xwnode import XWNode
    return XWNode.from_native("simple string value")


@pytest.fixture
def number_node():
    """Simple number leaf node."""
    from exonware.xwnode import XWNode
    return XWNode.from_native(42)


@pytest.fixture
def boolean_node():
    """Simple boolean leaf node."""
    from exonware.xwnode import XWNode
    return XWNode.from_native(True)


@pytest.fixture
def empty_dict_node():
    """Empty dictionary node."""
    from exonware.xwnode import XWNode
    return XWNode.from_native({})


@pytest.fixture
def empty_list_node():
    """Empty list node."""
    from exonware.xwnode import XWNode
    return XWNode.from_native([])


@pytest.fixture
def json_test_string():
    """JSON string for testing JSON parsing."""
    return '{"name": "Test", "value": 42, "items": [1, 2, {"nested": true}]}'


@pytest.fixture
def json_test_data():
    """Complex data for JSON testing."""
    return {
        "users": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ],
        "meta": {
            "count": 2,
            "version": "1.0"
        }
    }


@pytest.fixture
def complex_navigation_data():
    """Complex nested data for navigation testing."""
    return {
        "company": {
            "departments": [
                {
                    "name": "Engineering",
                    "teams": [
                        {
                            "name": "Backend",
                            "members": [
                                {"name": "Alice", "role": "lead"},
                                {"name": "Bob", "role": "developer"}
                            ]
                        },
                        {
                            "name": "Frontend", 
                            "members": [
                                {"name": "Charlie", "role": "lead"},
                                {"name": "David", "role": "developer"}
                            ]
                        }
                    ]
                },
                {
                    "name": "Sales",
                    "teams": [
                        {
                            "name": "Enterprise",
                            "members": [
                                {"name": "Eve", "role": "manager"},
                                {"name": "Frank", "role": "rep"}
                            ]
                        }
                    ]
                }
            ]
        },
        "config": {
            "features": {
                "api_limits": {
                    "requests_per_minute": 1000,
                    "max_payload_size": "10MB"
                }
            }
        }
    }


@pytest.fixture
def array_heavy_data():
    """Data with heavy array usage for navigation testing."""
    return {
        "matrix": [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ],
        "records": [
            {"values": [10, 20, 30]},
            {"values": [40, 50, 60]}
        ]
    }


@pytest.fixture
def edge_case_keys_data():
    """Data with edge case keys for testing."""
    return {
        "0": "string_zero",
        "1.5": "decimal_string",
        "spaces in key": "spaced_key",
        "special!@#$%": "special_chars",
        "unicode_ключ": "unicode_value",
        "": "empty_key"
    }


@pytest.fixture
def mixed_type_data():
    """Data with mixed types for comprehensive testing."""
    return {
        "string": "hello",
        "integer": 42,
        "float": 3.14,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3],
        "dict": {
            "nested": "value"
        }
    }


@pytest.fixture
def real_world_config():
    """Real-world configuration data for integration testing."""
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {
                "username": "admin",
                "password": "secret123"
            },
            "pools": [
                {"name": "read", "size": 10},
                {"name": "write", "size": 5}
            ]
        },
        "api": {
            "endpoints": [
                {"path": "/users", "method": "GET"},
                {"path": "/users", "method": "POST"},
                {"path": "/products", "method": "GET"}
            ],
            "rate_limits": {
                "requests_per_minute": 1000,
                "burst_size": 100
            }
        },
        "logging": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }


# Test data directory
@pytest.fixture
def test_data_dir():
    """Get the test data directory."""
    return Path(__file__).parent / "data"


# ============================================================================
# PERFORMANCE TESTING FIXTURES (Per Plan - Reusable Across All Strategies)
# ============================================================================

@pytest.fixture
def measure_time_complexity():
    """
    Reusable fixture to measure and validate time complexity.
    
    Following GUIDELINES_TEST.md for empirical performance validation.
    
    Usage:
        def test_hash_map_o1_complexity(measure_time_complexity):
            def operation(size):
                strategy = HashMapStrategy()
                for i in range(size):
                    strategy.put(f"k{i}", i)
                strategy.get(f"k{size//2}")
            
            # Validates O(1) complexity empirically
            measure_time_complexity(operation, [100, 1000, 10000], 'O(1)')
    """
    def _measure(operation: Callable, sizes: list, expected_complexity: str, tolerance: float = 2.5):
        """
        Measure operation time across different input sizes and validate complexity.
        
        Args:
            operation: Callable that takes size parameter
            sizes: List of sizes to test (e.g., [100, 1000, 10000])
            expected_complexity: 'O(1)', 'O(log n)', 'O(n)', 'O(n log n)'
            tolerance: Maximum acceptable ratio for validation
        
        Returns:
            Dict with timings for each size
            
        Raises:
            AssertionError: If empirical complexity doesn't match expected
        """
        timings = {}
        
        # Warm-up run
        operation(sizes[0])
        
        # Measure each size
        for size in sizes:
            measurements = []
            # Run 3 times and take median for stability
            for _ in range(3):
                start = time.perf_counter()
                operation(size)
                elapsed = time.perf_counter() - start
                measurements.append(elapsed)
            
            # Use median to reduce noise
            measurements.sort()
            timings[size] = measurements[1]
        
        # Validate complexity
        if expected_complexity == 'O(1)':
            # Constant time: ratio should be < tolerance
            ratio = timings[sizes[-1]] / timings[sizes[0]]
            assert ratio < tolerance, (
                f"Expected O(1), but ratio {ratio:.2f} exceeds tolerance {tolerance}. "
                f"Timings: {timings}"
            )
        
        elif expected_complexity == 'O(log n)':
            # Logarithmic: time should grow as log(n)
            expected_ratio = math.log(sizes[-1]) / math.log(sizes[0])
            actual_ratio = timings[sizes[-1]] / timings[sizes[0]]
            max_ratio = expected_ratio * tolerance
            assert actual_ratio < max_ratio, (
                f"Expected O(log n) with ratio ~{expected_ratio:.2f}, "
                f"got {actual_ratio:.2f} (max: {max_ratio:.2f})"
            )
        
        elif expected_complexity == 'O(n)':
            # Linear: time should grow linearly with n
            expected_ratio = sizes[-1] / sizes[0]
            actual_ratio = timings[sizes[-1]] / timings[sizes[0]]
            max_ratio = expected_ratio * tolerance
            assert actual_ratio < max_ratio, (
                f"Expected O(n) with ratio ~{expected_ratio:.2f}, "
                f"got {actual_ratio:.2f} (max: {max_ratio:.2f})"
            )
        
        elif expected_complexity == 'O(n log n)':
            # Linearithmic: time should grow as n * log(n)
            expected_ratio = (sizes[-1] * math.log(sizes[-1])) / (sizes[0] * math.log(sizes[0]))
            actual_ratio = timings[sizes[-1]] / timings[sizes[0]]
            max_ratio = expected_ratio * tolerance
            assert actual_ratio < max_ratio, (
                f"Expected O(n log n) with ratio ~{expected_ratio:.2f}, "
                f"got {actual_ratio:.2f} (max: {max_ratio:.2f})"
            )
        
        return timings
    
    return _measure


@pytest.fixture
def measure_memory():
    """
    Reusable fixture to measure memory usage.
    
    Following GUIDELINES_TEST.md for memory efficiency validation.
    
    Usage:
        def test_hash_map_memory(measure_memory):
            def operation():
                strategy = HashMapStrategy()
                for i in range(1000):
                    strategy.put(f"key_{i}", i)
                return strategy
            
            result, memory_bytes = measure_memory(operation)
            assert memory_bytes < 200 * 1024  # < 200KB
    """
    def _measure(operation: Callable) -> Tuple[Any, int]:
        """
        Measure peak memory usage of operation.
        
        Args:
            operation: Callable that returns result to measure
            
        Returns:
            Tuple of (result, peak_memory_bytes)
        """
        tracemalloc.start()
        result = operation()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return result, peak
    
    return _measure


@pytest.fixture
def benchmark_vs_stdlib():
    """
    Reusable fixture to compare performance against stdlib.
    
    Following GUIDELINES_TEST.md for competitive performance validation.
    
    Usage:
        def test_hash_map_vs_dict(benchmark_vs_stdlib):
            def strategy_op(size):
                s = HashMapStrategy()
                for i in range(size):
                    s.put(f"k{i}", i)
            
            def stdlib_op(size):
                d = {}
                for i in range(size):
                    d[f"k{i}"] = i
            
            results = benchmark_vs_stdlib(strategy_op, stdlib_op)
            assert results['acceptable']  # Within 5x of stdlib
    """
    def _benchmark(strategy_op: Callable, stdlib_op: Callable, size: int = 1000, max_ratio: float = 5.0):
        """
        Compare strategy performance against stdlib equivalent.
        
        Args:
            strategy_op: Strategy operation (takes size parameter)
            stdlib_op: Standard library equivalent (takes size parameter)
            size: Dataset size to test
            max_ratio: Maximum acceptable ratio (strategy_time / stdlib_time)
            
        Returns:
            Dict with comparison results
        """
        # Warm-up
        strategy_op(100)
        stdlib_op(100)
        
        # Measure strategy (3 runs, median)
        strategy_times = []
        for _ in range(3):
            start = time.perf_counter()
            strategy_op(size)
            elapsed = time.perf_counter() - start
            strategy_times.append(elapsed)
        strategy_times.sort()
        strategy_time = strategy_times[1]
        
        # Measure stdlib (3 runs, median)
        stdlib_times = []
        for _ in range(3):
            start = time.perf_counter()
            stdlib_op(size)
            elapsed = time.perf_counter() - start
            stdlib_times.append(elapsed)
        stdlib_times.sort()
        stdlib_time = stdlib_times[1]
        
        ratio = strategy_time / stdlib_time if stdlib_time > 0 else float('inf')
        
        return {
            'strategy_time': strategy_time,
            'stdlib_time': stdlib_time,
            'ratio': ratio,
            'acceptable': ratio < max_ratio,
            'message': (
                f"Strategy: {strategy_time*1000:.2f}ms, "
                f"Stdlib: {stdlib_time*1000:.2f}ms, "
                f"Ratio: {ratio:.2f}x (max: {max_ratio}x)"
            )
        }
    
    return _benchmark


@pytest.fixture
def strategy_factory():
    """
    Factory for creating strategy instances with common setup.
    
    Following GUIDELINES_TEST.md for reusable strategy creation.
    
    Usage:
        def test_initialization(strategy_factory):
            strategy = strategy_factory(HashMapStrategy, max_size=100)
            assert strategy is not None
    """
    def _create(strategy_class, **options):
        """
        Create strategy instance with options.
        
        Args:
            strategy_class: Strategy class to instantiate
            **options: Strategy-specific options
            
        Returns:
            Strategy instance
        """
        return strategy_class(**options)
    
    return _create


@pytest.fixture
def stress_dataset():
    """
    100,000 item dataset for stress testing.
    
    Following GUIDELINES_TEST.md for stress test validation.
    """
    return {f"key_{i}": f"value_{i}" for i in range(100000)}


# ============================================================================
# EDGE STRATEGY FIXTURES
# ============================================================================

@pytest.fixture
def graph_factory():
    """
    Create test graphs of various sizes.
    
    Generates random edges for testing edge strategies with configurable
    graph characteristics (size, directed/undirected, weighted/unweighted).
    
    Following GUIDELINES_TEST.md for reusable edge test data.
    
    Usage:
        def test_large_graph(graph_factory):
            edges = graph_factory(100, 500, directed=True, weighted=True)
            # edges is a list of (source, target, properties) tuples
    """
    def _create(num_vertices, num_edges, directed=True, weighted=False):
        """
        Create random graph with specified characteristics.
        
        Args:
            num_vertices: Number of vertices in graph
            num_edges: Number of edges to generate
            directed: Whether graph is directed (default: True)
            weighted: Whether edges have weights (default: False)
            
        Returns:
            List of (source, target, properties) tuples
        """
        import random
        edges = []
        for i in range(num_edges):
            src = f"v{random.randint(0, num_vertices-1)}"
            tgt = f"v{random.randint(0, num_vertices-1)}"
            props = {}
            if weighted:
                props['weight'] = random.uniform(0.1, 10.0)
            edges.append((src, tgt, props))
        return edges
    
    return _create


@pytest.fixture
def spatial_dataset():
    """
    Spatial edges for R_TREE, QUADTREE, OCTREE testing.
    
    Generates edges with spatial coordinates for testing spatial indexing
    strategies. Supports both 2D and 3D coordinate spaces.
    
    Following GUIDELINES_TEST.md for spatial test data.
    
    Usage:
        def test_2d_spatial(spatial_dataset):
            edges = spatial_dataset(dimensions=2, num_edges=100)
            # Each edge has x1, y1, x2, y2 coordinates
            
        def test_3d_spatial(spatial_dataset):
            edges = spatial_dataset(dimensions=3, num_edges=100)
            # Each edge has x1, y1, z1, x2, y2, z2 coordinates
    """
    def _create(dimensions=2, num_edges=100):
        """
        Create spatial edges with coordinate properties.
        
        Args:
            dimensions: 2 for 2D coordinates, 3 for 3D coordinates
            num_edges: Number of edges to generate
            
        Returns:
            List of (source, target, properties) tuples where properties
            contain spatial coordinates (x1, y1, [z1], x2, y2, [z2])
        """
        import random
        edges = []
        for i in range(num_edges):
            src = f"v{i}"
            tgt = f"v{(i+1)%num_edges}"
            if dimensions == 2:
                props = {
                    'x1': random.uniform(0, 100),
                    'y1': random.uniform(0, 100),
                    'x2': random.uniform(0, 100),
                    'y2': random.uniform(0, 100)
                }
            else:  # 3D
                props = {
                    'x1': random.uniform(0, 100),
                    'y1': random.uniform(0, 100),
                    'z1': random.uniform(0, 100),
                    'x2': random.uniform(0, 100),
                    'y2': random.uniform(0, 100),
                    'z2': random.uniform(0, 100)
                }
            edges.append((src, tgt, props))
        return edges
    
    return _create


@pytest.fixture
def temporal_dataset():
    """
    Time-series edges for TEMPORAL_EDGESET strategy testing.
    
    Generates edges with timestamps for testing temporal edge strategies.
    Edges are sorted by timestamp to simulate time-series data.
    
    Following GUIDELINES_TEST.md for temporal test data.
    
    Usage:
        def test_temporal_query(temporal_dataset):
            edges = temporal_dataset(num_edges=100, time_range=(0, 1000))
            # Each edge has a 'timestamp' property
            # Edges are sorted by timestamp
    """
    def _create(num_edges=100, time_range=(0, 1000)):
        """
        Create temporal edges with timestamps.
        
        Args:
            num_edges: Number of edges to generate
            time_range: Tuple of (min_time, max_time) for timestamp range
            
        Returns:
            List of (source, target, properties) tuples where properties
            contain a 'timestamp' field. List is sorted by timestamp.
        """
        import random
        edges = []
        for i in range(num_edges):
            src = f"v{i%10}"
            tgt = f"v{(i+1)%10}"
            timestamp = random.uniform(*time_range)
            edges.append((src, tgt, {'timestamp': timestamp}))
        # Sort by timestamp for temporal queries
        return sorted(edges, key=lambda x: x[2]['timestamp'])
    
    return _create 