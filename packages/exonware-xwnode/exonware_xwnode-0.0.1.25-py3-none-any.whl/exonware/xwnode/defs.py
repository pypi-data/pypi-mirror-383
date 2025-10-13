"""
XWNode Strategy Types and Enums

This module defines all the enums and types for the XWNode strategy system:
- NodeMode: 49 different node data structure strategies (including DATA_INTERCHANGE_OPTIMIZED)
- EdgeMode: 22 different edge storage strategies
- NodeTrait: Cross-cutting node capabilities
- EdgeTrait: Cross-cutting edge capabilities

Note: Query-related enums (QueryMode, QueryTrait) are in xwquery.defs module.
"""

from enum import Enum, Flag, auto as _auto
from typing import Dict, List, Any, Optional


# ============================================================================
# NODE MODES (57 total)
# ============================================================================

class NodeMode(Enum):
    """Node data structure strategies for GEMINI-2 (57 total)."""
    
    # Special modes
    AUTO = _auto()                    # Intelligent automatic selection
    TREE_GRAPH_HYBRID = _auto()       # Tree navigation + basic graph capabilities
    
    # Basic data structures
    HASH_MAP = _auto()                # Optimized for lookups
    ORDERED_MAP = _auto()             # Optimized for sorted operations
    ORDERED_MAP_BALANCED = _auto()    # Explicit balanced trees (RB/AVL/Treap)
    ARRAY_LIST = _auto()              # Optimized for small datasets
    LINKED_LIST = _auto()             # Optimized for insertions/deletions
    
    # Linear data structures
    STACK = _auto()                   # LIFO (Last In, First Out)
    QUEUE = _auto()                   # FIFO (First In, First Out)
    PRIORITY_QUEUE = _auto()          # Priority-based operations
    DEQUE = _auto()                   # Double-ended queue
    
    # Tree structures
    TRIE = _auto()                    # Basic trie implementation
    RADIX_TRIE = _auto()              # Compressed prefixes
    PATRICIA = _auto()                # Patricia trie (compressed binary trie)
    
    # Specialized structures
    HEAP = _auto()                    # Optimized for priority operations
    SET_HASH = _auto()                # Optimized for set operations
    SET_TREE = _auto()                # Optimized for ordered sets
    BLOOM_FILTER = _auto()            # Optimized for membership tests
    CUCKOO_HASH = _auto()             # Optimized for high load factors
    
    # Bitmap structures
    BITMAP = _auto()                  # Static bitmap operations
    BITSET_DYNAMIC = _auto()          # Resizable bitset
    ROARING_BITMAP = _auto()          # Optimized for sparse bitmaps
    
    # Matrix structures
    SPARSE_MATRIX = _auto()           # Sparse matrix operations
    
    # Graph structures
    ADJACENCY_LIST = _auto()          # Adjacency list representation
    
    # Persistent structures
    B_TREE = _auto()                  # Disk/page indexes
    B_PLUS_TREE = _auto()             # Database-friendly B+ tree
    LSM_TREE = _auto()                # Write-heavy key-value store
    PERSISTENT_TREE = _auto()         # Immutable functional tree
    COW_TREE = _auto()                # Copy-on-write tree
    
    # Algorithmic structures
    UNION_FIND = _auto()              # Connectivity/disjoint sets
    SEGMENT_TREE = _auto()            # Range queries and updates
    FENWICK_TREE = _auto()            # Prefix sums (Binary Indexed Tree)
    
    # String structures
    SUFFIX_ARRAY = _auto()            # Substring search
    AHO_CORASICK = _auto()            # Multi-pattern string matching
    
    # Probabilistic structures
    COUNT_MIN_SKETCH = _auto()        # Streaming frequency estimation
    HYPERLOGLOG = _auto()             # Cardinality estimation
    
    # Advanced tree structures
    SKIP_LIST = _auto()               # Probabilistic data structure
    RED_BLACK_TREE = _auto()          # Self-balancing binary search tree
    AVL_TREE = _auto()                # Strictly balanced binary search tree
    TREAP = _auto()                   # Randomized balanced tree
    SPLAY_TREE = _auto()              # Self-adjusting binary search tree
    
    # High-performance structures (NEW)
    ART = _auto()                     # Adaptive Radix Tree
    BW_TREE = _auto()                 # Lock-Free B-tree (Bw-Tree)
    HAMT = _auto()                    # Hash Array Mapped Trie
    MASSTREE = _auto()                # B+ tree + trie hybrid
    EXTENDIBLE_HASH = _auto()         # Dynamic hash table
    LINEAR_HASH = _auto()             # Linear dynamic hashing
    T_TREE = _auto()                  # In-memory T-tree
    LEARNED_INDEX = _auto()           # ML-based learned indexes (experimental)
    
    # Data interchange structures
    DATA_INTERCHANGE_OPTIMIZED = _auto()  # Ultra-lightweight for data interchange (COW, pooling, hash caching)
    
    # Advanced specialized structures
    VEB_TREE = _auto()                # van Emde Boas tree - O(log log U) integer ops
    DAWG = _auto()                    # DAWG/DAFSA - minimal automaton for strings
    HOPSCOTCH_HASH = _auto()          # Hopscotch hashing - bounded neighborhood search
    INTERVAL_TREE = _auto()           # Interval overlap queries - scheduling, genomics
    KD_TREE = _auto()                 # k-dimensional spatial tree - point queries
    ROPE = _auto()                    # Rope structure - efficient text operations
    CRDT_MAP = _auto()                # Conflict-free replicated map - distributed systems
    BLOOMIER_FILTER = _auto()         # Probabilistic key→value map - approximate dictionaries


# ============================================================================
# EDGE MODES (28 total)
# ============================================================================

