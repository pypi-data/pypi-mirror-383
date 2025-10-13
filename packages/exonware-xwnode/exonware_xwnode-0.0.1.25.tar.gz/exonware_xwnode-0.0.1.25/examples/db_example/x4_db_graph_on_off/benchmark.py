#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/db_graph_on_off/benchmark.py

Graph Manager ON/OFF Benchmark - All Combinations

Tests ALL NodeMode × EdgeMode combinations with Graph Manager ON and OFF.
Measures the performance impact of XWGraphManager indexing and caching.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

import sys
import json
import csv
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Configure UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass

# Add common module to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Add xwnode src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from exonware.xwnode.defs import NodeMode, EdgeMode, GraphOptimization

from x0_common import (
    BenchmarkMetrics, BaseDatabase,
    generate_user, generate_post, generate_comment, generate_relationship,
    generate_all_combinations
)

# ==============================================================================
# BENCHMARK CONFIGURATION
# ==============================================================================

# Test size configuration
TEST_CONFIG_SIZE = [1000, 10000, 100000]

# Model configuration (auto-generated from all NodeMode × EdgeMode combinations)
TEST_CONFIG_MODELS = []  # Auto-populated below

# Format configuration (not used in this benchmark)
TEST_CONFIG_FORMATS = []

# Operations configuration (not used in this benchmark)
TEST_CONFIG_OPERATIONS = []

# Legacy aliases for backward compatibility
TESTS = TEST_CONFIG_SIZE
MODELS = TEST_CONFIG_MODELS

def generate_models():
    """Generate all possible strategy combinations as MODELS"""
    global MODELS, TEST_CONFIG_MODELS
    combinations = generate_all_combinations()
    
    MODELS = []
    TEST_CONFIG_MODELS = []
    for combo in combinations:
        edge_name = combo.edge_mode.name if combo.edge_mode else 'None'
        
        # Only test with edge modes (Graph Manager requires edges)
        if combo.edge_mode is not None:
            # Add Graph OFF variant
            model_off = {
                'name': f"{combo.node_mode.name}+{edge_name}+GraphOFF",
                'description': f"{combo.node_mode.name} + {edge_name} (Graph: OFF)",
                'node_mode': combo.node_mode,
                'edge_mode': combo.edge_mode,
                'graph_manager': False
            }
            MODELS.append(model_off)
            TEST_CONFIG_MODELS.append(model_off)
            
            # Add Graph ON variant
            model_on = {
                'name': f"{combo.node_mode.name}+{edge_name}+GraphON",
                'description': f"{combo.node_mode.name} + {edge_name} (Graph: ON)",
                'node_mode': combo.node_mode,
                'edge_mode': combo.edge_mode,
                'graph_manager': True
            }
            MODELS.append(model_on)
            TEST_CONFIG_MODELS.append(model_on)
    
    return len(MODELS)

# Auto-generate models at import time
total_combinations = generate_models()
print(f"Auto-generated {total_combinations} graph on/off configurations ({total_combinations//2} combinations × 2 modes)")


class DynamicDatabase(BaseDatabase):
    """Dynamically configured database from MODELS configuration"""
    
    def __init__(self, model_config: dict):
        """
        Initialize database from model configuration.
        
        Args:
            model_config: Dictionary with name, node_mode, edge_mode, graph_manager
        """
        graph_opt = GraphOptimization.FULL if model_config.get('graph_manager') else GraphOptimization.OFF
        
        super().__init__(
            name=model_config['name'],
            node_mode=model_config['node_mode'],
            edge_mode=model_config.get('edge_mode'),
            graph_optimization=graph_opt
        )
        self.description = model_config.get('description', '')
        self.graph_enabled = model_config.get('graph_manager', False)
    
    def get_description(self) -> str:
        """Get database description"""
        return self.description


