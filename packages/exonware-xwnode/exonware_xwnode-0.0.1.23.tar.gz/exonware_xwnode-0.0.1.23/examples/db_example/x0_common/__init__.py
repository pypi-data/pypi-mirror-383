"""
Common utilities and base classes for database benchmarks.

This module provides shared code for all benchmark types:
- Entity schemas and data generators
- Performance metrics and measurement
- Base database class
- Predefined configurations
- Strategy discovery utilities

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

# Entity schemas and generators
from .schema import (
    User,
    Post,
    Comment,
    Relationship,
    generate_user,
    generate_post,
    generate_comment,
    generate_relationship
)

# Performance metrics
from .metrics import BenchmarkMetrics

# Base database
from .base import BaseDatabase

# Predefined configurations
from .db_configs import (
    ReadOptimizedDatabase,
    WriteOptimizedDatabase,
    MemoryEfficientDatabase,
    QueryOptimizedDatabase,
    PersistenceOptimizedDatabase,
    XWDataOptimizedDatabase,
    get_all_predefined_databases
)

# Strategy utilities
from .utils import (
    StrategyCombo,
    get_all_node_modes,
    get_all_edge_modes,
    generate_all_combinations
)

__all__ = [
    # Schemas
    'User',
    'Post',
    'Comment',
    'Relationship',
    'generate_user',
    'generate_post',
    'generate_comment',
    'generate_relationship',
    
    # Metrics
    'BenchmarkMetrics',
    
    # Base
    'BaseDatabase',
    
    # Configs
    'ReadOptimizedDatabase',
    'WriteOptimizedDatabase',
    'MemoryEfficientDatabase',
    'QueryOptimizedDatabase',
    'PersistenceOptimizedDatabase',
    'XWDataOptimizedDatabase',
    'get_all_predefined_databases',
    
    # Utils
    'StrategyCombo',
    'get_all_node_modes',
    'get_all_edge_modes',
    'generate_all_combinations',
]