class EdgeMode(Enum):
    """Edge storage strategies for GEMINI-2 (28 total)."""
    
    # Special modes
    AUTO = _auto()                    # Intelligent automatic selection
    TREE_GRAPH_BASIC = _auto()        # Basic edge storage for tree+graph hybrid
    
    # Basic graph structures
    ADJ_LIST = _auto()                # Optimized for sparse graphs
    DYNAMIC_ADJ_LIST = _auto()        # High churn graphs
    ADJ_MATRIX = _auto()              # Optimized for dense graphs
    BLOCK_ADJ_MATRIX = _auto()        # Cache-friendly dense operations
    
    # Sparse matrix formats
    CSR = _auto()                     # Compressed Sparse Row format
    CSC = _auto()                     # Compressed Sparse Column format
    COO = _auto()                     # Coordinate format
    
    # Specialized graph structures
    BIDIR_WRAPPER = _auto()           # Undirected via dual arcs
    TEMPORAL_EDGESET = _auto()        # Time-keyed edges
    HYPEREDGE_SET = _auto()           # Hypergraphs
    EDGE_PROPERTY_STORE = _auto()     # Columnar edge attributes
    
    # Spatial structures
    R_TREE = _auto()                  # Spatial indexing (2D/3D rectangles)
    QUADTREE = _auto()                # 2D spatial partitioning
    OCTREE = _auto()                  # 3D spatial partitioning
    
    # Flow and neural networks
    FLOW_NETWORK = _auto()            # Flow graphs with capacity constraints
    NEURAL_GRAPH = _auto()            # Neural network computation graphs
    
    # Weighted graph structures
    WEIGHTED_GRAPH = _auto()          # Graph with numerical edge weights
    
    # Graph representation structures (NEW)
    INCIDENCE_MATRIX = _auto()        # Incidence matrix representation
    EDGE_LIST = _auto()               # Simple edge list format
    COMPRESSED_GRAPH = _auto()        # WebGraph/LLP compression
    
    # Advanced graph structures
    K2_TREE = _auto()                 # k²-tree ultra-compact adjacency
    BV_GRAPH = _auto()                # BVGraph full WebGraph with Elias coding
    HNSW = _auto()                    # Hierarchical Navigable Small World - ANN search
    EULER_TOUR = _auto()              # Euler tour trees - dynamic connectivity
    LINK_CUT = _auto()                # Link-cut trees - dynamic trees with path queries
    HOP2_LABELS = _auto()             # 2-hop labeling - fast reachability queries
    GRAPHBLAS = _auto()               # GraphBLAS semiring-based operations
    ROARING_ADJ = _auto()             # Roaring bitmap adjacency - fast set operations
    MULTIPLEX = _auto()               # Multiplex/layered edges - multi-layer graphs
    BITEMPORAL = _auto()              # Bitemporal edges - valid and transaction time


# ============================================================================
# GRAPH OPTIMIZATION (4 levels)
# ============================================================================

class GraphOptimization(Enum):
    """
    Graph optimization levels for XWGraphManager.
    
    Controls indexing and caching behavior for performance tuning.
    """
    
    OFF = 0           # No optimization - fallback to O(n) iteration
    INDEX_ONLY = 1    # Only indexing - O(1) lookups, no caching
    CACHE_ONLY = 2    # Only caching - benefits from repeated queries
    FULL = 3          # Both indexing + caching - maximum performance
    
    # Aliases for clarity
    DISABLED = 0
    MINIMAL = 1
    MODERATE = 2
    MAXIMUM = 3


# ============================================================================
# NODE TRAITS (12 total)
# ============================================================================

class NodeTrait(Flag):
    """Cross-cutting node capabilities for GEMINI-2."""
    
    NONE = 0
    
    # Basic capabilities
    WEIGHTED = _auto()                # Supports weighted operations
    DIRECTED = _auto()                # Supports directed operations
    MULTI = _auto()                   # Supports multiple values per key
    COMPRESSED = _auto()              # Uses compression
    
    # Advanced capabilities
    PROBABILISTIC = _auto()           # Probabilistic data structures
    SPATIAL = _auto()                 # Spatial operations
    ORDERED = _auto()                 # Maintains order
    PERSISTENT = _auto()              # Disk-friendly
    
    # Performance capabilities
    STREAMING = _auto()               # Streaming operations
    INDEXED = _auto()                 # Indexed operations
    HIERARCHICAL = _auto()            # Hierarchical structure
    PRIORITY = _auto()                # Priority operations
    
    # Linear capabilities
    LIFO = _auto()                    # Last In, First Out
    FIFO = _auto()                    # First In, First Out
    DOUBLE_ENDED = _auto()            # Double-ended operations
    FAST_INSERT = _auto()             # Fast insertion operations
    FAST_DELETE = _auto()             # Fast deletion operations
    
    # Matrix capabilities
    MATRIX_OPS = _auto()              # Matrix operations
    SPARSE = _auto()                  # Sparse data structures
    MEMORY_EFFICIENT = _auto()        # Memory efficient
    
    # Graph capabilities
    FAST_NEIGHBORS = _auto()          # Fast neighbor queries
    
    # Advanced structure capabilities (from structures files)
    GRAPH = _auto()                   # Graph operations (Union-Find, FSM, DAG)
    NEURAL = _auto()                  # Neural network operations
    STATE_MACHINE = _auto()           # Finite state machine operations
    PREFIX_TREE = _auto()             # Trie/prefix tree operations
    UNION_FIND = _auto()              # Disjoint set operations
    HEAP_OPERATIONS = _auto()         # Priority queue operations


# ============================================================================
# EDGE TRAITS (12 total)
# ============================================================================

class EdgeTrait(Flag):
    """Cross-cutting edge capabilities for GEMINI-2."""
    
    NONE = 0
    
    # Basic capabilities
    WEIGHTED = _auto()                # Weighted edges
    DIRECTED = _auto()                # Directed edges
    MULTI = _auto()                   # Multiple edges between vertices
    COMPRESSED = _auto()              # Compressed storage
    
    # Advanced capabilities
    SPATIAL = _auto()                 # Spatial operations
    TEMPORAL = _auto()                # Time-aware edges
    HYPER = _auto()                   # Hyperedge support
    HIERARCHICAL = _auto()            # Hierarchical/tree structure
    
    # Performance capabilities
    DENSE = _auto()                   # Dense graph optimized
    SPARSE = _auto()                  # Sparse graph optimized
    CACHE_FRIENDLY = _auto()          # Cache-optimized
    COLUMNAR = _auto()                # Columnar storage


# ============================================================================
# CONVENIENCE CONSTANTS
# ============================================================================

