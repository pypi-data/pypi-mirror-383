"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/node_hamt.py

HAMT (Hash Array Mapped Trie) Node Strategy Implementation

This module implements the HAMT strategy for persistent data structures
with structural sharing and efficient immutable operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.25
Generation Date: 11-Oct-2025
"""

from typing import Any, Iterator, Dict, List, Optional, Union
from .base import ANodeStrategy
from ...defs import NodeMode, NodeTrait
from .contracts import NodeType
from ...common.utils import (
    safe_to_native_conversion,
    create_basic_metrics,
    create_basic_backend_info,
    create_size_tracker,
    create_access_tracker,
    update_size_tracker,
    record_access,
    get_access_metrics
)


class HAMTNode:
    """
    HAMT Node with bitmap-based indexing.
    
    Each node uses a 32-bit bitmap to track which slots are occupied,
    and stores only the occupied slots in a compact array.
    """
    
    def __init__(self):
        self.bitmap: int = 0  # 32-bit bitmap for tracking occupied slots
        self.children: List[Any] = []  # Compact array of children/values
    
    def index_for_bit(self, bit_pos: int) -> int:
        """Calculate array index for given bit position using popcount."""
        # Count number of 1s before bit_pos
        mask = (1 << bit_pos) - 1
        return bin(self.bitmap & mask).count('1')
    
    def has_child(self, bit_pos: int) -> bool:
        """Check if child exists at bit position."""
        return (self.bitmap & (1 << bit_pos)) != 0
    
    def get_child(self, bit_pos: int) -> Optional[Any]:
        """Get child at bit position."""
        if not self.has_child(bit_pos):
            return None
        idx = self.index_for_bit(bit_pos)
        return self.children[idx]
    
    def set_child(self, bit_pos: int, value: Any) -> 'HAMTNode':
        """
        Set child at bit position (immutable - returns new node).
        
        This creates a new node with structural sharing.
        """
        new_node = HAMTNode()
        new_node.bitmap = self.bitmap
        new_node.children = self.children.copy()
        
        if self.has_child(bit_pos):
            # Update existing child
            idx = self.index_for_bit(bit_pos)
            new_node.children[idx] = value
        else:
            # Insert new child
            new_node.bitmap |= (1 << bit_pos)
            idx = self.index_for_bit(bit_pos)
            new_node.children.insert(idx, value)
        
        return new_node
    
    def remove_child(self, bit_pos: int) -> 'HAMTNode':
        """Remove child at bit position (immutable - returns new node)."""
        if not self.has_child(bit_pos):
            return self  # No change
        
        new_node = HAMTNode()
        new_node.bitmap = self.bitmap & ~(1 << bit_pos)
        new_node.children = self.children.copy()
        idx = self.index_for_bit(bit_pos)
        new_node.children.pop(idx)
        
        return new_node


class HAMTLeaf:
    """Leaf node storing key-value pair."""
    
    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value


class HAMTStrategy(ANodeStrategy):
    """
    HAMT (Hash Array Mapped Trie) - Persistent data structure.
    
    HAMT is a persistent hash table that uses structural sharing
    for efficient immutable operations. Popular in functional
    programming languages like Clojure, Scala, and Haskell.
    
    Features:
    - Persistent/immutable operations
    - Structural sharing (memory efficient)
    - O(log32 n) operations (5-bit chunks)
    - Cache-friendly bitmap indexing
    - No rehashing needed
    
    Best for:
    - Functional programming
    - Immutable data structures
    - Version control systems
    - Undo/redo functionality
    - Concurrent read-heavy workloads
    """
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE
    
    # HAMT constants
    BITS_PER_LEVEL = 5  # 2^5 = 32 children per node
    LEVEL_MASK = 0x1F  # 0b11111
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the HAMT strategy."""
        super().__init__(NodeMode.HAMT, traits, **options)
        self._root: HAMTNode = HAMTNode()
        self._size = 0
        self._size_tracker = create_size_tracker()
        self._access_tracker = create_access_tracker()
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by HAMT strategy."""
        return NodeTrait.INDEXED | NodeTrait.PERSISTENT
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def _hash_key(self, key: Any) -> int:
        """Compute hash for key."""
        return hash(str(key)) & 0xFFFFFFFF  # 32-bit hash
    
    def _get_chunk(self, hash_val: int, level: int) -> int:
        """Extract 5-bit chunk at given level."""
        shift = level * self.BITS_PER_LEVEL
        return (hash_val >> shift) & self.LEVEL_MASK
    
    def _search(self, node: HAMTNode, key: Any, hash_val: int, level: int) -> Optional[Any]:
        """Recursively search for key in HAMT."""
        chunk = self._get_chunk(hash_val, level)
        
        if not node.has_child(chunk):
            return None
        
        child = node.get_child(chunk)
        
        if isinstance(child, HAMTLeaf):
            if child.key == key:
                return child.value
            return None
        elif isinstance(child, HAMTNode):
            return self._search(child, key, hash_val, level + 1)
        
        return None
    
    def get(self, path: str, default: Any = None) -> Any:
        """Retrieve a value by path."""
        record_access(self._access_tracker, 'get_count')
        
        if '.' in path:
            # Handle nested paths
            parts = path.split('.')
            current = self.get(parts[0])
            for part in parts[1:]:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            return current
        
        hash_val = self._hash_key(path)
        result = self._search(self._root, path, hash_val, 0)
        return result if result is not None else default
    
    def _insert(self, node: HAMTNode, key: Any, value: Any, 
                hash_val: int, level: int) -> HAMTNode:
        """
        Recursively insert key-value pair (immutable).
        
        Returns new node with structural sharing.
        """
        chunk = self._get_chunk(hash_val, level)
        
        if not node.has_child(chunk):
            # Empty slot - create leaf
            leaf = HAMTLeaf(key, value)
            return node.set_child(chunk, leaf)
        
        child = node.get_child(chunk)
        
        if isinstance(child, HAMTLeaf):
            if child.key == key:
                # Update existing key
                new_leaf = HAMTLeaf(key, value)
                return node.set_child(chunk, new_leaf)
            else:
                # Hash collision - create sub-node
                new_subnode = HAMTNode()
                
                # Insert existing leaf
                existing_hash = self._hash_key(child.key)
                existing_chunk = self._get_chunk(existing_hash, level + 1)
                new_subnode = new_subnode.set_child(existing_chunk, child)
                
                # Insert new leaf
                new_chunk = self._get_chunk(hash_val, level + 1)
                new_leaf = HAMTLeaf(key, value)
                new_subnode = new_subnode.set_child(new_chunk, new_leaf)
                
                return node.set_child(chunk, new_subnode)
        
        elif isinstance(child, HAMTNode):
            # Recurse into sub-node
            new_child = self._insert(child, key, value, hash_val, level + 1)
            return node.set_child(chunk, new_child)
        
        return node
    
    def put(self, path: str, value: Any = None) -> 'HAMTStrategy':
        """Set a value at path (immutable operation)."""
        record_access(self._access_tracker, 'put_count')
        
        if '.' in path:
            # Handle nested paths
            parts = path.split('.')
            root = self.get(parts[0])
            if root is None:
                root = {}
            elif not isinstance(root, dict):
                root = {parts[0]: root}
            
            current = root
            for part in parts[1:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
            
            # Create new root (structural sharing)
            hash_val = self._hash_key(parts[0])
            self._root = self._insert(self._root, parts[0], root, hash_val, 0)
        else:
            exists = self.exists(path)
            hash_val = self._hash_key(path)
            self._root = self._insert(self._root, path, value, hash_val, 0)
            
            if not exists:
                update_size_tracker(self._size_tracker, 1)
                self._size += 1
        
        return self
    
    def _remove(self, node: HAMTNode, key: Any, hash_val: int, level: int) -> Optional[HAMTNode]:
        """Recursively remove key (immutable)."""
        chunk = self._get_chunk(hash_val, level)
        
        if not node.has_child(chunk):
            return node  # Key not found
        
        child = node.get_child(chunk)
        
        if isinstance(child, HAMTLeaf):
            if child.key == key:
                # Remove leaf
                return node.remove_child(chunk)
            return node  # Different key
        
        elif isinstance(child, HAMTNode):
            # Recurse
            new_child = self._remove(child, key, hash_val, level + 1)
            if new_child is None or (new_child.bitmap == 0):
                # Child is now empty, remove it
                return node.remove_child(chunk)
            else:
                return node.set_child(chunk, new_child)
        
        return node
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair (immutable operation)."""
        key_str = str(key)
        if self.exists(key_str):
            hash_val = self._hash_key(key_str)
            self._root = self._remove(self._root, key_str, hash_val, 0)
            update_size_tracker(self._size_tracker, -1)
            record_access(self._access_tracker, 'delete_count')
            self._size -= 1
            return True
        return False
    
    def remove(self, key: Any) -> bool:
        """Remove a key-value pair (alias for delete)."""
        return self.delete(key)
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        return self.get(str(key)) is not None
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self.get(path) is not None
    
    # ============================================================================
    # ITERATION METHODS
    # ============================================================================
    
    def _collect_all(self, node: HAMTNode) -> List[tuple[Any, Any]]:
        """Collect all key-value pairs from HAMT."""
        results = []
        
        for child in node.children:
            if isinstance(child, HAMTLeaf):
                results.append((child.key, child.value))
            elif isinstance(child, HAMTNode):
                results.extend(self._collect_all(child))
        
        return results
    
    def keys(self) -> Iterator[Any]:
        """Get an iterator over all keys."""
        for key, _ in self._collect_all(self._root):
            yield key
    
    def values(self) -> Iterator[Any]:
        """Get an iterator over all values."""
        for _, value in self._collect_all(self._root):
            yield value
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get an iterator over all key-value pairs."""
        for item in self._collect_all(self._root):
            yield item
    
    def __len__(self) -> int:
        """Get the number of key-value pairs."""
        return self._size
    
    # ============================================================================
    # ADVANCED FEATURES
    # ============================================================================
    
    def snapshot(self) -> 'HAMTStrategy':
        """
        Create immutable snapshot of current state.
        
        Due to structural sharing, this is very efficient (O(1)).
        """
        new_strategy = HAMTStrategy(self.traits, **self.options)
        new_strategy._root = self._root  # Shared structure
        new_strategy._size = self._size
        return new_strategy
    
    def get_tree_depth(self) -> int:
        """Calculate maximum tree depth."""
        def depth(node: HAMTNode, current: int) -> int:
            max_d = current
            for child in node.children:
                if isinstance(child, HAMTNode):
                    max_d = max(max_d, depth(child, current + 1))
            return max_d
        
        return depth(self._root, 0)
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dictionary."""
        result = {}
        for key, value in self.items():
            result[str(key)] = safe_to_native_conversion(value)
        return result
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend information."""
        return {
            **create_basic_backend_info('HAMT', 'Hash Array Mapped Trie'),
            'total_keys': self._size,
            'tree_depth': self.get_tree_depth(),
            'bits_per_level': self.BITS_PER_LEVEL,
            **self._size_tracker,
            **get_access_metrics(self._access_tracker)
        }

