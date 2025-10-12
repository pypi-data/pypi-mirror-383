#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick query test"""
import sys
import os
from pathlib import Path

if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

xwnode_root = Path(__file__).parent.parent.parent
xwnode_src = xwnode_root / "src"
xwsystem_src = xwnode_root.parent / "xwsystem" / "src"

sys.path.insert(0, str(xwnode_src))
if xwsystem_src.exists():
    sys.path.insert(0, str(xwsystem_src))
sys.path.insert(0, str(xwnode_root / "examples"))

from xwnode_console.console import XWQueryConsole

print("Testing: SELECT * FROM users WHERE age > 30")
print("=" * 70)
print(f"\nPython paths:")
for i, p in enumerate(sys.path[:10], 1):
    print(f"  {i}. {p}")

# Check if exonware.xwnode can be imported
print("\nTrying to import exonware.xwnode...")
try:
    import exonware.xwnode
    print("✓ exonware.xwnode found!")
    print(f"  Location: {exonware.xwnode.__file__}")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    
    # Check if the path exists
    expected_path = xwnode_src / "exonware" / "xwnode"
    print(f"\nExpected location: {expected_path}")
    print(f"  Exists: {expected_path.exists()}")
    
    if expected_path.exists():
        print(f"\nPath is in sys.path: {str(xwnode_src) in sys.path}")
        print(f"  xwnode_src: {xwnode_src}")

print("\n" + "=" * 70)
console = XWQueryConsole(seed=42, verbose=True)
console._execute_query("SELECT * FROM users WHERE age > 30")

print("\n" + "=" * 70)
print("Query test complete!")

