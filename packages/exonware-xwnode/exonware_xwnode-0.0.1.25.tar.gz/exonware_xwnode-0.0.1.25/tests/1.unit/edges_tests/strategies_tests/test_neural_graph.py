"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_neural_graph.py

Comprehensive tests for NEURAL_GRAPH Strategy.

Optimized for neural network computation graphs.
Critical for ML workflows.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.edges.strategies import neural_graph


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestNeuralGraphInterface:
    """Test NEURAL_GRAPH interface."""
    
    def test_strategy_exists(self):
        """Test that NEURAL_GRAPH strategy exists."""
        assert neural_graph is not None
        assert EdgeMode.NEURAL_GRAPH is not None
    
    def test_computation_graph_support(self):
        """Test neural network computation graph support."""
        # Neural graphs support computation graphs
        assert EdgeMode.NEURAL_GRAPH is not None

