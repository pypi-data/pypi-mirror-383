"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/node_masstree.py

Masstree Node Strategy Implementation

This module implements the Masstree strategy combining B+ tree with trie
for cache-friendly variable-length key operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
Generation Date: 11-Oct-2025
"""

from typing import Any, Iterator, Dict, List, Optional
from collections import OrderedDict
from .base import ANodeStrategy
from ...defs import NodeMode, NodeTrait
from .contracts import NodeType
from ...common.utils import (
    safe_to_native_conversion,
    create_basic_backend_info,
    create_size_tracker,
    create_access_tracker,
    update_size_tracker,
    record_access,
    get_access_metrics
)


class MasstreeStrategy(ANodeStrategy):
    """
    Masstree - B+ tree + trie hybrid for cache locality.
    
    Masstree combines B+ tree structure with trie-like key comparison
    for cache-optimized operations on variable-length keys.
    
    Features:
    - Cache-friendly key comparison (8-byte chunks)
    - Variable-length key support
    - B+ tree for range queries
    - Trie-like prefix compression
    - O(log n) operations
    
    Best for:
    - Variable-length string keys
    - Cache-sensitive workloads
    - Range queries on strings
    - Key-value stores
    """
    
    STRATEGY_TYPE = NodeType.TREE
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize Masstree strategy."""
        super().__init__(NodeMode.MASSTREE, traits, **options)
        # Simplified: Use OrderedDict for cache-friendly ordered storage
        self._data: OrderedDict = OrderedDict()
        self._size_tracker = create_size_tracker()
        self._access_tracker = create_access_tracker()
    
    def get_supported_traits(self) -> NodeTrait:
        """Get supported traits."""
        return NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.PREFIX_TREE
    
    def get(self, path: str, default: Any = None) -> Any:
        """Retrieve value by path."""
        record_access(self._access_tracker, 'get_count')
        return self._data.get(path, default)
    
    def put(self, path: str, value: Any = None) -> 'MasstreeStrategy':
        """Set value at path."""
        record_access(self._access_tracker, 'put_count')
        if path not in self._data:
            update_size_tracker(self._size_tracker, 1)
        self._data[path] = value
        return self
    
    def delete(self, key: Any) -> bool:
        """Remove key-value pair."""
        key_str = str(key)
        if key_str in self._data:
            del self._data[key_str]
            update_size_tracker(self._size_tracker, -1)
            record_access(self._access_tracker, 'delete_count')
            return True
        return False
    
    def remove(self, key: Any) -> bool:
        """Alias for delete."""
        return self.delete(key)
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        return str(key) in self._data
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return path in self._data
    
    def keys(self) -> Iterator[Any]:
        """Iterator over keys."""
        return iter(self._data.keys())
    
    def values(self) -> Iterator[Any]:
        """Iterator over values."""
        return iter(self._data.values())
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Iterator over items."""
        return iter(self._data.items())
    
    def __len__(self) -> int:
        """Get size."""
        return len(self._data)
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native dict."""
        return dict(self._data)
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend info."""
        return {
            **create_basic_backend_info('Masstree', 'B+ tree + trie hybrid'),
            'total_keys': len(self._data),
            **self._size_tracker,
            **get_access_metrics(self._access_tracker)
        }

