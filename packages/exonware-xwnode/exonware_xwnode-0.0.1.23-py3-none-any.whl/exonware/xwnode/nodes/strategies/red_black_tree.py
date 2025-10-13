#exonware\xnode\strategies\impls\node_red_black_tree.py
"""
Red-Black Tree Node Strategy Implementation

This module implements the RED_BLACK_TREE strategy for self-balancing binary
search trees with guaranteed O(log n) height and operations.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class RedBlackTreeNode:
    """Node in the red-black tree."""
    
    def __init__(self, key: str, value: Any = None, color: str = 'RED'):
        self.key = key
        self.value = value
        self.color = color  # 'RED' or 'BLACK'
        self.left: Optional['RedBlackTreeNode'] = None
        self.right: Optional['RedBlackTreeNode'] = None
        self.parent: Optional['RedBlackTreeNode'] = None
        self._hash = None
    
    def __hash__(self) -> int:
        """Cache hash for performance."""
        if self._hash is None:
            self._hash = hash((self.key, self.value, self.color))
        return self._hash
    
    def __eq__(self, other) -> bool:
        """Structural equality."""
        if not isinstance(other, RedBlackTreeNode):
            return False
        return (self.key == other.key and 
                self.value == other.value and
                self.color == other.color)
    
    def is_red(self) -> bool:
        """Check if node is red."""
        return self.color == 'RED'
    
    def is_black(self) -> bool:
        """Check if node is black."""
        return self.color == 'BLACK'
    
    def set_red(self) -> None:
        """Set node color to red."""
        self.color = 'RED'
    
    def set_black(self) -> None:
        """Set node color to black."""
        self.color = 'BLACK'


class RedBlackTreeStrategy(ANodeTreeStrategy):
    """
    Red-Black Tree strategy for self-balancing binary search trees.
    
    WHY Red-Black Tree:
    - Guaranteed O(log n) worst-case for insert, search, delete
    - Simpler than AVL trees (less strict balancing = fewer rotations)
    - Industry standard (used in Java TreeMap, C++ std::map, Linux kernel)
    - Better insert/delete performance than AVL (relaxed balancing)
    - Maintains sorted order with efficient range queries
    
    WHY this implementation:
    - Color-based balancing rules (simpler than height-based AVL)
    - Parent pointers enable bottom-up fixup after operations
    - Case-based rotation logic handles all red-black violations
    - Tracks rotations and statistics for performance monitoring
    - Preserves BST property while maintaining logarithmic height
    
    Time Complexity:
    - Insert: O(log n) guaranteed (at most 2 rotations)
    - Search: O(log n) guaranteed
    - Delete: O(log n) guaranteed (at most 3 rotations)
    - Min/Max: O(log n) - leftmost/rightmost traversal
    - Iteration: O(n) in sorted order
    
    Space Complexity: O(n) - one node per key + parent pointers + color bit
    
    Trade-offs:
    - Advantage: Fewer rotations than AVL (better insert/delete performance)
    - Advantage: Guaranteed O(log n) worst-case (unlike Skip List)
    - Limitation: Slightly taller than AVL trees (height ≤ 2*log(n+1))
    - Limitation: More complex than simple BST (color rules and rotations)
    - Compared to AVL: Faster inserts/deletes, slightly slower searches
    - Compared to B-Tree: Better for in-memory, worse for disk-based storage
    
    Best for:
    - General-purpose sorted collections (maps, sets)
    - When insert/delete and search performance matter equally
    - Implementing associative containers (key-value stores)
    - When guaranteed O(log n) worst-case is required
    - In-memory databases and indices
    
    Not recommended for:
    - Read-heavy workloads (AVL Tree is better)
    - Disk-based storage (B-Tree is better)
    - Simple, unsorted data (Hash Map is faster)
    - Memory-constrained environments (overhead for parent pointers + color)
    - When probabilistic guarantees suffice (Skip List is simpler)
    
    Following eXonware Priorities:
    1. Usability: Self-balancing ensures consistent O(log n) performance
    2. Maintainability: Industry-standard algorithm, well-documented
    3. Performance: Optimized balance between insert and search operations
    4. Extensibility: Can be enhanced with augmentation (order statistics, intervals)
    5. Security: Input validation, bounded height prevents worst-case attacks
    
    Industry Best Practices:
    - Follows Cormen CLRS textbook implementation
    - Maintains 5 red-black properties:
      1. Every node is red or black
      2. Root is black
      3. Leaves (NIL) are black
      4. Red nodes have black children
      5. All paths have same number of black nodes
    - Uses case-based fixup (standard approach)
    - Tracks performance statistics
    
    Performance Note:
    Red-Black Trees provide GUARANTEED O(log n) in worst-case.
    Height is at most 2*log(n+1), ensuring consistent performance
    even with adversarial input patterns. This makes them ideal for
    production systems requiring predictable latency.
    """
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the red-black tree strategy."""
        super().__init__(NodeMode.RED_BLACK_TREE, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        
        # Core red-black tree
        self._root: Optional[RedBlackTreeNode] = None
        self._size = 0
        
        # Statistics
        self._total_insertions = 0
        self._total_deletions = 0
        self._total_rotations = 0
        self._max_height = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the red-black tree strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _get_height(self, node: Optional[RedBlackTreeNode]) -> int:
        """Get height of node."""
        if not node:
            return 0
        
        left_height = self._get_height(node.left)
        right_height = self._get_height(node.right)
        return 1 + max(left_height, right_height)
    
    def _rotate_left(self, node: RedBlackTreeNode) -> None:
        """Left rotation around node."""
        right_child = node.right
        if not right_child:
            return
        
        # Update parent connections
        node.right = right_child.left
        if right_child.left:
            right_child.left.parent = node
        
        right_child.parent = node.parent
        if not node.parent:
            self._root = right_child
        elif node == node.parent.left:
            node.parent.left = right_child
        else:
            node.parent.right = right_child
        
        # Update rotation
        right_child.left = node
        node.parent = right_child
        
        self._total_rotations += 1
    
    def _rotate_right(self, node: RedBlackTreeNode) -> None:
        """Right rotation around node."""
        left_child = node.left
        if not left_child:
            return
        
        # Update parent connections
        node.left = left_child.right
        if left_child.right:
            left_child.right.parent = node
        
        left_child.parent = node.parent
        if not node.parent:
            self._root = left_child
        elif node == node.parent.right:
            node.parent.right = left_child
        else:
            node.parent.left = left_child
        
        # Update rotation
        left_child.right = node
        node.parent = left_child
        
        self._total_rotations += 1
    
    def _fix_insertion(self, node: RedBlackTreeNode) -> None:
        """Fix red-black tree properties after insertion."""
        while node.parent and node.parent.is_red():
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle and uncle.is_red():
                    # Case 1: Uncle is red
                    node.parent.set_black()
                    uncle.set_black()
                    node.parent.parent.set_red()
                    node = node.parent.parent
                else:
                    # Case 2: Uncle is black and node is right child
                    if node == node.parent.right:
                        node = node.parent
                        self._rotate_left(node)
                    
                    # Case 3: Uncle is black and node is left child
                    node.parent.set_black()
                    node.parent.parent.set_red()
                    self._rotate_right(node.parent.parent)
            else:
                # Mirror cases for right side
                uncle = node.parent.parent.left
                if uncle and uncle.is_red():
                    # Case 1: Uncle is red
                    node.parent.set_black()
                    uncle.set_black()
                    node.parent.parent.set_red()
                    node = node.parent.parent
                else:
                    # Case 2: Uncle is black and node is left child
                    if node == node.parent.left:
                        node = node.parent
                        self._rotate_right(node)
                    
                    # Case 3: Uncle is black and node is right child
                    node.parent.set_black()
                    node.parent.parent.set_red()
                    self._rotate_left(node.parent.parent)
        
        self._root.set_black()
    
    def _insert_node(self, key: str, value: Any) -> bool:
        """Insert node with given key and value."""
        normalized_key = self._normalize_key(key)
        
        # Create new node
        new_node = RedBlackTreeNode(key, value, 'RED')
        
        # Find insertion point
        current = self._root
        parent = None
        
        while current:
            parent = current
            current_key = self._normalize_key(current.key)
            if normalized_key < current_key:
                current = current.left
            elif normalized_key > current_key:
                current = current.right
            else:
                # Key already exists, update value
                current.value = value
                return False
        
        # Insert new node
        new_node.parent = parent
        if not parent:
            self._root = new_node
        elif normalized_key < self._normalize_key(parent.key):
            parent.left = new_node
        else:
            parent.right = new_node
        
        # Fix red-black tree properties
        self._fix_insertion(new_node)
        
        self._size += 1
        self._total_insertions += 1
        self._max_height = max(self._max_height, self._get_height(self._root))
        return True
    
    def _find_node(self, key: str) -> Optional[RedBlackTreeNode]:
        """Find node with given key."""
        normalized_key = self._normalize_key(key)
        current = self._root
        
        while current:
            current_key = self._normalize_key(current.key)
            if normalized_key < current_key:
                current = current.left
            elif normalized_key > current_key:
                current = current.right
            else:
                return current
        
        return None
    
    def _find_min(self, node: RedBlackTreeNode) -> RedBlackTreeNode:
        """Find minimum node in subtree."""
        while node.left:
            node = node.left
        return node
    
    def _find_max(self, node: RedBlackTreeNode) -> RedBlackTreeNode:
        """Find maximum node in subtree."""
        while node.right:
            node = node.right
        return node
    
    def _delete_node(self, key: str) -> bool:
        """Delete node with given key."""
        node = self._find_node(key)
        if not node:
            return False
        
        # Store original color
        original_color = node.color
        
        # Case 1: No left child
        if not node.left:
            replacement = node.right
            self._transplant(node, node.right)
        # Case 2: No right child
        elif not node.right:
            replacement = node.left
            self._transplant(node, node.left)
        # Case 3: Two children
        else:
            # Find successor (minimum in right subtree)
            successor = self._find_min(node.right)
            original_color = successor.color
            replacement = successor.right
            
            if successor.parent == node:
                # Successor is direct right child
                if replacement:
                    replacement.parent = successor
            else:
                # Successor is deeper in tree
                self._transplant(successor, successor.right)
                successor.right = node.right
                successor.right.parent = successor
            
            # Replace node with successor
            self._transplant(node, successor)
            successor.left = node.left
            successor.left.parent = successor
            successor.color = node.color
        
        # Fix red-black tree properties if needed
        if original_color == 'BLACK' and replacement:
            self._fix_deletion(replacement)
        
        self._size -= 1
        self._total_deletions += 1
        return True
    
    def _transplant(self, old_node: RedBlackTreeNode, new_node: Optional[RedBlackTreeNode]) -> None:
        """Replace old_node with new_node in the tree."""
        if not old_node.parent:
            self._root = new_node
        elif old_node == old_node.parent.left:
            old_node.parent.left = new_node
        else:
            old_node.parent.right = new_node
        
        if new_node:
            new_node.parent = old_node.parent
    
    def _fix_deletion(self, node: RedBlackTreeNode) -> None:
        """Fix red-black tree properties after deletion."""
        while node != self._root and node.is_black():
            parent = node.parent
            if not parent:
                break
                
            if node == parent.left:
                sibling = parent.right
                if sibling and sibling.is_red():
                    # Case 1: Sibling is red
                    sibling.set_black()
                    parent.set_red()
                    self._rotate_left(parent)
                    sibling = parent.right
                
                if sibling:
                    if ((not sibling.left or sibling.left.is_black()) and 
                        (not sibling.right or sibling.right.is_black())):
                        # Case 2: Sibling and its children are black
                        sibling.set_red()
                        node = parent
                    else:
                        if not sibling.right or sibling.right.is_black():
                            # Case 3: Sibling's right child is black
                            if sibling.left:
                                sibling.left.set_black()
                            sibling.set_red()
                            self._rotate_right(sibling)
                            sibling = parent.right
                        
                        # Case 4: Sibling's right child is red
                        if sibling:
                            sibling.color = parent.color
                            parent.set_black()
                            if sibling.right:
                                sibling.right.set_black()
                            self._rotate_left(parent)
                        node = self._root
                else:
                    break
            else:
                # Mirror cases for right side
                sibling = parent.left
                if sibling and sibling.is_red():
                    # Case 1: Sibling is red
                    sibling.set_black()
                    parent.set_red()
                    self._rotate_right(parent)
                    sibling = parent.left
                
                if sibling:
                    if ((not sibling.right or sibling.right.is_black()) and 
                        (not sibling.left or sibling.left.is_black())):
                        # Case 2: Sibling and its children are black
                        sibling.set_red()
                        node = parent
                    else:
                        if not sibling.left or sibling.left.is_black():
                            # Case 3: Sibling's left child is black
                            if sibling.right:
                                sibling.right.set_black()
                            sibling.set_red()
                            self._rotate_left(sibling)
                            sibling = parent.left
                        
                        # Case 4: Sibling's left child is red
                        if sibling:
                            sibling.color = parent.color
                            parent.set_black()
                            if sibling.left:
                                sibling.left.set_black()
                            self._rotate_right(parent)
                        node = self._root
                else:
                    break
        
        if node:
            node.set_black()
    
    def _inorder_traversal(self, node: Optional[RedBlackTreeNode]) -> Iterator[Tuple[str, Any]]:
        """In-order traversal of tree."""
        if node:
            yield from self._inorder_traversal(node.left)
            yield (node.key, node.value)
            yield from self._inorder_traversal(node.right)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        self._insert_node(key, value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        if not isinstance(key, str):
            key = str(key)
        
        node = self._find_node(key)
        return node.value if node else default
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        return self._delete_node(key)
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        if not isinstance(key, str):
            key = str(key)
        
        return self._find_node(key) is not None
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._size = 0
    
    def size(self) -> int:
        """Get number of key-value pairs."""
        return self._size
    
    def __len__(self) -> int:
        """Get number of key-value pairs."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        return dict(self.items())
    
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
    # RED-BLACK TREE SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_min(self) -> Optional[Tuple[str, Any]]:
        """Get the minimum key-value pair."""
        if not self._root:
            return None
        
        min_node = self._find_min(self._root)
        return (min_node.key, min_node.value)
    
    def get_max(self) -> Optional[Tuple[str, Any]]:
        """Get the maximum key-value pair."""
        if not self._root:
            return None
        
        max_node = self._find_max(self._root)
        return (max_node.key, max_node.value)
    
    def get_height(self) -> int:
        """Get the height of the tree."""
        return self._get_height(self._root)
    
    def is_valid_rb_tree(self) -> bool:
        """Check if tree satisfies red-black tree properties."""
        if not self._root:
            return True
        
        # Check if root is black
        if self._root.is_red():
            return False
        
        # Check all paths have same number of black nodes
        def check_black_height(node: Optional[RedBlackTreeNode]) -> int:
            if not node:
                return 1
            
            left_height = check_black_height(node.left)
            right_height = check_black_height(node.right)
            
            if left_height != right_height:
                return -1
            
            return left_height + (1 if node.is_black() else 0)
        
        return check_black_height(self._root) != -1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'size': self._size,
            'height': self._get_height(self._root),
            'max_height': self._max_height,
            'total_insertions': self._total_insertions,
            'total_deletions': self._total_deletions,
            'total_rotations': self._total_rotations,
            'is_valid_rb_tree': self.is_valid_rb_tree(),
            'strategy': 'RED_BLACK_TREE',
            'backend': 'Self-balancing red-black tree with guaranteed O(log n) height',
            'traits': [trait.name for trait in NodeTrait if self.has_trait(trait)]
        }
