"""
#exonware/xwnode/tests/0.core/test_adjacency_list_node_strategy.py

Test Adjacency List Node Strategy Implementation

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

import pytest
from exonware.xwnode.nodes.strategies.adjacency_list import AdjacencyListStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


def test_adjacency_list_initialization():
    """Test adjacency list strategy initialization"""
    graph = AdjacencyListStrategy()
    assert len(graph) == 0
    assert graph.is_empty()
    assert NodeTrait.GRAPH in graph.get_supported_traits()


def test_adjacency_list_add_vertices():
    """Test adding vertices to the graph"""
    graph = AdjacencyListStrategy()
    
    graph.add_vertex("A", "Node A data")
    graph.add_vertex("B", "Node B data")
    graph.add_vertex("C", "Node C data")
    
    assert "A" in graph
    assert "B" in graph
    assert "C" in graph
    assert graph.vertex_count() == 3


def test_adjacency_list_add_edges():
    """Test adding edges between vertices"""
    graph = AdjacencyListStrategy()
    
    graph.add_edge("A", "B", 5.0)
    graph.add_edge("A", "C", 3.0)
    graph.add_edge("B", "C", 2.0)
    
    assert graph.has_edge("A", "B")
    assert graph.has_edge("A", "C")
    assert graph.has_edge("B", "C")
    assert graph.edge_count() == 3


def test_adjacency_list_get_neighbors():
    """Test getting neighbors of a vertex"""
    graph = AdjacencyListStrategy()
    
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    
    neighbors = graph.get_neighbors("A")
    assert len(neighbors) == 2
    assert "B" in neighbors
    assert "C" in neighbors
    
    neighbors_b = graph.get_neighbors("B")
    assert len(neighbors_b) == 0  # B has no outgoing edges


def test_adjacency_list_directed_vs_undirected():
    """Test directed vs undirected graph behavior"""
    # Directed graph
    directed = AdjacencyListStrategy(is_directed=True)
    directed.add_edge("A", "B")
    
    assert directed.has_edge("A", "B") is True
    assert directed.has_edge("B", "A") is False  # Directed
    
    # Undirected graph
    undirected = AdjacencyListStrategy(is_directed=False)
    undirected.add_edge("X", "Y")
    
    assert undirected.has_edge("X", "Y") is True
    assert undirected.has_edge("Y", "X") is True  # Undirected


def test_adjacency_list_bfs():
    """Test breadth-first search"""
    graph = AdjacencyListStrategy()
    
    # Create simple graph: A -> B -> C
    #                      A -> C
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "C")
    
    visited = graph.bfs("A")
    assert visited == ["A", "B", "C"]


def test_adjacency_list_dfs():
    """Test depth-first search"""
    graph = AdjacencyListStrategy()
    
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "D")
    
    visited = graph.dfs("A")
    assert "A" in visited
    assert "B" in visited
    assert "C" in visited
    assert "D" in visited


def test_adjacency_list_find_path():
    """Test path finding"""
    graph = AdjacencyListStrategy()
    
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "D")
    
    path = graph.find_path("A", "D")
    assert path == ["A", "B", "C", "D"]
    
    path_none = graph.find_path("D", "A")
    assert path_none == []  # No path (directed graph)


def test_adjacency_list_cycle_detection():
    """Test cycle detection"""
    # Acyclic graph
    acyclic = AdjacencyListStrategy()
    acyclic.add_edge("A", "B")
    acyclic.add_edge("B", "C")
    assert acyclic.has_cycle() is False
    
    # Cyclic graph
    cyclic = AdjacencyListStrategy()
    cyclic.add_edge("A", "B")
    cyclic.add_edge("B", "C")
    cyclic.add_edge("C", "A")
    assert cyclic.has_cycle() is True


def test_adjacency_list_topological_sort():
    """Test topological sorting"""
    graph = AdjacencyListStrategy()
    
    # DAG: A -> B -> D
    #      A -> C -> D
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "D")
    graph.add_edge("C", "D")
    
    topo = graph.topological_sort()
    assert topo is not None
    assert topo.index("A") < topo.index("B")
    assert topo.index("A") < topo.index("C")
    assert topo.index("B") < topo.index("D")
    assert topo.index("C") < topo.index("D")


def test_adjacency_list_connected_components():
    """Test connected components detection"""
    graph = AdjacencyListStrategy()
    
    # Two disconnected components
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("X", "Y")
    
    components = graph.get_connected_components()
    assert len(components) == 2


def test_adjacency_list_degree():
    """Test degree calculations"""
    graph = AdjacencyListStrategy()
    
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "A")
    
    assert graph.out_degree("A") == 2
    assert graph.in_degree("A") == 1


def test_adjacency_list_supported_traits():
    """Test that adjacency list supports correct traits"""
    graph = AdjacencyListStrategy()
    traits = graph.get_supported_traits()
    
    assert NodeTrait.GRAPH in traits
    assert NodeTrait.SPARSE in traits
    assert NodeTrait.FAST_NEIGHBORS in traits

