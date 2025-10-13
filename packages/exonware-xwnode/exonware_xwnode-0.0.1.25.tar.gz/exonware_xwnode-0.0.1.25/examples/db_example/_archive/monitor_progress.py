#!/usr/bin/env python3
"""Monitor exhaustive search progress"""

import json
import time
from pathlib import Path

results_file = Path(__file__).parent / "exhaustive_search_results.json"

print("Monitoring exhaustive search progress...")
print("Press Ctrl+C to stop monitoring\n")

last_count = 0
start_time = time.time()

try:
    while True:
        if results_file.exists():
            try:
                with open(results_file) as f:
                    data = json.load(f)
                    current_count = len(data.get('results', []))
                    
                    if current_count != last_count:
                        elapsed = time.time() - start_time
                        rate = current_count / elapsed if elapsed > 0 else 0
                        eta = (760 - current_count) / rate if rate > 0 else 0
                        
                        print(f"Progress: {current_count}/760 ({current_count/760*100:.1f}%) - "
                              f"Rate: {rate:.1f} tests/sec - ETA: {eta/60:.1f} min")
                        
                        if current_count > 0:
                            top = data['results'][0]
                            print(f"Current leader: {top['combo']} at {top['total_time_ms']:.2f}ms\n")
                        
                        last_count = current_count
            except:
                pass
        
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\nMonitoring stopped.")

