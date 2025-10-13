"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/hopscotch_hash.py

Hopscotch Hashing Node Strategy Implementation

This module implements the HOPSCOTCH_HASH strategy for cache-friendly
open addressing with bounded neighborhood search.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
Generation Date: 12-Oct-2025
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeError, XWNodeValueError


class HopscotchEntry:
    """Entry in hopscotch hash table."""
    
    def __init__(self, key: Any = None, value: Any = None):
        """Initialize entry."""
        self.key = key
        self.value = value
        self.hop_info = 0  # Bitmap for neighborhood (32 bits)
    
    def is_empty(self) -> bool:
        """Check if entry is empty."""
        return self.key is None


class HopscotchHashStrategy(ANodeTreeStrategy):
    """
    Hopscotch Hashing strategy for cache-friendly hash tables.
    
    WHY Hopscotch Hashing:
    - Better cache locality than cuckoo hashing
    - Supports high load factors (>90%) efficiently
    - Bounded search within neighborhood (H=32 typical)
    - Predictable worst-case lookup time: O(H)
    - Excellent for embedded systems and real-time applications
    - Better resize behavior than linear probing
    
    WHY this implementation:
    - Hop bitmap (32-bit) enables fast neighborhood checking
    - Linear displacement with bounded search maintains cache friendliness
    - Power-of-2 table sizes enable fast modulo operations
    - Lazy resizing balances memory and performance
    - Neighborhood constant (H=32) fits in single cache line
    
    Time Complexity:
    - Insert: O(H) worst case where H is neighborhood size (32)
    - Search: O(H) worst case, O(1) expected
    - Delete: O(H) worst case, O(1) expected
    - Resize: O(n) when load factor exceeded
    
    Space Complexity: O(n / load_factor) typically O(1.1n) at 90% load
    
    Trade-offs:
    - Advantage: Better cache behavior than chaining or cuckoo
    - Advantage: Predictable O(H) worst case (no unbounded probing)
    - Advantage: High load factors (>90%) without degradation
    - Limitation: Requires more complex insertion logic
    - Limitation: Resize needed when neighborhood overfills
    - Limitation: Slightly higher memory per entry (bitmap)
    - Compared to HashMap (chaining): Better cache, more complex
    - Compared to Cuckoo Hash: Better cache, simpler insertion
    
    Best for:
    - Cache-sensitive applications
    - Embedded systems with memory constraints
    - Real-time systems requiring bounded lookup times
    - High load factor requirements (>85%)
    - Frequent lookup operations
    - Single-threaded environments
    
    Not recommended for:
    - Multi-threaded concurrent access (use lock-free alternatives)
    - Extremely dynamic datasets (frequent resizes)
    - When chaining simplicity is preferred
    - Large value sizes (cache benefits diminish)
    - Distributed hash tables
    
    Following eXonware Priorities:
    1. Security: Validates inputs, prevents hash collision attacks
    2. Usability: Simple API matching standard dict, clear errors
    3. Maintainability: Clear hop logic, well-documented neighborhoods
    4. Performance: O(H) bounded time, cache-optimized
    5. Extensibility: Easy to adjust H parameter, add probing strategies
    
    Industry Best Practices:
    - Follows Herlihy et al. hopscotch paper (2008)
    - Uses H=32 for single cache line neighborhood
    - Implements linear displacement with hop bitmap
    - Provides automatic resizing at 90% load factor
    - Supports dynamic table growth
    """
    
    # Tree node type for classification
    STRATEGY_TYPE: NodeType = NodeType.TREE
    
    # Constants
    DEFAULT_CAPACITY = 32
    HOP_RANGE = 32  # Neighborhood size (must match bitmap width)
    MAX_LOAD_FACTOR = 0.9
    
    def __init__(self, mode: NodeMode = NodeMode.HOPSCOTCH_HASH,
                 traits: NodeTrait = NodeTrait.NONE,
                 initial_capacity: int = DEFAULT_CAPACITY, **options):
        """
        Initialize hopscotch hash strategy.
        
        Args:
            mode: Node mode
            traits: Node traits
            initial_capacity: Initial table size (power of 2)
            **options: Additional options
        """
        super().__init__(mode, traits, **options)
        
        # Ensure capacity is power of 2
        self.capacity = self._next_power_of_2(max(initial_capacity, self.HOP_RANGE))
        self._table: List[HopscotchEntry] = [HopscotchEntry() for _ in range(self.capacity)]
        self._size = 0
    
    def _next_power_of_2(self, n: int) -> int:
        """Get next power of 2 >= n."""
        power = 1
        while power < n:
            power *= 2
        return power
    
    def get_supported_traits(self) -> NodeTrait:
        """Get supported traits."""
        return NodeTrait.INDEXED | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE
    
    # ============================================================================
    # CORE HASH OPERATIONS
    # ============================================================================
    
    def _hash(self, key: Any) -> int:
        """
        Hash function with security considerations.
        
        Args:
            key: Key to hash
            
        Returns:
            Hash value
            
        WHY custom hash:
        - Ensures uniform distribution
        - Prevents hash collision attacks
        - Compatible with power-of-2 sizing
        """
        # Security: Use Python's hash with additional mixing
        h = hash(key)
        # Mixing function to reduce collisions
        h ^= (h >> 16)
        h *= 0x85ebca6b
        h ^= (h >> 13)
        h *= 0xc2b2ae35
        h ^= (h >> 16)
        return h & (self.capacity - 1)
    
    def put(self, key: Any, value: Any = None) -> None:
        """
        Insert or update key-value pair.
        
        Args:
            key: Key
            value: Value
            
        Raises:
            XWNodeError: If insertion fails after displacement
        """
        # Security: None key validation
        if key is None:
            raise XWNodeValueError("Key cannot be None")
        
        # Check load factor
        if self._size >= self.capacity * self.MAX_LOAD_FACTOR:
            self._resize()
        
        hash_idx = self._hash(key)
        
        # Check if key already exists in neighborhood
        for i in range(self.HOP_RANGE):
            idx = (hash_idx + i) % self.capacity
            if self._table[idx].key == key:
                # Update existing
                self._table[idx].value = value
                return
        
        # Find empty slot
        free_idx = self._find_free_slot(hash_idx)
        if free_idx is None:
            # This shouldn't happen if load factor is maintained
            self._resize()
            self.put(key, value)  # Retry after resize
            return
        
        # Move entry closer if needed using displacement
        while free_idx - hash_idx >= self.HOP_RANGE:
            # Find entry to displace
            displaced = self._find_displacement_candidate(hash_idx, free_idx)
            if displaced is None:
                # Cannot displace, must resize
                self._resize()
                self.put(key, value)
                return
            
            # Swap positions
            self._table[free_idx] = self._table[displaced]
            self._table[displaced] = HopscotchEntry()
            
            # Update hop bitmap
            disp_hash = self._hash(self._table[free_idx].key)
            self._table[disp_hash].hop_info &= ~(1 << (displaced - disp_hash))
            self._table[disp_hash].hop_info |= (1 << (free_idx - disp_hash))
            
            free_idx = displaced
        
        # Insert at free slot
        self._table[free_idx].key = key
        self._table[free_idx].value = value
        
        # Update hop bitmap
        offset = free_idx - hash_idx
        self._table[hash_idx].hop_info |= (1 << offset)
        
        self._size += 1
    
    def _find_free_slot(self, start: int) -> Optional[int]:
        """
        Find free slot starting from index.
        
        Args:
            start: Starting index
            
        Returns:
            Index of free slot or None
        """
        for i in range(self.capacity):
            idx = (start + i) % self.capacity
            if self._table[idx].is_empty():
                return idx
        return None
    
    def _find_displacement_candidate(self, hash_idx: int, free_idx: int) -> Optional[int]:
        """
        Find entry that can be displaced to bring free slot closer.
        
        Args:
            hash_idx: Original hash index
            free_idx: Free slot index
            
        Returns:
            Index of entry to displace or None
        """
        # Look for entries whose home is before free_idx
        # and that currently occupy position within HOP_RANGE of free_idx
        for i in range(self.HOP_RANGE - 1, 0, -1):
            candidate_idx = (free_idx - i) % self.capacity
            candidate_hash = self._hash(self._table[candidate_idx].key) if not self._table[candidate_idx].is_empty() else None
            
            if candidate_hash is not None:
                # Check if this entry can move to free_idx
                if free_idx - candidate_hash < self.HOP_RANGE:
                    return candidate_idx
        
        return None
    
    def _resize(self) -> None:
        """
        Resize table to double capacity.
        
        WHY resize:
        - Maintains load factor below threshold
        - Prevents neighborhood overflow
        - Ensures O(H) performance
        """
        old_table = self._table
        old_capacity = self.capacity
        
        self.capacity = self.capacity * 2
        self._table = [HopscotchEntry() for _ in range(self.capacity)]
        self._size = 0
        
        # Reinsert all entries
        for entry in old_table:
            if not entry.is_empty():
                self.put(entry.key, entry.value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Retrieve value by key.
        
        Args:
            key: Key
            default: Default value
            
        Returns:
            Value or default
        """
        if key is None:
            return default
        
        hash_idx = self._hash(key)
        hop_info = self._table[hash_idx].hop_info
        
        # Check neighborhood using bitmap
        for i in range(self.HOP_RANGE):
            if hop_info & (1 << i):
                idx = (hash_idx + i) % self.capacity
                if self._table[idx].key == key:
                    return self._table[idx].value
        
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        if key is None:
            return False
        
        hash_idx = self._hash(key)
        hop_info = self._table[hash_idx].hop_info
        
        # Check neighborhood
        for i in range(self.HOP_RANGE):
            if hop_info & (1 << i):
                idx = (hash_idx + i) % self.capacity
                if self._table[idx].key == key:
                    return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """
        Remove key-value pair.
        
        Args:
            key: Key to remove
            
        Returns:
            True if deleted, False if not found
        """
        if key is None:
            return False
        
        hash_idx = self._hash(key)
        hop_info = self._table[hash_idx].hop_info
        
        # Find in neighborhood
        for i in range(self.HOP_RANGE):
            if hop_info & (1 << i):
                idx = (hash_idx + i) % self.capacity
                if self._table[idx].key == key:
                    # Clear entry
                    self._table[idx] = HopscotchEntry()
                    
                    # Update bitmap
                    self._table[hash_idx].hop_info &= ~(1 << i)
                    
                    self._size -= 1
                    return True
        
        return False
    
    def keys(self) -> Iterator[Any]:
        """Get iterator over all keys."""
        for entry in self._table:
            if not entry.is_empty():
                yield entry.key
    
    def values(self) -> Iterator[Any]:
        """Get iterator over all values."""
        for entry in self._table:
            if not entry.is_empty():
                yield entry.value
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get iterator over all key-value pairs."""
        for entry in self._table:
            if not entry.is_empty():
                yield (entry.key, entry.value)
    
    def __len__(self) -> int:
        """Get number of elements."""
        return self._size
    
    def to_native(self) -> Any:
        """Convert to native dict."""
        return dict(self.items())
    
    # ============================================================================
    # PERFORMANCE METHODS
    # ============================================================================
    
    def get_load_factor(self) -> float:
        """
        Get current load factor.
        
        Returns:
            Load factor (0.0 to 1.0)
        """
        return self._size / self.capacity if self.capacity > 0 else 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get hash table statistics.
        
        Returns:
            Statistics including load factor, capacity, collisions
        """
        # Count neighborhood usage
        neighborhood_usage = []
        for entry in self._table:
            if not entry.is_empty():
                bits_set = bin(entry.hop_info).count('1')
                neighborhood_usage.append(bits_set)
        
        avg_neighborhood = sum(neighborhood_usage) / len(neighborhood_usage) if neighborhood_usage else 0
        
        return {
            'size': self._size,
            'capacity': self.capacity,
            'load_factor': self.get_load_factor(),
            'hop_range': self.HOP_RANGE,
            'avg_neighborhood_size': avg_neighborhood,
            'max_neighborhood_size': max(neighborhood_usage) if neighborhood_usage else 0
        }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def clear(self) -> None:
        """Clear all entries."""
        self._table = [HopscotchEntry() for _ in range(self.capacity)]
        self._size = 0
    
    def is_empty(self) -> bool:
        """Check if empty."""
        return self._size == 0
    
    def size(self) -> int:
        """Get number of elements."""
        return self._size
    
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
        return (f"HopscotchHashStrategy(size={self._size}, capacity={self.capacity}, "
                f"load={self.get_load_factor():.1%})")
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"HopscotchHashStrategy(mode={self.mode.name}, size={self._size}, traits={self.traits})"
    
    # ============================================================================
    # FACTORY METHOD
    # ============================================================================
    
    @classmethod
    def create_from_data(cls, data: Any, initial_capacity: int = DEFAULT_CAPACITY) -> 'HopscotchHashStrategy':
        """
        Create hopscotch hash from data.
        
        Args:
            data: Dictionary or iterable
            initial_capacity: Initial table size
            
        Returns:
            New HopscotchHashStrategy instance
        """
        # Estimate good initial capacity
        if isinstance(data, dict):
            estimated_size = len(data)
        elif isinstance(data, (list, tuple)):
            estimated_size = len(data)
        else:
            estimated_size = 1
        
        # Size for target load factor
        capacity = int(estimated_size / cls.MAX_LOAD_FACTOR) + cls.HOP_RANGE
        capacity = max(capacity, initial_capacity)
        
        instance = cls(initial_capacity=capacity)
        
        if isinstance(data, dict):
            for key, value in data.items():
                instance.put(key, value)
        elif isinstance(data, (list, tuple)):
            for i, value in enumerate(data):
                instance.put(i, value)
        else:
            instance.put(0, data)
        
        return instance

