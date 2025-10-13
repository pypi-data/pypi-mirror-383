#!/usr/bin/env python3
"""Display all configuration rankings"""

import json
from pathlib import Path

# Load results
with open('exhaustive_search_results.json') as f:
    data = json.load(f)

results = data['results']

print("\n" + "="*80)
print("ALL 30 CONFIGURATIONS RANKED")
print("="*80)
print(f"\n{'Rank':<6} {'Configuration':<45} {'Time':<12} {'Memory':<10}")
print("-"*80)

for i, r in enumerate(results[:30], 1):
    medal = "[WINNER]" if i == 1 else "[2nd]" if i == 2 else "[3rd]" if i == 3 else ""
    print(f"{i:<6} {r['combo']:<45} {r['total_time_ms']:<12.2f} {r['peak_memory_mb']:<10.1f} {medal}")

print("\n" + "="*80)
print(f"Fastest: {results[0]['combo']} at {results[0]['total_time_ms']:.2f}ms")
print(f"Slowest: {results[-1]['combo']} at {results[-1]['total_time_ms']:.2f}ms")
print(f"Range: {results[-1]['total_time_ms'] - results[0]['total_time_ms']:.2f}ms")
print("="*80)

