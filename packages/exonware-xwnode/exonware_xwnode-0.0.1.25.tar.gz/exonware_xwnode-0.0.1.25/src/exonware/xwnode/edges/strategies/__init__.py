"""
Edge Strategies Package

This package contains all edge strategy implementations organized by type:
- Linear edges (sequential connections)
- Tree edges (hierarchical connections)  
- Graph edges (network connections)

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.25
Generation Date: January 2, 2025
"""

from .base import AEdgeStrategy, ALinearEdgeStrategy, ATreeEdgeStrategy, AGraphEdgeStrategy

# Graph edge strategies - Batch 1 (Core structures)
from .adj_list import AdjListStrategy
from .adj_matrix import AdjMatrixStrategy
from .csr import CSRStrategy
from .dynamic_adj_list import DynamicAdjListStrategy
from .weighted_graph import WeightedGraphStrategy

# Batch 2: Sparse matrix formats
from .csc import CSCStrategy
from .coo import COOStrategy
from .block_adj_matrix import BlockAdjMatrixStrategy

# Batch 3: Spatial structures
from .rtree import RTreeStrategy
from .quadtree import QuadTreeStrategy
from .octree import OctreeStrategy

# Batch 4: Graph representations
from .incidence_matrix import IncidenceMatrixStrategy
from .edge_list import EdgeListStrategy
from .compressed_graph import CompressedGraphStrategy
from .bidir_wrapper import BidirWrapperStrategy

# Batch 5: Specialized structures
from .temporal_edgeset import TemporalEdgeSetStrategy
from .hyperedge_set import HyperEdgeSetStrategy
from .edge_property_store import EdgePropertyStoreStrategy
from .flow_network import FlowNetworkStrategy
from .neural_graph import NeuralGraphStrategy

# Batch 6: Basic & hybrid
from .tree_graph_basic import TreeGraphBasicStrategy

# Batch 7: Advanced graph structures
from .k2_tree import K2TreeStrategy
from .bv_graph import BVGraphStrategy
from .hnsw import HNSWStrategy
from .euler_tour import EulerTourStrategy
from .link_cut import LinkCutStrategy
from .hop2_labels import Hop2LabelsStrategy
from .graphblas import GraphBLASStrategy
from .roaring_adj import RoaringAdjStrategy
from .multiplex import MultiplexStrategy
from .bitemporal import BitemporalStrategy

__all__ = [
    # Base classes
    'AEdgeStrategy',
    'ALinearEdgeStrategy',
    'ATreeEdgeStrategy', 
    'AGraphEdgeStrategy',
    
    # Batch 1: Core graph structures
    'AdjListStrategy',
    'AdjMatrixStrategy',
    'CSRStrategy',
    'DynamicAdjListStrategy',
    'WeightedGraphStrategy',
    
    # Batch 2: Sparse matrix formats
    'CSCStrategy',
    'COOStrategy',
    'BlockAdjMatrixStrategy',
    
    # Batch 3: Spatial structures
    'RTreeStrategy',
    'QuadTreeStrategy',
    'OctreeStrategy',
    
    # Batch 4: Graph representations
    'IncidenceMatrixStrategy',
    'EdgeListStrategy',
    'CompressedGraphStrategy',
    'BidirWrapperStrategy',
    
    # Batch 5: Specialized structures
    'TemporalEdgeSetStrategy',
    'HyperEdgeSetStrategy',
    'EdgePropertyStoreStrategy',
    'FlowNetworkStrategy',
    'NeuralGraphStrategy',
    
    # Batch 6: Basic & hybrid
    'TreeGraphBasicStrategy',
    
    # Batch 7: Advanced graph structures
    'K2TreeStrategy',
    'BVGraphStrategy',
    'HNSWStrategy',
    'EulerTourStrategy',
    'LinkCutStrategy',
    'Hop2LabelsStrategy',
    'GraphBLASStrategy',
    'RoaringAdjStrategy',
    'MultiplexStrategy',
    'BitemporalStrategy',
]
