#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/x1_basic_db/benchmark.py

Basic Database Benchmark - Node-Only Testing (No Edges)

Tests ALL NodeModes with edge_mode=None (table-only storage).
Categorizes into Group A (Matrix/Array types) vs Group B (Others).

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
from typing import Dict, Any, List

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

from exonware.xwnode.defs import NodeMode

from x0_common import (
    BenchmarkMetrics, BaseDatabase,
    generate_user, generate_post, generate_comment,
    get_all_node_modes
)

# ==============================================================================
# BENCHMARK CONFIGURATION
# ==============================================================================

# Test size configuration
TEST_CONFIG_SIZE = [1000, 10000, 100000]

# Model groups
GROUP_A_MODELS = []  # Matrix/Array-based types
GROUP_B_MODELS = []  # All other types
TEST_CONFIG_MODELS = []  # All models combined

# Format configuration (not used in this benchmark)
TEST_CONFIG_FORMATS = []

# Operations configuration (not used in this benchmark)
TEST_CONFIG_OPERATIONS = []

# Legacy aliases
TESTS = TEST_CONFIG_SIZE
MODELS = TEST_CONFIG_MODELS

def generate_models():
    """Auto-discover and categorize all NodeModes"""
    global GROUP_A_MODELS, GROUP_B_MODELS, TEST_CONFIG_MODELS, MODELS
    
    all_node_modes = get_all_node_modes()
    
    # Group A: Matrix/Array-based types (optimized for table-like data)
    matrix_types = {
        NodeMode.SPARSE_MATRIX, NodeMode.ARRAY_LIST, NodeMode.BITMAP,
    }
    
    GROUP_A_MODELS = []
    GROUP_B_MODELS = []
    
    for node_mode in all_node_modes:
        model = {
            'name': node_mode.name,
            'node_mode': node_mode,
            'edge_mode': None
        }
        if node_mode in matrix_types:
            GROUP_A_MODELS.append(model)
        else:
            GROUP_B_MODELS.append(model)
    
    TEST_CONFIG_MODELS = GROUP_A_MODELS + GROUP_B_MODELS
    MODELS = TEST_CONFIG_MODELS
    
    return len(TEST_CONFIG_MODELS)

# Auto-generate models at import time
total_models = generate_models()
print(f"Auto-generated {total_models} node-only models ({len(GROUP_A_MODELS)} matrix types, {len(GROUP_B_MODELS)} others)")


class DynamicDatabase(BaseDatabase):
    """Dynamically configured database from MODELS configuration"""
    
    def __init__(self, model_config: dict):
        """
        Initialize database from model configuration.
        
        Args:
            model_config: Dictionary with name, node_mode, edge_mode
        """
        super().__init__(
            name=model_config['name'],
            node_mode=model_config['node_mode'],
            edge_mode=model_config.get('edge_mode')
        )
        self.description = model_config.get('description', '')
    
    def get_description(self) -> str:
        """Get database description"""
        return self.description