# Node Mode Constants
AUTO = NodeMode.AUTO
TREE_GRAPH_HYBRID = NodeMode.TREE_GRAPH_HYBRID
# Backwards compatibility
LEGACY = NodeMode.TREE_GRAPH_HYBRID  # Maps to new name
HASH_MAP = NodeMode.HASH_MAP
ORDERED_MAP = NodeMode.ORDERED_MAP
ORDERED_MAP_BALANCED = NodeMode.ORDERED_MAP_BALANCED
ARRAY_LIST = NodeMode.ARRAY_LIST
LINKED_LIST = NodeMode.LINKED_LIST
STACK = NodeMode.STACK
QUEUE = NodeMode.QUEUE
PRIORITY_QUEUE = NodeMode.PRIORITY_QUEUE
DEQUE = NodeMode.DEQUE
TRIE = NodeMode.TRIE
RADIX_TRIE = NodeMode.RADIX_TRIE
PATRICIA = NodeMode.PATRICIA
HEAP = NodeMode.HEAP
SET_HASH = NodeMode.SET_HASH
SET_TREE = NodeMode.SET_TREE
BLOOM_FILTER = NodeMode.BLOOM_FILTER
CUCKOO_HASH = NodeMode.CUCKOO_HASH
BITMAP = NodeMode.BITMAP
BITSET_DYNAMIC = NodeMode.BITSET_DYNAMIC
ROARING_BITMAP = NodeMode.ROARING_BITMAP
SPARSE_MATRIX = NodeMode.SPARSE_MATRIX
ADJACENCY_LIST = NodeMode.ADJACENCY_LIST
B_TREE = NodeMode.B_TREE
B_PLUS_TREE = NodeMode.B_PLUS_TREE
LSM_TREE = NodeMode.LSM_TREE
PERSISTENT_TREE = NodeMode.PERSISTENT_TREE
COW_TREE = NodeMode.COW_TREE
UNION_FIND = NodeMode.UNION_FIND
SEGMENT_TREE = NodeMode.SEGMENT_TREE
FENWICK_TREE = NodeMode.FENWICK_TREE
SUFFIX_ARRAY = NodeMode.SUFFIX_ARRAY
AHO_CORASICK = NodeMode.AHO_CORASICK
COUNT_MIN_SKETCH = NodeMode.COUNT_MIN_SKETCH
HYPERLOGLOG = NodeMode.HYPERLOGLOG
SKIP_LIST = NodeMode.SKIP_LIST
RED_BLACK_TREE = NodeMode.RED_BLACK_TREE
AVL_TREE = NodeMode.AVL_TREE
TREAP = NodeMode.TREAP
SPLAY_TREE = NodeMode.SPLAY_TREE
ART = NodeMode.ART
BW_TREE = NodeMode.BW_TREE
HAMT = NodeMode.HAMT
MASSTREE = NodeMode.MASSTREE
EXTENDIBLE_HASH = NodeMode.EXTENDIBLE_HASH
LINEAR_HASH = NodeMode.LINEAR_HASH
T_TREE = NodeMode.T_TREE
LEARNED_INDEX = NodeMode.LEARNED_INDEX
DATA_INTERCHANGE_OPTIMIZED = NodeMode.DATA_INTERCHANGE_OPTIMIZED
VEB_TREE = NodeMode.VEB_TREE
DAWG = NodeMode.DAWG
HOPSCOTCH_HASH = NodeMode.HOPSCOTCH_HASH
INTERVAL_TREE = NodeMode.INTERVAL_TREE
KD_TREE = NodeMode.KD_TREE
ROPE = NodeMode.ROPE
CRDT_MAP = NodeMode.CRDT_MAP
BLOOMIER_FILTER = NodeMode.BLOOMIER_FILTER

# Edge Mode Constants
ADJ_LIST = EdgeMode.ADJ_LIST
DYNAMIC_ADJ_LIST = EdgeMode.DYNAMIC_ADJ_LIST
ADJ_MATRIX = EdgeMode.ADJ_MATRIX
BLOCK_ADJ_MATRIX = EdgeMode.BLOCK_ADJ_MATRIX
CSR = EdgeMode.CSR
CSC = EdgeMode.CSC
COO = EdgeMode.COO
BIDIR_WRAPPER = EdgeMode.BIDIR_WRAPPER
TEMPORAL_EDGESET = EdgeMode.TEMPORAL_EDGESET
HYPEREDGE_SET = EdgeMode.HYPEREDGE_SET
EDGE_PROPERTY_STORE = EdgeMode.EDGE_PROPERTY_STORE
R_TREE = EdgeMode.R_TREE
QUADTREE = EdgeMode.QUADTREE
OCTREE = EdgeMode.OCTREE
TREE_GRAPH_BASIC = EdgeMode.TREE_GRAPH_BASIC
WEIGHTED_GRAPH = EdgeMode.WEIGHTED_GRAPH
INCIDENCE_MATRIX = EdgeMode.INCIDENCE_MATRIX
EDGE_LIST = EdgeMode.EDGE_LIST
COMPRESSED_GRAPH = EdgeMode.COMPRESSED_GRAPH
K2_TREE = EdgeMode.K2_TREE
BV_GRAPH = EdgeMode.BV_GRAPH
HNSW = EdgeMode.HNSW
EULER_TOUR = EdgeMode.EULER_TOUR
LINK_CUT = EdgeMode.LINK_CUT
HOP2_LABELS = EdgeMode.HOP2_LABELS
GRAPHBLAS = EdgeMode.GRAPHBLAS
ROARING_ADJ = EdgeMode.ROARING_ADJ
MULTIPLEX = EdgeMode.MULTIPLEX
BITEMPORAL = EdgeMode.BITEMPORAL


# ============================================================================
# STRATEGY METADATA
# ============================================================================

class StrategyMetadata:
    """Metadata for strategy modes including capabilities and performance characteristics."""
    
    def __init__(self, 
                 mode: NodeMode | EdgeMode,
                 traits: NodeTrait | EdgeTrait,
                 description: str,
                 best_for: List[str],
                 performance_gain: str,
                 memory_usage: str = "medium",
                 time_complexity: Dict[str, str] = None):
        self.mode = mode
        self.traits = traits
        self.description = description
        self.best_for = best_for
        self.performance_gain = performance_gain
        self.memory_usage = memory_usage
        self.time_complexity = time_complexity or {}