class GraphOnOffBenchmark:
    """Benchmark runner for Graph Manager ON/OFF comparison"""
    
    def __init__(self, total_entities: int = 1000):
        """
        Initialize benchmark.
        
        Args:
            total_entities: Total number of entities (users + posts + comments)
        """
        self.total_entities = total_entities
        self.databases = [DynamicDatabase(model) for model in MODELS]
        self.results = {}
        
        # Calculate scale factor for display
        self.scale_factor = total_entities // 1000
        
        # Entity distribution (lighter for exhaustive tests - 10% of full scale)
        base_scale = total_entities // 10
        self.num_users = int(base_scale * 0.5)
        self.num_posts = int(base_scale * 0.3)
        self.num_comments = int(base_scale * 0.2)
        
        # Relationships scale with users
        self.num_relationships = self.num_users * 2
        
        # Operations
        self.num_read_ops = max(10, int(self.num_users * 0.1))
        self.num_update_ops = max(10, int(self.num_users * 0.1))
    
    def run_benchmark(self, db: BaseDatabase) -> Dict[str, Any]:
        """Run lightweight benchmark on a single database"""
        metrics = BenchmarkMetrics()
        user_ids = []
        post_ids = []
        comment_ids = []
        
        try:
            # Phase 1: Insert operations
            with metrics.measure("insert"):
                for i in range(self.num_users):
                    user_ids.append(db.insert_user(generate_user(i)))
                for i in range(self.num_posts):
                    post_ids.append(db.insert_post(generate_post(i, random.choice(user_ids))))
                for i in range(self.num_comments):
                    comment_ids.append(db.insert_comment(generate_comment(i, random.choice(post_ids), random.choice(user_ids))))
                for i in range(self.num_relationships):
                    source, target = random.choice(user_ids), random.choice(user_ids)
                    if source != target:
                        db.add_relationship(generate_relationship(source, target))
            
            # Phase 2: Read operations
            with metrics.measure("read"):
                for _ in range(self.num_read_ops):
                    db.get_user(random.choice(user_ids))
                    db.get_post(random.choice(post_ids))
                    db.get_comment(random.choice(comment_ids))
            
            # Phase 3: Update operations
            with metrics.measure("update"):
                for i in range(self.num_update_ops):
                    db.update_user(user_ids[i], {'bio': f'Updated {i}'})
                    if i < len(post_ids):
                        db.update_post(post_ids[i], {'likes_count': i})
                    if i < len(comment_ids):
                        db.update_comment(comment_ids[i], {'content': f'Updated {i}'})
            
            # Phase 4: Relationship queries (THIS IS WHERE GRAPH MANAGER HELPS!)
            with metrics.measure("relationships"):
                for _ in range(self.num_read_ops):
                    db.get_followers(random.choice(user_ids))
                    db.get_following(random.choice(user_ids))
            
            total_time = metrics.get_total_time()
            peak_memory = metrics.get_peak_memory()
            
            # Handle both NodeMode enum and preset strings
            node_mode_name = db.node_mode if isinstance(db.node_mode, str) else db.node_mode.name
            
            return {
                'database': db.name,
                'node_mode': node_mode_name,
                'edge_mode': db.edge_mode.name if db.edge_mode else 'None',
                'graph_enabled': db.graph_enabled,
                'total_entities': self.total_entities,
                'scale': f'{self.scale_factor}x',
                'total_time_ms': total_time,
                'peak_memory_mb': peak_memory,
                'metrics': metrics.get_metrics(),
                'stats': db.get_stats(),
                'success': True
            }
            
        except Exception as e:
            node_mode_name = db.node_mode if isinstance(db.node_mode, str) else db.node_mode.name
            return {
                'database': db.name,
                'node_mode': node_mode_name,
                'edge_mode': db.edge_mode.name if db.edge_mode else 'None',
                'graph_enabled': db.graph_enabled,
                'total_entities': self.total_entities,
                'scale': f'{self.scale_factor}x',
                'total_time_ms': float('inf'),
                'peak_memory_mb': float('inf'),
                'success': False,
                'error': str(e)
            }
    
    def run_all(self):
        """Run benchmarks on all configurations"""
        print(f"\n{'='*80}")
        print(f"GRAPH ON/OFF BENCHMARK - {self.total_entities:,} ENTITIES")
        print(f"{'='*80}")
        print(f"\nConfiguration:")
        print(f"  Total Entities (actual): {self.num_users + self.num_posts + self.num_comments:,}")
        print(f"  Distribution: {self.num_users:,} users, {self.num_posts:,} posts, {self.num_comments:,} comments")
        print(f"  Relationships: {self.num_relationships:,}")
        print(f"  Total Configurations: {len(self.databases)}")
        print(f"\nTesting each combination with Graph Manager OFF and ON...")
        print(f"This tests {len(self.databases)//2} combinations × 2 modes = {len(self.databases)} configs!\n")
        
        successful = 0
        failed = 0
        
        for i, db in enumerate(self.databases):
            # Progress indicator
            if (i + 1) % 100 == 0 or i == 0 or (i + 1) == len(self.databases):
                progress = (i + 1) / len(self.databases) * 100
                print(f"Progress: {i+1}/{len(self.databases)} ({progress:.1f}%) - Success: {successful}, Failed: {failed}")
            
            try:
                result = self.run_benchmark(db)
                self.results[db.name] = result
                
                if result.get('success', True):
                    successful += 1
                else:
                    failed += 1
                    # Show first few internal errors for debugging
                    if failed <= 3:
                        error_msg = result.get('error', 'Unknown error')
                        print(f"  [FAIL] {db.name}: {error_msg}")
                    
            except Exception as e:
                # Show first few errors for debugging
                if failed < 3:
                    print(f"  [ERROR] {db.name}: {e}")
                failed += 1
                node_mode_name = db.node_mode if isinstance(db.node_mode, str) else db.node_mode.name
                self.results[db.name] = {
                    'database': db.name,
                    'node_mode': node_mode_name,
                    'edge_mode': db.edge_mode.name if db.edge_mode else 'None',
                    'graph_enabled': db.graph_enabled,
                    'total_entities': self.total_entities,
                    'scale': f'{self.scale_factor}x',
                    'success': False,
                    'error': str(e)
                }
        
        print(f"\nCompleted: {successful} successful, {failed} failed")
        
        # Show top 10 winners for Graph OFF and Graph ON separately
        successful_results = {k: v for k, v in self.results.items() if v.get('success', True)}
        
        # Split by graph status
        results_off = {k: v for k, v in successful_results.items() if not v.get('graph_enabled')}
        results_on = {k: v for k, v in successful_results.items() if v.get('graph_enabled')}
        
        if results_off:
            sorted_off = sorted(results_off.items(), 
                               key=lambda x: x[1].get('total_time_ms', float('inf')))
            
            print(f"\n{'='*80}")
            print(f"TOP 10 WINNERS - GRAPH OFF - {self.total_entities:,} ENTITIES")
            print(f"{'='*80}")
            for rank, (name, data) in enumerate(sorted_off[:10], 1):
                time_ms = data.get('total_time_ms', 0)
                memory = data.get('peak_memory_mb', 0)
                rel_time = data.get('metrics', {}).get('relationships', {}).get('total_time_ms', 0)
                print(f"  {rank:2}. {name.replace('+GraphOFF', '')}: {time_ms:.2f}ms (Rel: {rel_time:.2f}ms), {memory:.1f}MB")
        
        if results_on:
            sorted_on = sorted(results_on.items(), 
                              key=lambda x: x[1].get('total_time_ms', float('inf')))
            
            print(f"\n{'='*80}")
            print(f"TOP 10 WINNERS - GRAPH ON - {self.total_entities:,} ENTITIES")
            print(f"{'='*80}")
            for rank, (name, data) in enumerate(sorted_on[:10], 1):
                time_ms = data.get('total_time_ms', 0)
                memory = data.get('peak_memory_mb', 0)
                rel_time = data.get('metrics', {}).get('relationships', {}).get('total_time_ms', 0)
                print(f"  {rank:2}. {name.replace('+GraphON', '')}: {time_ms:.2f}ms (Rel: {rel_time:.2f}ms), {memory:.1f}MB")
        
        # Calculate and show speedups
        if results_off and results_on:
            print(f"\n{'='*80}")
            print(f"TOP 10 SPEEDUPS FROM GRAPH MANAGER")
            print(f"{'='*80}")
            
            speedups = []
            for name_off, data_off in results_off.items():
                # Find matching ON result
                base_name = name_off.replace('+GraphOFF', '')
                name_on = f"{base_name}+GraphON"
                
                if name_on in results_on:
                    data_on = results_on[name_on]
                    off_time = data_off.get('total_time_ms', 0)
                    on_time = data_on.get('total_time_ms', 0)
                    
                    if on_time > 0 and off_time > 0:
                        speedup = off_time / on_time
                        speedups.append({
                            'name': base_name,
                            'speedup': speedup,
                            'off_time': off_time,
                            'on_time': on_time
                        })
            
            speedups.sort(key=lambda x: x['speedup'], reverse=True)
            
            for rank, s in enumerate(speedups[:10], 1):
                print(f"  {rank:2}. {s['name']}: {s['speedup']:.2f}x faster ({s['off_time']:.2f}ms → {s['on_time']:.2f}ms)")
            
            if speedups:
                avg_speedup = sum(s['speedup'] for s in speedups) / len(speedups)
                print(f"\n  Average Speedup: {avg_speedup:.2f}x")



