#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/runner.py

Test runner for edges module
Auto-discovers sub-modules or runs all edge tests directly.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
from pathlib import Path

# Add src to Python path for imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from exonware.xwsystem.utils.test_runner import TestRunner

if __name__ == "__main__":
    runner = TestRunner(
        library_name="xwnode",
        layer_name="1.unit.edges",
        description="Unit Tests - Edges Module (strategies, executors)",
        test_dir=Path(__file__).parent
    )
    sys.exit(runner.run())

