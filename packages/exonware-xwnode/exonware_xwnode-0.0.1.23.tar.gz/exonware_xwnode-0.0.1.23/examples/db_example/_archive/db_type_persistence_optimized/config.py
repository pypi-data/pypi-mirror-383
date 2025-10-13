#!/usr/bin/env python3
"""
Persistence-Optimized Database Configuration

Optimizes for: Durability, ACID, crash recovery
- Node Strategy: B_PLUS_TREE (database-grade persistence)
- Edge Strategy: EDGE_PROPERTY_STORE (columnar edge storage for efficient disk I/O)

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 11, 2025
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from exonware.xwnode.defs import NodeMode, EdgeMode
from base_database import BaseDatabase


class PersistenceOptimizedDatabase(BaseDatabase):
    """
    Persistence-Optimized Database
    
    Uses B_PLUS_TREE for database-grade persistence with ACID guarantees.
    EDGE_PROPERTY_STORE provides columnar storage for efficient disk I/O.
    """
    
    def __init__(self):
        super().__init__(
            name="Persistence-Optimized",
            node_mode=NodeMode.B_PLUS_TREE,
            edge_mode=EdgeMode.EDGE_PROPERTY_STORE
        )
    
    def get_description(self) -> str:
        """Get database description"""
        return (
            "Persistence-Optimized Database using B_PLUS_TREE + EDGE_PROPERTY_STORE.\n"
            "Optimized for durability, ACID compliance, and crash recovery.\n"
            "Best for: Mission-critical data, transactional workloads, reliability"
        )

