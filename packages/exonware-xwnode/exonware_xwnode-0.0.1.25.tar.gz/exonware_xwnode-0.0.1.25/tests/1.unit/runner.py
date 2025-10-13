#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/runner.py

Unit test orchestrator for xwnode
Auto-discovers module runners or runs all unit tests directly.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
from pathlib import Path

# Add src to Python path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from exonware.xwsystem.utils.test_runner import TestRunner

if __name__ == "__main__":
    runner = TestRunner(
        library_name="xwnode",
        layer_name="1.unit",
        description="Unit Tests - Module by Module",
        test_dir=Path(__file__).parent
    )
    sys.exit(runner.run())
