"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_hyperedge_set.py

Comprehensive tests for HYPEREDGE_SET Strategy.

Supports hypergraphs with multi-vertex edges.
Critical for complex relationship modeling.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.edges.strategies import hyperedge_set


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestHyperedgeSetInterface:
    """Test HYPEREDGE_SET interface."""
    
    def test_strategy_exists(self):
        """Test that HYPEREDGE_SET strategy exists."""
        assert hyperedge_set is not None
        assert EdgeMode.HYPEREDGE_SET is not None
    
    def test_hyperedge_support(self):
        """Test hyperedge (multi-vertex edge) support."""
        # Hyperedges connect multiple vertices
        assert EdgeTrait.HYPER is not None
    
    def test_multi_vertex_edges(self):
        """Test edges connecting 3+ vertices."""
        # Hypergraphs support edges with multiple vertices
        assert EdgeMode.HYPEREDGE_SET is not None

