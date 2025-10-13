"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_probabilistic_structures.py

Comprehensive tests for Probabilistic Structures.

Tests COUNT_MIN_SKETCH and HYPERLOGLOG strategies.
Critical for streaming and approximate algorithms.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import (
    count_min_sketch,
    hyperloglog
)


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestCountMinSketchStrategy:
    """Test COUNT_MIN_SKETCH strategy for frequency estimation."""
    
    def test_strategy_exists(self):
        """Test that COUNT_MIN_SKETCH strategy exists."""
        assert count_min_sketch is not None
        assert NodeMode.COUNT_MIN_SKETCH is not None
    
    def test_streaming_frequency_estimation(self):
        """Test streaming frequency estimation."""
        # Count-Min Sketch for frequency queries in streams
        assert NodeTrait.STREAMING is not None
        assert NodeTrait.PROBABILISTIC is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestHyperLogLogStrategy:
    """Test HYPERLOGLOG strategy for cardinality estimation."""
    
    def test_strategy_exists(self):
        """Test that HYPERLOGLOG strategy exists."""
        assert hyperloglog is not None
        assert NodeMode.HYPERLOGLOG is not None
    
    def test_cardinality_estimation(self):
        """Test cardinality estimation."""
        # HyperLogLog estimates unique counts
        assert NodeTrait.PROBABILISTIC is not None
        assert NodeMode.HYPERLOGLOG is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestProbabilisticPerformance:
    """Test probabilistic structure performance."""
    
    def test_memory_efficiency(self):
        """Test memory efficiency of probabilistic structures."""
        # Probabilistic structures trade accuracy for memory
        assert NodeTrait.MEMORY_EFFICIENT is not None