class BasicBenchmark:
    """Benchmark runner for node-only configurations"""
    
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
            # Phase 1: Insert operations (NO relationships since edge_mode=None)
            with metrics.measure("insert"):
                for i in range(self.num_users):
                    user_ids.append(db.insert_user(generate_user(i)))
                for i in range(self.num_posts):
                    post_ids.append(db.insert_post(generate_post(i, random.choice(user_ids))))
                for i in range(self.num_comments):
                    comment_ids.append(db.insert_comment(generate_comment(i, random.choice(post_ids), random.choice(user_ids))))
            
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
            
            total_time = metrics.get_total_time()
            peak_memory = metrics.get_peak_memory()
            
            # Handle both NodeMode enum and preset strings
            node_mode_name = db.node_mode if isinstance(db.node_mode, str) else db.node_mode.name
            
            return {
                'database': db.name,
                'node_mode': node_mode_name,
                'edge_mode': 'None',
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
                'edge_mode': 'None',
                'total_entities': self.total_entities,
                'scale': f'{self.scale_factor}x',
                'total_time_ms': float('inf'),
                'peak_memory_mb': float('inf'),
                'success': False,
                'error': str(e)
            }
    
    def run_all(self):
        """Run benchmarks on all node-only configurations"""
        print(f"\n{'='*80}")
        print(f"BASIC DATABASE BENCHMARK (NODE-ONLY) - {self.total_entities:,} ENTITIES")
        print(f"{'='*80}")
        print(f"\nConfiguration:")
        print(f"  Total Entities (actual): {self.num_users + self.num_posts + self.num_comments:,}")
        print(f"  Distribution: {self.num_users:,} users, {self.num_posts:,} posts, {self.num_comments:,} comments")
        print(f"  Total Models: {len(self.databases)}")
        print(f"    Group A (Matrix/Array): {len(GROUP_A_MODELS)}")
        print(f"    Group B (Others): {len(GROUP_B_MODELS)}")
        print(f"\nTesting ALL NodeModes with edge_mode=None (table-only storage)...")
        print(f"This tests the hypothesis: 'Matrix types win for table-only storage'\n")
        
        successful = 0
        failed = 0
        
        for i, db in enumerate(self.databases):
            # Progress indicator
            if (i + 1) % 50 == 0 or i == 0 or (i + 1) == len(self.databases):
                progress = (i + 1) / len(self.databases) * 100
                print(f"Progress: {i+1}/{len(self.databases)} ({progress:.1f}%) - Success: {successful}, Failed: {failed}")
            
            try:
                result = self.run_benchmark(db)
                self.results[db.name] = result
                
                if result.get('success', True):
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                failed += 1
                node_mode_name = db.node_mode if isinstance(db.node_mode, str) else db.node_mode.name
                self.results[db.name] = {
                    'database': db.name,
                    'node_mode': node_mode_name,
                    'edge_mode': 'None',
                    'total_entities': self.total_entities,
                    'scale': f'{self.scale_factor}x',
                    'success': False,
                    'error': str(e)
                }
        
        print(f"\nCompleted: {successful} successful, {failed} failed")
        
        # Show top 10 winners overall
        successful_results = {k: v for k, v in self.results.items() if v.get('success', True)}
        if successful_results:
            sorted_results = sorted(successful_results.items(), 
                                   key=lambda x: x[1].get('total_time_ms', float('inf')))
            
            print(f"\n{'='*80}")
            print(f"TOP 10 WINNERS (ALL GROUPS) - {self.total_entities:,} ENTITIES")
            print(f"{'='*80}")
            for rank, (name, data) in enumerate(sorted_results[:10], 1):
                time_ms = data.get('total_time_ms', 0)
                memory = data.get('peak_memory_mb', 0)
                # Determine group
                is_group_a = any(m['name'] == name for m in GROUP_A_MODELS)
                group = "Group A" if is_group_a else "Group B"
                print(f"  {rank:2}. {name} ({group}): {time_ms:.2f}ms, {memory:.1f}MB")
            
            # Show top 5 from each group
            group_a_results = {k: v for k, v in successful_results.items() 
                              if any(m['name'] == k for m in GROUP_A_MODELS)}
            group_b_results = {k: v for k, v in successful_results.items() 
                              if any(m['name'] == k for m in GROUP_B_MODELS)}
            
            if group_a_results:
                sorted_a = sorted(group_a_results.items(), 
                                 key=lambda x: x[1].get('total_time_ms', float('inf')))
                print(f"\n{'='*80}")
                print(f"TOP 5 - GROUP A (MATRIX/ARRAY TYPES) - {self.total_entities:,} ENTITIES")
                print(f"{'='*80}")
                for rank, (name, data) in enumerate(sorted_a[:5], 1):
                    time_ms = data.get('total_time_ms', 0)
                    memory = data.get('peak_memory_mb', 0)
                    print(f"  {rank}. {name}: {time_ms:.2f}ms, {memory:.1f}MB")
            
            if group_b_results:
                sorted_b = sorted(group_b_results.items(), 
                                 key=lambda x: x[1].get('total_time_ms', float('inf')))
                print(f"\n{'='*80}")
                print(f"TOP 5 - GROUP B (OTHER TYPES) - {self.total_entities:,} ENTITIES")
                print(f"{'='*80}")
                for rank, (name, data) in enumerate(sorted_b[:5], 1):
                    time_ms = data.get('total_time_ms', 0)
                    memory = data.get('peak_memory_mb', 0)
                    print(f"  {rank}. {name}: {time_ms:.2f}ms, {memory:.1f}MB")


