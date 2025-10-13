#!/usr/bin/env python3
"""
10x Exhaustive Search with Incremental Progress Saving

This version saves results after every batch for monitoring.
"""

import sys
import json
import os
from pathlib import Path

# Change to script directory
os.chdir(Path(__file__).parent)

# Import the main runner
sys.path.insert(0, str(Path(__file__).parent))

# Import everything from the main script
from run_exhaustive_search_10x import ExhaustiveSearch10xRunner, PREDICTIONS_10X

print("\n" + "="*80)
print("MONITORED 10x EXHAUSTIVE SEARCH")
print("="*80)
print("\nThis version saves progress incrementally for monitoring.")
print("Check 'exhaustive_search_results_10x.json' for real-time progress!")
print("\nStarting now...")

runner = ExhaustiveSearch10xRunner()
results = runner.run_exhaustive_search()

print("\n10x SWEEP COMPLETE!")
if results:
    print(f"Winner: {results[0]['combo']} at {results[0]['total_time_ms']:.2f}ms")

