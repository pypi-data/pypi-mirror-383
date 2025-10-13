#!/usr/bin/env python3
"""
Memory-Efficient Database Configuration

Optimizes for: Minimal memory footprint
- Node Strategy: B_TREE (disk-based, minimal RAM)
- Edge Strategy: CSR (Compressed Sparse Row - minimal edge storage)

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


class MemoryEfficientDatabase(BaseDatabase):
    """
    Memory-Efficient Database
    
    Uses B_TREE for disk-based storage with minimal RAM usage.
    CSR (Compressed Sparse Row) minimizes edge storage requirements.
    """
    
    def __init__(self):
        super().__init__(
            name="Memory-Efficient",
            node_mode=NodeMode.B_TREE,
            edge_mode=EdgeMode.CSR
        )
    
    def get_description(self) -> str:
        """Get database description"""
        return (
            "Memory-Efficient Database using B_TREE + CSR.\n"
            "Optimized for minimal memory footprint with disk-based storage.\n"
            "Best for: Large datasets, limited RAM, sparse relationships"
        )

