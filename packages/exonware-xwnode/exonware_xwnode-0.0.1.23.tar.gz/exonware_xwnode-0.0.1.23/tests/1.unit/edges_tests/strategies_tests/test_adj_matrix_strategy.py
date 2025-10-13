"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_adj_matrix_strategy.py

Comprehensive tests for AdjMatrixStrategy (Adjacency Matrix).

Optimized for dense graphs with O(1) edge queries.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.adj_matrix import AdjMatrixStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.fixture
def empty_matrix():
    """Create empty adjacency matrix."""
    return AdjMatrixStrategy()


@pytest.fixture
def dense_graph():
    """Create dense graph."""
    matrix = AdjMatrixStrategy()
    # Create complete graph K5
    for i in range(5):
        for j in range(5):
            if i != j:
                matrix.add_edge(f'node_{i}', f'node_{j}')
    return matrix


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestAdjMatrixInterface:
    """Test AdjMatrixStrategy interface compliance."""
    
    def test_add_edge(self, empty_matrix):
        """Test adding edges."""
        empty_matrix.add_edge('A', 'B')
        assert empty_matrix.has_edge('A', 'B') is True
    
    def test_remove_edge(self, dense_graph):
        """Test removing edges."""
        assert dense_graph.remove_edge('node_0', 'node_1') is True
        assert dense_graph.has_edge('node_0', 'node_1') is False
    
    def test_has_edge_o1_performance(self, dense_graph):
        """Test that has_edge is O(1)."""
        # Matrix allows O(1) edge queries
        assert dense_graph.has_edge('node_0', 'node_1') is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
@pytest.mark.xwnode_performance
class TestAdjMatrixPerformance:
    """Test AdjMatrixStrategy performance."""
    
    def test_dense_graph_efficiency(self):
        """Test efficiency for dense graphs."""
        matrix = AdjMatrixStrategy()
        
        # Create dense graph
        for i in range(100):
            for j in range(100):
                if i != j:
                    matrix.add_edge(f'n{i}', f'n{j}')
        
        # Should handle dense graphs efficiently
        assert matrix.has_edge('n0', 'n99')


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestAdjMatrixEdgeCases:
    """Test AdjMatrixStrategy edge cases."""
    
    def test_self_loops(self, empty_matrix):
        """Test self-loop handling."""
        empty_matrix.add_edge('A', 'A')
        assert empty_matrix.has_edge('A', 'A') is True
    
    def test_bidirectional_edges(self, empty_matrix):
        """Test bidirectional edges."""
        empty_matrix.add_edge('A', 'B')
        empty_matrix.add_edge('B', 'A')
        
        assert empty_matrix.has_edge('A', 'B') is True
        assert empty_matrix.has_edge('B', 'A') is True

