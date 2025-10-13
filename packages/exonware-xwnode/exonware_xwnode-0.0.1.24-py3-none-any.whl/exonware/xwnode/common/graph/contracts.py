"""
#exonware/xwnode/src/exonware/xwnode/common/graph/contracts.py

Graph manager contracts and enums.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.24
Generation Date: 11-Oct-2025
"""

from enum import Enum
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class GraphOptimization(Enum):
    """
    Graph optimization levels for XWGraphManager.
    
    Controls indexing and caching behavior for performance tuning.
    """
    
    OFF = 0           # No optimization - fallback to O(n) iteration
    INDEX_ONLY = 1    # Only indexing - O(1) lookups, no caching
    CACHE_ONLY = 2    # Only caching - benefits from repeated queries
    FULL = 3          # Both indexing + caching - maximum performance
    
    # Aliases for clarity
    DISABLED = 0
    MINIMAL = 1
    MODERATE = 2
    MAXIMUM = 3


class IGraphManager(ABC):
    """Interface for graph manager implementations."""
    
    @abstractmethod
    def add_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str,
        **properties
    ) -> str:
        """Add a relationship between entities."""
        pass
    
    @abstractmethod
    def remove_relationship(
        self,
        source: str,
        target: str,
        relationship_type: Optional[str] = None
    ) -> bool:
        """Remove relationship(s) between entities."""
        pass
    
    @abstractmethod
    def get_outgoing(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get outgoing relationships for entity."""
        pass
    
    @abstractmethod
    def get_incoming(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get incoming relationships for entity."""
        pass
    
    @abstractmethod
    def has_relationship(
        self,
        source: str,
        target: str,
        relationship_type: Optional[str] = None
    ) -> bool:
        """Check if relationship exists."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        pass
    
    @abstractmethod
    def clear_cache(self) -> None:
        """Clear query cache."""
        pass

