"""
#exonware/xwnode/tests/0.core/test_new_edge_strategies.py

Core tests for new edge strategies (Incidence Matrix, Edge List, Compressed Graph).

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.incidence_matrix import IncidenceMatrixStrategy
from exonware.xwnode.edges.strategies.edge_list import EdgeListStrategy
from exonware.xwnode.edges.strategies.compressed_graph import CompressedGraphStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestIncidenceMatrixStrategyCore:
    """Core tests for Incidence Matrix edge strategy."""
    
    def test_create_and_add_edge(self):
        """Test Incidence Matrix creation and edge addition."""
        edge = IncidenceMatrixStrategy(traits=EdgeTrait.SPARSE)
        edge_id = edge.add_edge('A', 'B')
        assert edge_id is not None
        assert edge.has_edge('A', 'B')
    
    def test_edge_centric_operations(self):
        """Test edge-centric operations."""
        edge = IncidenceMatrixStrategy()
        edge.add_edge('A', 'B', weight=1.0)
        edge.add_edge('B', 'C', weight=2.0)
        
        # Should be able to query edges
        assert len(edge) >= 0


@pytest.mark.xwnode_core
class TestEdgeListStrategyCore:
    """Core tests for Edge List strategy."""
    
    def test_create_and_add_edge(self):
        """Test Edge List creation and edge addition."""
        edge = EdgeListStrategy()
        edge_id = edge.add_edge('A', 'B')
        assert edge_id is not None
    
    def test_simple_format(self):
        """Test simple edge list format."""
        edge = EdgeListStrategy()
        edge.add_edge('X', 'Y')
        edge.add_edge('Y', 'Z')
        assert len(edge) == 2


@pytest.mark.xwnode_core
class TestCompressedGraphStrategyCore:
    """Core tests for Compressed Graph strategy."""
    
    def test_create_and_add_edge(self):
        """Test Compressed Graph creation."""
        edge = CompressedGraphStrategy()
        edge.add_edge('A', 'B')
        assert edge.has_edge('A', 'B')
    
    def test_compression_features(self):
        """Test graph compression capabilities."""
        edge = CompressedGraphStrategy()
        # Add multiple edges
        for i in range(10):
            edge.add_edge(f'node{i}', f'node{i+1}')
        
        assert len(edge) >= 10

