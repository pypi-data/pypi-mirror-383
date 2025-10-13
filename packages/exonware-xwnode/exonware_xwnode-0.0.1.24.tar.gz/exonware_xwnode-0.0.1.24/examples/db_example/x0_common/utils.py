"""
Utility Functions

Helper functions for benchmarking.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

import sys
from pathlib import Path
from typing import List
from dataclasses import dataclass

# Add xwnode src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from exonware.xwnode.defs import NodeMode, EdgeMode


@dataclass
class StrategyCombo:
    """Represents a node+edge strategy combination"""
    node_mode: NodeMode
    edge_mode: EdgeMode | None
    name: str
    
    def __str__(self):
        edge_str = self.edge_mode.name if self.edge_mode else "None"
        return f"{self.node_mode.name}+{edge_str}"


def get_all_node_modes() -> List[NodeMode]:
    """Get all available node modes (excluding AUTO)"""
    return [mode for mode in NodeMode if mode != NodeMode.AUTO]


def get_all_edge_modes() -> List[EdgeMode | None]:
    """Get all available edge modes (including None, excluding AUTO)"""
    return [None] + [mode for mode in EdgeMode if mode != EdgeMode.AUTO]


def generate_all_combinations() -> List[StrategyCombo]:
    """Generate all valid node+edge combinations"""
    combinations = []
    
    for node_mode in get_all_node_modes():
        for edge_mode in get_all_edge_modes():
            combo = StrategyCombo(
                node_mode=node_mode,
                edge_mode=edge_mode,
                name=f"{node_mode.name}+{edge_mode.name if edge_mode else 'None'}"
            )
            combinations.append(combo)
    
    return combinations

