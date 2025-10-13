"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/dawg.py

DAWG (Directed Acyclic Word Graph) Node Strategy Implementation

This module implements the DAWG strategy for minimal automaton representation
of string sets with massive memory savings over standard tries.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
Generation Date: 12-Oct-2025
"""

from typing import Any, Iterator, List, Dict, Optional, Set, Tuple
from collections import defaultdict
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeError, XWNodeValueError


class DawgNode:
    """
    Node in the DAWG structure.
    
    WHY suffix sharing:
    - Multiple words can share common suffixes
    - Drastically reduces memory compared to trie
    - 10-100x smaller for large dictionaries
    """
    
    def __init__(self):
        """Initialize DAWG node."""
        self.edges: Dict[str, 'DawgNode'] = {}
        self.is_final = False
        self.value: Any = None
        self._hash: Optional[int] = None
        self._id = id(self)
    
    def __hash__(self) -> int:
        """
        Hash based on structure for suffix sharing.
        
        WHY structural hashing:
        - Identifies identical subtrees for merging
        - Enables suffix sharing optimization
        - Critical for DAWG compression
        """
        if self._hash is None:
            # Hash based on edges and final status
            edge_tuple = tuple(sorted(
                (char, id(node)) for char, node in self.edges.items()
            ))
            self._hash = hash((edge_tuple, self.is_final, self.value))
        return self._hash
    
    def __eq__(self, other: Any) -> bool:
        """
        Structural equality for suffix sharing.
        
        WHY structural equality:
        - Two nodes with same structure can be merged
        - Enables automatic suffix compression
        """
        if not isinstance(other, DawgNode):
            return False
        
        if self.is_final != other.is_final:
            return False
        
        if self.value != other.value:
            return False
        
        if len(self.edges) != len(other.edges):
            return False
        
        for char, node in self.edges.items():
            if char not in other.edges:
                return False
            if node != other.edges[char]:
                return False
        
        return True
    
    def invalidate_hash(self) -> None:
        """Invalidate cached hash after modification."""
        self._hash = None


class DawgStrategy(ANodeTreeStrategy):
    """
    DAWG (Directed Acyclic Word Graph) strategy for minimal string storage.
    
    WHY DAWG:
    - 10-100x memory reduction vs standard trie through suffix sharing
    - Perfect for large dictionaries, lexicons, spell checkers
    - Fast prefix queries while using minimal space
    - Deterministic automaton enables efficient string matching
    - Excellent for autocomplete with memory constraints
    
    WHY this implementation:
    - Incremental construction allows online updates
    - Structural hashing enables automatic suffix detection
    - Final state markers support both sets and maps
    - Value storage enables key-value DAWG variant
    - Lazy minimization balances construction time and space
    
    Time Complexity:
    - Insert: O(k) where k is string length (amortized with minimization)
    - Search: O(k) where k is string length
    - Prefix query: O(k + m) where m is result size
    - Delete: O(k) with lazy minimization
    - Minimization: O(n log n) where n is total nodes
    
    Space Complexity: O(c) where c is total unique characters across all suffixes
    (10-100x smaller than trie which is O(alphabet_size × total_chars))
    
    Trade-offs:
    - Advantage: Massive space savings (10-100x vs trie)
    - Advantage: Still O(k) lookups like trie
    - Advantage: Perfect for read-heavy dictionary workloads
    - Limitation: Construction more complex than trie
    - Limitation: Minimization step adds overhead
    - Limitation: Best for static or slowly-changing dictionaries
    - Compared to Trie: Much smaller, same lookup speed
    - Compared to HashMap: Supports prefix queries, more memory efficient
    
    Best for:
    - Large dictionaries and lexicons (>100k words)
    - Spell checkers and autocomplete systems
    - Natural language processing applications
    - Genomics sequence storage
    - Memory-constrained environments
    - Read-heavy string matching workloads
    
    Not recommended for:
    - Small string sets (<1000 words) - overhead not worth it
    - Frequently updated dictionaries - minimization expensive
    - Non-string keys
    - Random access by index (use array instead)
    - When trie memory usage is acceptable
    - Real-time insertion requirements
    
    Following eXonware Priorities:
    1. Security: Validates string inputs, prevents malicious data
    2. Usability: Simple API for dictionary operations, clear errors
    3. Maintainability: Clean automaton structure, well-documented
    4. Performance: O(k) operations with minimal memory
    5. Extensibility: Easy to add pattern matching, fuzzy search
    
    Industry Best Practices:
    - Follows Daciuk et al. incremental construction algorithm
    - Implements structural hashing for suffix detection
    - Supports both DAWG (set) and DAFSA (map) variants
    - Provides lazy minimization for performance
    - Compatible with Aho-Corasick for multi-pattern matching
    """
    
    # Tree node type for classification
    STRATEGY_TYPE: NodeType = NodeType.TREE
    
    def __init__(self, mode: NodeMode = NodeMode.DAWG,
                 traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize DAWG strategy.
        
        Args:
            mode: Node mode (DAWG)
            traits: Node traits
            **options: Additional options
        """
        super().__init__(mode, traits, **options)
        
        self._root = DawgNode()
        self._size = 0
        self._word_count = 0
        
        # For incremental minimization
        self._unchecked_nodes: List[Tuple[DawgNode, str, DawgNode]] = []
        self._minimized_nodes: Dict[DawgNode, DawgNode] = {}
        self._previous_word = ""
    
    def get_supported_traits(self) -> NodeTrait:
        """Get supported traits."""
        return (NodeTrait.HIERARCHICAL | NodeTrait.INDEXED | 
                NodeTrait.MEMORY_EFFICIENT | NodeTrait.PREFIX_TREE)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """
        Insert word into DAWG.
        
        Args:
            key: String key (word)
            value: Associated value
            
        Raises:
            XWNodeValueError: If key is not a string
        """
        # Security: Type validation
        if not isinstance(key, str):
            raise XWNodeValueError(
                f"DAWG requires string keys, got {type(key).__name__}"
            )
        
        # Security: Empty string validation
        if not key:
            raise XWNodeValueError("DAWG does not support empty string keys")
        
        # Incremental insertion with minimization
        self._insert_with_minimization(key, value)
        self._size += 1
        self._word_count += 1
    
    def _insert_with_minimization(self, word: str, value: Any) -> None:
        """
        Insert word using incremental minimization algorithm.
        
        WHY incremental minimization:
        - Maintains DAWG property during construction
        - Avoids full reconstruction after each insert
        - Balances construction time and space efficiency
        """
        # Find common prefix with previous word
        common_prefix_len = 0
        for i in range(min(len(word), len(self._previous_word))):
            if word[i] == self._previous_word[i]:
                common_prefix_len += 1
            else:
                break
        
        # Minimize nodes from previous word
        self._minimize(common_prefix_len)
        
        # Add suffix for current word
        current_node = self._root
        for i in range(len(self._unchecked_nodes)):
            if i < common_prefix_len:
                current_node = self._unchecked_nodes[i][2]
        
        for char in word[common_prefix_len:]:
            next_node = DawgNode()
            current_node.edges[char] = next_node
            self._unchecked_nodes.append((current_node, char, next_node))
            current_node = next_node
        
        # Mark as final and store value
        current_node.is_final = True
        current_node.value = value
        self._previous_word = word
    
    def _minimize(self, down_to: int) -> None:
        """
        Minimize unchecked nodes down to specified prefix length.
        
        Args:
            down_to: Prefix length to minimize to
            
        WHY minimization:
        - Merges structurally equivalent nodes
        - Achieves suffix sharing compression
        - Maintains DAWG minimality property
        """
        # Pop unchecked nodes and minimize
        while len(self._unchecked_nodes) > down_to:
            parent, char, child = self._unchecked_nodes.pop()
            
            # Check if equivalent node exists
            if child in self._minimized_nodes:
                # Replace with existing equivalent node
                parent.edges[char] = self._minimized_nodes[child]
            else:
                # Add to minimized set
                self._minimized_nodes[child] = child
            
            parent.invalidate_hash()
    
    def finish_construction(self) -> None:
        """
        Finish DAWG construction by minimizing all remaining nodes.
        
        WHY explicit finish:
        - Completes minimization for all inserted words
        - Maximizes compression ratio
        - Should be called after bulk inserts
        """
        self._minimize(0)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Retrieve value by key.
        
        Args:
            key: String key
            default: Default value if not found
            
        Returns:
            Value or default
        """
        if not isinstance(key, str):
            return default
        
        current_node = self._root
        
        # Traverse DAWG
        for char in key:
            if char not in current_node.edges:
                return default
            current_node = current_node.edges[char]
        
        # Check if final state
        if current_node.is_final:
            return current_node.value
        
        return default
    
    def has(self, key: Any) -> bool:
        """
        Check if key exists.
        
        Args:
            key: String key
            
        Returns:
            True if exists, False otherwise
        """
        if not isinstance(key, str):
            return False
        
        current_node = self._root
        
        # Traverse DAWG
        for char in key:
            if char not in current_node.edges:
                return False
            current_node = current_node.edges[char]
        
        return current_node.is_final
    
    def delete(self, key: Any) -> bool:
        """
        Remove key from DAWG.
        
        Args:
            key: String key
            
        Returns:
            True if deleted, False if not found
            
        Note: This is a simplified deletion. Full implementation
        would rebuild DAWG for optimal compression.
        """
        if not isinstance(key, str):
            return False
        
        # Navigate to node
        path: List[Tuple[DawgNode, str]] = []
        current_node = self._root
        
        for char in key:
            if char not in current_node.edges:
                return False
            path.append((current_node, char))
            current_node = current_node.edges[char]
        
        # Check if it's a final node
        if not current_node.is_final:
            return False
        
        # Unmark as final
        current_node.is_final = False
        current_node.value = None
        current_node.invalidate_hash()
        
        # Remove nodes if they have no children and aren't final
        for i in range(len(path) - 1, -1, -1):
            parent, char = path[i]
            child = parent.edges[char]
            
            if not child.edges and not child.is_final:
                del parent.edges[char]
                parent.invalidate_hash()
            else:
                break
        
        self._size -= 1
        self._word_count -= 1
        return True
    
    def keys(self) -> Iterator[Any]:
        """
        Get iterator over all keys in lexicographic order.
        
        Returns:
            Iterator of string keys
        """
        yield from self._collect_words(self._root, "")
    
    def _collect_words(self, node: DawgNode, prefix: str) -> Iterator[str]:
        """
        Recursively collect all words from node.
        
        Args:
            node: Current DAWG node
            prefix: Current prefix string
            
        Yields:
            Complete words in lexicographic order
        """
        if node.is_final:
            yield prefix
        
        # Traverse in sorted order for lexicographic output
        for char in sorted(node.edges.keys()):
            yield from self._collect_words(node.edges[char], prefix + char)
    
    def values(self) -> Iterator[Any]:
        """
        Get iterator over all values in key-sorted order.
        
        Returns:
            Iterator of values
        """
        for key in self.keys():
            yield self.get(key)
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """
        Get iterator over all key-value pairs.
        
        Returns:
            Iterator of (key, value) tuples
        """
        for key in self.keys():
            yield (key, self.get(key))
    
    def __len__(self) -> int:
        """Get number of words."""
        return self._word_count
    
    def to_native(self) -> Any:
        """
        Convert to native Python dict.
        
        Returns:
            Dictionary representation
        """
        return dict(self.items())
    
    # ============================================================================
    # DAWG-SPECIFIC OPERATIONS
    # ============================================================================
    
    def has_prefix(self, prefix: str) -> bool:
        """
        Check if any word starts with prefix.
        
        Args:
            prefix: Prefix string to check
            
        Returns:
            True if prefix exists, False otherwise
            
        Raises:
            XWNodeValueError: If prefix is not a string
        """
        if not isinstance(prefix, str):
            raise XWNodeValueError(
                f"Prefix must be string, got {type(prefix).__name__}"
            )
        
        current_node = self._root
        
        for char in prefix:
            if char not in current_node.edges:
                return False
            current_node = current_node.edges[char]
        
        return True
    
    def get_with_prefix(self, prefix: str) -> List[str]:
        """
        Get all words with given prefix.
        
        Args:
            prefix: Prefix string
            
        Returns:
            List of words starting with prefix
            
        Raises:
            XWNodeValueError: If prefix is not a string
        """
        if not isinstance(prefix, str):
            raise XWNodeValueError(
                f"Prefix must be string, got {type(prefix).__name__}"
            )
        
        # Navigate to prefix node
        current_node = self._root
        for char in prefix:
            if char not in current_node.edges:
                return []
            current_node = current_node.edges[char]
        
        # Collect all words from this node
        return list(self._collect_words(current_node, prefix))
    
    def longest_prefix(self, text: str) -> Optional[str]:
        """
        Find longest prefix in DAWG that matches text.
        
        Args:
            text: Text to search
            
        Returns:
            Longest matching prefix or None
            
        Raises:
            XWNodeValueError: If text is not a string
        """
        if not isinstance(text, str):
            raise XWNodeValueError(
                f"Text must be string, got {type(text).__name__}"
            )
        
        current_node = self._root
        longest = None
        current_prefix = ""
        
        for char in text:
            if char not in current_node.edges:
                break
            current_prefix += char
            current_node = current_node.edges[char]
            
            if current_node.is_final:
                longest = current_prefix
        
        return longest
    
    def count_words_with_prefix(self, prefix: str) -> int:
        """
        Count words with given prefix.
        
        Args:
            prefix: Prefix string
            
        Returns:
            Number of words with prefix
        """
        return len(self.get_with_prefix(prefix))
    
    # ============================================================================
    # COMPRESSION STATISTICS
    # ============================================================================
    
    def get_node_count(self) -> int:
        """
        Count total nodes in DAWG.
        
        Returns:
            Number of nodes
        """
        visited: Set[int] = set()
        return self._count_nodes(self._root, visited)
    
    def _count_nodes(self, node: DawgNode, visited: Set[int]) -> int:
        """
        Recursively count unique nodes.
        
        Args:
            node: Current node
            visited: Set of visited node IDs
            
        Returns:
            Node count
        """
        if node._id in visited:
            return 0
        
        visited.add(node._id)
        count = 1
        
        for child in node.edges.values():
            count += self._count_nodes(child, visited)
        
        return count
    
    def get_compression_ratio(self) -> float:
        """
        Calculate compression ratio vs standard trie.
        
        Returns:
            Estimated compression ratio
            
        WHY this matters:
        - Quantifies space savings
        - Validates DAWG effectiveness
        - Helps choose between DAWG and trie
        """
        if self._word_count == 0:
            return 1.0
        
        # Estimate trie nodes (sum of word lengths)
        trie_nodes = sum(len(word) for word in self.keys())
        
        # Actual DAWG nodes
        dawg_nodes = self.get_node_count()
        
        if dawg_nodes == 0:
            return 1.0
        
        return trie_nodes / dawg_nodes
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive DAWG statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'word_count': self._word_count,
            'node_count': self.get_node_count(),
            'compression_ratio': self.get_compression_ratio(),
            'minimized_nodes': len(self._minimized_nodes),
            'unchecked_nodes': len(self._unchecked_nodes),
            'memory_saved_percent': (1 - 1/self.get_compression_ratio()) * 100
        }
    
    # ============================================================================
    # BULK OPERATIONS
    # ============================================================================
    
    def build_from_sorted_words(self, words: List[str], values: Optional[List[Any]] = None) -> None:
        """
        Build DAWG from sorted word list efficiently.
        
        Args:
            words: Sorted list of words
            values: Optional list of values (must match words length)
            
        Raises:
            XWNodeValueError: If words not sorted or values length mismatch
            
        WHY sorted requirement:
        - Enables incremental minimization algorithm
        - Ensures optimal compression
        - O(n) construction vs O(n log n) for unsorted
        """
        # Security: Validation
        if not all(isinstance(w, str) for w in words):
            raise XWNodeValueError("All words must be strings")
        
        # Check sorted
        for i in range(len(words) - 1):
            if words[i] > words[i + 1]:
                raise XWNodeValueError(
                    f"Words must be sorted, but '{words[i]}' > '{words[i+1]}'"
                )
        
        if values is not None and len(values) != len(words):
            raise XWNodeValueError(
                f"Values length ({len(values)}) must match words length ({len(words)})"
            )
        
        # Clear existing data
        self.clear()
        
        # Insert all words
        for i, word in enumerate(words):
            value = values[i] if values else None
            self.put(word, value)
        
        # Final minimization
        self.finish_construction()
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Retrieve value by key.
        
        Args:
            key: String key
            default: Default value
            
        Returns:
            Value or default
        """
        if not isinstance(key, str):
            return default
        
        current_node = self._root
        
        for char in key:
            if char not in current_node.edges:
                return default
            current_node = current_node.edges[char]
        
        if current_node.is_final:
            return current_node.value if current_node.value is not None else default
        
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        if not isinstance(key, str):
            return False
        
        current_node = self._root
        
        for char in key:
            if char not in current_node.edges:
                return False
            current_node = current_node.edges[char]
        
        return current_node.is_final
    
    # ============================================================================
    # PATTERN MATCHING
    # ============================================================================
    
    def fuzzy_search(self, word: str, max_distance: int = 1) -> List[str]:
        """
        Find words within edit distance.
        
        Args:
            word: Search word
            max_distance: Maximum Levenshtein distance
            
        Returns:
            List of matching words
            
        WHY fuzzy search:
        - Essential for spell checkers
        - Handles typos in autocomplete
        - Improves usability
        """
        results = []
        
        def _fuzzy_helper(node: DawgNode, prefix: str, 
                         remaining: str, distance: int) -> None:
            """Recursive fuzzy matching."""
            # Found match
            if not remaining:
                if node.is_final and distance <= max_distance:
                    results.append(prefix)
                # Continue for insertions
                if distance < max_distance:
                    for char, child in node.edges.items():
                        _fuzzy_helper(child, prefix + char, "", distance + 1)
                return
            
            # Exact match
            if remaining[0] in node.edges:
                _fuzzy_helper(
                    node.edges[remaining[0]], 
                    prefix + remaining[0],
                    remaining[1:], 
                    distance
                )
            
            # Try edits if distance allows
            if distance < max_distance:
                # Deletion
                _fuzzy_helper(node, prefix, remaining[1:], distance + 1)
                
                # Substitution and Insertion
                for char, child in node.edges.items():
                    # Substitution
                    _fuzzy_helper(child, prefix + char, remaining[1:], distance + 1)
                    # Insertion
                    _fuzzy_helper(child, prefix + char, remaining, distance + 1)
        
        _fuzzy_helper(self._root, "", word, 0)
        return results
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = DawgNode()
        self._size = 0
        self._word_count = 0
        self._unchecked_nodes.clear()
        self._minimized_nodes.clear()
        self._previous_word = ""
    
    def is_empty(self) -> bool:
        """Check if empty."""
        return self._word_count == 0
    
    def size(self) -> int:
        """Get number of words."""
        return self._word_count
    
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
        """Find value by key."""
        return self.get(key)
    
    def insert(self, key: Any, value: Any = None) -> None:
        """Insert key-value pair."""
        self.put(key, value)
    
    def __str__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        return (f"DawgStrategy(words={stats['word_count']}, "
                f"nodes={stats['node_count']}, "
                f"compression={stats['compression_ratio']:.1f}x)")
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"DawgStrategy(mode={self.mode.name}, words={self._word_count}, traits={self.traits})"
    
    # ============================================================================
    # FACTORY METHOD
    # ============================================================================
    
    @classmethod
    def create_from_data(cls, data: Any) -> 'DawgStrategy':
        """
        Create DAWG from data.
        
        Args:
            data: Dictionary with string keys or list of strings
            
        Returns:
            New DawgStrategy instance
            
        Raises:
            XWNodeValueError: If data contains non-string keys
        """
        instance = cls()
        
        if isinstance(data, dict):
            # Sort keys for optimal compression
            sorted_keys = sorted(data.keys())
            for key in sorted_keys:
                if not isinstance(key, str):
                    raise XWNodeValueError(
                        f"DAWG requires string keys, found {type(key).__name__}"
                    )
                instance.put(key, data[key])
            instance.finish_construction()
        elif isinstance(data, (list, tuple)):
            # Treat as list of strings (set variant)
            sorted_words = sorted(str(item) for item in data)
            for word in sorted_words:
                instance.put(word, None)
            instance.finish_construction()
        else:
            # Store scalar as single word
            instance.put(str(data), data)
        
        return instance

