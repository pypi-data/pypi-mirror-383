#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Test Script

Simulates user interaction with the XWQuery console.
"""

import sys
import os
from pathlib import Path
from io import StringIO

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add source directories
xwnode_root = Path(__file__).parent.parent.parent
xwnode_src = xwnode_root / "src"
xwsystem_src = xwnode_root.parent / "xwsystem" / "src"

sys.path.insert(0, str(xwnode_src))
if xwsystem_src.exists():
    sys.path.insert(0, str(xwsystem_src))

sys.path.insert(0, str(xwnode_root / "examples"))

from xwnode_console.console import XWQueryConsole


def simulate_user_input(console, commands):
    """Simulate user input commands."""
    print("\n" + "=" * 70)
    print("SIMULATED USER SESSION")
    print("=" * 70)
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n[{i}/{len(commands)}] XWQuery> {cmd}")
        print("-" * 70)
        
        try:
            if cmd.startswith('.'):
                console._handle_command(cmd)
            else:
                console._execute_query(cmd)
            console.history.append(cmd)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")


def main():
    """Run interactive simulation."""
    print("=" * 70)
    print("XWQuery Console - Interactive Test")
    print("=" * 70)
    
    # Create console
    console = XWQueryConsole(seed=42, verbose=False)
    
    # Test commands
    commands = [
        # Console commands
        ".help",
        ".collections",
        ".show users",
        ".examples",
        ".examples core",
        ".random",
        
        # Basic queries
        "SELECT * FROM users",
        "SELECT name, age FROM users",
        "SELECT * FROM users WHERE age > 30",
        "SELECT * FROM products WHERE price < 50",
        
        # Aggregations
        "SELECT category, COUNT(*) FROM products GROUP BY category",
        
        # Ordering
        "SELECT * FROM users ORDER BY age",
        "SELECT * FROM products ORDER BY price DESC",
        
        # Limits
        "SELECT * FROM events LIMIT 10",
        
        # Show history
        ".history",
    ]
    
    simulate_user_input(console, commands)
    
    print("\n" + "=" * 70)
    print("INTERACTIVE TEST COMPLETE")
    print("=" * 70)
    print(f"\nExecuted {len(console.history)} commands successfully!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

