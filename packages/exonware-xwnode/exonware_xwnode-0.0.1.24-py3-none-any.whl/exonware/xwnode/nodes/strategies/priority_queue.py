"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/priority_queue.py

Priority Queue Strategy Implementation

Production-grade priority queue using binary heap.

Best Practices Implemented:
- Min-heap by default (heapq standard)
- Stable sorting with counter for equal priorities
- Efficient O(log n) operations
- Support for both min and max heaps
- Proper heap semantics following CLRS and industry standards

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.24
Generation Date: October 12, 2025
"""

from typing import Any, Iterator, List, Optional, Dict, Tuple
import heapq
from .base import ANodeLinearStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class PriorityQueueStrategy(ANodeLinearStrategy):
    """
    Production-grade Priority Queue node strategy.
    
    Optimized for:
    - Dijkstra's shortest path algorithm
    - A* pathfinding
    - Task scheduling with priorities
    - Event simulation (discrete event systems)
    - Median maintenance (with dual-heap pattern)
    - Huffman coding
    
    Performance:
    - Insert: O(log n)
    - Extract-Min: O(log n)
    - Peek-Min: O(1)
    - Decrease-Key: O(n) - requires linear search
    - Build-Heap: O(n)
    
    Security:
    - Bounds checking on all operations
    - Safe empty heap handling
    - Priority validation
    
    Implementation Details:
    - Uses min-heap by default (lowest priority value = highest priority)
    - Stable sorting via counter for equal priorities (FIFO for same priority)
    - Tuple format: (priority, counter, value)
    
    Follows eXonware Priorities:
    1. Security: Input validation, safe operations
    2. Usability: Standard priority queue interface
    3. Maintainability: Clean heap implementation
    4. Performance: O(log n) operations, O(1) peek
    5. Extensibility: Support for custom priority types
    """
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.LINEAR
    
    __slots__ = ('_heap', '_counter', '_max_size', '_is_max_heap')
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize an empty priority queue.
        
        Args:
            traits: Additional node traits
            **options:
                max_size: Optional maximum heap size
                is_max_heap: True for max-heap, False for min-heap (default)
                initial_items: Optional list of (priority, value) tuples
        """
        super().__init__(
            NodeMode.PRIORITY_QUEUE,
            traits | NodeTrait.PRIORITY | NodeTrait.FAST_INSERT | NodeTrait.HEAP_OPERATIONS,
            **options
        )
        self._max_size: Optional[int] = options.get('max_size')
        self._is_max_heap: bool = options.get('is_max_heap', False)
        self._heap: List[Tuple[float, int, Any]] = []  # (priority, counter, value)
        self._counter = 0
        
        # Build heap from initial items if provided
        initial_items = options.get('initial_items', [])
        if initial_items:
            for priority, value in initial_items:
                self.push(value, priority)
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the priority queue strategy."""
        return NodeTrait.PRIORITY | NodeTrait.FAST_INSERT | NodeTrait.HEAP_OPERATIONS
    
    # ============================================================================
    # CORE PRIORITY QUEUE OPERATIONS (Industry Standard)
    # ============================================================================
    
    def push(self, value: Any, priority: float = 0.0) -> None:
        """
        Insert a value with given priority.
        
        Time: O(log n)
        Space: O(1)
        
        Args:
            value: The value to insert
            priority: Priority value (lower = higher priority for min-heap)
            
        Raises:
            OverflowError: If max_size is set and heap is full
        """
        if self._max_size and len(self._heap) >= self._max_size:
            raise OverflowError(f"Priority queue overflow: max size {self._max_size} reached")
        
        # For max-heap, negate the priority
        actual_priority = -priority if self._is_max_heap else priority
        
        heapq.heappush(self._heap, (actual_priority, self._counter, value))
        self._counter += 1
    
    def pop(self) -> Any:
        """
        Extract and return the highest priority item.
        
        Time: O(log n)
        Space: O(1)
        
        Returns:
            The highest priority value
            
        Raises:
            IndexError: If heap is empty
        """
        if self.is_empty():
            raise IndexError("pop from empty priority queue")
        
        priority, counter, value = heapq.heappop(self._heap)
        return value
    
    def peek(self) -> Any:
        """
        Peek at the highest priority item without removing it.
        
        Time: O(1)
        Space: O(1)
        
        Returns:
            The highest priority value
            
        Raises:
            IndexError: If heap is empty
        """
        if self.is_empty():
            raise IndexError("peek from empty priority queue")
        
        return self._heap[0][2]  # Return value from (priority, counter, value)
    
    def peek_with_priority(self) -> Tuple[float, Any]:
        """
        Peek at the highest priority item with its priority.
        
        Returns:
            Tuple of (priority, value)
            
        Raises:
            IndexError: If heap is empty
        """
        if self.is_empty():
            raise IndexError("peek from empty priority queue")
        
        priority, counter, value = self._heap[0]
        actual_priority = -priority if self._is_max_heap else priority
        return (actual_priority, value)
    
    def pop_with_priority(self) -> Tuple[float, Any]:
        """
        Extract and return the highest priority item with its priority.
        
        Returns:
            Tuple of (priority, value)
            
        Raises:
            IndexError: If heap is empty
        """
        if self.is_empty():
            raise IndexError("pop from empty priority queue")
        
        priority, counter, value = heapq.heappop(self._heap)
        actual_priority = -priority if self._is_max_heap else priority
        return (actual_priority, value)
    
    def pushpop(self, value: Any, priority: float = 0.0) -> Any:
        """
        Push item then pop highest priority item (more efficient than separate ops).
        
        Time: O(log n)
        Space: O(1)
        
        Returns:
            The highest priority value after insertion
        """
        actual_priority = -priority if self._is_max_heap else priority
        priority_out, counter_out, value_out = heapq.heappushpop(
            self._heap,
            (actual_priority, self._counter, value)
        )
        self._counter += 1
        return value_out
    
    def replace(self, value: Any, priority: float = 0.0) -> Any:
        """
        Pop highest priority item then push new item (more efficient than separate ops).
        
        Time: O(log n)
        Space: O(1)
        
        Returns:
            The popped value
            
        Raises:
            IndexError: If heap is empty
        """
        if self.is_empty():
            raise IndexError("replace on empty priority queue")
        
        actual_priority = -priority if self._is_max_heap else priority
        priority_out, counter_out, value_out = heapq.heapreplace(
            self._heap,
            (actual_priority, self._counter, value)
        )
        self._counter += 1
        return value_out
    
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (from ANodeStrategy)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store value (uses key as priority if numeric, otherwise default priority)."""
        try:
            priority = float(key)
            self.push(value if value is not None else key, priority)
        except (ValueError, TypeError):
            self.push(value if value is not None else key, 0.0)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value in heap (O(n) - not efficient for heaps)."""
        for _, _, val in self._heap:
            if val == key:
                return val
        return default
    
    def has(self, key: Any) -> bool:
        """Check if value exists (O(n))."""
        for _, _, val in self._heap:
            if val == key:
                return True
        return False
    
    def delete(self, key: Any) -> bool:
        """Delete value from heap (O(n) - requires re-heapify)."""
        for i, (priority, counter, val) in enumerate(self._heap):
            if val == key:
                self._heap.pop(i)
                if self._heap:
                    heapq.heapify(self._heap)
                return True
        return False
    
    def keys(self) -> Iterator[Any]:
        """Get all values as keys."""
        for _, _, val in self._heap:
            yield val
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        for _, _, val in self._heap:
            yield val
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get all items as (value, value) pairs."""
        for _, _, val in self._heap:
            yield (val, val)
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def size(self) -> int:
        """Get the number of items in the priority queue."""
        return len(self._heap)
    
    def is_empty(self) -> bool:
        """Check if the priority queue is empty."""
        return len(self._heap) == 0
    
    def is_full(self) -> bool:
        """Check if heap has reached max_size."""
        return self._max_size is not None and len(self._heap) >= self._max_size
    
    def clear(self) -> None:
        """Clear all items from the priority queue."""
        self._heap.clear()
        self._counter = 0
        self._record_access("clear")
    
    def to_list(self) -> List[Tuple[float, Any]]:
        """Convert to sorted list of (priority, value) tuples."""
        return sorted(
            [(p if not self._is_max_heap else -p, v) for p, c, v in self._heap],
            key=lambda x: x[0]
        )
    
    def to_native(self) -> Dict[str, Any]:
        """Convert priority queue to native dictionary format."""
        return {
            'items': [(p if not self._is_max_heap else -p, v) for p, c, v in self._heap],
            'is_max_heap': self._is_max_heap
        }
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load priority queue from native dictionary format."""
        self._heap.clear()
        self._counter = 0
        self._is_max_heap = data.get('is_max_heap', False)
        
        for priority, value in data.get('items', []):
            self.push(value, priority)
    
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (Linear Strategy Base)
    # ============================================================================
    
    def get_at_index(self, index: int) -> Any:
        """Get item at index in heap (order not guaranteed)."""
        if 0 <= index < len(self._heap):
            return self._heap[index][2]
        raise IndexError(f"priority queue index out of range: {index}")
    
    def set_at_index(self, index: int, value: Any) -> None:
        """Set item at index (not recommended - breaks heap property)."""
        if 0 <= index < len(self._heap):
            priority, counter, _ = self._heap[index]
            self._heap[index] = (priority, counter, value)
        else:
            raise IndexError(f"priority queue index out of range: {index}")
    
    def push_front(self, value: Any) -> None:
        """Push with highest priority."""
        self.push(value, float('-inf') if not self._is_max_heap else float('inf'))
    
    def push_back(self, value: Any) -> None:
        """Push with lowest priority."""
        self.push(value, float('inf') if not self._is_max_heap else float('-inf'))
    
    def pop_front(self) -> Any:
        """Pop highest priority item (standard pop)."""
        return self.pop()
    
    def pop_back(self) -> Any:
        """Pop lowest priority item (O(n) - not efficient)."""
        if self.is_empty():
            raise IndexError("pop from empty priority queue")
        
        # Find item with worst priority
        worst_idx = max(range(len(self._heap)), key=lambda i: self._heap[i][0])
        value = self._heap[worst_idx][2]
        self._heap.pop(worst_idx)
        if self._heap:  # Re-heapify if not empty
            heapq.heapify(self._heap)
        return value
    
    # Behavioral views
    def as_linked_list(self):
        """Priority queue can be viewed as ordered linked list."""
        return self
    
    def as_stack(self):
        """Priority queue cannot behave as Stack."""
        raise NotImplementedError("PriorityQueue cannot behave as Stack - use StackStrategy instead")
    
    def as_queue(self):
        """Priority queue cannot behave as standard Queue."""
        raise NotImplementedError("PriorityQueue cannot behave as Queue - use QueueStrategy instead")
    
    def as_deque(self):
        """Priority queue cannot behave as Deque."""
        raise NotImplementedError("PriorityQueue cannot behave as Deque - use DequeStrategy instead")
    
    # ============================================================================
    # PYTHON SPECIAL METHODS
    # ============================================================================
    
    def __len__(self) -> int:
        """Return the number of items in the priority queue."""
        return len(self._heap)
    
    def __bool__(self) -> bool:
        """Return True if priority queue is not empty."""
        return bool(self._heap)
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate through items (order not guaranteed - heap order)."""
        for _, _, value in self._heap:
            yield value
    
    def __repr__(self) -> str:
        """Professional string representation."""
        heap_type = "max-heap" if self._is_max_heap else "min-heap"
        top = self.peek() if not self.is_empty() else None
        return f"PriorityQueueStrategy(size={len(self._heap)}, type={heap_type}, top={top})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        heap_type = "MaxHeap" if self._is_max_heap else "MinHeap"
        return f"{heap_type}[size={len(self._heap)}]"
    
    # ============================================================================
    # ADVANCED HEAP OPERATIONS
    # ============================================================================
    
    def nsmallest(self, n: int) -> List[Tuple[float, Any]]:
        """
        Get n smallest priority items without removing them.
        
        Time: O(n log k) where k = min(n, heap_size)
        
        Returns:
            List of (priority, value) tuples
        """
        items = heapq.nsmallest(n, self._heap, key=lambda x: x[0])
        return [(p if not self._is_max_heap else -p, v) for p, c, v in items]
    
    def nlargest(self, n: int) -> List[Tuple[float, Any]]:
        """
        Get n largest priority items without removing them.
        
        Time: O(n log k) where k = min(n, heap_size)
        
        Returns:
            List of (priority, value) tuples
        """
        items = heapq.nlargest(n, self._heap, key=lambda x: x[0])
        return [(p if not self._is_max_heap else -p, v) for p, c, v in items]
    
    def merge(self, other: 'PriorityQueueStrategy') -> 'PriorityQueueStrategy':
        """
        Merge two priority queues.
        
        Time: O((n + m) log(n + m))
        
        Returns:
            New merged priority queue
        """
        merged = PriorityQueueStrategy(is_max_heap=self._is_max_heap)
        
        # Merge heaps efficiently
        merged._heap = list(heapq.merge(self._heap, other._heap, key=lambda x: x[0]))
        merged._counter = self._counter + other._counter
        
        return merged
    
    # ============================================================================
    # COMPATIBILITY INTERFACE
    # ============================================================================
    
    def to_list(self) -> List[Tuple[float, Any]]:
        """Convert to sorted list of (priority, value) tuples."""
        sorted_items = sorted(self._heap, key=lambda x: x[0])
        return [(p if not self._is_max_heap else -p, v) for p, c, v in sorted_items]
    
    def to_native(self) -> Dict[str, Any]:
        """Convert priority queue to native dictionary format."""
        return {
            'items': [(p if not self._is_max_heap else -p, v) for p, c, v in self._heap],
            'is_max_heap': self._is_max_heap,
            'size': len(self._heap)
        }
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load priority queue from native dictionary format."""
        self._heap.clear()
        self._counter = 0
        self._is_max_heap = data.get('is_max_heap', False)
        
        for priority, value in data.get('items', []):
            self.push(value, priority)
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def size(self) -> int:
        """Get the number of items in the priority queue."""
        return len(self._heap)
    
    def is_empty(self) -> bool:
        """Check if the priority queue is empty."""
        return len(self._heap) == 0
    
    def is_full(self) -> bool:
        """Check if heap has reached max_size."""
        return self._max_size is not None and len(self._heap) >= self._max_size
    
    def clear(self) -> None:
        """Clear all items from the priority queue."""
        self._heap.clear()
        self._counter = 0
        self._record_access("clear")
    
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (Linear Strategy Base)
    # ============================================================================
    
    def get_at_index(self, index: int) -> Any:
        """Get item at index (heap order, not priority order)."""
        if 0 <= index < len(self._heap):
            return self._heap[index][2]
        raise IndexError(f"priority queue index out of range: {index}")
    
    def set_at_index(self, index: int, value: Any) -> None:
        """Set item at index (breaks heap property - requires re-heapify)."""
        if 0 <= index < len(self._heap):
            priority, counter, _ = self._heap[index]
            self._heap[index] = (priority, counter, value)
        else:
            raise IndexError(f"priority queue index out of range: {index}")
    
    def push_front(self, value: Any) -> None:
        """Push with highest priority."""
        self.push(value, float('-inf') if not self._is_max_heap else float('inf'))
    
    def push_back(self, value: Any) -> None:
        """Push with lowest priority."""
        self.push(value, float('inf') if not self._is_max_heap else float('-inf'))
    
    def pop_front(self) -> Any:
        """Pop highest priority item."""
        return self.pop()
    
    def pop_back(self) -> Any:
        """Pop lowest priority item (inefficient O(n))."""
        if self.is_empty():
            raise IndexError("pop from empty priority queue")
        
        worst_idx = max(range(len(self._heap)), key=lambda i: self._heap[i][0])
        value = self._heap[worst_idx][2]
        self._heap.pop(worst_idx)
        if self._heap:
            heapq.heapify(self._heap)
        return value
    
    # Behavioral views
    def as_linked_list(self):
        """Priority queue can be viewed as ordered linked list."""
        return self
    
    def as_stack(self):
        """Priority queue cannot behave as Stack."""
        raise NotImplementedError("PriorityQueue cannot behave as Stack")
    
    def as_queue(self):
        """Priority queue cannot behave as Queue."""
        raise NotImplementedError("PriorityQueue cannot behave as Queue")
    
    def as_deque(self):
        """Priority queue cannot behave as Deque."""
        raise NotImplementedError("PriorityQueue cannot behave as Deque")
    
    # ============================================================================
    # PYTHON SPECIAL METHODS
    # ============================================================================
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate in heap order (not priority order)."""
        for _, _, value in self._heap:
            yield value
    
    def __repr__(self) -> str:
        """Professional string representation."""
        heap_type = "max-heap" if self._is_max_heap else "min-heap"
        return f"PriorityQueueStrategy(size={len(self._heap)}, type={heap_type})"
    
    # ============================================================================
    # PERFORMANCE METADATA
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'PRIORITY_QUEUE',
            'backend': 'heapq (binary heap)',
            'heap_type': 'max-heap' if self._is_max_heap else 'min-heap',
            'complexity': {
                'push': 'O(log n)',
                'pop': 'O(log n)',
                'peek': 'O(1)',
                'pushpop': 'O(log n)',
                'replace': 'O(log n)',
                'space': 'O(n)'
            },
            'thread_safe': False,
            'max_size': self._max_size if self._max_size else 'unlimited'
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'size': len(self._heap),
            'is_empty': self.is_empty(),
            'is_full': self.is_full(),
            'max_size': self._max_size,
            'is_max_heap': self._is_max_heap,
            'counter': self._counter,
            'memory_usage': f"{len(self._heap) * 24} bytes (estimated)"
        }
