#!/usr/bin/env python3
"""
XWData-Optimized Database Configuration

Optimizes for: Data interchange patterns (xData library)
- Node Strategy: HASH_MAP with DATA_INTERCHANGE_OPTIMIZED preset
- Edge Strategy: None (zero graph overhead for maximum efficiency)
- Copy-on-write (COW) semantics for data interchange
- Structural hash caching for fast equality checks
- Object pooling support for factory patterns
- __slots__ optimization for minimal memory footprint

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


class XWDataOptimizedDatabase(BaseDatabase):
    """
    XWData-Optimized Database (DATA_INTERCHANGE_OPTIMIZED Preset)
    
    Uses HASH_MAP with DATA_INTERCHANGE_OPTIMIZED optimizations.
    Specifically designed for xData serialization/deserialization patterns.
    
    Features:
    - Zero graph overhead (no edge storage)
    - Copy-on-write semantics
    - Structural hash caching for fast equality
    - Object pooling support
    - Minimal memory footprint with __slots__
    - Ultra-lightweight for data interchange
    """
    
    def __init__(self):
        super().__init__(
            name="XWData-Optimized",
            node_mode=NodeMode.HASH_MAP,  # Base mode for DATA_INTERCHANGE_OPTIMIZED
            edge_mode=None  # No edge support - maximum efficiency for xData
        )
    
    def get_description(self) -> str:
        """Get database description"""
        return (
            "XWData-Optimized Database using DATA_INTERCHANGE_OPTIMIZED preset.\n"
            "Optimized for xData serialization with COW, pooling, and zero graph overhead.\n"
            "Best for: xData serialization, format conversion, high-throughput pipelines"
        )