def run_all_tests():
    """Run all tests defined in TESTS array and generate combined output files"""
    print(f"\n{'='*80}")
    print(f"BASIC DATABASE BENCHMARK (NODE-ONLY) - AUTO RUN")
    print(f"{'='*80}")
    print(f"\nTests to run: {', '.join([f'{t:,}' for t in TESTS])} entities")
    print(f"Total models per test: {len(MODELS)}")
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
        
        benchmark = BasicBenchmark(total_entities=entities)
        benchmark.run_all()
        
        # Store results with entity count as key
        all_results[str(entities)] = benchmark.results
    
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
    
    # Generate combined CSV file
    csv_file = output_dir / f"results{timestamp}.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['# Basic Database Benchmark (Node-Only) Results - Combined'])
            writer.writerow([f'# All Tests: {", ".join([f"{k} entities" for k in all_results.keys()])}'])
            writer.writerow([f'# Total models per test: {len(MODELS)}'])
            writer.writerow([])
            
            # Write results for each test
            for entities_str, results in all_results.items():
                # Filter successful results
                successful_results = {k: v for k, v in results.items() if v.get('success', True)}
                
                writer.writerow([f'=== DETAILED RESULTS - {entities_str} Entities ==='])
                writer.writerow([f'# Successful: {len(successful_results)} / {len(results)}'])
                writer.writerow([])
                
                # Detailed results header
                writer.writerow([
                    'Rank', 'Configuration', 'Node Mode', 'Group', 
                    'Total Time (ms)', 'Peak Memory (MB)', 'Operations/sec',
                    'Insert Time (ms)', 'Insert Memory (MB)',
                    'Read Time (ms)', 'Read Memory (MB)',
                    'Update Time (ms)', 'Update Memory (MB)'
                ])
                
                # Sort by total time
                sorted_results = sorted(successful_results.items(), 
                                      key=lambda x: x[1].get('total_time_ms', float('inf')))
                
                # Write ALL results with detailed metrics
                for rank, (name, data) in enumerate(sorted_results, 1):
                    node = data.get('node_mode', 'N/A')
                    time_ms = data.get('total_time_ms', 0)
                    memory = data.get('peak_memory_mb', 0)
                    ops_sec = (50000 / (time_ms / 1000)) if time_ms > 0 else 0
                    
                    # Determine group
                    is_group_a = any(m['name'] == name for m in GROUP_A_MODELS)
                    group = "Group A (Matrix)" if is_group_a else "Group B (Others)"
                    
                    # Extract detailed metrics
                    metrics = data.get('metrics', {})
                    insert_metrics = metrics.get('insert', {})
                    read_metrics = metrics.get('read', {})
                    update_metrics = metrics.get('update', {})
                    
                    writer.writerow([
                        rank, name, node, group,
                        f'{time_ms:.2f}', f'{memory:.1f}', f'{ops_sec:.0f}',
                        f'{insert_metrics.get("total_time_ms", 0):.2f}', f'{insert_metrics.get("peak_memory_mb", 0):.1f}',
                        f'{read_metrics.get("total_time_ms", 0):.2f}', f'{read_metrics.get("peak_memory_mb", 0):.1f}',
                        f'{update_metrics.get("total_time_ms", 0):.2f}', f'{update_metrics.get("peak_memory_mb", 0):.1f}'
                    ])
                
                writer.writerow([])
                writer.writerow([f'=== SUMMARY - {entities_str} Entities ==='])
                writer.writerow([])
                
                # Summary statistics
                if sorted_results:
                    times = [r.get('total_time_ms', 0) for r in successful_results.values()]
                    memories = [r.get('peak_memory_mb', 0) for r in successful_results.values()]
                    
                    writer.writerow(['Metric', 'Value'])
                    writer.writerow(['Total Models Tested', len(results)])
                    writer.writerow(['Successful', len(successful_results)])
                    writer.writerow(['Failed', len(results) - len(successful_results)])
                    writer.writerow(['Fastest Time (ms)', f'{min(times):.2f}'])
                    writer.writerow(['Slowest Time (ms)', f'{max(times):.2f}'])
                    writer.writerow(['Average Time (ms)', f'{sum(times)/len(times):.2f}'])
                    writer.writerow(['Lowest Memory (MB)', f'{min(memories):.1f}'])
                    writer.writerow(['Highest Memory (MB)', f'{max(memories):.1f}'])
                    writer.writerow(['Average Memory (MB)', f'{sum(memories)/len(memories):.1f}'])
                    writer.writerow(['Winner (Fastest)', sorted_results[0][0]])
                writer.writerow([])
        
        print(f"✓ Combined CSV: {csv_file.name}")
    
    except PermissionError:
        print(f"⚠️  WARNING: Could not write {csv_file.name} - file is open")
    
    print(f"\n{'='*80}")
    print(f"ALL BASIC BENCHMARKS COMPLETE")
    print(f"{'='*80}")
    print(f"\nTotal benchmarks completed: {sum(len(r) for r in all_results.values()):,}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Basic Database Benchmark (Node-Only)')
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
        
        benchmark = BasicBenchmark(total_entities=args.entities)
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
        print(f"\nSuccessful: {len(successful_results)} / {len(benchmark.results)}")


if __name__ == "__main__":
    main()

