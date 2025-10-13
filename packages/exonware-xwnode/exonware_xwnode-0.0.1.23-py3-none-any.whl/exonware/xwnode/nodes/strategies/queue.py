"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/queue.py

Queue Strategy Implementation

Production-grade FIFO (First In, First Out) data structure.

Best Practices Implemented:
- Pure queue operations using collections.deque
- O(1) enqueue and dequeue operations
- Thread-safe for single-producer single-consumer
- Memory-efficient with minimal overhead
- Proper FIFO semantics following CLRS and industry standards

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
Generation Date: October 12, 2025
"""

from typing import Any, Iterator, List, Optional, Dict
from collections import deque
from .base import ANodeLinearStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class QueueStrategy(ANodeLinearStrategy):
    """
    Production-grade Queue (FIFO) node strategy.
    
    Optimized for:
    - Task scheduling (job queues, worker pools)
    - Breadth-first search (BFS algorithms)
    - Request buffering (rate limiting, throttling)
    - Message passing (producer-consumer patterns)
    - Event handling (event loops, message queues)
    
    Performance:
    - Enqueue: O(1)
    - Dequeue: O(1)
    - Peek: O(1)
    - Space: O(n)
    
    Security:
    - Bounds checking on all operations
    - Safe empty queue handling
    - Optional max size for memory protection
    
    Thread-Safety:
    - Thread-safe for single-producer single-consumer
    - Use queue.Queue for multi-threaded scenarios
    
    Follows eXonware Priorities:
    1. Security: Proper bounds checking, memory limits
    2. Usability: Standard FIFO interface
    3. Maintainability: Clean, well-documented implementation
    4. Performance: O(1) operations using deque
    5. Extensibility: Easy to extend for specific use cases
    """
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.LINEAR
    
    __slots__ = ('_queue', '_max_size')
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize an empty queue.
        
        Args:
            traits: Additional node traits
            **options:
                max_size: Optional maximum queue size (default: unlimited)
                initial_values: Optional list of initial values
        """
        super().__init__(
            NodeMode.QUEUE,
            traits | NodeTrait.FIFO | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE,
            **options
        )
        self._max_size: Optional[int] = options.get('max_size')
        self._queue: deque = deque(options.get('initial_values', []))
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the queue strategy."""
        return NodeTrait.FIFO | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE
    
    # ============================================================================
    # CORE QUEUE OPERATIONS (Industry Standard)
    # ============================================================================
    
    def enqueue(self, value: Any) -> None:
        """
        Add an item to the back of the queue.
        
        Time: O(1)
        Space: O(1)
        
        Raises:
            OverflowError: If max_size is set and queue is full
        """
        if self._max_size and len(self._queue) >= self._max_size:
            raise OverflowError(f"Queue overflow: max size {self._max_size} reached")
        
        self._queue.append(value)
    
    def dequeue(self) -> Any:
        """
        Remove and return the front item from the queue.
        
        Time: O(1)
        Space: O(1)
        
        Returns:
            The front item
            
        Raises:
            IndexError: If queue is empty
        """
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        
        return self._queue.popleft()
    
    def front(self) -> Any:
        """
        Peek at the front item without removing it.
        
        Time: O(1)
        Space: O(1)
        
        Returns:
            The front item
            
        Raises:
            IndexError: If queue is empty
        """
        if self.is_empty():
            raise IndexError("peek from empty queue")
        
        return self._queue[0]
    
    def rear(self) -> Any:
        """
        Peek at the back item without removing it.
        
        Time: O(1)
        Space: O(1)
        
        Returns:
            The back item
            
        Raises:
            IndexError: If queue is empty
        """
        if self.is_empty():
            raise IndexError("peek from empty queue")
        
        return self._queue[-1]
    
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (from ANodeStrategy)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store value (enqueues to queue, ignores key)."""
        self.enqueue(value if value is not None else key)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key (O(n) search - not recommended for queue)."""
        for val in self._queue:
            if val == key:
                return val
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists (O(n) - not recommended for queue)."""
        return key in self._queue
    
    def delete(self, key: Any) -> bool:
        """Delete specific value (O(n) - not recommended for queue)."""
        try:
            self._queue.remove(key)
            return True
        except ValueError:
            return False
    
    def keys(self) -> Iterator[Any]:
        """Get all values as keys (queue doesn't have traditional keys)."""
        return iter(self._queue)
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        return iter(self._queue)
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get all items as (value, value) pairs."""
        for val in self._queue:
            yield (val, val)
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def size(self) -> int:
        """Get the number of items in the queue."""
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._queue) == 0
    
    def is_full(self) -> bool:
        """Check if queue has reached max_size."""
        return self._max_size is not None and len(self._queue) >= self._max_size
    
    def clear(self) -> None:
        """Clear all items from the queue."""
        self._queue.clear()
    
    def to_list(self) -> List[Any]:
        """Convert queue to list (front to back)."""
        return list(self._queue)
    
    def to_native(self) -> Dict[str, Any]:
        """Convert queue to native dictionary format."""
        return {str(i): val for i, val in enumerate(self._queue)}
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load queue from native dictionary format."""
        self._queue.clear()
        # Sort by keys to maintain order
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0)
        self._queue.extend(val for _, val in sorted_items)
    
    
    # ============================================================================
    # PYTHON SPECIAL METHODS
    # ============================================================================
    
    def __len__(self) -> int:
        """Return the number of items in the queue."""
        return len(self._queue)
    
    def __bool__(self) -> bool:
        """Return True if queue is not empty."""
        return bool(self._queue)
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate through queue items (front to back)."""
        return iter(self._queue)
    
    def __repr__(self) -> str:
        """Professional string representation."""
        return f"QueueStrategy(size={len(self._queue)}, front={self.front() if not self.is_empty() else None})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        items = ', '.join(str(item) for item in list(self._queue)[:5])
        suffix = '...' if len(self._queue) > 5 else ''
        return f"Queue[{items}{suffix}]"
    
    # ============================================================================
    # PERFORMANCE METADATA
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'QUEUE',
            'backend': 'collections.deque (doubly-linked list)',
            'complexity': {
                'enqueue': 'O(1)',
                'dequeue': 'O(1)',
                'front': 'O(1)',
                'search': 'O(n)',  # Not recommended
                'space': 'O(n)'
            },
            'thread_safe': 'single-producer single-consumer only',
            'max_size': self._max_size if self._max_size else 'unlimited'
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'size': len(self._queue),
            'is_empty': self.is_empty(),
            'is_full': self.is_full(),
            'max_size': self._max_size,
            'memory_usage': f"{len(self._queue) * 8} bytes (estimated)"
        }
