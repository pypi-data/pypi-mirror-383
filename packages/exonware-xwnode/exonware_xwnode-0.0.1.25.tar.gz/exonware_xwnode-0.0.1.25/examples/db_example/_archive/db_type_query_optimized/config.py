#!/usr/bin/env python3
"""
Query-Optimized Database Configuration

Optimizes for: Complex queries and graph traversal
- Node Strategy: TREE_GRAPH_HYBRID (unified tree + graph navigation)
- Edge Strategy: WEIGHTED_GRAPH (supports graph algorithms)

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


class QueryOptimizedDatabase(BaseDatabase):
    """
    Query-Optimized Database
    
    Uses TREE_GRAPH_HYBRID for both hierarchical and graph operations.
    WEIGHTED_GRAPH enables shortest path, PageRank, and other graph algorithms.
    """
    
    def __init__(self):
        super().__init__(
            name="Query-Optimized",
            node_mode=NodeMode.TREE_GRAPH_HYBRID,
            edge_mode=EdgeMode.WEIGHTED_GRAPH
        )
    
    def get_description(self) -> str:
        """Get database description"""
        return (
            "Query-Optimized Database using TREE_GRAPH_HYBRID + WEIGHTED_GRAPH.\n"
            "Optimized for complex queries and graph traversal algorithms.\n"
            "Best for: Complex queries, graph algorithms, mixed workloads"
        )

