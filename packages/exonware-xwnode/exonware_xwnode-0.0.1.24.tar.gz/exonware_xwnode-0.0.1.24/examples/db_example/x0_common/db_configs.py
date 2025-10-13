"""
Predefined Database Configurations

Standard database configurations for benchmarking.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

import sys
from pathlib import Path
from typing import List

# Add xwnode src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from exonware.xwnode.defs import NodeMode, EdgeMode
from .base import BaseDatabase


class ReadOptimizedDatabase(BaseDatabase):
    """Read-Optimized: HASH_MAP + None (O(1) lookups)"""
    
    def __init__(self):
        super().__init__(
            name="Read-Optimized",
            node_mode=NodeMode.HASH_MAP,
            edge_mode=None
        )
    
    def get_description(self) -> str:
        return "Read-Optimized Database using HASH_MAP. Best for: Fast lookups, frequent reads"


class WriteOptimizedDatabase(BaseDatabase):
    """Write-Optimized: LSM_TREE + DYNAMIC_ADJ_LIST (High-throughput writes)"""
    
    def __init__(self):
        super().__init__(
            name="Write-Optimized",
            node_mode=NodeMode.LSM_TREE,
            edge_mode=EdgeMode.DYNAMIC_ADJ_LIST
        )
    
    def get_description(self) -> str:
        return "Write-Optimized Database using LSM_TREE. Best for: High write throughput, inserts"


class MemoryEfficientDatabase(BaseDatabase):
    """Memory-Efficient: B_TREE + CSR (Minimal memory footprint)"""
    
    def __init__(self):
        super().__init__(
            name="Memory-Efficient",
            node_mode=NodeMode.B_TREE,
            edge_mode=EdgeMode.CSR
        )
    
    def get_description(self) -> str:
        return "Memory-Efficient Database using B_TREE. Best for: Large datasets, minimal RAM"


class QueryOptimizedDatabase(BaseDatabase):
    """Query-Optimized: TREE_GRAPH_HYBRID + WEIGHTED_GRAPH (Complex queries)"""
    
    def __init__(self):
        super().__init__(
            name="Query-Optimized",
            node_mode=NodeMode.TREE_GRAPH_HYBRID,
            edge_mode=EdgeMode.WEIGHTED_GRAPH
        )
    
    def get_description(self) -> str:
        return "Query-Optimized Database using TREE_GRAPH_HYBRID. Best for: Graph traversal, complex queries"


class PersistenceOptimizedDatabase(BaseDatabase):
    """Persistence-Optimized: B_PLUS_TREE + EDGE_PROPERTY_STORE (Durability)"""
    
    def __init__(self):
        super().__init__(
            name="Persistence-Optimized",
            node_mode=NodeMode.B_PLUS_TREE,
            edge_mode=EdgeMode.EDGE_PROPERTY_STORE
        )
    
    def get_description(self) -> str:
        return "Persistence-Optimized Database using B_PLUS_TREE. Best for: Durability, ACID compliance"


class XWDataOptimizedDatabase(BaseDatabase):
    """XWData-Optimized: HASH_MAP + None (Data interchange patterns)"""
    
    def __init__(self):
        super().__init__(
            name="XWData-Optimized",
            node_mode=NodeMode.HASH_MAP,
            edge_mode=None
        )
    
    def get_description(self) -> str:
        return "XWData-Optimized Database using DATA_INTERCHANGE_OPTIMIZED. Best for: Serialization, format conversion"


def get_all_predefined_databases() -> List[BaseDatabase]:
    """Get all predefined database configurations"""
    return [
        ReadOptimizedDatabase(),
        WriteOptimizedDatabase(),
        MemoryEfficientDatabase(),
        QueryOptimizedDatabase(),
        PersistenceOptimizedDatabase(),
        XWDataOptimizedDatabase()
    ]

