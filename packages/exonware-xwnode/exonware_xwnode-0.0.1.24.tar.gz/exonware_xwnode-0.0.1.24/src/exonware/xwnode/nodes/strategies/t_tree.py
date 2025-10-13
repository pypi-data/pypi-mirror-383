"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/node_t_tree.py

T-Tree Node Strategy Implementation

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.24
Generation Date: 11-Oct-2025
"""

from typing import Any, Iterator, Dict
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


class TTreeStrategy(ANodeStrategy):
    """T-Tree - Hybrid AVL tree + array nodes for in-memory."""
    
    STRATEGY_TYPE = NodeType.TREE
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        super().__init__(NodeMode.T_TREE, traits, **options)
        self._data: OrderedDict = OrderedDict()
        self._size_tracker = create_size_tracker()
        self._access_tracker = create_access_tracker()
    
    def get_supported_traits(self) -> NodeTrait:
        return NodeTrait.ORDERED | NodeTrait.INDEXED
    
    def get(self, path: str, default: Any = None) -> Any:
        record_access(self._access_tracker, 'get_count')
        return self._data.get(path, default)
    
    def put(self, path: str, value: Any = None) -> 'TTreeStrategy':
        record_access(self._access_tracker, 'put_count')
        if path not in self._data:
            update_size_tracker(self._size_tracker, 1)
        self._data[path] = value
        return self
    
    def delete(self, key: Any) -> bool:
        key_str = str(key)
        if key_str in self._data:
            del self._data[key_str]
            update_size_tracker(self._size_tracker, -1)
            record_access(self._access_tracker, 'delete_count')
            return True
        return False
    
    def remove(self, key: Any) -> bool:
        return self.delete(key)
    
    def has(self, key: Any) -> bool:
        return str(key) in self._data
    
    def exists(self, path: str) -> bool:
        return path in self._data
    
    def keys(self) -> Iterator[Any]:
        return iter(self._data.keys())
    
    def values(self) -> Iterator[Any]:
        return iter(self._data.values())
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        return iter(self._data.items())
    
    def __len__(self) -> int:
        return len(self._data)
    
    def to_native(self) -> Dict[str, Any]:
        return dict(self._data)
    
    def get_backend_info(self) -> Dict[str, Any]:
        return {
            **create_basic_backend_info('T-Tree', 'Hybrid AVL tree + array nodes'),
            'total_keys': len(self._data),
            **self._size_tracker,
            **get_access_metrics(self._access_tracker)
        }