def run_all_tests():
    """Run all tests defined in TESTS array and generate combined output files"""
    print(f"\n{'='*80}")
    print(f"GRAPH ON/OFF BENCHMARK - AUTO RUN")
    print(f"{'='*80}")
    print(f"\nTests to run: {', '.join([f'{t:,}' for t in TESTS])} entities")
    print(f"Configurations per test: {len(MODELS)} ({len(MODELS)//2} combinations × 2 graph modes)")
    print(f"Total benchmarks: {len(TESTS)} × {len(MODELS)} = {len(TESTS) * len(MODELS):,}")
    print(f"{'='*80}\n")
    
    # Store all results
    all_results = {}
    output_dir = Path(__file__).resolve().parent
    
    # Run each test
    for i, entities in enumerate(TESTS, 1):
        print(f"\n{'*'*80}")
        print(f"TEST {i}/{len(TESTS)}: {entities:,} entities")
        print(f"{'*'*80}")
        
        benchmark = GraphOnOffBenchmark(total_entities=entities)
        benchmark.run_all()
        
        # Store results with entity count as key
        all_results[str(entities)] = benchmark.results
        
        # Show top 10 for this test
        successful_results = {k: v for k, v in benchmark.results.items() if v.get('success', True)}
        results_off = {k: v for k, v in successful_results.items() if not v.get('graph_enabled')}
        results_on = {k: v for k, v in successful_results.items() if v.get('graph_enabled')}
        
        if results_off:
            sorted_off = sorted(results_off.items(), 
                               key=lambda x: x[1].get('total_time_ms', float('inf')))
            
            print(f"\n{'='*80}")
            print(f"TOP 10 - GRAPH OFF - TEST {i}/{len(TESTS)} ({entities:,} entities)")
            print(f"{'='*80}")
            for rank, (name, data) in enumerate(sorted_off[:10], 1):
                time_ms = data.get('total_time_ms', 0)
                memory = data.get('peak_memory_mb', 0)
                print(f"  {rank:2}. {name.replace('+GraphOFF', '')}: {time_ms:.2f}ms, {memory:.1f}MB")
        
        if results_on:
            sorted_on = sorted(results_on.items(), 
                              key=lambda x: x[1].get('total_time_ms', float('inf')))
            
            print(f"\n{'='*80}")
            print(f"TOP 10 - GRAPH ON - TEST {i}/{len(TESTS)} ({entities:,} entities)")
            print(f"{'='*80}")
            for rank, (name, data) in enumerate(sorted_on[:10], 1):
                time_ms = data.get('total_time_ms', 0)
                memory = data.get('peak_memory_mb', 0)
                print(f"  {rank:2}. {name.replace('+GraphON', '')}: {time_ms:.2f}ms, {memory:.1f}MB")
    
    # Generate combined JSON file
    print(f"\n{'='*80}")
    print(f"GENERATING COMBINED OUTPUT FILES")
    print(f"{'='*80}")
    
    # Generate timestamp for output files
    timestamp = datetime.now().strftime("_%y%m%d%H%M%S")
    
    combined_json = output_dir / f"results{timestamp}.json"
    try:
        with open(combined_json, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"✓ Combined JSON: {combined_json.name}")
    except PermissionError:
        print(f"⚠️  WARNING: Could not write {combined_json.name} - file is open in another program")
        print(f"   Please close the file and run again")
    
    # Generate combined CSV file
    csv_file = output_dir / f"results{timestamp}.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['# Graph Manager ON/OFF Benchmark Results - Combined'])
            writer.writerow([f'# All Tests: {", ".join([f"{k} entities" for k in all_results.keys()])}'])
            writer.writerow([f'# Total configurations per test: {len(MODELS)}'])
            writer.writerow([f'# Each combination tested with Graph OFF and Graph ON'])
            writer.writerow([])
            
            # Write results for each test
            for entities_str, results in all_results.items():
                # Filter successful results
                successful_results = {k: v for k, v in results.items() if v.get('success', True)}
                
                writer.writerow([f'=== DETAILED RESULTS - {entities_str} Entities ==='])
                writer.writerow([f'# Successful: {len(successful_results)} / {len(results)}'])
                writer.writerow([])
                
                # Detailed results header (same as classic/exhaustive)
                writer.writerow([
                    'Rank', 'Configuration', 'Node Mode', 'Edge Mode', 'Graph Manager',
                    'Total Time (ms)', 'Peak Memory (MB)', 'Operations/sec',
                    'Insert Time (ms)', 'Insert Memory (MB)',
                    'Read Time (ms)', 'Read Memory (MB)',
                    'Update Time (ms)', 'Update Memory (MB)',
                    'Relationships Time (ms)', 'Relationships Memory (MB)'
                ])
                
                # Sort by total time
                sorted_results = sorted(successful_results.items(), 
                                      key=lambda x: x[1].get('total_time_ms', float('inf')))
                
                # Write ALL results with detailed metrics
                for rank, (name, data) in enumerate(sorted_results, 1):
                    node = data.get('node_mode', 'N/A')
                    edge = data.get('edge_mode', 'None')
                    graph = 'ON' if data.get('graph_enabled') else 'OFF'
                    time_ms = data.get('total_time_ms', 0)
                    memory = data.get('peak_memory_mb', 0)
                    ops_sec = (50000 / (time_ms / 1000)) if time_ms > 0 else 0
                    
                    # Extract detailed metrics
                    metrics = data.get('metrics', {})
                    insert_metrics = metrics.get('insert', {})
                    read_metrics = metrics.get('read', {})
                    update_metrics = metrics.get('update', {})
                    rel_metrics = metrics.get('relationships', {})
                    
                    writer.writerow([
                        rank, name, node, edge, graph,
                        f'{time_ms:.2f}', f'{memory:.1f}', f'{ops_sec:.0f}',
                        f'{insert_metrics.get("total_time_ms", 0):.2f}', f'{insert_metrics.get("peak_memory_mb", 0):.1f}',
                        f'{read_metrics.get("total_time_ms", 0):.2f}', f'{read_metrics.get("peak_memory_mb", 0):.1f}',
                        f'{update_metrics.get("total_time_ms", 0):.2f}', f'{update_metrics.get("peak_memory_mb", 0):.1f}',
                        f'{rel_metrics.get("total_time_ms", 0):.2f}', f'{rel_metrics.get("peak_memory_mb", 0):.1f}'
                    ])
                
                writer.writerow([])
                writer.writerow([f'=== SUMMARY - {entities_str} Entities ==='])
                writer.writerow([])
                
                # Summary statistics
                if sorted_results:
                    times = [r.get('total_time_ms', 0) for r in successful_results.values()]
                    memories = [r.get('peak_memory_mb', 0) for r in successful_results.values()]
                    
                    writer.writerow(['Metric', 'Value'])
                    writer.writerow(['Total Configurations Tested', len(results)])
                    writer.writerow(['Successful', len(successful_results)])
                    writer.writerow(['Failed', len(results) - len(successful_results)])
                    writer.writerow(['Fastest Time (ms)', f'{min(times):.2f}'])
                    writer.writerow(['Slowest Time (ms)', f'{max(times):.2f}'])
                    writer.writerow(['Average Time (ms)', f'{sum(times)/len(times):.2f}'])
                    writer.writerow(['Lowest Memory (MB)', f'{min(memories):.1f}'])
                    writer.writerow(['Highest Memory (MB)', f'{max(memories):.1f}'])
                    writer.writerow(['Average Memory (MB)', f'{sum(memories)/len(memories):.1f}'])
                    writer.writerow(['Overall Winner (Fastest)', sorted_results[0][0]])
                    
                    # Calculate graph manager impact
                    results_off_list = {k: v for k, v in successful_results.items() if not v.get('graph_enabled')}
                    results_on_list = {k: v for k, v in successful_results.items() if v.get('graph_enabled')}
                    
                    if results_off_list and results_on_list:
                        avg_time_off = sum(r.get('total_time_ms', 0) for r in results_off_list.values()) / len(results_off_list)
                        avg_time_on = sum(r.get('total_time_ms', 0) for r in results_on_list.values()) / len(results_on_list)
                        avg_speedup = avg_time_off / avg_time_on if avg_time_on > 0 else 1.0
                        
                        writer.writerow(['Average Speedup (Graph ON vs OFF)', f'{avg_speedup:.2f}x'])
                writer.writerow([])
        
        print(f"✓ Combined CSV: {csv_file.name}")
    
    except PermissionError:
        print(f"⚠️  WARNING: Could not write {csv_file.name} - file is open in another program")
        print(f"   Please close the file in Excel/IDE and run again")
    
    print(f"\n{'='*80}")
    print(f"ALL GRAPH ON/OFF BENCHMARKS COMPLETE")
    print(f"{'='*80}")
    print(f"\nFiles generated:")
    print(f"  ✓ results.json (combined JSON with all {len(TESTS)} tests)")
    print(f"  ✓ results.csv (combined CSV with all {len(TESTS)} tests)")
    print(f"\nTotal benchmarks completed: {sum(len(r) for r in all_results.values()):,}")
    print(f"Tests completed: {', '.join([f'{t:,}' for t in TESTS])} entities")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Graph Manager ON/OFF Benchmark - All Combinations')
    parser.add_argument('entities', type=int, nargs='?', default=None,
                        help='Total number of entities. If omitted, runs all tests from TESTS array.')
    args = parser.parse_args()
    
    if args.entities is None:
        # Run all tests from TESTS array
        run_all_tests()
    else:
        # Run single test
        if args.entities < 100:
            print(f"Error: Minimum 100 entities required (got {args.entities})")
            return 1
        
        benchmark = GraphOnOffBenchmark(total_entities=args.entities)
        benchmark.run_all()
        
        # Save individual results
        output_dir = Path(__file__).parent
        timestamp = datetime.now().strftime("_%y%m%d%H%M%S")
        json_file = output_dir / f"results_{args.entities}{timestamp}.json"
        
        # Filter successful results only
        successful_results = {k: v for k, v in benchmark.results.items() if v.get('success', True)}
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(successful_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK COMPLETE - {args.entities:,} ENTITIES")
        print(f"{'='*80}")
        print(f"\nFiles generated:")
        print(f"  - results_{args.entities}.json")
        print(f"\nSuccessful: {len(successful_results)} / {len(benchmark.results)}")


if __name__ == "__main__":
    main()

