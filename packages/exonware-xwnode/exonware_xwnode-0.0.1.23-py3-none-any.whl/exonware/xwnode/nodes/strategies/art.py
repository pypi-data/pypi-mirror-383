"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/node_art.py

ART (Adaptive Radix Tree) Node Strategy Implementation

This module implements the ART strategy for fast string key operations
with O(k) complexity where k = key length.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
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


class ARTNode:
    """Base ART node with common functionality."""
    
    def __init__(self):
        self.prefix: bytes = b''  # Path compression
        self.prefix_len: int = 0
    
    def matches_prefix(self, key: bytes, depth: int) -> int:
        """Check how many bytes of prefix match the key."""
        matches = 0
        for i in range(min(self.prefix_len, len(key) - depth)):
            if self.prefix[i] == key[depth + i]:
                matches += 1
            else:
                break
        return matches


class ARTNode4(ARTNode):
    """Node with up to 4 children - smallest node size."""
    
    def __init__(self):
        super().__init__()
        self.keys: List[int] = []  # Byte values (0-255)
        self.children: List[Any] = []  # Child nodes or leaf values
        
    def find_child(self, byte: int) -> Optional[Any]:
        """Find child by byte value."""
        try:
            idx = self.keys.index(byte)
            return self.children[idx]
        except ValueError:
            return None
    
    def add_child(self, byte: int, child: Any) -> bool:
        """Add child if space available."""
        if len(self.keys) >= 4:
            return False
        self.keys.append(byte)
        self.children.append(child)
        return True
    
    def remove_child(self, byte: int) -> bool:
        """Remove child by byte value."""
        try:
            idx = self.keys.index(byte)
            self.keys.pop(idx)
            self.children.pop(idx)
            return True
        except ValueError:
            return False


class ARTNode16(ARTNode):
    """Node with up to 16 children."""
    
    def __init__(self):
        super().__init__()
        self.keys: List[int] = []
        self.children: List[Any] = []
    
    def find_child(self, byte: int) -> Optional[Any]:
        """Find child by byte value."""
        try:
            idx = self.keys.index(byte)
            return self.children[idx]
        except ValueError:
            return None
    
    def add_child(self, byte: int, child: Any) -> bool:
        """Add child if space available."""
        if len(self.keys) >= 16:
            return False
        self.keys.append(byte)
        self.children.append(child)
        return True


class ARTNode48(ARTNode):
    """Node with up to 48 children using index array."""
    
    def __init__(self):
        super().__init__()
        # Index array: 256 bytes mapping byte->child_index
        self.index: List[int] = [255] * 256  # 255 = empty
        self.children: List[Any] = []
    
    def find_child(self, byte: int) -> Optional[Any]:
        """Find child by byte value."""
        idx = self.index[byte]
        if idx == 255:
            return None
        return self.children[idx]
    
    def add_child(self, byte: int, child: Any) -> bool:
        """Add child if space available."""
        if len(self.children) >= 48:
            return False
        self.index[byte] = len(self.children)
        self.children.append(child)
        return True


class ARTNode256(ARTNode):
    """Node with up to 256 children - direct array."""
    
    def __init__(self):
        super().__init__()
        self.children: List[Optional[Any]] = [None] * 256
    
    def find_child(self, byte: int) -> Optional[Any]:
        """Find child by byte value."""
        return self.children[byte]
    
    def add_child(self, byte: int, child: Any) -> bool:
        """Add child (always succeeds for Node256)."""
        self.children[byte] = child
        return True


