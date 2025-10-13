#!/usr/bin/env python3
"""
Write-Optimized Database Configuration

Optimizes for: High-throughput writes
- Node Strategy: LSM_TREE (write-optimized with compaction)
- Edge Strategy: DYNAMIC_ADJ_LIST (handles high churn)

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


class WriteOptimizedDatabase(BaseDatabase):
    """
    Write-Optimized Database
    
    Uses LSM_TREE for write-optimized operations with compaction.
    DYNAMIC_ADJ_LIST handles frequent relationship changes efficiently.
    """
    
    def __init__(self):
        super().__init__(
            name="Write-Optimized",
            node_mode=NodeMode.LSM_TREE,
            edge_mode=EdgeMode.DYNAMIC_ADJ_LIST
        )
    
    def get_description(self) -> str:
        """Get database description"""
        return (
            "Write-Optimized Database using LSM_TREE + DYNAMIC_ADJ_LIST.\n"
            "Optimized for high-throughput writes and frequent updates.\n"
            "Best for: Write-heavy workloads, frequent relationship changes"
        )

