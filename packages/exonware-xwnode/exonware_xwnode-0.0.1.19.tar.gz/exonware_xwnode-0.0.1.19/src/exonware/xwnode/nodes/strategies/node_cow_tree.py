#exonware\xnode\strategies\impls\node_cow_tree.py
"""
Copy-on-Write Tree Node Strategy Implementation

This module implements the COW_TREE strategy for copy-on-write trees with
atomic snapshots and versioning capabilities.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple, Set
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class COWTreeNode:
    """Copy-on-write node in the tree."""
    
    def __init__(self, key: str, value: Any = None, left: Optional['COWTreeNode'] = None,
                 right: Optional['COWTreeNode'] = None, ref_count: int = 1):
        self.key = key
        self.value = value
        self.left = left
        self.right = right
        self.ref_count = ref_count
        self._frozen = False
        self._hash = None
    
    def __hash__(self) -> int:
        """Cache hash for performance."""
        if self._hash is None:
            self._hash = hash((self.key, self.value, id(self.left), id(self.right)))
        return self._hash
    
    def __eq__(self, other) -> bool:
        """Structural equality."""
        if not isinstance(other, COWTreeNode):
            return False
        return (self.key == other.key and 
                self.value == other.value and
                self.left is other.left and
                self.right is other.right)
    
    def increment_ref(self) -> None:
        """Increment reference count."""
        if not self._frozen:
            self.ref_count += 1
    
    def decrement_ref(self) -> bool:
        """Decrement reference count, return True if should be deleted."""
        if not self._frozen:
            self.ref_count -= 1
            return self.ref_count <= 0
        return False
    
    def freeze(self) -> None:
        """Freeze node to prevent modifications."""
        self._frozen = True
    
    def is_shared(self) -> bool:
        """Check if node is shared (ref_count > 1)."""
        return self.ref_count > 1


class COWTreeStrategy(ANodeTreeStrategy):
    """
    Copy-on-write tree node strategy with atomic snapshots.
    
    Provides instant snapshots, atomic updates, and versioning through
    copy-on-write semantics 
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE
with reference counting.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the COW tree strategy."""
        super().__init__(NodeMode.COW_TREE, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        self.balanced = options.get('balanced', True)  # Use AVL balancing
        self.auto_snapshot = options.get('auto_snapshot', False)
        
        # Core COW tree
        self._root: Optional[COWTreeNode] = None
        self._size = 0
        self._version = 0
        self._snapshots: List['xCOWTreeStrategy'] = []
        
        # Statistics
        self._total_copies = 0
        self._total_shares = 0
        self._max_height = 0
        self._snapshot_count = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the COW tree strategy."""
        return (NodeTrait.PERSISTENT | NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _create_node(self, key: str, value: Any, left: Optional[COWTreeNode] = None,
                    right: Optional[COWTreeNode] = None) -> COWTreeNode:
        """Create new node."""
        return COWTreeNode(key, value, left, right)
    
    def _copy_node(self, node: COWTreeNode) -> COWTreeNode:
        """Copy node with COW semantics."""
        if not node.is_shared():
            # Node is not shared, can modify in place
            return node
        
        # Node is shared, need to copy
        self._total_copies += 1
        new_node = COWTreeNode(node.key, node.value, node.left, node.right)
        
        # Increment reference counts for shared children
        if node.left:
            node.left.increment_ref()
        if node.right:
            node.right.increment_ref()
        
        return new_node
    
    def _get_height(self, node: Optional[COWTreeNode]) -> int:
        """Get height of node."""
        if not node:
            return 0
        
        left_height = self._get_height(node.left)
        right_height = self._get_height(node.right)
        return 1 + max(left_height, right_height)
    
    def _get_balance(self, node: Optional[COWTreeNode]) -> int:
        """Get balance factor of node."""
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)
    
    def _rotate_right(self, node: COWTreeNode) -> COWTreeNode:
        """Right rotation for AVL balancing."""
        left = node.left
        if not left:
            return node
        
        # Copy nodes if shared
        left = self._copy_node(left)
        node = self._copy_node(node)
        
        # Perform rotation
        new_right = self._create_node(node.key, node.value, left.right, node.right)
        new_root = self._create_node(left.key, left.value, left.left, new_right)
        
        return new_root
    
    def _rotate_left(self, node: COWTreeNode) -> COWTreeNode:
        """Left rotation for AVL balancing."""
        right = node.right
        if not right:
            return node
        
        # Copy nodes if shared
        right = self._copy_node(right)
        node = self._copy_node(node)
        
        # Perform rotation
        new_left = self._create_node(node.key, node.value, node.left, right.left)
        new_root = self._create_node(right.key, right.value, new_left, right.right)
        
        return new_root
    
    def _balance_node(self, node: COWTreeNode) -> COWTreeNode:
        """Balance node using AVL rotations."""
        if not self.balanced:
            return node
        
        balance = self._get_balance(node)
        
        # Left heavy
        if balance > 1:
            if self._get_balance(node.left) < 0:
                # Left-Right case
                new_left = self._rotate_left(node.left)
                new_node = self._create_node(node.key, node.value, new_left, node.right)
                return self._rotate_right(new_node)
            else:
                # Left-Left case
                return self._rotate_right(node)
        
        # Right heavy
        if balance < -1:
            if self._get_balance(node.right) > 0:
                # Right-Left case
                new_right = self._rotate_right(node.right)
                new_node = self._create_node(node.key, node.value, node.left, new_right)
                return self._rotate_left(new_node)
            else:
                # Right-Right case
                return self._rotate_left(node)
        
        return node
    
    def _insert_node(self, node: Optional[COWTreeNode], key: str, value: Any) -> Tuple[Optional[COWTreeNode], bool]:
        """Insert node with COW semantics."""
        if not node:
            new_node = self._create_node(key, value)
            return new_node, True
        
        # Copy node if shared
        if node.is_shared():
            node = self._copy_node(node)
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            new_left, inserted = self._insert_node(node.left, key, value)
            if inserted or new_left is not node.left:
                new_node = self._create_node(node.key, node.value, new_left, node.right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        elif normalized_key > node_key:
            new_right, inserted = self._insert_node(node.right, key, value)
            if inserted or new_right is not node.right:
                new_node = self._create_node(node.key, node.value, node.left, new_right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        else:
            # Key exists, update value
            if node.value == value:
                # Share unchanged node
                self._total_shares += 1
                return node, False
            else:
                new_node = self._create_node(node.key, value, node.left, node.right)
                return new_node, False
    
    def _find_node(self, node: Optional[COWTreeNode], key: str) -> Optional[COWTreeNode]:
        """Find node by key."""
        if not node:
            return None
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            return self._find_node(node.left, key)
        elif normalized_key > node_key:
            return self._find_node(node.right, key)
        else:
            return node
    
    def _delete_node(self, node: Optional[COWTreeNode], key: str) -> Tuple[Optional[COWTreeNode], bool]:
        """Delete node with COW semantics."""
        if not node:
            return None, False
        
        # Copy node if shared
        if node.is_shared():
            node = self._copy_node(node)
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            new_left, deleted = self._delete_node(node.left, key)
            if deleted or new_left is not node.left:
                new_node = self._create_node(node.key, node.value, new_left, node.right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        elif normalized_key > node_key:
            new_right, deleted = self._delete_node(node.right, key)
            if deleted or new_right is not node.right:
                new_node = self._create_node(node.key, node.value, node.left, new_right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        else:
            # Found node to delete
            if not node.left:
                return node.right, True
            elif not node.right:
                return node.left, True
            else:
                # Node has both children, find successor
                successor = self._find_min(node.right)
                new_right, _ = self._delete_node(node.right, successor.key)
                new_node = self._create_node(successor.key, successor.value, node.left, new_right)
                return self._balance_node(new_node), True
    
    def _find_min(self, node: COWTreeNode) -> COWTreeNode:
        """Find minimum node in subtree."""
        while node.left:
            node = node.left
        return node
    
    def _inorder_traversal(self, node: Optional[COWTreeNode]) -> Iterator[Tuple[str, Any]]:
        """In-order traversal of tree."""
        if node:
            yield from self._inorder_traversal(node.left)
            yield (node.key, node.value)
            yield from self._inorder_traversal(node.right)
    
    def _freeze_tree(self, node: Optional[COWTreeNode]) -> None:
        """Freeze entire tree to prevent modifications."""
        if node:
            node.freeze()
            self._freeze_tree(node.left)
            self._freeze_tree(node.right)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        new_root, inserted = self._insert_node(self._root, key, value)
        self._root = new_root
        
        if inserted:
            self._size += 1
            self._version += 1
        
        self._max_height = max(self._max_height, self._get_height(self._root))
        
        # Auto-snapshot if enabled
        if self.auto_snapshot and inserted:
            self.snapshot()
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        if not isinstance(key, str):
            key = str(key)
        
        node = self._find_node(self._root, key)
        return node.value if node else default
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        new_root, deleted = self._delete_node(self._root, key)
        self._root = new_root
        
        if deleted:
            self._size -= 1
            self._version += 1
        
        return deleted
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        if not isinstance(key, str):
            key = str(key)
        
        return self._find_node(self._root, key) is not None
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._size = 0
        self._version += 1
    
    def size(self) -> int:
        """Get number of key-value pairs."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if tree is empty."""
        return self._root is None
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def keys(self) -> Iterator[str]:
        """Iterate over keys in sorted order."""
        for key, _ in self._inorder_traversal(self._root):
            yield key
    
    def values(self) -> Iterator[Any]:
        """Iterate over values in key order."""
        for _, value in self._inorder_traversal(self._root):
            yield value
    
    def items(self) -> Iterator[Tuple[str, Any]]:
        """Iterate over key-value pairs in sorted order."""
        yield from self._inorder_traversal(self._root)
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        yield from self.keys()
    
    # ============================================================================
    # COW TREE SPECIFIC OPERATIONS
    # ============================================================================
    
    def snapshot(self) -> 'xCOWTreeStrategy':
        """Create an atomic snapshot of the current tree."""
        snapshot = xCOWTreeStrategy(self.traits, **self.options)
        snapshot._root = self._root
        snapshot._size = self._size
        snapshot._version = self._version
        
        # Increment reference counts for shared nodes
        if self._root:
            self._root.increment_ref()
        
        # Freeze the snapshot to prevent modifications
        snapshot._freeze_tree(snapshot._root)
        
        self._snapshots.append(snapshot)
        self._snapshot_count += 1
        
        return snapshot
    
    def restore_snapshot(self, snapshot: 'xCOWTreeStrategy') -> None:
        """Restore from a snapshot."""
        # Decrement reference counts for current tree
        if self._root:
            self._root.decrement_ref()
        
        # Copy snapshot state
        self._root = snapshot._root
        self._size = snapshot._size
        self._version = snapshot._version
        
        # Increment reference counts for restored tree
        if self._root:
            self._root.increment_ref()
    
    def get_snapshots(self) -> List['xCOWTreeStrategy']:
        """Get list of all snapshots."""
        return self._snapshots.copy()
    
    def cleanup_snapshots(self) -> int:
        """Clean up old snapshots, return number of snapshots removed."""
        removed = len(self._snapshots)
        self._snapshots.clear()
        self._snapshot_count = 0
        return removed
    
    def get_version(self) -> int:
        """Get current version number."""
        return self._version
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'size': self._size,
            'height': self._get_height(self._root),
            'max_height': self._max_height,
            'version': self._version,
            'snapshot_count': self._snapshot_count,
            'total_copies': self._total_copies,
            'total_shares': self._total_shares,
            'copy_ratio': self._total_copies / max(1, self._total_shares + self._total_copies),
            'strategy': 'COW_TREE',
            'backend': 'Copy-on-write AVL tree with reference counting',
            'traits': [trait.name for trait in NodeTrait if self.has_trait(trait)]
        }
