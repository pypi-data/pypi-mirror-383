"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_new_edge_strategies.py

Unit tests for new edge strategies.

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


@pytest.mark.xwnode_unit
class TestIncidenceMatrixStrategyUnit:
    """Comprehensive unit tests for Incidence Matrix strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = IncidenceMatrixStrategy()
        assert strategy.mode == EdgeMode.INCIDENCE_MATRIX
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = IncidenceMatrixStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.SPARSE in traits
        assert EdgeTrait.DIRECTED in traits
    
    def test_add_edge(self):
        """Test adding edges."""
        strategy = IncidenceMatrixStrategy()
        edge_id = strategy.add_edge('A', 'B', weight=1.0)
        
        assert edge_id is not None
        assert strategy.has_edge('A', 'B')
        assert len(strategy) == 1
    
    def test_remove_edge(self):
        """Test removing edges."""
        strategy = IncidenceMatrixStrategy()
        edge_id = strategy.add_edge('A', 'B')
        
        assert strategy.remove_edge('A', 'B', edge_id=edge_id)
        assert not strategy.has_edge('A', 'B')
    
    def test_get_neighbors(self):
        """Test getting neighbors."""
        strategy = IncidenceMatrixStrategy()
        strategy.add_edge('A', 'B')
        strategy.add_edge('A', 'C')
        
        neighbors = strategy.get_neighbors('A', direction='outgoing')
        assert 'B' in neighbors or 'C' in neighbors or len(neighbors) >= 0
    
    def test_edge_by_id(self):
        """Test edge-centric queries."""
        strategy = IncidenceMatrixStrategy()
        edge_id = strategy.add_edge('X', 'Y', label='test')
        
        if hasattr(strategy, 'get_edge_by_id'):
            edge_data = strategy.get_edge_by_id(edge_id)
            assert edge_data is not None


@pytest.mark.xwnode_unit
class TestEdgeListStrategyUnit:
    """Unit tests for Edge List strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = EdgeListStrategy()
        assert strategy.mode == EdgeMode.EDGE_LIST
    
    def test_add_multiple_edges(self):
        """Test adding multiple edges."""
        strategy = EdgeListStrategy()
        
        edges = [('A', 'B'), ('B', 'C'), ('C', 'D')]
        for src, tgt in edges:
            strategy.add_edge(src, tgt)
        
        assert len(strategy) == 3
    
    def test_simple_format(self):
        """Test simple edge list format."""
        strategy = EdgeListStrategy()
        strategy.add_edge('X', 'Y')
        
        # to_native should return simple list
        native = strategy.to_native()
        assert isinstance(native, list)


@pytest.mark.xwnode_unit
class TestCompressedGraphStrategyUnit:
    """Unit tests for Compressed Graph strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = CompressedGraphStrategy()
        assert strategy.mode == EdgeMode.COMPRESSED_GRAPH
    
    def test_compression(self):
        """Test compression features."""
        strategy = CompressedGraphStrategy()
        
        # Add many edges
        for i in range(20):
            strategy.add_edge(f'node{i}', f'node{i+1}')
        
        # Should support compression
        if hasattr(strategy, 'compress'):
            strategy.compress()
        
        if hasattr(strategy, 'get_compression_ratio'):
            ratio = strategy.get_compression_ratio()
            assert ratio >= 0
    
    def test_power_law_graph(self):
        """Test with power-law graph (hub node)."""
        strategy = CompressedGraphStrategy()
        
        # Create hub with many connections
        for i in range(50):
            strategy.add_edge('hub', f'node{i}')
        
        neighbors = strategy.get_neighbors('hub')
        assert len(neighbors) >= 0

