"""
#exonware/xwnode/src/exonware/xwnode/common/graph/indexing.py

Multi-index manager for O(1) relationship lookups.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.24
Generation Date: 11-Oct-2025
"""

import threading
from typing import Dict, List, Optional, Any
from collections import defaultdict


class IndexManager:
    """
    Maintains multiple indexes for fast relationship queries.
    
    Provides O(1) average case lookups for:
    - Outgoing relationships by source entity
    - Incoming relationships by target entity
    - Relationships by type
    """
    
    def __init__(self):
        """Initialize index manager with empty indexes."""
        # Index 1: Outgoing relationships by source
        # source_id -> {relationship_type -> [relationship_data]}
        self._outgoing_index: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
        
        # Index 2: Incoming relationships by target
        # target_id -> {relationship_type -> [relationship_data]}
        self._incoming_index: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
        
        # Index 3: All relationships by ID
        # relationship_id -> relationship_data
        self._relationships: Dict[str, Dict[str, Any]] = {}
        
        # Relationship ID counter
        self._rel_id_counter = 0
        self._lock = threading.RLock()
    
    def add_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str,
        **properties
    ) -> str:
        """
        Add relationship to all indexes.
        
        Args:
            source: Source entity ID
            target: Target entity ID
            relationship_type: Type of relationship
            **properties: Additional relationship properties
        
        Returns:
            Relationship ID
            
        Time Complexity: O(1) amortized
        """
        with self._lock:
            # Generate unique relationship ID
            rel_id = f"rel_{self._rel_id_counter}"
            self._rel_id_counter += 1
            
            # Create relationship data
            rel_data = {
                'id': rel_id,
                'source': source,
                'target': target,
                'type': relationship_type,
                **properties
            }
            
            # Store in main dict
            self._relationships[rel_id] = rel_data
            
            # Index by source (outgoing)
            self._outgoing_index[source][relationship_type].append(rel_data)
            
            # Index by target (incoming)
            self._incoming_index[target][relationship_type].append(rel_data)
            
            return rel_id
    
    def remove_relationship(
        self,
        source: str,
        target: str,
        relationship_type: Optional[str] = None
    ) -> bool:
        """
        Remove relationship(s) between entities.
        
        Args:
            source: Source entity ID
            target: Target entity ID
            relationship_type: Optional type filter
        
        Returns:
            True if removed, False if not found
            
        Time Complexity: O(degree) where degree is number of relationships for entity
        """
        with self._lock:
            removed = False
            
            # Find matching relationships
            to_remove = []
            for rel_id, rel_data in self._relationships.items():
                if rel_data['source'] == source and rel_data['target'] == target:
                    if relationship_type is None or rel_data['type'] == relationship_type:
                        to_remove.append(rel_id)
            
            # Remove from all indexes
            for rel_id in to_remove:
                rel_data = self._relationships.pop(rel_id)
                
                # Remove from outgoing index
                source_rels = self._outgoing_index[source][rel_data['type']]
                self._outgoing_index[source][rel_data['type']] = [
                    r for r in source_rels if r['id'] != rel_id
                ]
                
                # Remove from incoming index
                target_rels = self._incoming_index[target][rel_data['type']]
                self._incoming_index[target][rel_data['type']] = [
                    r for r in target_rels if r['id'] != rel_id
                ]
                
                removed = True
            
            return removed
    
    def query_outgoing(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query outgoing relationships for entity.
        
        Args:
            entity_id: Entity to query
            relationship_type: Optional type filter
        
        Returns:
            List of relationship data dictionaries
            
        Time Complexity: O(1) average case
        """
        with self._lock:
            if entity_id not in self._outgoing_index:
                return []
            
            if relationship_type:
                # Return specific type
                return self._outgoing_index[entity_id].get(relationship_type, []).copy()
            
            # Return all types
            results = []
            for rels in self._outgoing_index[entity_id].values():
                results.extend(rels)
            return results
    
    def query_incoming(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query incoming relationships for entity.
        
        Args:
            entity_id: Entity to query
            relationship_type: Optional type filter
        
        Returns:
            List of relationship data dictionaries
            
        Time Complexity: O(1) average case
        """
        with self._lock:
            if entity_id not in self._incoming_index:
                return []
            
            if relationship_type:
                # Return specific type
                return self._incoming_index[entity_id].get(relationship_type, []).copy()
            
            # Return all types
            results = []
            for rels in self._incoming_index[entity_id].values():
                results.extend(rels)
            return results
    
    def has_relationship(
        self,
        source: str,
        target: str,
        relationship_type: Optional[str] = None
    ) -> bool:
        """
        Check if relationship exists.
        
        Args:
            source: Source entity ID
            target: Target entity ID
            relationship_type: Optional type filter
        
        Returns:
            True if exists, False otherwise
            
        Time Complexity: O(degree) where degree is relationships for source
        """
        with self._lock:
            if source not in self._outgoing_index:
                return False
            
            # Check outgoing relationships
            if relationship_type:
                rels = self._outgoing_index[source].get(relationship_type, [])
            else:
                rels = []
                for type_rels in self._outgoing_index[source].values():
                    rels.extend(type_rels)
            
            # Check if any match target
            return any(r['target'] == target for r in rels)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index metrics
        """
        with self._lock:
            return {
                'total_relationships': len(self._relationships),
                'indexed_sources': len(self._outgoing_index),
                'indexed_targets': len(self._incoming_index),
                'relationship_types': len(set(
                    r['type'] for r in self._relationships.values()
                ))
            }
    
    def clear(self):
        """Clear all indexes."""
        with self._lock:
            self._outgoing_index.clear()
            self._incoming_index.clear()
            self._relationships.clear()

