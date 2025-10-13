"""
#exonware/xwnode/src/exonware/xwnode/common/patterns/registry.py

Strategy Registry

This module provides the StrategyRegistry class for managing strategy registration,
discovery, and instantiation in the strategy system.
"""

import threading
from typing import Dict, Type, List, Optional, Any, Callable
from exonware.xwsystem import get_logger

logger = get_logger(__name__)

from ...defs import NodeMode, EdgeMode, NodeTrait, EdgeTrait, NODE_STRATEGY_METADATA, EDGE_STRATEGY_METADATA
# Note: QueryMode and QueryTrait are in xwquery.defs module
from ...errors import XWNodeStrategyError, XWNodeError


class StrategyRegistry:
    """
    Central registry for managing strategy implementations.
    
    This class provides thread-safe registration and discovery of strategy
    implementations for both nodes and edges in the strategy system.
    """
    
    def __init__(self):
        """Initialize the strategy registry."""
        self._node_strategies: Dict[NodeMode, Type] = {}
        self._edge_strategies: Dict[EdgeMode, Type] = {}
        self._query_strategies: Dict[str, Type] = {}
        self._node_factories: Dict[NodeMode, Callable] = {}
        self._edge_factories: Dict[EdgeMode, Callable] = {}
        self._query_factories: Dict[str, Callable] = {}
        self._lock = threading.RLock()
        
        # Register default strategies
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register default strategy implementations."""
        # Import default strategies
        from ...edges.strategies.adj_list import AdjListStrategy
        from ...edges.strategies.adj_matrix import AdjMatrixStrategy
        from ...edges.strategies.csr import CSRStrategy
        from ...edges.strategies.dynamic_adj_list import DynamicAdjListStrategy
        from ...edges.strategies.temporal_edgeset import TemporalEdgeSetStrategy
        from ...edges.strategies.hyperedge_set import HyperEdgeSetStrategy
        from ...edges.strategies.rtree import RTreeStrategy
        from ...edges.strategies.flow_network import FlowNetworkStrategy
        from ...edges.strategies.neural_graph import NeuralGraphStrategy
        from ...edges.strategies.csc import CSCStrategy
        from ...edges.strategies.bidir_wrapper import BidirWrapperStrategy
        from ...edges.strategies.quadtree import QuadTreeStrategy
        from ...edges.strategies.coo import COOStrategy
        from ...edges.strategies.octree import OctreeStrategy
        from ...edges.strategies.edge_property_store import EdgePropertyStoreStrategy
        from ...edges.strategies.tree_graph_basic import TreeGraphBasicStrategy
        from ...edges.strategies.weighted_graph import WeightedGraphStrategy
        
        # Import new strategy implementations
        from ...nodes.strategies.hash_map import HashMapStrategy
        from ...nodes.strategies.array_list import ArrayListStrategy
        from ...nodes.strategies.trie import TrieStrategy
        from ...nodes.strategies.heap import HeapStrategy
        from ...nodes.strategies.b_tree import BTreeStrategy
        from ...nodes.strategies.union_find import UnionFindStrategy
        from ...nodes.strategies.segment_tree import SegmentTreeStrategy
        from ...nodes.strategies.lsm_tree import LSMTreeStrategy
        from ...nodes.strategies.fenwick_tree import FenwickTreeStrategy
        from ...nodes.strategies.set_hash import SetHashStrategy
        from ...nodes.strategies.bloom_filter import BloomFilterStrategy
        from ...nodes.strategies.cuckoo_hash import CuckooHashStrategy
        from ...nodes.strategies.bitmap import BitmapStrategy
        from ...nodes.strategies.roaring_bitmap import RoaringBitmapStrategy
        from ...nodes.strategies.suffix_array import SuffixArrayStrategy
        from ...nodes.strategies.aho_corasick import AhoCorasickStrategy
        from ...nodes.strategies.count_min_sketch import CountMinSketchStrategy
        from ...nodes.strategies.hyperloglog import HyperLogLogStrategy
        from ...nodes.strategies.set_tree import SetTreeStrategy
        from ...nodes.strategies.linked_list import LinkedListStrategy
        from ...nodes.strategies.ordered_map import OrderedMapStrategy
        from ...nodes.strategies.radix_trie import RadixTrieStrategy
        from ...nodes.strategies.patricia import PatriciaStrategy
        from ...nodes.strategies.b_plus_tree import BPlusTreeStrategy
        from ...nodes.strategies.persistent_tree import PersistentTreeStrategy
        from ...nodes.strategies.cow_tree import COWTreeStrategy
        from ...nodes.strategies.skip_list import SkipListStrategy
        from ...nodes.strategies.red_black_tree import RedBlackTreeStrategy
        from ...nodes.strategies.avl_tree import AVLTreeStrategy
        from ...nodes.strategies.treap import TreapStrategy
        from ...nodes.strategies.splay_tree import SplayTreeStrategy
        from ...nodes.strategies.ordered_map_balanced import OrderedMapBalancedStrategy
        from ...nodes.strategies.bitset_dynamic import BitsetDynamicStrategy
        from ...edges.strategies.block_adj_matrix import BlockAdjMatrixStrategy
        
        # Import linear data structure strategies
        from ...nodes.strategies.stack import StackStrategy
        from ...nodes.strategies.queue import QueueStrategy
        from ...nodes.strategies.priority_queue import PriorityQueueStrategy
        from ...nodes.strategies.deque import DequeStrategy
        
        # Import matrix and graph strategies
        from ...nodes.strategies.sparse_matrix import SparseMatrixStrategy
        from ...nodes.strategies.adjacency_list import AdjacencyListStrategy
        
        # Import NEW node strategies
        from ...nodes.strategies.art import ARTStrategy
        from ...nodes.strategies.bw_tree import BwTreeStrategy
        from ...nodes.strategies.hamt import HAMTStrategy
        from ...nodes.strategies.masstree import MasstreeStrategy
        from ...nodes.strategies.extendible_hash import ExtendibleHashStrategy
        from ...nodes.strategies.linear_hash import LinearHashStrategy
        from ...nodes.strategies.t_tree import TTreeStrategy
        from ...nodes.strategies.learned_index import LearnedIndexStrategy
        
        # Import NEW edge strategies
        from ...edges.strategies.incidence_matrix import IncidenceMatrixStrategy
        from ...edges.strategies.edge_list import EdgeListStrategy
        from ...edges.strategies.compressed_graph import CompressedGraphStrategy
        
        # Import data interchange optimized strategy
        from ...nodes.strategies.data_interchange_optimized import DataInterchangeOptimizedStrategy
        
        # Register tree-graph hybrid strategies
        from ...nodes.strategies.tree_graph_hybrid import TreeGraphHybridStrategy
        self.register_node_strategy(NodeMode.TREE_GRAPH_HYBRID, TreeGraphHybridStrategy)
        
        # Register edge strategies
        self.register_edge_strategy(EdgeMode.ADJ_LIST, AdjListStrategy)
        self.register_edge_strategy(EdgeMode.ADJ_MATRIX, AdjMatrixStrategy)
        self.register_edge_strategy(EdgeMode.CSR, CSRStrategy)
        self.register_edge_strategy(EdgeMode.DYNAMIC_ADJ_LIST, DynamicAdjListStrategy)
        self.register_edge_strategy(EdgeMode.TEMPORAL_EDGESET, TemporalEdgeSetStrategy)
        self.register_edge_strategy(EdgeMode.HYPEREDGE_SET, HyperEdgeSetStrategy)
        self.register_edge_strategy(EdgeMode.R_TREE, RTreeStrategy)
        self.register_edge_strategy(EdgeMode.FLOW_NETWORK, FlowNetworkStrategy)
        self.register_edge_strategy(EdgeMode.NEURAL_GRAPH, NeuralGraphStrategy)
        self.register_edge_strategy(EdgeMode.CSC, CSCStrategy)
        self.register_edge_strategy(EdgeMode.BIDIR_WRAPPER, BidirWrapperStrategy)
        self.register_edge_strategy(EdgeMode.QUADTREE, QuadTreeStrategy)
        self.register_edge_strategy(EdgeMode.COO, COOStrategy)
        self.register_edge_strategy(EdgeMode.OCTREE, OctreeStrategy)
        self.register_edge_strategy(EdgeMode.EDGE_PROPERTY_STORE, EdgePropertyStoreStrategy)
        self.register_edge_strategy(EdgeMode.TREE_GRAPH_BASIC, TreeGraphBasicStrategy)
        self.register_edge_strategy(EdgeMode.WEIGHTED_GRAPH, WeightedGraphStrategy)
        
        # Register advanced edge strategies
        from ...edges.strategies.k2_tree import K2TreeStrategy
        from ...edges.strategies.bv_graph import BVGraphStrategy
        from ...edges.strategies.hnsw import HNSWStrategy
        from ...edges.strategies.euler_tour import EulerTourStrategy
        from ...edges.strategies.link_cut import LinkCutStrategy
        from ...edges.strategies.hop2_labels import Hop2LabelsStrategy
        from ...edges.strategies.graphblas import GraphBLASStrategy
        from ...edges.strategies.roaring_adj import RoaringAdjStrategy
        from ...edges.strategies.multiplex import MultiplexStrategy
        from ...edges.strategies.bitemporal import BitemporalStrategy
        
        self.register_edge_strategy(EdgeMode.K2_TREE, K2TreeStrategy)
        self.register_edge_strategy(EdgeMode.BV_GRAPH, BVGraphStrategy)
        self.register_edge_strategy(EdgeMode.HNSW, HNSWStrategy)
        self.register_edge_strategy(EdgeMode.EULER_TOUR, EulerTourStrategy)
        self.register_edge_strategy(EdgeMode.LINK_CUT, LinkCutStrategy)
        self.register_edge_strategy(EdgeMode.HOP2_LABELS, Hop2LabelsStrategy)
        self.register_edge_strategy(EdgeMode.GRAPHBLAS, GraphBLASStrategy)
        self.register_edge_strategy(EdgeMode.ROARING_ADJ, RoaringAdjStrategy)
        self.register_edge_strategy(EdgeMode.MULTIPLEX, MultiplexStrategy)
        self.register_edge_strategy(EdgeMode.BITEMPORAL, BitemporalStrategy)
        
        # Register new node strategies
        self.register_node_strategy(NodeMode.HASH_MAP, HashMapStrategy)
        self.register_node_strategy(NodeMode.ARRAY_LIST, ArrayListStrategy)
        self.register_node_strategy(NodeMode.TRIE, TrieStrategy)
        self.register_node_strategy(NodeMode.HEAP, HeapStrategy)
        self.register_node_strategy(NodeMode.B_TREE, BTreeStrategy)
        self.register_node_strategy(NodeMode.UNION_FIND, UnionFindStrategy)
        self.register_node_strategy(NodeMode.SEGMENT_TREE, SegmentTreeStrategy)
        self.register_node_strategy(NodeMode.LSM_TREE, LSMTreeStrategy)
        self.register_node_strategy(NodeMode.FENWICK_TREE, FenwickTreeStrategy)
        self.register_node_strategy(NodeMode.SET_HASH, SetHashStrategy)
        self.register_node_strategy(NodeMode.BLOOM_FILTER, BloomFilterStrategy)
        self.register_node_strategy(NodeMode.CUCKOO_HASH, CuckooHashStrategy)
        self.register_node_strategy(NodeMode.BITMAP, BitmapStrategy)
        self.register_node_strategy(NodeMode.ROARING_BITMAP, RoaringBitmapStrategy)
        self.register_node_strategy(NodeMode.SUFFIX_ARRAY, SuffixArrayStrategy)
        self.register_node_strategy(NodeMode.AHO_CORASICK, AhoCorasickStrategy)
        self.register_node_strategy(NodeMode.COUNT_MIN_SKETCH, CountMinSketchStrategy)
        self.register_node_strategy(NodeMode.HYPERLOGLOG, HyperLogLogStrategy)
        self.register_node_strategy(NodeMode.SET_TREE, SetTreeStrategy)
        self.register_node_strategy(NodeMode.LINKED_LIST, LinkedListStrategy)
        self.register_node_strategy(NodeMode.ORDERED_MAP, OrderedMapStrategy)
        self.register_node_strategy(NodeMode.RADIX_TRIE, RadixTrieStrategy)
        self.register_node_strategy(NodeMode.PATRICIA, PatriciaStrategy)
        self.register_node_strategy(NodeMode.B_PLUS_TREE, BPlusTreeStrategy)
        self.register_node_strategy(NodeMode.PERSISTENT_TREE, PersistentTreeStrategy)
        self.register_node_strategy(NodeMode.COW_TREE, COWTreeStrategy)
        self.register_node_strategy(NodeMode.SKIP_LIST, SkipListStrategy)
        self.register_node_strategy(NodeMode.RED_BLACK_TREE, RedBlackTreeStrategy)
        self.register_node_strategy(NodeMode.AVL_TREE, AVLTreeStrategy)
        self.register_node_strategy(NodeMode.TREAP, TreapStrategy)
        self.register_node_strategy(NodeMode.SPLAY_TREE, SplayTreeStrategy)
        self.register_node_strategy(NodeMode.ORDERED_MAP_BALANCED, OrderedMapBalancedStrategy)
        self.register_node_strategy(NodeMode.BITSET_DYNAMIC, BitsetDynamicStrategy)
        
        # Register linear data structure strategies
        self.register_node_strategy(NodeMode.STACK, StackStrategy)
        self.register_node_strategy(NodeMode.QUEUE, QueueStrategy)
        self.register_node_strategy(NodeMode.PRIORITY_QUEUE, PriorityQueueStrategy)
        self.register_node_strategy(NodeMode.DEQUE, DequeStrategy)
        
        # Register matrix and graph strategies
        self.register_node_strategy(NodeMode.SPARSE_MATRIX, SparseMatrixStrategy)
        self.register_node_strategy(NodeMode.ADJACENCY_LIST, AdjacencyListStrategy)
        
        # Register NEW node strategies
        self.register_node_strategy(NodeMode.ART, ARTStrategy)
        self.register_node_strategy(NodeMode.BW_TREE, BwTreeStrategy)
        self.register_node_strategy(NodeMode.HAMT, HAMTStrategy)
        self.register_node_strategy(NodeMode.MASSTREE, MasstreeStrategy)
        self.register_node_strategy(NodeMode.EXTENDIBLE_HASH, ExtendibleHashStrategy)
        self.register_node_strategy(NodeMode.LINEAR_HASH, LinearHashStrategy)
        self.register_node_strategy(NodeMode.T_TREE, TTreeStrategy)
        self.register_node_strategy(NodeMode.LEARNED_INDEX, LearnedIndexStrategy)
        
        # Register data interchange optimized strategy
        self.register_node_strategy(NodeMode.DATA_INTERCHANGE_OPTIMIZED, DataInterchangeOptimizedStrategy)
        
        # Register advanced specialized node strategies
        from ...nodes.strategies.veb_tree import VebTreeStrategy
        from ...nodes.strategies.dawg import DawgStrategy
        from ...nodes.strategies.hopscotch_hash import HopscotchHashStrategy
        from ...nodes.strategies.interval_tree import IntervalTreeStrategy
        from ...nodes.strategies.kd_tree import KdTreeStrategy
        from ...nodes.strategies.rope import RopeStrategy
        from ...nodes.strategies.crdt_map import CRDTMapStrategy
        from ...nodes.strategies.bloomier_filter import BloomierFilterStrategy
        
        self.register_node_strategy(NodeMode.VEB_TREE, VebTreeStrategy)
        self.register_node_strategy(NodeMode.DAWG, DawgStrategy)
        self.register_node_strategy(NodeMode.HOPSCOTCH_HASH, HopscotchHashStrategy)
        self.register_node_strategy(NodeMode.INTERVAL_TREE, IntervalTreeStrategy)
        self.register_node_strategy(NodeMode.KD_TREE, KdTreeStrategy)
        self.register_node_strategy(NodeMode.ROPE, RopeStrategy)
        self.register_node_strategy(NodeMode.CRDT_MAP, CRDTMapStrategy)
        self.register_node_strategy(NodeMode.BLOOMIER_FILTER, BloomierFilterStrategy)
        
        # Edge strategies
        self.register_edge_strategy(EdgeMode.BLOCK_ADJ_MATRIX, BlockAdjMatrixStrategy)
        
        # Register NEW edge strategies
        self.register_edge_strategy(EdgeMode.INCIDENCE_MATRIX, IncidenceMatrixStrategy)
        self.register_edge_strategy(EdgeMode.EDGE_LIST, EdgeListStrategy)
        self.register_edge_strategy(EdgeMode.COMPRESSED_GRAPH, CompressedGraphStrategy)
        
        # Register data interchange optimized strategy factory
        # Note: This will be used by strategy manager when DATA_INTERCHANGE_OPTIMIZED preset is detected
        self.register_data_interchange_optimized_factory()
        
        logger.info("✅ Registered default strategies")
    
    def register_data_interchange_optimized_factory(self):
        """Register special factory for DATA_INTERCHANGE_OPTIMIZED preset handling."""
        # We'll store this in a special attribute for the strategy manager to use
        def data_interchange_factory(**options):
            from ...nodes.strategies.data_interchange_optimized import DataInterchangeOptimizedStrategy
            return DataInterchangeOptimizedStrategy(NodeTrait.INDEXED, **options)
        
        self._data_interchange_optimized_factory = data_interchange_factory
        logger.debug("📝 Registered data interchange optimized strategy factory")
    
    def get_data_interchange_optimized_factory(self):
        """Get the data interchange optimized strategy factory."""
        return getattr(self, '_data_interchange_optimized_factory', None)
    
    def register_node_strategy(self, mode: NodeMode, strategy_class: Type, 
                             factory: Optional[Callable] = None) -> None:
        """
        Register a node strategy implementation.
        
        Args:
            mode: The node mode to register
            strategy_class: The strategy implementation class
            factory: Optional factory function for custom instantiation
        """
        with self._lock:
            self._node_strategies[mode] = strategy_class
            if factory:
                self._node_factories[mode] = factory
            
            logger.debug(f"📝 Registered node strategy: {mode.name} -> {strategy_class.__name__}")
    
    def register_edge_strategy(self, mode: EdgeMode, strategy_class: Type,
                             factory: Optional[Callable] = None) -> None:
        """
        Register an edge strategy implementation.
        
        Args:
            mode: The edge mode to register
            strategy_class: The strategy implementation class
            factory: Optional factory function for custom instantiation
        """
        with self._lock:
            self._edge_strategies[mode] = strategy_class
            if factory:
                self._edge_factories[mode] = factory
            
            logger.debug(f"📝 Registered edge strategy: {mode.name} -> {strategy_class.__name__}")
    
    def register_query_strategy(self, query_type: str, strategy_class: Type,
                              factory: Optional[Callable] = None) -> None:
        """
        Register a query strategy implementation.
        
        Args:
            query_type: The query type to register (e.g., "SQL", "GRAPHQL")
            strategy_class: The strategy implementation class
            factory: Optional factory function for custom instantiation
        """
        with self._lock:
            self._query_strategies[query_type.upper()] = strategy_class
            if factory:
                self._query_factories[query_type.upper()] = factory
            
            logger.debug(f"📝 Registered query strategy: {query_type.upper()} -> {strategy_class.__name__}")
    
    def get_node_strategy(self, mode: NodeMode, **kwargs) -> Any:
        """
        Get a node strategy instance.
        
        Args:
            mode: The node mode to instantiate
            **kwargs: Arguments to pass to the strategy constructor
            
        Returns:
            Strategy instance
            
        Raises:
            StrategyNotFoundError: If the strategy is not registered
            StrategyInitializationError: If strategy initialization fails
        """
        with self._lock:
            if mode not in self._node_strategies:
                raise XWNodeStrategyError(message=f"Strategy '{mode.name}' not found for node")
            
            strategy_class = self._node_strategies[mode]
            
            try:
                if mode in self._node_factories:
                    return self._node_factories[mode](**kwargs)
                else:
                    # Handle new interface that doesn't accept traits and other arguments
                    if mode == NodeMode.TREE_GRAPH_HYBRID:
                        # For TreeGraphHybridStrategy, ignore traits and other arguments
                        return strategy_class()
                    else:
                        return strategy_class(**kwargs)
                    
            except Exception as e:
                raise XWNodeError(message=f"Failed to initialize strategy '{mode.name}': {e}", cause=e)
    
    def get_node_strategy_class(self, mode: NodeMode) -> Type:
        """
        Get the strategy class for the specified mode.
        
        Args:
            mode: Node mode
            
        Returns:
            Strategy class
            
        Raises:
            XWNodeStrategyError: If strategy not found
        """
        with self._lock:
            if mode not in self._node_strategies:
                raise XWNodeStrategyError(message=f"Strategy '{mode.name}' not found for node")
            
            return self._node_strategies[mode]
    
    def get_edge_strategy(self, mode: EdgeMode, **kwargs) -> Any:
        """
        Get an edge strategy instance.
        
        Args:
            mode: The edge mode to instantiate
            **kwargs: Arguments to pass to the strategy constructor
            
        Returns:
            Strategy instance
            
        Raises:
            StrategyNotFoundError: If the strategy is not registered
            StrategyInitializationError: If strategy initialization fails
        """
        with self._lock:
            if mode not in self._edge_strategies:
                raise XWNodeStrategyError(message=f"Strategy '{mode.name}' not found for edge")
            
            strategy_class = self._edge_strategies[mode]
            
            try:
                if mode in self._edge_factories:
                    return self._edge_factories[mode](**kwargs)
                else:
                    return strategy_class(**kwargs)
                    
            except Exception as e:
                raise XWNodeError(message=f"Failed to initialize strategy '{mode.name}': {e}", cause=e)
    
    def get_query_strategy(self, query_type: str, **kwargs) -> Any:
        """
        Get a query strategy instance.
        
        Args:
            query_type: The query type to instantiate (e.g., "SQL", "GRAPHQL")
            **kwargs: Arguments to pass to the strategy constructor
            
        Returns:
            Strategy instance
            
        Raises:
            XWNodeStrategyError: If the strategy is not registered
            XWNodeError: If strategy initialization fails
        """
        with self._lock:
            query_type_upper = query_type.upper()
            if query_type_upper not in self._query_strategies:
                raise XWNodeStrategyError(message=f"Query strategy '{query_type}' not found")
            
            strategy_class = self._query_strategies[query_type_upper]
            
            try:
                if query_type_upper in self._query_factories:
                    return self._query_factories[query_type_upper](**kwargs)
                else:
                    return strategy_class(**kwargs)
                    
            except Exception as e:
                raise XWNodeError(message=f"Failed to initialize query strategy '{query_type}': {e}", cause=e)
    
    def get_query_strategy_class(self, query_type: str) -> Type:
        """
        Get the query strategy class for the specified type.
        
        Args:
            query_type: Query type
            
        Returns:
            Strategy class
            
        Raises:
            XWNodeStrategyError: If strategy not found
        """
        with self._lock:
            query_type_upper = query_type.upper()
            if query_type_upper not in self._query_strategies:
                raise XWNodeStrategyError(message=f"Query strategy '{query_type}' not found")
            
            return self._query_strategies[query_type_upper]
    
    def list_node_modes(self) -> List[NodeMode]:
        """List all registered node modes."""
        with self._lock:
            return list(self._node_strategies.keys())
    
    def list_edge_modes(self) -> List[EdgeMode]:
        """List all registered edge modes."""
        with self._lock:
            return list(self._edge_strategies.keys())
    
    def list_query_types(self) -> List[str]:
        """List all registered query types."""
        with self._lock:
            return list(self._query_strategies.keys())
    
    def get_node_metadata(self, mode: NodeMode) -> Optional[Any]:
        """Get metadata for a node mode."""
        return NODE_STRATEGY_METADATA.get(mode)
    
    def get_edge_metadata(self, mode: EdgeMode) -> Optional[Any]:
        """Get metadata for an edge mode."""
        return EDGE_STRATEGY_METADATA.get(mode)
    
    def has_node_strategy(self, mode: NodeMode) -> bool:
        """Check if a node strategy is registered."""
        with self._lock:
            return mode in self._node_strategies
    
    def has_edge_strategy(self, mode: EdgeMode) -> bool:
        """Check if an edge strategy is registered."""
        with self._lock:
            return mode in self._edge_strategies
    
    def has_query_strategy(self, query_type: str) -> bool:
        """Check if a query strategy is registered."""
        with self._lock:
            return query_type.upper() in self._query_strategies
    
    def unregister_node_strategy(self, mode: NodeMode) -> bool:
        """
        Unregister a node strategy.
        
        Returns:
            True if strategy was unregistered, False if not found
        """
        with self._lock:
            if mode in self._node_strategies:
                del self._node_strategies[mode]
                if mode in self._node_factories:
                    del self._node_factories[mode]
                logger.debug(f"🗑️ Unregistered node strategy: {mode.name}")
                return True
            return False
    
    def unregister_edge_strategy(self, mode: EdgeMode) -> bool:
        """
        Unregister an edge strategy.
        
        Returns:
            True if strategy was unregistered, False if not found
        """
        with self._lock:
            if mode in self._edge_strategies:
                del self._edge_strategies[mode]
                if mode in self._edge_factories:
                    del self._edge_factories[mode]
                logger.debug(f"🗑️ Unregistered edge strategy: {mode.name}")
                return True
            return False
    
    def unregister_query_strategy(self, query_type: str) -> bool:
        """
        Unregister a query strategy.
        
        Returns:
            True if strategy was unregistered, False if not found
        """
        with self._lock:
            query_type_upper = query_type.upper()
            if query_type_upper in self._query_strategies:
                del self._query_strategies[query_type_upper]
                if query_type_upper in self._query_factories:
                    del self._query_factories[query_type_upper]
                logger.debug(f"🗑️ Unregistered query strategy: {query_type_upper}")
                return True
            return False
    
    def clear_node_strategies(self) -> None:
        """Clear all registered node strategies."""
        with self._lock:
            self._node_strategies.clear()
            self._node_factories.clear()
            logger.info("🗑️ Cleared all node strategies")
    
    def clear_edge_strategies(self) -> None:
        """Clear all registered edge strategies."""
        with self._lock:
            self._edge_strategies.clear()
            self._edge_factories.clear()
            logger.info("🗑️ Cleared all edge strategies")
    
    def clear_query_strategies(self) -> None:
        """Clear all registered query strategies."""
        with self._lock:
            self._query_strategies.clear()
            self._query_factories.clear()
            logger.info("🗑️ Cleared all query strategies")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            return {
                "node_strategies": len(self._node_strategies),
                "edge_strategies": len(self._edge_strategies),
                "query_strategies": len(self._query_strategies),
                "node_factories": len(self._node_factories),
                "edge_factories": len(self._edge_factories),
                "query_factories": len(self._query_factories),
                "registered_node_modes": [mode.name for mode in self._node_strategies.keys()],
                "registered_edge_modes": [mode.name for mode in self._edge_strategies.keys()],
                "registered_query_types": list(self._query_strategies.keys())
            }


# Global registry instance
_registry = None


def get_registry() -> StrategyRegistry:
    """Get the global strategy registry instance."""
    global _registry
    if _registry is None:
        _registry = StrategyRegistry()
    return _registry


def register_node_strategy(mode: NodeMode, strategy_class: Type, 
                         factory: Optional[Callable] = None) -> None:
    """Register a node strategy with the global registry."""
    get_registry().register_node_strategy(mode, strategy_class, factory)


def register_edge_strategy(mode: EdgeMode, strategy_class: Type,
                         factory: Optional[Callable] = None) -> None:
    """Register an edge strategy with the global registry."""
    get_registry().register_edge_strategy(mode, strategy_class, factory)


def register_query_strategy(query_type: str, strategy_class: Type,
                          factory: Optional[Callable] = None) -> None:
    """Register a query strategy with the global registry."""
    get_registry().register_query_strategy(query_type, strategy_class, factory)


def get_strategy_registry() -> StrategyRegistry:
    """Get the global strategy registry instance (alias for get_registry)."""
    return get_registry()
