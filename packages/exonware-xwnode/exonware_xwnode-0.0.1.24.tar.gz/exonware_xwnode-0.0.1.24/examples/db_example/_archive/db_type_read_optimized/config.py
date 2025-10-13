#!/usr/bin/env python3
"""
Read-Optimized Database Configuration

Optimizes for: Lightning-fast read operations
- Node Strategy: HASH_MAP (O(1) lookups)
- Edge Strategy: None (relationships embedded in entity data as foreign keys)

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


class ReadOptimizedDatabase(BaseDatabase):
    """
    Read-Optimized Database
    
    Uses HASH_MAP for O(1) lookups with no edge storage.
    Relationships are stored as foreign keys in the entity data (denormalized).
    """
    
    def __init__(self):
        super().__init__(
            name="Read-Optimized",
            node_mode=NodeMode.HASH_MAP,
            edge_mode=None  # No edge storage for maximum efficiency
        )
    
    def get_description(self) -> str:
        """Get database description"""
        return (
            "Read-Optimized Database using HASH_MAP strategy.\n"
            "Optimized for O(1) read operations with denormalized data.\n"
            "Best for: Fast lookups, frequent reads, minimal relationships"
        )

