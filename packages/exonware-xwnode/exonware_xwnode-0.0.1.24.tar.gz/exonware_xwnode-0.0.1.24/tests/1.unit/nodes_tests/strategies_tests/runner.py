#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/runner.py

Test runner for node strategies module
Auto-discovers and runs all 45+ node strategy tests.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
from pathlib import Path

# Add src to Python path for imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from exonware.xwsystem.utils.test_runner import TestRunner

if __name__ == "__main__":
    runner = TestRunner(
        library_name="xwnode",
        layer_name="1.unit.nodes.strategies",
        description="Unit Tests - Node Strategies (45+ strategies: HASH_MAP, TRIE, LSM_TREE, etc.)",
        test_dir=Path(__file__).parent,
        markers=["xwnode_unit", "xwnode_node_strategy"]
    )
    sys.exit(runner.run())

