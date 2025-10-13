#!/usr/bin/env python3
"""
#exonware/xwnode/tests/run_comprehensive_tests.py

Comprehensive test runner for xwnode library.

Runs all test categories in sequence:
1. Security tests (Priority #1)
2. Core functionality tests
3. Unit tests
4. Integration tests
5. Performance benchmarks

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
import pytest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))


def run_all_tests():
    """Run comprehensive test suite for xwnode."""
    
    print("="*80)
    print("xwnode Comprehensive Test Suite")
    print("="*80)
    print()
    
    # Test categories to run (in priority order)
    test_categories = [
        {
            'name': 'Security Tests (Priority #1)',
            'markers': '-m xwnode_security',
            'critical': True
        },
        {
            'name': 'Core Functionality Tests',
            'markers': '-m xwnode_core',
            'critical': True
        },
        {
            'name': 'Node Strategy Tests',
            'markers': 'tests/core/test_all_node_strategies.py',
            'critical': True
        },
        {
            'name': 'Edge Strategy Tests',
            'markers': 'tests/core/test_all_edge_strategies.py',
            'critical': True
        },
        {
            'name': 'Unit Tests',
            'markers': 'tests/unit/',
            'critical': False
        },
        {
            'name': 'Integration Tests',
            'markers': 'tests/integration/',
            'critical': False
        },
        {
            'name': 'Performance Benchmarks',
            'markers': '-m performance',
            'critical': False
        },
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    
    for category in test_categories:
        print(f"\n{'='*80}")
        print(f"Running: {category['name']}")
        print(f"{'='*80}\n")
        
        # Run tests for this category
        args = [
            category['markers'],
            '-v',
            '--tb=short',
            '--maxfail=5' if category['critical'] else '--maxfail=20',
        ]
        
        result = pytest.main(args)
        
        # Store results
        results[category['name']] = {
            'exit_code': result,
            'passed': result == 0,
            'critical': category['critical']
        }
        
        if result == 0:
            total_passed += 1
        else:
            total_failed += 1
            if category['critical']:
                print(f"\n⚠️  CRITICAL TEST FAILURE in {category['name']}")
                print("   Stopping test run - fix critical issues first")
                break
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    for name, result in results.items():
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        critical = " [CRITICAL]" if result['critical'] else ""
        print(f"{status}{critical}: {name}")
    
    print(f"\nTotal: {total_passed} passed, {total_failed} failed")
    
    # Exit with appropriate code
    if total_failed == 0:
        print("\n✅ ALL TESTS PASSED - Production Ready!")
        return 0
    else:
        print(f"\n❌ {total_failed} TEST CATEGORIES FAILED - Fix required")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)

