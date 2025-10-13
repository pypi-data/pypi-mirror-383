"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/deque.py

Deque Strategy Implementation

Production-grade double-ended queue data structure.

Best Practices Implemented:
- Python's collections.deque for optimal performance
- O(1) operations at both ends
- Thread-safe for certain operations
- Memory-efficient with block-based storage
- Proper deque semantics following industry standards

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.25
Generation Date: October 12, 2025
"""

from typing import Any, Iterator, List, Optional, Dict
from collections import deque
from .base import ANodeLinearStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class DequeStrategy(ANodeLinearStrategy):
    """
    Production-grade Deque (Double-Ended Queue) node strategy.
    
    Optimized for:
    - Sliding window algorithms (maximum/minimum in window)
    - Breadth-first search with bidirectional traversal
    - Work-stealing algorithms (task scheduling)
    - Palindrome checking
    - Undo/redo with bounded history
    - Cache implementations (LRU with deque)
    
    Performance:
    - Append (both ends): O(1)
    - Pop (both ends): O(1)
    - Rotate: O(k) where k is rotation count
    - Random access: O(n)
    - Space: O(n)
    
    Security:
    - Bounds checking on all operations
    - Safe empty deque handling
    - Optional max size for memory protection
    
    Thread-Safety:
    - Thread-safe for append/pop on same end
    - NOT thread-safe for operations on opposite ends
    - Use queue.Queue for full thread-safety
    
    Implementation Details:
    - Uses collections.deque (doubly-linked list of blocks)
    - Block size optimized for cache performance
    - Memory-efficient with contiguous memory blocks
    
    Follows eXonware Priorities:
    1. Security: Bounds checking, memory limits
    2. Usability: Intuitive double-ended interface
    3. Maintainability: Clean implementation using stdlib
    4. Performance: O(1) operations at both ends
    5. Extensibility: Easy to build LRU caches and other patterns
    """
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.LINEAR
    
    __slots__ = ('_deque', '_max_size')
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize an empty deque.
        
        Args:
            traits: Additional node traits
            **options:
                max_size: Optional maximum deque size (default: unlimited)
                initial_values: Optional list of initial values
        """
        super().__init__(
            NodeMode.DEQUE,
            traits | NodeTrait.DOUBLE_ENDED | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE,
            **options
        )
        self._max_size: Optional[int] = options.get('max_size')
        initial_values = options.get('initial_values', [])
        self._deque: deque = deque(initial_values, maxlen=self._max_size)
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the deque strategy."""
        return NodeTrait.DOUBLE_ENDED | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE
    
    # ============================================================================
    # CORE DEQUE OPERATIONS (Industry Standard)
    # ============================================================================
    
    def append(self, value: Any) -> None:
        """
        Add an item to the right end.
        
        Time: O(1)
        Space: O(1)
        
        Note: If max_size is set, leftmost item is discarded when full
        """
        self._deque.append(value)
    
    def appendleft(self, value: Any) -> None:
        """
        Add an item to the left end.
        
        Time: O(1)
        Space: O(1)
        
        Note: If max_size is set, rightmost item is discarded when full
        """
        self._deque.appendleft(value)
    
    def pop(self) -> Any:
        """
        Remove and return an item from the right end.
        
        Time: O(1)
        Space: O(1)
        
        Raises:
            IndexError: If deque is empty
        """
        if self.is_empty():
            raise IndexError("pop from empty deque")
        
        return self._deque.pop()
    
    def popleft(self) -> Any:
        """
        Remove and return an item from the left end.
        
        Time: O(1)
        Space: O(1)
        
        Raises:
            IndexError: If deque is empty
        """
        if self.is_empty():
            raise IndexError("pop from empty deque")
        
        return self._deque.popleft()
    
    def peek_right(self) -> Any:
        """
        Peek at the rightmost item without removing it.
        
        Time: O(1)
        
        Raises:
            IndexError: If deque is empty
        """
        if self.is_empty():
            raise IndexError("peek from empty deque")
        
        return self._deque[-1]
    
    def peek_left(self) -> Any:
        """
        Peek at the leftmost item without removing it.
        
        Time: O(1)
        
        Raises:
            IndexError: If deque is empty
        """
        if self.is_empty():
            raise IndexError("peek from empty deque")
        
        return self._deque[0]
    
    def rotate(self, n: int = 1) -> None:
        """
        Rotate the deque n steps to the right (positive) or left (negative).
        
        Time: O(k) where k = abs(n)
        Space: O(1)
        
        Args:
            n: Number of steps to rotate (positive=right, negative=left)
        """
        self._deque.rotate(n)
    
    def reverse(self) -> None:
        """
        Reverse the deque in place.
        
        Time: O(n)
        Space: O(1)
        """
        self._deque.reverse()
    
    def extend(self, values: List[Any]) -> None:
        """
        Extend the deque by appending elements from the iterable (right end).
        
        Time: O(k) where k = len(values)
        """
        self._deque.extend(values)
    
    def extendleft(self, values: List[Any]) -> None:
        """
        Extend the deque by appending elements from the iterable (left end).
        
        Time: O(k) where k = len(values)
        
        Note: Values are added in reverse order
        """
        self._deque.extendleft(values)
    
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (from ANodeStrategy)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store value (appends to right end)."""
        self.append(value if value is not None else key)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key (O(n) search)."""
        for val in self._deque:
            if val == key:
                return val
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists (O(n))."""
        return key in self._deque
    
    def delete(self, key: Any) -> bool:
        """Delete first occurrence of value (O(n))."""
        try:
            self._deque.remove(key)
            return True
        except ValueError:
            return False
    
    def keys(self) -> Iterator[Any]:
        """Get all values as keys."""
        return iter(self._deque)
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        return iter(self._deque)
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get all items as (value, value) pairs."""
        for val in self._deque:
            yield (val, val)
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def size(self) -> int:
        """Get the number of items in the deque."""
        return len(self._deque)
    
    def is_empty(self) -> bool:
        """Check if the deque is empty."""
        return len(self._deque) == 0
    
    def is_full(self) -> bool:
        """Check if deque has reached max_size."""
        return self._max_size is not None and len(self._deque) >= self._max_size
    
    def clear(self) -> None:
        """Clear all items from the deque."""
        self._deque.clear()
        self._record_access("clear")
    
    def count(self, value: Any) -> int:
        """Count occurrences of value."""
        return self._deque.count(value)
    
    def to_list(self) -> List[Any]:
        """Convert deque to list (left to right)."""
        return list(self._deque)
    
    def to_native(self) -> Dict[str, Any]:
        """Convert deque to native dictionary format."""
        return {str(i): val for i, val in enumerate(self._deque)}
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load deque from native dictionary format."""
        self._deque.clear()
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0)
        self._deque.extend(val for _, val in sorted_items)
    
    
    # ============================================================================
    # PYTHON SPECIAL METHODS
    # ============================================================================
    
    def __len__(self) -> int:
        """Return the number of items in the deque."""
        return len(self._deque)
    
    def __bool__(self) -> bool:
        """Return True if deque is not empty."""
        return bool(self._deque)
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate through deque items (left to right)."""
        return iter(self._deque)
    
    def __reversed__(self) -> Iterator[Any]:
        """Iterate in reverse (right to left)."""
        return reversed(self._deque)
    
    def __getitem__(self, index: int) -> Any:
        """Get item at index."""
        return self._deque[index]
    
    def __setitem__(self, index: int, value: Any) -> None:
        """Set item at index."""
        self._deque[index] = value
    
    def __repr__(self) -> str:
        """Professional string representation."""
        return f"DequeStrategy(size={len(self._deque)}, maxlen={self._max_size})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        items = ', '.join(str(item) for item in list(self._deque)[:5])
        suffix = '...' if len(self._deque) > 5 else ''
        return f"Deque[{items}{suffix}]"
    
    # ============================================================================
    # PERFORMANCE METADATA
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'DEQUE',
            'backend': 'collections.deque (doubly-linked list blocks)',
            'complexity': {
                'append': 'O(1)',
                'appendleft': 'O(1)',
                'pop': 'O(1)',
                'popleft': 'O(1)',
                'rotate': 'O(k)',
                'random_access': 'O(n)',
                'space': 'O(n)'
            },
            'thread_safe': 'append/pop same end only',
            'max_size': self._max_size if self._max_size else 'unlimited',
            'block_size': 64  # CPython implementation detail
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'size': len(self._deque),
            'is_empty': self.is_empty(),
            'is_full': self.is_full(),
            'max_size': self._max_size,
            'memory_usage': f"{len(self._deque) * 8} bytes (estimated)"
        }
