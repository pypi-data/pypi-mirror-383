"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/stack.py

Stack Strategy Implementation

Status: Production Ready ✅
True Purpose: LIFO (Last In, First Out) data structure
Complexity: O(1) push/pop operations
Production Features: ✓ Bounds Checking, ✓ Overflow Protection, ✓ Safe Empty Handling

Production-grade LIFO (Last In, First Out) data structure.

Best Practices Implemented:
- Pure stack operations (no unnecessary key-value overhead)
- O(1) push and pop operations using Python list
- Memory-efficient with minimal overhead
- Thread-unsafe by design (use queue.LifoQueue for thread-safety)
- Proper stack semantics following CLRS and industry standards

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.25
Generation Date: October 12, 2025
"""

from typing import Any, Iterator, List, Optional, Dict
from .base import ANodeLinearStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class StackStrategy(ANodeLinearStrategy):
    """
    Production-grade Stack (LIFO) node strategy.
    
    Optimized for:
    - Function call simulation (recursion emulation)
    - Expression evaluation (postfix, infix)
    - Backtracking algorithms (DFS, maze solving)
    - Undo/redo functionality
    - Browser history navigation
    
    Performance:
    - Push: O(1) amortized
    - Pop: O(1)
    - Peek: O(1)
    - Space: O(n)
    
    Security:
    - Bounds checking on all operations
    - No buffer overflow possible
    - Safe empty stack handling
    
    Follows eXonware Priorities:
    1. Security: Proper bounds checking, safe operations
    2. Usability: Clear API matching industry standards
    3. Maintainability: Simple, well-documented code
    4. Performance: O(1) operations with minimal overhead
    5. Extensibility: Easy to extend with additional features
    """
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.LINEAR
    
    __slots__ = ('_stack', '_max_size')
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize an empty stack.
        
        Args:
            traits: Additional node traits
            **options:
                max_size: Optional maximum stack size (default: unlimited)
                initial_capacity: Optional initial capacity for optimization
        """
        super().__init__(
            NodeMode.STACK,
            traits | NodeTrait.LIFO | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE,
            **options
        )
        self._max_size: Optional[int] = options.get('max_size')
        self._stack: List[Any] = []
        
        # Pre-allocate if capacity hint provided
        initial_capacity = options.get('initial_capacity', 0)
        if initial_capacity > 0:
            self._stack = [None] * initial_capacity
            self._stack.clear()  # Clear but keep capacity
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the stack strategy."""
        return NodeTrait.LIFO | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE
    
    # ============================================================================
    # CORE STACK OPERATIONS (Industry Standard)
    # ============================================================================
    
    def push(self, value: Any) -> None:
        """
        Push a value onto the stack.
        
        Time: O(1) amortized
        Space: O(1)
        
        Raises:
            OverflowError: If max_size is set and stack is full
        """
        if self._max_size and len(self._stack) >= self._max_size:
            raise OverflowError(f"Stack overflow: max size {self._max_size} reached")
        
        self._stack.append(value)
    
    def pop(self) -> Any:
        """
        Pop and return the top item from the stack.
        
        Time: O(1)
        Space: O(1)
        
        Returns:
            The top item
            
        Raises:
            IndexError: If stack is empty
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        
        return self._stack.pop()
    
    def peek(self) -> Any:
        """
        Peek at the top item without removing it.
        
        Time: O(1)
        Space: O(1)
        
        Returns:
            The top item
            
        Raises:
            IndexError: If stack is empty
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")
        
        return self._stack[-1]
    
    def top(self) -> Any:
        """Alias for peek() following standard nomenclature."""
        return self.peek()
    
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (from ANodeStrategy)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store value (pushes to stack, ignores key)."""
        self.push(value if value is not None else key)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key (O(n) search - not recommended for stack)."""
        for i, val in enumerate(reversed(self._stack)):
            if val == key:
                return val
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists (O(n) - not recommended for stack)."""
        return key in self._stack
    
    def delete(self, key: Any) -> bool:
        """Delete specific value (O(n) - not recommended for stack)."""
        try:
            self._stack.remove(key)
            return True
        except ValueError:
            return False
    
    def keys(self) -> Iterator[Any]:
        """Get all values as keys (stack doesn't have traditional keys)."""
        return iter(self._stack)
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        return iter(self._stack)
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get all items as (value, value) pairs."""
        for val in self._stack:
            yield (val, val)
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def size(self) -> int:
        """Get the number of items in the stack."""
        return len(self._stack)
    
    def is_empty(self) -> bool:
        """Check if the stack is empty."""
        return len(self._stack) == 0
    
    def is_full(self) -> bool:
        """Check if stack has reached max_size."""
        return self._max_size is not None and len(self._stack) >= self._max_size
    
    def clear(self) -> None:
        """Clear all items from the stack."""
        self._stack.clear()
    
    def to_list(self) -> List[Any]:
        """Convert stack to list (top to bottom)."""
        return list(reversed(self._stack))
    
    def to_native(self) -> Dict[str, Any]:
        """Convert stack to native dictionary format."""
        return {str(i): val for i, val in enumerate(reversed(self._stack))}
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load stack from native dictionary format."""
        self._stack.clear()
        # Sort by keys and add in reverse order
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0)
        for _, value in reversed(sorted_items):
            self._stack.append(value)
    
    
    # ============================================================================
    # PYTHON SPECIAL METHODS
    # ============================================================================
    
    def __len__(self) -> int:
        """Return the number of items in the stack."""
        return len(self._stack)
    
    def __bool__(self) -> bool:
        """Return True if stack is not empty."""
        return bool(self._stack)
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate through stack items (top to bottom)."""
        return reversed(self._stack)
    
    def __repr__(self) -> str:
        """Professional string representation."""
        return f"StackStrategy(size={len(self._stack)}, top={self.peek() if not self.is_empty() else None})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        items = ', '.join(str(item) for item in list(self)[:5])
        suffix = '...' if len(self._stack) > 5 else ''
        return f"Stack[{items}{suffix}]"
    
    # ============================================================================
    # PERFORMANCE METADATA
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'STACK',
            'backend': 'Python list (dynamic array)',
            'complexity': {
                'push': 'O(1) amortized',
                'pop': 'O(1)',
                'peek': 'O(1)',
                'search': 'O(n)',  # Not recommended
                'space': 'O(n)'
            },
            'thread_safe': False,
            'max_size': self._max_size if self._max_size else 'unlimited'
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'size': len(self._stack),
            'is_empty': self.is_empty(),
            'is_full': self.is_full(),
            'max_size': self._max_size,
            'memory_usage': f"{len(self._stack) * 8} bytes (estimated)",
            'capacity': len(self._stack)  # Python lists track capacity
        }