# Node strategy metadata
NODE_STRATEGY_METADATA: Dict[NodeMode, StrategyMetadata] = {
    NodeMode.TREE_GRAPH_HYBRID: StrategyMetadata(
        NodeMode.TREE_GRAPH_HYBRID,
        NodeTrait.HIERARCHICAL,
        "Tree navigation with basic graph capabilities",
        ["general purpose", "tree + graph hybrid", "backward compatibility"],
        "balanced performance",
        "medium"
    ),
    
    NodeMode.HASH_MAP: StrategyMetadata(
        NodeMode.HASH_MAP,
        NodeTrait.INDEXED,
        "Optimized hash table for fast lookups",
        ["frequent lookups", "large datasets", "unordered data"],
        "10-100x faster lookups",
        "high",
        {"get": "O(1)", "set": "O(1)", "delete": "O(1)"}
    ),
    
    NodeMode.ORDERED_MAP: StrategyMetadata(
        NodeMode.ORDERED_MAP,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Ordered map with sorted key traversal",
        ["ordered iteration", "range queries", "sorted data"],
        "5-20x faster ordered operations",
        "medium",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.ARRAY_LIST: StrategyMetadata(
        NodeMode.ARRAY_LIST,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Dynamic array for small datasets",
        ["small datasets", "sequential access", "frequent iteration"],
        "2-5x faster for small datasets",
        "low",
        {"get": "O(1)", "set": "O(1)", "delete": "O(n)"}
    ),
    
    NodeMode.TRIE: StrategyMetadata(
        NodeMode.TRIE,
        NodeTrait.HIERARCHICAL | NodeTrait.INDEXED,
        "Prefix tree for string operations",
        ["prefix searches", "autocomplete", "string keys"],
        "10-50x faster prefix operations",
        "medium",
        {"get": "O(k)", "set": "O(k)", "delete": "O(k)"}
    ),
    
    NodeMode.HEAP: StrategyMetadata(
        NodeMode.HEAP,
        NodeTrait.PRIORITY | NodeTrait.ORDERED,
        "Priority queue for ordered access",
        ["priority operations", "top-k queries", "scheduling"],
        "5-10x faster priority operations",
        "low",
        {"get_min": "O(1)", "insert": "O(log n)", "delete_min": "O(log n)"}
    ),
    
    NodeMode.BLOOM_FILTER: StrategyMetadata(
        NodeMode.BLOOM_FILTER,
        NodeTrait.PROBABILISTIC,
        "Probabilistic membership testing",
        ["membership tests", "large datasets", "memory efficiency"],
        "100-1000x memory reduction",
        "very low",
        {"contains": "O(k)", "add": "O(k)"}
    ),
    
    NodeMode.B_TREE: StrategyMetadata(
        NodeMode.B_TREE,
        NodeTrait.PERSISTENT | NodeTrait.ORDERED | NodeTrait.INDEXED,
        "B-tree for disk-based storage",
        ["large datasets", "disk storage", "range queries"],
        "10-100x faster disk I/O",
        "medium",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.LSM_TREE: StrategyMetadata(
        NodeMode.LSM_TREE,
        NodeTrait.PERSISTENT | NodeTrait.STREAMING,
        "Log-structured merge tree for write-heavy workloads",
        ["write-heavy workloads", "append operations", "large datasets"],
        "100-1000x faster writes",
        "high",
        {"get": "O(log n)", "set": "O(1)", "delete": "O(1)"}
    ),
    
    NodeMode.PERSISTENT_TREE: StrategyMetadata(
        NodeMode.PERSISTENT_TREE,
        NodeTrait.PERSISTENT | NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Immutable functional tree with structural sharing",
        ["functional programming", "versioning", "concurrent access", "undo/redo"],
        "Lock-free concurrency, memory efficient",
        "medium",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.COW_TREE: StrategyMetadata(
        NodeMode.COW_TREE,
        NodeTrait.PERSISTENT | NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Copy-on-write tree with atomic snapshots",
        ["snapshots", "versioning", "crash consistency", "backup"],
        "Instant snapshots, atomic updates",
        "medium",
        {"get": "O(log n)", "set": "O(log n)", "snapshot": "O(1)"}
    ),
    
    NodeMode.SKIP_LIST: StrategyMetadata(
        NodeMode.SKIP_LIST,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Probabilistic data structure with O(log n) expected performance",
        ["probabilistic", "concurrent access", "simple implementation"],
        "Simple, fast, concurrent-friendly",
        "high",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.RED_BLACK_TREE: StrategyMetadata(
        NodeMode.RED_BLACK_TREE,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Self-balancing binary search tree with color properties",
        ["self-balancing", "guaranteed height", "industry standard"],
        "Guaranteed O(log n) height, widely used",
        "high",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.AVL_TREE: StrategyMetadata(
        NodeMode.AVL_TREE,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Strictly balanced binary search tree with height balance",
        ["strict balance", "height-based", "database optimization"],
        "More balanced than red-black trees",
        "high",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.TREAP: StrategyMetadata(
        NodeMode.TREAP,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Randomized balanced tree combining BST and heap properties",
        ["randomized", "heap property", "self-balancing"],
        "Randomized balancing, simple implementation",
        "medium",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.SPLAY_TREE: StrategyMetadata(
        NodeMode.SPLAY_TREE,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Self-adjusting binary search tree with amortized performance",
        ["self-adjusting", "cache-friendly", "recent access"],
        "Recently accessed elements moved to root",
        "medium",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.UNION_FIND: StrategyMetadata(
        NodeMode.UNION_FIND,
        NodeTrait.INDEXED,
        "Disjoint-set data structure for connectivity",
        ["connectivity queries", "graph algorithms", "component tracking"],
        "10-100x faster union/find",
        "low",
        {"find": "O(α(n))", "union": "O(α(n))"}
    ),
    
    NodeMode.SEGMENT_TREE: StrategyMetadata(
        NodeMode.SEGMENT_TREE,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Segment tree for range queries and updates",
        ["range queries", "range updates", "interval operations"],
        "10-50x faster range operations",
        "medium",
        {"query": "O(log n)", "update": "O(log n)"}
    ),
    
    NodeMode.ROARING_BITMAP: StrategyMetadata(
        NodeMode.ROARING_BITMAP,
        NodeTrait.COMPRESSED | NodeTrait.INDEXED,
        "Compressed bitmap for sparse sets",
        ["sparse sets", "boolean operations", "analytics"],
        "10-100x memory reduction for sparse data",
        "very low",
        {"contains": "O(1)", "add": "O(1)", "remove": "O(1)"}
    ),
    
    # NEW High-Performance Strategies
    NodeMode.ART: StrategyMetadata(
        NodeMode.ART,
        NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.PREFIX_TREE,
        "Adaptive Radix Tree for string keys",
        ["string keys", "prefix search", "memory efficiency"],
        "3-10x faster than B-trees for strings",
        "low",
        {"get": "O(k)", "set": "O(k)", "delete": "O(k)"}
    ),
    
    NodeMode.BW_TREE: StrategyMetadata(
        NodeMode.BW_TREE,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Lock-free B-tree with delta updates",
        ["concurrent access", "lock-free", "cache-optimized"],
        "Lock-free operations, high concurrency",
        "medium",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.HAMT: StrategyMetadata(
        NodeMode.HAMT,
        NodeTrait.INDEXED | NodeTrait.PERSISTENT,
        "Hash Array Mapped Trie with structural sharing",
        ["persistent data", "functional programming", "immutable"],
        "Structural sharing, memory efficient",
        "medium",
        {"get": "O(log32 n)", "set": "O(log32 n)", "delete": "O(log32 n)"}
    ),
    
    NodeMode.MASSTREE: StrategyMetadata(
        NodeMode.MASSTREE,
        NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.PREFIX_TREE,
        "B+ tree + trie hybrid for cache locality",
        ["cache-optimized", "variable keys", "high performance"],
        "Cache-friendly, fast key comparison",
        "medium",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.EXTENDIBLE_HASH: StrategyMetadata(
        NodeMode.EXTENDIBLE_HASH,
        NodeTrait.INDEXED,
        "Directory-based dynamic hash table",
        ["dynamic hashing", "no full rehash", "grows incrementally"],
        "Split buckets without full rehashing",
        "medium",
        {"get": "O(1)", "set": "O(1)", "delete": "O(1)"}
    ),
    
    NodeMode.LINEAR_HASH: StrategyMetadata(
        NodeMode.LINEAR_HASH,
        NodeTrait.INDEXED,
        "Linear dynamic hashing without directory",
        ["dynamic hashing", "no directory overhead", "gradual growth"],
        "Linear bucket splitting, no directory",
        "low",
        {"get": "O(1)", "set": "O(1)", "delete": "O(1)"}
    ),
    
    NodeMode.T_TREE: StrategyMetadata(
        NodeMode.T_TREE,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "Hybrid AVL tree + array nodes for in-memory",
        ["in-memory", "reduced pointers", "cache-friendly"],
        "Optimized for in-memory databases",
        "medium",
        {"get": "O(log n)", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.LEARNED_INDEX: StrategyMetadata(
        NodeMode.LEARNED_INDEX,
        NodeTrait.ORDERED | NodeTrait.INDEXED,
        "ML-based learned index (EXPERIMENTAL)",
        ["machine learning", "adaptive", "research"],
        "10-100x faster lookups (when fully implemented)",
        "medium",
        {"get": "O(1) amortized", "set": "O(log n)", "delete": "O(log n)"}
    ),
    
    NodeMode.DATA_INTERCHANGE_OPTIMIZED: StrategyMetadata(
        NodeMode.DATA_INTERCHANGE_OPTIMIZED,
        NodeTrait.INDEXED,
        "Ultra-lightweight hash map with COW, pooling, and hash caching",
        ["data interchange", "serialization", "format conversion", "copy-on-write"],
        "Optimized for data interchange patterns with minimal overhead",
        "very low",
        {"get": "O(1)", "set": "O(1)", "delete": "O(1)", "copy": "O(1) lazy"}
    ),
    
    # Advanced specialized structures
    NodeMode.VEB_TREE: StrategyMetadata(
        NodeMode.VEB_TREE,
        NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.FAST_INSERT,
        "van Emde Boas tree for O(log log U) integer operations",
        ["routing tables", "IP lookups", "small universe integers", "priority queues"],
        "Faster than BST for small universes: O(log log U) vs O(log n)",
        "high",
        {"get": "O(log log U)", "set": "O(log log U)", "delete": "O(log log U)", "min/max": "O(1)"}
    ),
    
    NodeMode.DAWG: StrategyMetadata(
        NodeMode.DAWG,
        NodeTrait.HIERARCHICAL | NodeTrait.INDEXED | NodeTrait.MEMORY_EFFICIENT | NodeTrait.PREFIX_TREE,
        "DAWG/DAFSA minimal automaton for string sets",
        ["dictionaries", "lexicons", "spell check", "autocomplete", "genomics"],
        "10-100x memory savings vs trie through suffix sharing",
        "very low",
        {"get": "O(k)", "insert": "O(k)", "prefix_query": "O(k+m)"}
    ),
    
    NodeMode.HOPSCOTCH_HASH: StrategyMetadata(
        NodeMode.HOPSCOTCH_HASH,
        NodeTrait.INDEXED | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE,
        "Hopscotch hashing with bounded neighborhood search",
        ["cache-friendly hash", "embedded systems", "high load factors", "predictable performance"],
        "Better cache behavior than cuckoo, supports >90% load",
        "medium",
        {"get": "O(H)", "set": "O(H)", "delete": "O(H)"}  # H=32 typical
    ),
    
    NodeMode.INTERVAL_TREE: StrategyMetadata(
        NodeMode.INTERVAL_TREE,
        NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.HIERARCHICAL,
        "Augmented tree for interval overlap queries",
        ["scheduling", "genomics", "collision detection", "time windows", "range caching"],
        "O(log n + k) overlap queries vs O(n) scan",
        "medium",
        {"insert": "O(log n)", "delete": "O(log n)", "overlaps": "O(log n + k)"}
    ),
    
    NodeMode.KD_TREE: StrategyMetadata(
        NodeMode.KD_TREE,
        NodeTrait.SPATIAL | NodeTrait.INDEXED | NodeTrait.HIERARCHICAL,
        "k-dimensional tree for multi-dimensional point queries",
        ["2D/3D points", "k-NN search", "spatial indexing", "graphics", "ML"],
        "O(log n) nearest neighbor for low dimensions",
        "medium",
        {"insert": "O(log n)", "search": "O(log n)", "knn": "O(log n)"}
    ),
    
    NodeMode.ROPE: StrategyMetadata(
        NodeMode.ROPE,
        NodeTrait.HIERARCHICAL | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE,
        "Binary tree for efficient text/string operations",
        ["text editors", "large documents", "undo/redo", "collaborative editing"],
        "O(log n) insert/delete vs O(n) for strings",
        "medium",
        {"index": "O(log n)", "concat": "O(log n)", "split": "O(log n)", "insert": "O(log n)"}
    ),
    
    NodeMode.CRDT_MAP: StrategyMetadata(
        NodeMode.CRDT_MAP,
        NodeTrait.INDEXED | NodeTrait.PERSISTENT | NodeTrait.STREAMING,
        "Conflict-free replicated map for distributed systems",
        ["distributed databases", "offline-first apps", "collaborative editing", "multi-master"],
        "Conflict-free merging with eventual consistency",
        "high",
        {"put": "O(1)", "get": "O(1)", "merge": "O(m)"}
    ),
    
    NodeMode.BLOOMIER_FILTER: StrategyMetadata(
        NodeMode.BLOOMIER_FILTER,
        NodeTrait.PROBABILISTIC | NodeTrait.MEMORY_EFFICIENT | NodeTrait.INDEXED,
        "Probabilistic key→value map with false positives",
        ["approximate caches", "distributed sketches", "memory-constrained", "spell check"],
        "10-100x memory savings vs hash map with controlled FP rate",
        "very low",
        {"get": "O(k)", "contains": "O(k)"}  # k = hash functions
    ),
}


# Edge strategy metadata
EDGE_STRATEGY_METADATA: Dict[EdgeMode, StrategyMetadata] = {
    EdgeMode.TREE_GRAPH_BASIC: StrategyMetadata(
        EdgeMode.TREE_GRAPH_BASIC,
        EdgeTrait.SPARSE,
        "Basic edge storage for tree+graph hybrid",
        ["general purpose", "lightweight graphs", "backward compatibility"],
        "balanced performance",
        "medium"
    ),
    
    EdgeMode.WEIGHTED_GRAPH: StrategyMetadata(
        EdgeMode.WEIGHTED_GRAPH,
        EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.SPARSE,
        "Graph with numerical edge weights for network algorithms",
        ["weighted edges", "network algorithms", "shortest path"],
        "Essential for network algorithms and routing",
        "high",
        {"add_edge": "O(1)", "get_edge": "O(1)", "delete_edge": "O(1)"}
    ),
    
    EdgeMode.ADJ_LIST: StrategyMetadata(
        EdgeMode.ADJ_LIST,
        EdgeTrait.SPARSE,
        "Adjacency list for sparse graphs",
        ["sparse graphs", "dynamic graphs", "memory efficiency"],
        "5-20x faster for sparse graphs",
        "low",
        {"add_edge": "O(1)", "remove_edge": "O(1)", "neighbors": "O(degree)"}
    ),
    
    EdgeMode.ADJ_MATRIX: StrategyMetadata(
        EdgeMode.ADJ_MATRIX,
        EdgeTrait.DENSE,
        "Adjacency matrix for dense graphs",
        ["dense graphs", "matrix operations", "edge queries"],
        "10-100x faster for dense graphs",
        "high",
        {"add_edge": "O(1)", "remove_edge": "O(1)", "neighbors": "O(n)"}
    ),
    
    EdgeMode.CSR: StrategyMetadata(
        EdgeMode.CSR,
        EdgeTrait.SPARSE | EdgeTrait.COMPRESSED,
        "Compressed Sparse Row format",
        ["sparse graphs", "matrix operations", "memory efficiency"],
        "2-5x memory reduction",
        "low",
        {"add_edge": "O(m)", "remove_edge": "O(m)", "neighbors": "O(degree)"}
    ),
    
    EdgeMode.BLOCK_ADJ_MATRIX: StrategyMetadata(
        EdgeMode.BLOCK_ADJ_MATRIX,
        EdgeTrait.DENSE | EdgeTrait.CACHE_FRIENDLY,
        "Cache-friendly block adjacency matrix",
        ["dense graphs", "cache optimization", "matrix algorithms"],
        "5-20x faster matrix operations",
        "high",
        {"add_edge": "O(1)", "remove_edge": "O(1)", "neighbors": "O(n)"}
    ),
    
    EdgeMode.R_TREE: StrategyMetadata(
        EdgeMode.R_TREE,
        EdgeTrait.SPATIAL,
        "R-tree for spatial indexing",
        ["spatial queries", "geographic data", "2D/3D graphs"],
        "10-100x faster spatial queries",
        "medium",
        {"add_edge": "O(log n)", "remove_edge": "O(log n)", "spatial_query": "O(log n)"}
    ),
    
    EdgeMode.TEMPORAL_EDGESET: StrategyMetadata(
        EdgeMode.TEMPORAL_EDGESET,
        EdgeTrait.TEMPORAL | EdgeTrait.DIRECTED,
        "Time-aware edge storage",
        ["temporal graphs", "time-series data", "evolution tracking"],
        "5-10x faster temporal queries",
        "medium",
        {"add_edge": "O(log n)", "remove_edge": "O(log n)", "temporal_query": "O(log n)"}
    ),
    
    EdgeMode.HYPEREDGE_SET: StrategyMetadata(
        EdgeMode.HYPEREDGE_SET,
        EdgeTrait.HYPER | EdgeTrait.MULTI,
        "Hypergraph edge storage",
        ["hypergraphs", "multi-vertex edges", "complex relationships"],
        "2-5x faster hyperedge operations",
        "medium",
        {"add_hyperedge": "O(1)", "remove_hyperedge": "O(1)", "incident_edges": "O(degree)"}
    ),
    
    # NEW Graph Representation Strategies
    EdgeMode.INCIDENCE_MATRIX: StrategyMetadata(
        EdgeMode.INCIDENCE_MATRIX,
        EdgeTrait.SPARSE | EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED,
        "Incidence matrix for edge-centric queries",
        ["edge properties", "edge-centric", "graph theory"],
        "Optimal for edge-focused operations",
        "medium",
        {"add_edge": "O(1)", "remove_edge": "O(1)", "edge_properties": "O(1)"}
    ),
    
    EdgeMode.EDGE_LIST: StrategyMetadata(
        EdgeMode.EDGE_LIST,
        EdgeTrait.SPARSE | EdgeTrait.DIRECTED,
        "Simple edge list format",
        ["minimal storage", "edge list files", "simple graphs"],
        "Minimal overhead, simple format",
        "low",
        {"add_edge": "O(1)", "remove_edge": "O(n)", "neighbors": "O(m)"}
    ),
    
    EdgeMode.COMPRESSED_GRAPH: StrategyMetadata(
        EdgeMode.COMPRESSED_GRAPH,
        EdgeTrait.SPARSE | EdgeTrait.COMPRESSED,
        "WebGraph/LLP compression for power-law graphs",
        ["web graphs", "social networks", "high compression"],
        "100x compression for power-law graphs",
        "very low",
        {"add_edge": "O(1)", "neighbors": "O(degree)", "compression": "100x"}
    ),
    
    # Advanced graph structures
    EdgeMode.K2_TREE: StrategyMetadata(
        EdgeMode.K2_TREE,
        EdgeTrait.SPARSE | EdgeTrait.COMPRESSED,
        "k²-tree ultra-compact adjacency with quadtree compression",
        ["web graphs", "social networks", "billions of edges", "memory-constrained"],
        "2-10 bits per edge for power-law graphs",
        "very low",
        {"add_edge": "O(log n)", "has_edge": "O(log n)", "neighbors": "O(log n + degree)"}
    ),
    
    EdgeMode.BV_GRAPH: StrategyMetadata(
        EdgeMode.BV_GRAPH,
        EdgeTrait.SPARSE | EdgeTrait.COMPRESSED,
        "BVGraph full WebGraph with Elias coding and reference lists",
        ["web crawls", "social networks", "billion-edge graphs", "graph archives"],
        "100-1000x compression with fast decompression",
        "very low",
        {"add_edge": "O(1) batch", "neighbors": "O(degree)", "compression": "100-1000x"}
    ),
    
    EdgeMode.HNSW: StrategyMetadata(
        EdgeMode.HNSW,
        EdgeTrait.SPARSE | EdgeTrait.MULTI,
        "Hierarchical Navigable Small World for ANN search",
        ["vector search", "embeddings", "recommendations", "semantic search", "image retrieval"],
        "O(log n) approximate nearest neighbor search",
        "high",
        {"insert": "O(M log n)", "search_knn": "O(ef log n)", "recall": ">95%"}
    ),
    
    EdgeMode.EULER_TOUR: StrategyMetadata(
        EdgeMode.EULER_TOUR,
        EdgeTrait.DIRECTED | EdgeTrait.SPARSE,
        "Euler tour trees for dynamic forest connectivity",
        ["dynamic networks", "MST with changes", "network reliability", "forest decomposition"],
        "O(log n) link/cut operations for dynamic connectivity",
        "medium",
        {"link": "O(log n)", "cut": "O(log n)", "connected": "O(log n)"}
    ),
    
    EdgeMode.LINK_CUT: StrategyMetadata(
        EdgeMode.LINK_CUT,
        EdgeTrait.DIRECTED | EdgeTrait.SPARSE,
        "Link-cut trees with path queries and aggregates",
        ["dynamic MST", "network flows", "path aggregates", "dynamic matching"],
        "O(log n) amortized for link/cut/path operations",
        "medium",
        {"link": "O(log n)", "cut": "O(log n)", "path_sum": "O(log n)"}
    ),
    
    EdgeMode.HOP2_LABELS: StrategyMetadata(
        EdgeMode.HOP2_LABELS,
        EdgeTrait.SPARSE | EdgeTrait.WEIGHTED,
        "2-hop labeling for constant-time reachability queries",
        ["road networks", "social graphs", "navigation", "read-heavy workloads"],
        "O(1) to O(log n) reachability after O(n²m) preprocessing",
        "medium",
        {"reachability": "O(|L(u)| + |L(v)|)", "distance": "O(|L(u)| × |L(v)|)"}
    ),
    
    EdgeMode.GRAPHBLAS: StrategyMetadata(
        EdgeMode.GRAPHBLAS,
        EdgeTrait.SPARSE | EdgeTrait.DENSE | EdgeTrait.WEIGHTED,
        "GraphBLAS semiring-based matrix operations",
        ["graph analytics", "linear algebra", "GPU acceleration", "algorithm composition"],
        "Express graph algorithms as matrix ops, enable hardware acceleration",
        "medium",
        {"mxm": "O(nnz(A) + nnz(B))", "element_wise": "O(nnz)"}
    ),
    
    EdgeMode.ROARING_ADJ: StrategyMetadata(
        EdgeMode.ROARING_ADJ,
        EdgeTrait.SPARSE | EdgeTrait.COMPRESSED,
        "Roaring bitmap per-vertex adjacency for fast set operations",
        ["BFS/DFS", "frontier operations", "graph traversals", "label propagation"],
        "Ultra-fast frontier unions/intersections in microseconds",
        "low",
        {"add_edge": "O(1)", "has_edge": "O(1)", "union": "O(min(n1, n2))"}
    ),
    
    EdgeMode.MULTIPLEX: StrategyMetadata(
        EdgeMode.MULTIPLEX,
        EdgeTrait.MULTI | EdgeTrait.DIRECTED,
        "Multi-layer graphs with per-layer semantics",
        ["social networks", "transportation", "multi-relationship", "communication networks"],
        "Natural modeling of multiple relationship types",
        "high",
        {"add_edge": "O(1)", "neighbors_layer": "O(degree)", "cross_layer": "O(L × degree)"}
    ),
    
    EdgeMode.BITEMPORAL: StrategyMetadata(
        EdgeMode.BITEMPORAL,
        EdgeTrait.TEMPORAL | EdgeTrait.DIRECTED,
        "Bitemporal edges with valid-time and transaction-time",
        ["financial systems", "compliance", "audit trails", "healthcare", "time-travel queries"],
        "Complete audit trail with as-of queries and corrections",
        "very high",
        {"add_edge": "O(1)", "as_of_query": "O(n)", "temporal_query": "O(log n + k)"}
    ),
}


# ============================================================================
# A+ USABILITY PRESET SYSTEM  
# ============================================================================

class PresetConfig:
    """Configuration for a usability preset."""
    
    def __init__(self, 
                 node_mode: NodeMode,
                 edge_mode: Optional[EdgeMode] = None,
                 node_traits: NodeTrait = NodeTrait.NONE,
                 edge_traits: EdgeTrait = EdgeTrait.NONE,
                 description: str = "",
                 performance_class: str = "balanced",
                 disabled_features: List[str] = None,
                 internal_config: Dict[str, Any] = None):
        self.node_mode = node_mode
        self.edge_mode = edge_mode
        self.node_traits = node_traits
        self.edge_traits = edge_traits
        self.description = description
        self.performance_class = performance_class
        self.disabled_features = disabled_features or []
        self.internal_config = internal_config or {}


# === A+ USABILITY PRESETS ===
USABILITY_PRESETS: Dict[str, PresetConfig] = {
    # === DATA INTERCHANGE OPTIMIZATION ===
    'DATA_INTERCHANGE_OPTIMIZED': PresetConfig(
        node_mode=NodeMode.HASH_MAP,
        edge_mode=None,  # No edge support for maximum efficiency
        node_traits=NodeTrait.INDEXED,
        edge_traits=EdgeTrait.NONE,
        description='Ultra-lightweight preset optimized for data interchange patterns',
        performance_class='maximum_efficiency',
        disabled_features=[
            'graph_operations', 'edge_storage', 'spatial_indexing',
            'temporal_tracking', 'hypergraph_support', 'advanced_traversal'
        ],
        internal_config={
            'enable_cow': True,           # Copy-on-write for data interchange
            'enable_pooling': True,       # Object pooling support
            'enable_hash_caching': True,  # Structural hash caching
            'minimal_metadata': True,     # Reduce memory footprint
            'slots_optimization': True,   # __slots__ for memory
            'fast_creation': True,        # Factory pattern optimization
            'lazy_loading': False,        # Eager loading for predictability
            'memory_profile': 'ultra_minimal'
        }
    ),
    
    # === GENERAL PURPOSE ===
    'DEFAULT': PresetConfig(
        node_mode=NodeMode.AUTO,
        edge_mode=EdgeMode.AUTO,
        description='Smart auto-selection for general use',
        performance_class='balanced'
    ),
    
    'PURE_TREE': PresetConfig(
        node_mode=NodeMode.HASH_MAP,
        edge_mode=None,  # Tree-only, no graph
        node_traits=NodeTrait.INDEXED,
        description='Pure tree operations, maximum performance',
        performance_class='high_performance',
        disabled_features=['graph_operations', 'edge_storage']
    ),
    
    'TREE_GRAPH_MIX': PresetConfig(
        node_mode=NodeMode.TREE_GRAPH_HYBRID,
        edge_mode=EdgeMode.TREE_GRAPH_BASIC,
        node_traits=NodeTrait.HIERARCHICAL,
        edge_traits=EdgeTrait.SPARSE,
        description='Balanced tree + graph capabilities (replaces old legacy)',
        performance_class='balanced'
    ),
    
    # === PERFORMANCE-ORIENTED ===
    'FAST_LOOKUP': PresetConfig(
        node_mode=NodeMode.HASH_MAP,
        edge_mode=EdgeMode.ADJ_LIST,
        node_traits=NodeTrait.INDEXED,
        edge_traits=EdgeTrait.SPARSE,
        description='Optimized for frequent key-based access',
        performance_class='high_performance'
    ),
    
    'PERFORMANCE_OPTIMIZED': PresetConfig(
        node_mode=NodeMode.HASH_MAP,
        edge_mode=EdgeMode.ADJ_LIST,
        node_traits=NodeTrait.INDEXED,
        edge_traits=EdgeTrait.SPARSE,
        description='General performance optimization for most use cases',
        performance_class='high_performance'
    ),
    
    'MEMORY_EFFICIENT': PresetConfig(
        node_mode=NodeMode.HASH_MAP,
        edge_mode=EdgeMode.CSR,
        node_traits=NodeTrait.INDEXED,
        edge_traits=EdgeTrait.SPARSE,
        description='Minimizes memory usage',
        performance_class='memory_optimized'
    ),
    
    # === DOMAIN-SPECIFIC ===
    'SOCIAL_GRAPH': PresetConfig(
        node_mode=NodeMode.TREE_GRAPH_HYBRID,
        edge_mode=EdgeMode.ADJ_LIST,
        node_traits=NodeTrait.INDEXED,
        edge_traits=EdgeTrait.SPARSE | EdgeTrait.MULTI,
        description='Optimized for social networks and relationships',
        performance_class='graph_optimized'
    ),
    
    'ANALYTICS': PresetConfig(
        node_mode=NodeMode.ORDERED_MAP_BALANCED,
        edge_mode=EdgeMode.EDGE_PROPERTY_STORE,
        node_traits=NodeTrait.ORDERED | NodeTrait.INDEXED,
        edge_traits=EdgeTrait.COLUMNAR,
        description='Column-oriented for data analysis',
        performance_class='analytics_optimized'
    ),
    
    'SEARCH_ENGINE': PresetConfig(
        node_mode=NodeMode.TRIE,
        edge_mode=EdgeMode.ADJ_LIST,
        node_traits=NodeTrait.HIERARCHICAL | NodeTrait.INDEXED,
        edge_traits=EdgeTrait.SPARSE,
        description='Optimized for text search and autocomplete',
        performance_class='search_optimized'
    ),
    
    'TIME_SERIES': PresetConfig(
        node_mode=NodeMode.ORDERED_MAP,
        edge_mode=EdgeMode.TEMPORAL_EDGESET,
        node_traits=NodeTrait.ORDERED | NodeTrait.STREAMING,
        edge_traits=EdgeTrait.TEMPORAL,
        description='Optimized for time-ordered data',
        performance_class='temporal_optimized'
    ),
    
    'SPATIAL_MAP': PresetConfig(
        node_mode=NodeMode.HASH_MAP,
        edge_mode=EdgeMode.R_TREE,
        node_traits=NodeTrait.INDEXED,
        edge_traits=EdgeTrait.SPATIAL,
        description='Optimized for geographic/spatial data',
        performance_class='spatial_optimized'
    ),
    
    'ML_DATASET': PresetConfig(
        node_mode=NodeMode.ARRAY_LIST,
        edge_mode=EdgeMode.NEURAL_GRAPH,
        node_traits=NodeTrait.STREAMING | NodeTrait.INDEXED,
        edge_traits=EdgeTrait.SPARSE,
        description='Optimized for machine learning workflows',
        performance_class='ml_optimized'
    )
}


def get_preset(name: str) -> PresetConfig:
    """Get preset configuration by name."""
    if name not in USABILITY_PRESETS:
        available = ', '.join(USABILITY_PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")
    return USABILITY_PRESETS[name]


def list_presets() -> List[str]:
    """Get list of available preset names."""
    return list(USABILITY_PRESETS.keys())


def get_presets_by_performance_class(performance_class: str) -> List[str]:
    """Get presets by performance class."""
    return [name for name, config in USABILITY_PRESETS.items() 
            if config.performance_class == performance_class]
