"""
Trie Node Strategy Implementation

This module implements the TRIE strategy for efficient string prefix operations.
"""

from typing import Any, Iterator, Dict, List, Optional
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class TrieNode:
    """Node in the trie structure."""
    
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word = False
        self.value: Any = None


class TrieStrategy(ANodeTreeStrategy):
    """
    Trie (Prefix Tree) strategy for efficient prefix-based string operations.
    
    WHY Trie:
    - O(k) operations where k = key length (independent of dataset size)
    - Exceptional prefix matching and autocomplete
    - Natural string organization by shared prefixes
    - Memory-efficient for datasets with common prefixes
    
    WHY this implementation:
    - Standard trie algorithm with character-by-character nodes
    - Dictionary-based children for flexible character sets
    - End-of-word markers for distinguishing prefixes from complete words
    - Supports full Unicode character set
    
    Time Complexity:
    - Insert: O(k) where k = key length
    - Search: O(k) - traverse k characters
    - Delete: O(k) - traverse and cleanup
    - Prefix search: O(k + m) where m = matching words
    - Autocomplete: O(k + m) where m = suggestions
    
    Space Complexity: O(ALPHABET_SIZE * N * K) worst case, often much better
    
    Trade-offs:
    - Advantage: Time independent of dataset size
    - Advantage: Natural prefix operations
    - Advantage: Memory sharing for common prefixes
    - Limitation: Higher memory than hash for unique keys
    - Compared to Hash Map: Slower exact match, better for prefixes
    
    Best for:
    - Autocomplete systems
    - Dictionary/spell check
    - IP routing tables
    - String prefix matching
    
    Not recommended for:
    - Non-string keys (use HASH_MAP)
    - Exact match only (use HASH_MAP)
    - Numeric keys (use B_TREE)
    
    Following eXonware Priorities:
    1. Security: Bounded by key length
    2. Usability: Intuitive for string operations
    3. Maintainability: Well-known algorithm
    4. Performance: O(k) guaranteed
    5. Extensibility: Can add compression (Radix)
    """
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the trie strategy."""
        super().__init__(NodeMode.TRIE, traits, **options)
        self._root = TrieNode()
        self._size = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the trie strategy."""
        return (NodeTrait.ORDERED | NodeTrait.HIERARCHICAL | NodeTrait.INDEXED)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def insert(self, key: Any, value: Any) -> None:
        """Store a key-value pair (key should be string-like)."""
        word = str(key)
        node = self._root
        
        # Traverse/create path
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # Mark end of word and store value
        if not node.is_end_of_word:
            self._size += 1
        node.is_end_of_word = True
        node.value = value
    
    def find(self, key: Any) -> Any:
        """Retrieve a value by key."""
        word = str(key)
        node = self._root
        
        # Traverse path
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        
        return node.value if node.is_end_of_word else None
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        word = str(key)
        return self._delete_helper(self._root, word, 0)
    
    def _delete_helper(self, node: TrieNode, word: str, index: int) -> bool:
        """Helper method for deletion."""
        if index == len(word):
            if node.is_end_of_word:
                node.is_end_of_word = False
                node.value = None
                self._size -= 1
                return True
            return False
        
        char = word[index]
        if char not in node.children:
            return False
        
        deleted = self._delete_helper(node.children[char], word, index + 1)
        
        # Clean up empty nodes
        if deleted and not node.children[char].children and not node.children[char].is_end_of_word:
            del node.children[char]
        
        return deleted
    
    def size(self) -> int:
        """Get the number of items."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if the structure is empty."""
        return self._size == 0
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dictionary."""
        result = {}
        self._collect_words(self._root, "", result)
        return result
    
    def _collect_words(self, node: TrieNode, prefix: str, result: Dict[str, Any]) -> None:
        """Collect all words from trie."""
        if node.is_end_of_word:
            result[prefix] = node.value
        
        for char, child in node.children.items():
            self._collect_words(child, prefix + char, result)
    
    # ============================================================================
    # TREE STRATEGY METHODS
    # ============================================================================
    
    def traverse(self, order: str = 'inorder') -> List[Any]:
        """Traverse tree in specified order."""
        result = []
        self._collect_words(self._root, "", result)
        return list(result.values())
    
    def get_min(self) -> Any:
        """Get minimum key."""
        # Find leftmost word
        node = self._root
        word = ""
        while node.children:
            char = min(node.children.keys())
            word += char
            node = node.children[char]
        return word if node.is_end_of_word else None
    
    def get_max(self) -> Any:
        """Get maximum key."""
        # Find rightmost word
        node = self._root
        word = ""
        while node.children:
            char = max(node.children.keys())
            word += char
            node = node.children[char]
        return word if node.is_end_of_word else None
    
    # ============================================================================
    # AUTO-3 Phase 2 methods
    # ============================================================================
    
    def as_trie(self):
        """Provide Trie behavioral view."""
        return self
    
    def as_heap(self):
        """Provide Heap behavioral view."""
        # TODO: Implement Heap view
        return self
    
    def as_skip_list(self):
        """Provide SkipList behavioral view."""
        # TODO: Implement SkipList view
        return self
    
    # ============================================================================
    # TRIE SPECIFIC OPERATIONS
    # ============================================================================
    
    def prefix_search(self, prefix: str) -> List[str]:
        """Find all keys with given prefix."""
        node = self._root
        
        # Navigate to prefix
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all words with this prefix
        result = []
        self._collect_words(node, prefix, result)
        return list(result.keys())
    
    def longest_common_prefix(self) -> str:
        """Find longest common prefix of all keys."""
        if not self._root.children:
            return ""
        
        prefix = ""
        node = self._root
        
        while len(node.children) == 1 and not node.is_end_of_word:
            char = list(node.children.keys())[0]
            prefix += char
            node = node.children[char]
        
        return prefix
    
    def keys_with_prefix(self, prefix: str) -> List[str]:
        """Get all keys with given prefix."""
        return self.prefix_search(prefix)
    
    def keys_with_suffix(self, suffix: str) -> List[str]:
        """Get all keys with given suffix."""
        # TODO: Implement suffix search
        return []
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        result = {}
        self._collect_words(self._root, "", result)
        return iter(result.keys())
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        result = {}
        self._collect_words(self._root, "", result)
        return iter(result.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        result = {}
        self._collect_words(self._root, "", result)
        return iter(result.items())
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'TRIE',
            'backend': 'Trie tree',
            'complexity': {
                'insert': 'O(m)',
                'search': 'O(m)',
                'delete': 'O(m)',
                'prefix_search': 'O(m + k)',
                'space': 'O(ALPHABET_SIZE * N * M)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'size': self._size,
            'memory_usage': f"{self._size * 32} bytes (estimated)",
            'height': self._get_height()
        }
    
    def _get_height(self) -> int:
        """Get height of trie."""
        return self._height_helper(self._root)
    
    def _height_helper(self, node: TrieNode) -> int:
        """Helper for height calculation."""
        if not node.children:
            return 0
        return 1 + max(self._height_helper(child) for child in node.children.values())
    
    # ============================================================================
    # REQUIRED INTERFACE METHODS (iNodeStrategy)
    # ============================================================================
    
    def create_from_data(self, data: Any) -> 'TrieStrategy':
        """Create strategy instance from data."""
        new_strategy = TrieStrategy(self._traits)
        if isinstance(data, dict):
            for key, value in data.items():
                new_strategy.insert(key, value)
        elif isinstance(data, list):
            for item in data:
                new_strategy.insert(item, item)
        return new_strategy
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get value by path (trie uses find)."""
        result = self.find(path)
        return result if result is not None else default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        return self.find(str(key)) is not None
    
    def put(self, path: str, value: Any) -> 'TrieStrategy':
        """Put value at path."""
        self.insert(path, value)
        return self
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self.find(path) is not None
    
    # Container protocol
    def __len__(self) -> int:
        """Get length."""
        return self._size
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate over values."""
        return self.values()
    
    def __getitem__(self, key: Any) -> Any:
        """Get item by key."""
        result = self.find(key)
        if result is None:
            raise KeyError(str(key))
        return result
    
    def __setitem__(self, key: Any, value: Any) -> None:
        """Set item by key."""
        self.insert(key, value)
    
    def __contains__(self, key: Any) -> bool:
        """Check if key exists."""
        return self.find(key) is not None
    
    # Type checking properties
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self._size == 0
    
    @property
    def is_list(self) -> bool:
        """Check if this is a list node."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        return True  # Trie is dict-like (maps strings to values)
    
    @property
    def is_reference(self) -> bool:
        """Check if this is a reference node."""
        return False
    
    @property
    def is_object(self) -> bool:
        """Check if this is an object node."""
        return False
    
    @property
    def type(self) -> str:
        """Get the type of this node."""
        return "trie"
    
    @property
    def value(self) -> Any:
        """Get the value of this node."""
        return self.to_native()
    
    @property
    def strategy_name(self) -> str:
        """Get strategy name."""
        return "TRIE"
    
    @property
    def supported_traits(self) -> NodeTrait:
        """Get supported traits."""
        return self.get_supported_traits()