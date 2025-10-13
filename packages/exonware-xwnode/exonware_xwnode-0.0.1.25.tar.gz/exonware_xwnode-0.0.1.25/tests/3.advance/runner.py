#!/usr/bin/env python3
"""
#exonware/xwnode/tests/3.advance/runner.py

Advance test runner for xwnode - Production Excellence Validation
Auto-discovers and runs advance tests with support for priority filtering.

OPTIONAL until v1.0.0, MANDATORY for production releases.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025

Usage:
    python tests/3.advance/runner.py                 # Run all advance tests
    python tests/3.advance/runner.py --security      # Priority #1
    python tests/3.advance/runner.py --usability     # Priority #2
    python tests/3.advance/runner.py --maintainability  # Priority #3
    python tests/3.advance/runner.py --performance   # Priority #4
    python tests/3.advance/runner.py --extensibility # Priority #5
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from exonware.xwsystem.utils.test_runner import TestRunner

if __name__ == "__main__":
    # Parse arguments for specific priority
    args = sys.argv[1:]
    
    marker = "xwnode_advance"
    description = "Advance Tests - Production Excellence (All 5 Priorities)"
    
    # Determine which advance tests to run
    if "--security" in args:
        marker = "xwnode_security"
        description = "Advance Tests - Priority #1: Security Excellence"
    elif "--usability" in args:
        marker = "xwnode_usability"
        description = "Advance Tests - Priority #2: Usability Excellence"
    elif "--maintainability" in args:
        marker = "xwnode_maintainability"
        description = "Advance Tests - Priority #3: Maintainability Excellence"
    elif "--performance" in args:
        marker = "xwnode_performance"
        description = "Advance Tests - Priority #4: Performance Excellence"
    elif "--extensibility" in args:
        marker = "xwnode_extensibility"
        description = "Advance Tests - Priority #5: Extensibility Excellence"
    
    runner = TestRunner(
        library_name="xwnode",
        layer_name="3.advance",
        description=description,
        test_dir=Path(__file__).parent,
        markers=[marker]
    )
    sys.exit(runner.run())
