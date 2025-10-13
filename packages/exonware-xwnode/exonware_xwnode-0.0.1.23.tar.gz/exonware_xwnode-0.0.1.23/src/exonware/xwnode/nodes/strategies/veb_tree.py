"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/veb_tree.py

van Emde Boas Tree Node Strategy Implementation

This module implements the VEB_TREE strategy for O(log log U) operations
on fixed-universe integer keys.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
Generation Date: 12-Oct-2025
"""

import math
from typing import Any, Iterator, List, Dict, Optional, Set
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeError, XWNodeValueError


class VebNode:
    """
    Node in the van Emde Boas tree structure.
    
    WHY recursive structure:
    - Enables O(log log U) time complexity through universe splitting
    - Each cluster handles √U elements recursively
    - Summary structure provides constant-time minimum/maximum
    """
    
    def __init__(self, universe_size: int):
        """
        Initialize vEB node.
        
        Args:
            universe_size: Size of universe (must be power of 2)
        """
        self.universe_size = universe_size
        self.min = None
        self.max = None
        
        # Base case: universe size 2
        if universe_size <= 2:
            self.summary = None
            self.clusters = None
        else:
            # Recursive case - for power of 2, use exact sqrt
            # For universe_size = 2^k, sqrt = 2^(k/2)
            lower_sqrt = 1 << (universe_size.bit_length() // 2)  # Power of 2 sqrt
            upper_sqrt = (universe_size + lower_sqrt - 1) // lower_sqrt  # Ceiling division
            
            # Summary structure for non-empty clusters
            self.summary = VebNode(upper_sqrt)
            
            # Array of cluster nodes (one per possible cluster)
            self.clusters = [None] * upper_sqrt
    
    def is_empty(self) -> bool:
        """Check if tree is empty."""
        return self.min is None
    
    def high(self, x: int) -> int:
        """Get high-order bits (cluster index)."""
        lower_sqrt = 1 << (self.universe_size.bit_length() // 2)
        return x // lower_sqrt
    
    def low(self, x: int) -> int:
        """Get low-order bits (position in cluster)."""
        lower_sqrt = 1 << (self.universe_size.bit_length() // 2)
        return x % lower_sqrt
    
    def index(self, high: int, low: int) -> int:
        """Combine high and low to get original index."""
        lower_sqrt = 1 << (self.universe_size.bit_length() // 2)
        return high * lower_sqrt + low


class VebTreeStrategy(ANodeTreeStrategy):
    """
    van Emde Boas Tree strategy for O(log log U) integer operations.
    
    WHY van Emde Boas Tree:
    - Asymptotically faster than balanced BSTs: O(log log U) vs O(log n)
    - Predictable performance for fixed-universe integers
    - Excellent for routing tables, IP address lookups, priority queues
    - Constant-time min/max queries through summary caching
    - Ideal for small-universe scenarios (16-bit, 32-bit integers)
    
    WHY this implementation:
    - Recursive cluster decomposition enables logarithmic speedup
    - Min/max caching at each level for O(1) extreme queries
    - Summary structure enables fast successor/predecessor
    - Lazy cluster initialization saves memory for sparse data
    - Direct indexing eliminates pointer indirection overhead
    
    Time Complexity:
    - Insert: O(log log U) where U is universe size
    - Delete: O(log log U)
    - Search: O(log log U)
    - Min/Max: O(1) through caching
    - Successor: O(log log U)
    - Predecessor: O(log log U)
    
    Space Complexity: O(U) worst case, O(n) for n elements with lazy allocation
    
    Trade-offs:
    - Advantage: Faster than BST for small universes (log log U << log n)
    - Advantage: Constant-time min/max queries
    - Advantage: Excellent for dense integer keys
    - Limitation: High space overhead O(U) for sparse data
    - Limitation: Universe size must be power of 2
    - Limitation: Integer keys only (no strings, floats)
    - Compared to HashMap: Better ordered operations, worse space
    - Compared to B-Tree: Faster for small universes, worse for large
    
    Best for:
    - Routing tables with IP addresses (32-bit universe)
    - Priority queues with small integer priorities
    - Network switches and routers
    - Small-universe integer key-value stores
    - Real-time systems requiring predictable performance
    - Dense integer key distributions
    
    Not recommended for:
    - Large universes (2^64) - excessive memory
    - Sparse data (few elements, large universe)
    - String or floating-point keys
    - Dynamic universe size requirements
    - Memory-constrained environments
    - Non-integer key types
    
    Following eXonware Priorities:
    1. Security: Validates universe bounds, prevents overflow attacks
    2. Usability: Simple API for integer operations, clear errors
    3. Maintainability: Clean recursive structure, well-documented
    4. Performance: O(log log U) operations, optimal for use case
    5. Extensibility: Easy to add weighted variants or range queries
    
    Industry Best Practices:
    - Follows van Emde Boas original paper (1975)
    - Implements lazy cluster allocation for memory efficiency
    - Uses power-of-2 universe sizes for optimal splitting
    - Provides min/max caching for constant-time queries
    - Supports both membership and key-value storage
    """
    
    # Tree node type for classification
    STRATEGY_TYPE: NodeType = NodeType.TREE
    
    def __init__(self, mode: NodeMode = NodeMode.VEB_TREE, 
                 traits: NodeTrait = NodeTrait.NONE, 
                 universe_size: int = 65536, **options):
        """
        Initialize van Emde Boas tree strategy.
        
        Args:
            mode: Node mode (VEB_TREE)
            traits: Node traits
            universe_size: Maximum key value (must be power of 2)
            **options: Additional options
            
        Raises:
            XWNodeValueError: If universe_size is not power of 2
        """
        # Validate universe size is power of 2
        if universe_size <= 0 or (universe_size & (universe_size - 1)) != 0:
            raise XWNodeValueError(
                f"Universe size must be a power of 2, got {universe_size}"
            )
        
        super().__init__(mode, traits, **options)
        
        self.universe_size = universe_size
        self._root = VebNode(universe_size)
        self._values: Dict[int, Any] = {}  # Store actual values
        self._size = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get supported traits."""
        return NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE
    
    # ============================================================================
    # CORE VEB OPERATIONS
    # ============================================================================
    
    def _veb_insert(self, node: VebNode, x: int) -> None:
        """
        Insert element into vEB tree.
        
        Args:
            node: Current vEB node
            x: Integer key to insert
        """
        # Security: Validate bounds
        if x < 0 or x >= node.universe_size:
            raise XWNodeValueError(
                f"Key {x} out of bounds [0, {node.universe_size})"
            )
        
        # Empty tree case
        if node.is_empty():
            node.min = node.max = x
            return
        
        # Ensure x is not already min or max
        if x == node.min or x == node.max:
            return  # Already present
        
        # Swap to ensure min is minimum
        if x < node.min:
            x, node.min = node.min, x
        
        # Base case
        if node.universe_size == 2:
            node.max = max(x, node.max) if node.max is not None else x
            return
        
        # Recursive case
        high = node.high(x)
        low = node.low(x)
        
        # Lazy cluster creation
        if node.clusters[high] is None:
            lower_sqrt = 1 << (node.universe_size.bit_length() // 2)
            node.clusters[high] = VebNode(lower_sqrt)
        
        # If cluster is empty, update summary
        if node.clusters[high].is_empty():
            self._veb_insert(node.summary, high)
        
        # Insert into cluster
        self._veb_insert(node.clusters[high], low)
        
        # Update max if necessary
        if x > node.max:
            node.max = x
    
    def _veb_delete(self, node: VebNode, x: int) -> bool:
        """
        Delete element from vEB tree.
        
        Args:
            node: Current vEB node
            x: Integer key to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Security: Validate bounds
        if x < 0 or x >= node.universe_size:
            return False
        
        # Element not in tree
        if node.is_empty() or x < node.min or x > node.max:
            return False
        
        # Single element case
        if node.min == node.max:
            if x == node.min:
                node.min = node.max = None
                return True
            return False
        
        # Base case: universe size 2
        if node.universe_size == 2:
            if x == 0:
                node.min = 1
            else:
                node.max = 0
            return True
        
        # Recursive case
        # If deleting min, replace with successor
        if x == node.min:
            first_cluster = node.summary.min
            if first_cluster is None:
                # No other elements
                node.min = node.max
                return True
            
            x = node.index(first_cluster, node.clusters[first_cluster].min)
            node.min = x
        
        # Delete from appropriate cluster
        high = node.high(x)
        low = node.low(x)
        
        if node.clusters[high] is None:
            return False
        
        deleted = self._veb_delete(node.clusters[high], low)
        
        if not deleted:
            return False
        
        # Update summary if cluster becomes empty
        if node.clusters[high].is_empty():
            self._veb_delete(node.summary, high)
            
            # Update max if we deleted it
            if x == node.max:
                if node.summary.is_empty():
                    node.max = node.min
                else:
                    max_cluster = node.summary.max
                    node.max = node.index(max_cluster, node.clusters[max_cluster].max)
        elif x == node.max:
            # Update max within same cluster
            node.max = node.index(high, node.clusters[high].max)
        
        return True
    
    def _veb_member(self, node: VebNode, x: int) -> bool:
        """
        Check membership in vEB tree.
        
        Args:
            node: Current vEB node
            x: Integer key to check
            
        Returns:
            True if present, False otherwise
        """
        # Security: Validate bounds
        if x < 0 or x >= node.universe_size:
            return False
        
        # Check cached min/max
        if x == node.min or x == node.max:
            return True
        
        # Empty or out of range
        if node.is_empty() or x < node.min or x > node.max:
            return False
        
        # Base case
        if node.universe_size == 2:
            return False
        
        # Recursive case
        high = node.high(x)
        low = node.low(x)
        
        if node.clusters[high] is None:
            return False
        
        return self._veb_member(node.clusters[high], low)
    
    def _veb_successor(self, node: VebNode, x: int) -> Optional[int]:
        """
        Find successor of x (smallest element > x).
        
        Args:
            node: Current vEB node
            x: Integer key
            
        Returns:
            Successor key or None if no successor exists
        """
        # Security: Validate bounds
        if x < 0 or x >= node.universe_size:
            return None
        
        # Base case
        if node.universe_size == 2:
            if x == 0 and node.max == 1:
                return 1
            return None
        
        # If x < min, min is successor
        if not node.is_empty() and x < node.min:
            return node.min
        
        # Check within same cluster
        high = node.high(x)
        low = node.low(x)
        
        if node.clusters[high] is not None and not node.clusters[high].is_empty():
            if low < node.clusters[high].max:
                offset = self._veb_successor(node.clusters[high], low)
                if offset is not None:
                    return node.index(high, offset)
        
        # Find next non-empty cluster
        succ_cluster = self._veb_successor(node.summary, high)
        if succ_cluster is None:
            return None
        
        if node.clusters[succ_cluster] is None:
            return None
        
        offset = node.clusters[succ_cluster].min
        return node.index(succ_cluster, offset)
    
    def _veb_predecessor(self, node: VebNode, x: int) -> Optional[int]:
        """
        Find predecessor of x (largest element < x).
        
        Args:
            node: Current vEB node
            x: Integer key
            
        Returns:
            Predecessor key or None if no predecessor exists
        """
        # Security: Validate bounds
        if x < 0 or x >= node.universe_size:
            return None
        
        # Base case
        if node.universe_size == 2:
            if x == 1 and node.min == 0:
                return 0
            return None
        
        # If x > max, max is predecessor
        if not node.is_empty() and x > node.max:
            return node.max
        
        # Check within same cluster
        high = node.high(x)
        low = node.low(x)
        
        if node.clusters[high] is not None and not node.clusters[high].is_empty():
            if low > node.clusters[high].min:
                offset = self._veb_predecessor(node.clusters[high], low)
                if offset is not None:
                    return node.index(high, offset)
        
        # Find previous non-empty cluster
        pred_cluster = self._veb_predecessor(node.summary, high)
        if pred_cluster is None:
            # Check if min is predecessor
            if not node.is_empty() and x > node.min:
                return node.min
            return None
        
        if node.clusters[pred_cluster] is None:
            return None
        
        offset = node.clusters[pred_cluster].max
        return node.index(pred_cluster, offset)
    
    # ============================================================================
    # STRATEGY INTERFACE IMPLEMENTATION
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """
        Store key-value pair.
        
        Args:
            key: Integer key (0 to universe_size-1)
            value: Associated value
            
        Raises:
            XWNodeValueError: If key is not an integer or out of bounds
        """
        # Security: Type validation
        if not isinstance(key, int):
            raise XWNodeValueError(
                f"vEB tree requires integer keys, got {type(key).__name__}"
            )
        
        # Security: Bounds validation
        if key < 0 or key >= self.universe_size:
            raise XWNodeValueError(
                f"Key {key} out of universe bounds [0, {self.universe_size})"
            )
        
        # Insert into vEB structure
        was_present = self._veb_member(self._root, key)
        self._veb_insert(self._root, key)
        
        # Store value
        self._values[key] = value
        
        if not was_present:
            self._size += 1
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Retrieve value by key.
        
        Args:
            key: Integer key
            default: Default value if not found
            
        Returns:
            Value or default
        """
        # Type check
        if not isinstance(key, int):
            return default
        
        # Bounds check
        if key < 0 or key >= self.universe_size:
            return default
        
        # Check membership
        if not self._veb_member(self._root, key):
            return default
        
        return self._values.get(key, default)
    
    def has(self, key: Any) -> bool:
        """
        Check if key exists.
        
        Args:
            key: Integer key
            
        Returns:
            True if exists, False otherwise
        """
        if not isinstance(key, int):
            return False
        
        if key < 0 or key >= self.universe_size:
            return False
        
        return self._veb_member(self._root, key)
    
    def delete(self, key: Any) -> bool:
        """
        Remove key-value pair.
        
        Args:
            key: Integer key
            
        Returns:
            True if deleted, False if not found
        """
        if not isinstance(key, int):
            return False
        
        if key < 0 or key >= self.universe_size:
            return False
        
        # Delete from vEB structure
        deleted = self._veb_delete(self._root, key)
        
        if deleted:
            if key in self._values:
                del self._values[key]
            self._size -= 1
        
        return deleted
    
    def keys(self) -> Iterator[Any]:
        """
        Get iterator over all keys in sorted order.
        
        Returns:
            Iterator of keys
        """
        if self._root.is_empty():
            return
        
        # Start with minimum
        current = self._root.min
        while current is not None:
            yield current
            current = self._veb_successor(self._root, current)
    
    def values(self) -> Iterator[Any]:
        """
        Get iterator over all values in key-sorted order.
        
        Returns:
            Iterator of values
        """
        for key in self.keys():
            yield self._values.get(key)
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """
        Get iterator over all key-value pairs in sorted order.
        
        Returns:
            Iterator of (key, value) tuples
        """
        for key in self.keys():
            yield (key, self._values.get(key))
    
    def __len__(self) -> int:
        """Get number of elements."""
        return self._size
    
    def to_native(self) -> Any:
        """
        Convert to native Python dict.
        
        Returns:
            Dictionary representation
        """
        return dict(self.items())
    
    # ============================================================================
    # VEB-SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_min(self) -> Optional[int]:
        """
        Get minimum key in O(1) time.
        
        Returns:
            Minimum key or None if empty
        """
        return self._root.min
    
    def get_max(self) -> Optional[int]:
        """
        Get maximum key in O(1) time.
        
        Returns:
            Maximum key or None if empty
        """
        return self._root.max
    
    def successor(self, key: int) -> Optional[int]:
        """
        Find successor of key (smallest key > given key).
        
        Args:
            key: Integer key
            
        Returns:
            Successor key or None
            
        Raises:
            XWNodeValueError: If key is invalid
        """
        if not isinstance(key, int):
            raise XWNodeValueError(f"vEB tree requires integer keys")
        
        if key < 0 or key >= self.universe_size:
            raise XWNodeValueError(
                f"Key {key} out of universe bounds [0, {self.universe_size})"
            )
        
        return self._veb_successor(self._root, key)
    
    def predecessor(self, key: int) -> Optional[int]:
        """
        Find predecessor of key (largest key < given key).
        
        Args:
            key: Integer key
            
        Returns:
            Predecessor key or None
            
        Raises:
            XWNodeValueError: If key is invalid
        """
        if not isinstance(key, int):
            raise XWNodeValueError(f"vEB tree requires integer keys")
        
        if key < 0 or key >= self.universe_size:
            raise XWNodeValueError(
                f"Key {key} out of universe bounds [0, {self.universe_size})"
            )
        
        return self._veb_predecessor(self._root, key)
    
    def range_query(self, low: int, high: int) -> List[tuple[int, Any]]:
        """
        Find all keys in range [low, high].
        
        Args:
            low: Lower bound (inclusive)
            high: Upper bound (inclusive)
            
        Returns:
            List of (key, value) pairs in range
            
        Raises:
            XWNodeValueError: If bounds are invalid
        """
        # Security: Validate inputs
        if not isinstance(low, int) or not isinstance(high, int):
            raise XWNodeValueError("Range bounds must be integers")
        
        if low < 0 or high >= self.universe_size or low > high:
            raise XWNodeValueError(
                f"Invalid range [{low}, {high}] for universe [0, {self.universe_size})"
            )
        
        result = []
        
        # Find first key >= low
        if self._veb_member(self._root, low):
            current = low
        else:
            current = self._veb_successor(self._root, low)
        
        # Collect all keys up to high
        while current is not None and current <= high:
            result.append((current, self._values.get(current)))
            current = self._veb_successor(self._root, current)
        
        return result
    
    # ============================================================================
    # PERFORMANCE METHODS
    # ============================================================================
    
    def get_depth(self) -> int:
        """
        Get tree depth.
        
        Returns:
            Depth of recursion (log log U)
        """
        depth = 0
        u = self.universe_size
        while u > 2:
            u = int(math.sqrt(u))
            depth += 1
        return depth
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Estimate memory usage.
        
        Returns:
            Memory usage statistics
        """
        def count_nodes(node: VebNode) -> int:
            """Recursively count allocated nodes."""
            if node is None:
                return 0
            
            count = 1
            if node.summary is not None:
                count += count_nodes(node.summary)
            
            if node.clusters is not None:
                for cluster in node.clusters:
                    if cluster is not None:
                        count += count_nodes(cluster)
            
            return count
        
        node_count = count_nodes(self._root)
        
        return {
            'allocated_nodes': node_count,
            'universe_size': self.universe_size,
            'stored_values': len(self._values),
            'depth': self.get_depth(),
            'memory_efficiency': len(self._values) / max(node_count, 1)
        }
    
    # ============================================================================
    # ADDITIONAL HELPER METHODS
    # ============================================================================
    
    def clear(self) -> None:
        """Clear all elements."""
        self._root = VebNode(self.universe_size)
        self._values.clear()
        self._size = 0
    
    def is_empty(self) -> bool:
        """Check if tree is empty."""
        return self._root.is_empty()
    
    def size(self) -> int:
        """Get number of elements."""
        return self._size
    
    def get_mode(self) -> NodeMode:
        """Get strategy mode."""
        return self.mode
    
    def get_traits(self) -> NodeTrait:
        """Get strategy traits."""
        return self.traits
    
    # ============================================================================
    # COMPATIBILITY METHODS
    # ============================================================================
    
    def find(self, key: Any) -> Optional[Any]:
        """
        Find value by key (alias for get).
        
        Args:
            key: Integer key
            
        Returns:
            Value or None
        """
        return self.get(key)
    
    def insert(self, key: Any, value: Any = None) -> None:
        """
        Insert key-value pair (alias for put).
        
        Args:
            key: Integer key
            value: Associated value
        """
        self.put(key, value)
    
    def __str__(self) -> str:
        """String representation."""
        return f"VebTreeStrategy(universe={self.universe_size}, size={self._size}, depth={self.get_depth()})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"VebTreeStrategy(mode={self.mode.name}, universe={self.universe_size}, "
                f"size={self._size}, traits={self.traits})")
    
    # ============================================================================
    # FACTORY METHOD
    # ============================================================================
    
    @classmethod
    def create_from_data(cls, data: Any, universe_size: int = 65536) -> 'VebTreeStrategy':
        """
        Create vEB tree from data.
        
        Args:
            data: Dictionary with integer keys
            universe_size: Maximum key value
            
        Returns:
            New VebTreeStrategy instance
            
        Raises:
            XWNodeValueError: If data contains non-integer keys
        """
        instance = cls(universe_size=universe_size)
        
        if isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(key, int):
                    raise XWNodeValueError(
                        f"vEB tree requires integer keys, found {type(key).__name__}"
                    )
                instance.put(key, value)
        elif isinstance(data, (list, tuple)):
            for i, value in enumerate(data):
                instance.put(i, value)
        else:
            # Store scalar as single element
            instance.put(0, data)
        
        return instance

