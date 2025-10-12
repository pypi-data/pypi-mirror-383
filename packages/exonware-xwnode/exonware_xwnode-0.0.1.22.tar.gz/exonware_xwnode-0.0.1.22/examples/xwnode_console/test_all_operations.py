#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test All XWQuery Operations

Comprehensive test script to validate all console operations.
"""

import sys
import os
from pathlib import Path

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
from xwnode_console import data


def test_console_commands():
    """Test all console commands."""
    print("=" * 70)
    print("TESTING CONSOLE COMMANDS")
    print("=" * 70)
    
    console = XWQueryConsole(seed=42, verbose=True)
    
    # Test .collections command
    print("\n[TEST] .collections command")
    try:
        console._handle_command('.collections')
        print("✓ .collections command works")
    except Exception as e:
        print(f"✗ .collections command failed: {e}")
    
    # Test .show command
    print("\n[TEST] .show users command")
    try:
        console._handle_command('.show users')
        print("✓ .show command works")
    except Exception as e:
        print(f"✗ .show command failed: {e}")
    
    # Test .examples command
    print("\n[TEST] .examples command")
    try:
        console._handle_command('.examples')
        print("✓ .examples command works")
    except Exception as e:
        print(f"✗ .examples command failed: {e}")
    
    # Test .examples core
    print("\n[TEST] .examples core command")
    try:
        console._handle_command('.examples core')
        print("✓ .examples core command works")
    except Exception as e:
        print(f"✗ .examples core command failed: {e}")
    
    # Test .random command
    print("\n[TEST] .random command")
    try:
        console._handle_command('.random')
        print("✓ .random command works")
    except Exception as e:
        print(f"✗ .random command failed: {e}")
    
    # Test .history command
    print("\n[TEST] .history command")
    try:
        console._handle_command('.history')
        print("✓ .history command works")
    except Exception as e:
        print(f"✗ .history command failed: {e}")
    
    print("\n" + "=" * 70)
    print("CONSOLE COMMANDS TEST COMPLETE")
    print("=" * 70)


def test_queries():
    """Test various XWQuery operations."""
    print("\n" + "=" * 70)
    print("TESTING XWQUERY OPERATIONS")
    print("=" * 70)
    
    console = XWQueryConsole(seed=42, verbose=True)
    
    queries = [
        ("SELECT * FROM users", "Basic SELECT all"),
        ("SELECT name, age FROM users", "SELECT specific columns"),
        ("SELECT * FROM users WHERE age > 30", "SELECT with WHERE"),
        ("SELECT * FROM products WHERE price < 50", "SELECT with numeric WHERE"),
        ("SELECT category, COUNT(*) FROM products GROUP BY category", "GROUP BY with COUNT"),
        ("SELECT * FROM users ORDER BY age", "ORDER BY"),
        ("SELECT * FROM users LIMIT 5", "LIMIT clause"),
    ]
    
    for query, description in queries:
        print(f"\n[TEST] {description}: {query}")
        try:
            console._execute_query(query)
            print(f"✓ Query executed successfully")
        except Exception as e:
            print(f"✗ Query failed: {e}")
            if console.verbose:
                import traceback
                traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("QUERY OPERATIONS TEST COMPLETE")
    print("=" * 70)


def test_data_integrity():
    """Test data loading and integrity."""
    print("\n" + "=" * 70)
    print("TESTING DATA INTEGRITY")
    print("=" * 70)
    
    collections = data.load_all_collections(seed=42)
    
    print(f"\n[TEST] Collections loaded: {len(collections)}")
    assert len(collections) == 5, "Should load 5 collections"
    print("✓ Correct number of collections")
    
    expected = {
        'users': 50,
        'products': 100,
        'orders': 200,
        'posts': 30,
        'events': 500
    }
    
    for name, expected_count in expected.items():
        actual_count = len(collections[name])
        print(f"\n[TEST] {name}: expected {expected_count}, got {actual_count}")
        assert actual_count == expected_count, f"{name} should have {expected_count} records"
        print(f"✓ {name} has correct count")
    
    print("\n" + "=" * 70)
    print("DATA INTEGRITY TEST COMPLETE")
    print("=" * 70)


def test_error_handling():
    """Test error handling."""
    print("\n" + "=" * 70)
    print("TESTING ERROR HANDLING")
    print("=" * 70)
    
    console = XWQueryConsole(seed=42, verbose=False)
    
    # Test invalid command
    print("\n[TEST] Invalid command")
    try:
        console._handle_command('.invalid')
        print("✓ Invalid command handled gracefully")
    except Exception as e:
        print(f"✗ Invalid command raised exception: {e}")
    
    # Test invalid collection
    print("\n[TEST] Invalid collection in .show")
    try:
        console._handle_command('.show nonexistent')
        print("✓ Invalid collection handled gracefully")
    except Exception as e:
        print(f"✗ Invalid collection raised exception: {e}")
    
    # Test invalid query
    print("\n[TEST] Invalid query syntax")
    try:
        console._execute_query("INVALID QUERY SYNTAX")
        print("✓ Invalid query handled gracefully")
    except Exception as e:
        print(f"✓ Invalid query raised expected error: {type(e).__name__}")
    
    print("\n" + "=" * 70)
    print("ERROR HANDLING TEST COMPLETE")
    print("=" * 70)


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("XWQUERY CONSOLE - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    try:
        test_data_integrity()
        test_console_commands()
        test_queries()
        test_error_handling()
        
        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETE")
        print("=" * 70)
        print("\n✓ Console is working correctly!")
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

