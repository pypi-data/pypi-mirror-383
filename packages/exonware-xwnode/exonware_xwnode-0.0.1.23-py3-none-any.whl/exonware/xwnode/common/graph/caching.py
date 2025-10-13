"""
#exonware/xwnode/src/exonware/xwnode/common/graph/caching.py

LRU cache manager for frequent relationship queries.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
Generation Date: 11-Oct-2025
"""

import threading
from typing import Any, Optional, List
from collections import OrderedDict


class CacheManager:
    """
    Thread-safe LRU cache for query results.
    
    Provides O(1) cache operations with automatic eviction
    of least recently used entries.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize cache manager.
        
        Args:
            max_size: Maximum number of cached entries
        """
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached result.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
            
        Time Complexity: O(1)
        """
        with self._lock:
            if key in self._cache:
                self._hits += 1
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                return self._cache[key]
            
            self._misses += 1
            return None
    
    def put(self, key: str, value: Any) -> None:
        """
        Cache a query result.
        
        Args:
            key: Cache key
            value: Value to cache
            
        Time Complexity: O(1)
        """
        with self._lock:
            if key in self._cache:
                # Update existing entry
                self._cache.move_to_end(key)
                self._cache[key] = value
            else:
                # Add new entry
                if len(self._cache) >= self._max_size:
                    # Remove least recently used (first item)
                    self._cache.popitem(last=False)
                self._cache[key] = value
    
    def invalidate(self, entity_id: str) -> None:
        """
        Invalidate cache entries for entity.
        
        Removes all cached queries that involve the specified entity.
        
        Args:
            entity_id: Entity whose cache entries should be invalidated
        """
        with self._lock:
            # Find all cache keys containing this entity
            keys_to_remove = [k for k in self._cache.keys() if entity_id in k]
            
            # Remove them
            for key in keys_to_remove:
                del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
    
    def get_hit_rate(self) -> float:
        """
        Get cache hit rate.
        
        Returns:
            Hit rate as float between 0.0 and 1.0
        """
        with self._lock:
            total = self._hits + self._misses
            return self._hits / total if total > 0 else 0.0
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics
        """
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self._max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': self.get_hit_rate()
            }