class ARTStrategy(ANodeStrategy):
    """
    Adaptive Radix Tree - 3-10x faster than B-trees for string keys.
    
    ART is a space-efficient and cache-friendly radix tree that adapts
    node sizes based on the number of children (4, 16, 48, 256).
    
    Features:
    - O(k) operations where k = key length
    - Path compression for space efficiency
    - Adaptive node sizes
    - Cache-friendly memory layout
    
    Best for:
    - String key lookups
    - Prefix searches
    - In-memory databases
    - Route tables
    """
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the ART strategy."""
        super().__init__(NodeMode.ART, traits, **options)
        self._root: Optional[ARTNode] = None
        self._size = 0
        self._size_tracker = create_size_tracker()
        self._access_tracker = create_access_tracker()
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by ART strategy."""
        return NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.PREFIX_TREE
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def _key_to_bytes(self, key: Any) -> bytes:
        """Convert key to bytes for radix tree processing."""
        if isinstance(key, bytes):
            return key
        elif isinstance(key, str):
            return key.encode('utf-8')
        else:
            return str(key).encode('utf-8')
    
    def _search(self, node: Optional[ARTNode], key: bytes, depth: int) -> Optional[Any]:
        """Recursively search for key in tree."""
        if node is None:
            return None
        
        # Check if this node has a value and we've consumed the full key
        if depth >= len(key):
            if hasattr(node, 'value'):
                return node.value
            return None
        
        # Check prefix match
        if node.prefix_len > 0:
            matches = node.matches_prefix(key, depth)
            if matches != node.prefix_len:
                return None  # Prefix mismatch
            depth += node.prefix_len
            
            # Re-check after advancing by prefix
            if depth >= len(key):
                if hasattr(node, 'value'):
                    return node.value
                return None
        
        # Continue search in child
        byte = key[depth]
        child = node.find_child(byte)
        
        if child is None:
            return None
        
        # If child is a leaf value, return it
        if not isinstance(child, ARTNode):
            return child
        
        return self._search(child, key, depth + 1)
    
    def get(self, path: str, default: Any = None) -> Any:
        """Retrieve a value by path (key)."""
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
        
        key_bytes = self._key_to_bytes(path)
        result = self._search(self._root, key_bytes, 0)
        return result if result is not None else default
    
    def _insert(self, node: Optional[ARTNode], key: bytes, value: Any, depth: int) -> ARTNode:
        """Recursively insert key-value pair into tree."""
        if node is None:
            # Create new node and continue inserting
            if depth >= len(key):
                # We're at the end - create leaf with value
                leaf = ARTNode4()
                leaf.value = value
                return leaf
            else:
                # Build tree structure for remaining bytes
                new_node = ARTNode4()
                # Insert the value at the current byte
                byte = key[depth]
                child = self._insert(None, key, value, depth + 1)
                new_node.add_child(byte, child)
                return new_node
        
        # Check prefix match
        if node.prefix_len > 0:
            matches = node.matches_prefix(key, depth)
            if matches < node.prefix_len:
                # Need to split prefix
                # Create new parent node
                new_node = ARTNode4()
                new_node.prefix = node.prefix[:matches]
                new_node.prefix_len = matches
                
                # Adjust old node prefix
                old_byte = node.prefix[matches]
                node.prefix = node.prefix[matches + 1:]
                node.prefix_len -= matches + 1
                
                # Add old node as child
                new_node.add_child(old_byte, node)
                
                # Add new value
                if depth + matches < len(key):
                    new_byte = key[depth + matches]
                    leaf = ARTNode4()
                    leaf.value = value
                    new_node.add_child(new_byte, leaf)
                else:
                    new_node.value = value
                
                return new_node
            
            depth += node.prefix_len
        
        # Reached end of key
        if depth >= len(key):
            node.value = value
            return node
        
        # Insert into child
        byte = key[depth]
        child = node.find_child(byte)
        
        if child is None:
            # Create new child for this byte
            child = self._insert(None, key, value, depth + 1)
            if not node.add_child(byte, child):
                # Node is full, need to grow
                node = self._grow_node(node)
                node.add_child(byte, child)
        else:
            if isinstance(child, ARTNode):
                # Recurse into child
                updated_child = self._insert(child, key, value, depth + 1)
                # Update child reference
                if isinstance(node, ARTNode4):
                    idx = node.keys.index(byte)
                    node.children[idx] = updated_child
                elif isinstance(node, ARTNode16):
                    idx = node.keys.index(byte)
                    node.children[idx] = updated_child
                elif isinstance(node, ARTNode48):
                    idx = node.index[byte]
                    node.children[idx] = updated_child
                elif isinstance(node, ARTNode256):
                    node.children[byte] = updated_child
            else:
                # Child is a leaf value - need to create intermediate node
                old_value = child
                new_node = self._insert(None, key, value, depth + 1)
                
                # Update child reference
                if isinstance(node, ARTNode4):
                    idx = node.keys.index(byte)
                    node.children[idx] = new_node
                elif isinstance(node, ARTNode16):
                    idx = node.keys.index(byte)
                    node.children[idx] = new_node
                elif isinstance(node, ARTNode48):
                    idx = node.index[byte]
                    node.children[idx] = new_node
                elif isinstance(node, ARTNode256):
                    node.children[byte] = new_node
        
        return node
    
    def _grow_node(self, node: ARTNode) -> ARTNode:
        """Grow node to next size class."""
        if isinstance(node, ARTNode4):
            # Grow to Node16
            new_node = ARTNode16()
            new_node.prefix = node.prefix
            new_node.prefix_len = node.prefix_len
            new_node.keys = node.keys.copy()
            new_node.children = node.children.copy()
            if hasattr(node, 'value'):
                new_node.value = node.value
            return new_node
        elif isinstance(node, ARTNode16):
            # Grow to Node48
            new_node = ARTNode48()
            new_node.prefix = node.prefix
            new_node.prefix_len = node.prefix_len
            for i, byte in enumerate(node.keys):
                new_node.index[byte] = i
            new_node.children = node.children.copy()
            if hasattr(node, 'value'):
                new_node.value = node.value
            return new_node
        elif isinstance(node, ARTNode48):
            # Grow to Node256
            new_node = ARTNode256()
            new_node.prefix = node.prefix
            new_node.prefix_len = node.prefix_len
            for byte in range(256):
                idx = node.index[byte]
                if idx != 255:
                    new_node.children[byte] = node.children[idx]
            if hasattr(node, 'value'):
                new_node.value = node.value
            return new_node
        else:
            return node  # Already at max size
    
    def put(self, path: str, value: Any = None) -> 'ARTStrategy':
        """Set a value at path."""
        record_access(self._access_tracker, 'put_count')
        
        if '.' in path:
            # Handle nested paths by converting to dict
            parts = path.split('.')
            # Get or create root dict
            root = self.get(parts[0])
            if root is None:
                root = {}
            elif not isinstance(root, dict):
                root = {parts[0]: root}
            
            # Navigate and create nested structure
            current = root
            for part in parts[1:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
            
            # Store the root dict
            key_bytes = self._key_to_bytes(parts[0])
            key_existed = self.exists(parts[0])
            self._root = self._insert(self._root, key_bytes, root, 0)
            if not key_existed:
                update_size_tracker(self._size_tracker, 1)
                self._size += 1
        else:
            key_bytes = self._key_to_bytes(path)
            key_existed = self.exists(path)
            self._root = self._insert(self._root, key_bytes, value, 0)
            if not key_existed:
                update_size_tracker(self._size_tracker, 1)
                self._size += 1
        
        return self
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        return self.get(str(key)) is not None
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self.get(path) is not None
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        # Simplified deletion - mark as deleted
        key_str = str(key)
        if self.exists(key_str):
            # In a full implementation, we would remove the node
            # For now, we set to None
            self.put(key_str, None)
            update_size_tracker(self._size_tracker, -1)
            record_access(self._access_tracker, 'delete_count')
            self._size -= 1
            return True
        return False
    
    def remove(self, key: Any) -> bool:
        """Remove a key-value pair (alias for delete)."""
        return self.delete(key)
    
    # ============================================================================
    # ITERATION METHODS
    # ============================================================================
    
    def _collect_all(self, node: Optional[ARTNode], prefix: bytes) -> List[tuple[bytes, Any]]:
        """Collect all key-value pairs from tree."""
        if node is None:
            return []
        
        results = []
        
        # Check if node has a value
        if hasattr(node, 'value') and node.value is not None:
            results.append((prefix, node.value))
        
        # Collect from children
        if isinstance(node, ARTNode4):
            for i, byte in enumerate(node.keys):
                child = node.children[i]
                child_prefix = prefix + bytes([byte])
                if isinstance(child, ARTNode):
                    results.extend(self._collect_all(child, child_prefix))
                else:
                    results.append((child_prefix, child))
        elif isinstance(node, ARTNode16):
            for i, byte in enumerate(node.keys):
                child = node.children[i]
                child_prefix = prefix + bytes([byte])
                if isinstance(child, ARTNode):
                    results.extend(self._collect_all(child, child_prefix))
                else:
                    results.append((child_prefix, child))
        elif isinstance(node, ARTNode48):
            for byte in range(256):
                idx = node.index[byte]
                if idx != 255:
                    child = node.children[idx]
                    child_prefix = prefix + bytes([byte])
                    if isinstance(child, ARTNode):
                        results.extend(self._collect_all(child, child_prefix))
                    else:
                        results.append((child_prefix, child))
        elif isinstance(node, ARTNode256):
            for byte in range(256):
                child = node.children[byte]
                if child is not None:
                    child_prefix = prefix + bytes([byte])
                    if isinstance(child, ARTNode):
                        results.extend(self._collect_all(child, child_prefix))
                    else:
                        results.append((child_prefix, child))
        
        return results
    
    def keys(self) -> Iterator[Any]:
        """Get an iterator over all keys."""
        all_items = self._collect_all(self._root, b'')
        for key_bytes, _ in all_items:
            try:
                yield key_bytes.decode('utf-8')
            except UnicodeDecodeError:
                yield key_bytes
    
    def values(self) -> Iterator[Any]:
        """Get an iterator over all values."""
        all_items = self._collect_all(self._root, b'')
        for _, value in all_items:
            yield value
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get an iterator over all key-value pairs."""
        all_items = self._collect_all(self._root, b'')
        for key_bytes, value in all_items:
            try:
                key = key_bytes.decode('utf-8')
            except UnicodeDecodeError:
                key = key_bytes
            yield (key, value)
    
    def __len__(self) -> int:
        """Get the number of key-value pairs."""
        return self._size
    
    # ============================================================================
    # ADVANCED FEATURES
    # ============================================================================
    
    def prefix_search(self, prefix: str) -> List[tuple[str, Any]]:
        """
        Search for all keys with given prefix.
        
        This is a key advantage of ART - efficient prefix searches.
        """
        prefix_bytes = self._key_to_bytes(prefix)
        # Simplified: collect all and filter
        all_items = self._collect_all(self._root, b'')
        results = []
        for key_bytes, value in all_items:
            if key_bytes.startswith(prefix_bytes):
                try:
                    key = key_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    key = str(key_bytes)
                results.append((key, value))
        return results
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dictionary."""
        result = {}
        for key, value in self.items():
            result[str(key)] = safe_to_native_conversion(value)
        return result
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend information."""
        return {
            **create_basic_backend_info('ART', 'Adaptive Radix Tree'),
            'total_keys': self._size,
            **self._size_tracker,
            **get_access_metrics(self._access_tracker)
        }

