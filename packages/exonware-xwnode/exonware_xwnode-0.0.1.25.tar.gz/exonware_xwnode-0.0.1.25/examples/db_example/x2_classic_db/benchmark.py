#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/db_classic_mix/benchmark.py

Classic Database Benchmark - Predefined Configurations

Tests the 6 predefined database configurations at both 1x and 10x scales.

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

# Configure UTF-8 encoding for Windows console (emoji support)
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass  # Fallback to default encoding if configuration fails

# Add common module to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Add xwnode src to path for importing strategies
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from exonware.xwnode.defs import NodeMode, EdgeMode, GraphOptimization

from x0_common import (
    BenchmarkMetrics, BaseDatabase,
    generate_user, generate_post, generate_comment, generate_relationship
)

# ==============================================================================
# BENCHMARK CONFIGURATION
# ==============================================================================

# Test size configuration
TEST_CONFIG_SIZE = [1000, 10000, 100000]

# Model configuration (predefined classic database configurations)
TEST_CONFIG_MODELS = [
    {
        'name': 'Read-Optimized',
        'description': 'HASH_MAP + None. Best for: Fast lookups, frequent reads',
        'node_mode': NodeMode.HASH_MAP,
        'edge_mode': None
    },
    {
        'name': 'Write-Optimized',
        'description': 'LSM_TREE + DYNAMIC_ADJ_LIST. Best for: High write throughput, inserts',
        'node_mode': NodeMode.LSM_TREE,
        'edge_mode': EdgeMode.DYNAMIC_ADJ_LIST
    },
    {
        'name': 'Memory-Efficient',
        'description': 'B_TREE + CSR. Best for: Large datasets, minimal RAM',
        'node_mode': NodeMode.B_TREE,
        'edge_mode': EdgeMode.CSR
    },
    {
        'name': 'Query-Optimized',
        'description': 'TREE_GRAPH_HYBRID + WEIGHTED_GRAPH. Best for: Graph traversal, complex queries',
        'node_mode': NodeMode.TREE_GRAPH_HYBRID,
        'edge_mode': EdgeMode.WEIGHTED_GRAPH
    },
    {
        'name': 'Persistence-Optimized',
        'description': 'B_PLUS_TREE + EDGE_PROPERTY_STORE. Best for: Durability, ACID compliance',
        'node_mode': NodeMode.B_PLUS_TREE,
        'edge_mode': EdgeMode.EDGE_PROPERTY_STORE
    },
    {
        'name': 'XWData-Optimized',
        'description': 'DATA_INTERCHANGE_OPTIMIZED. Best for: Serialization, format conversion',
        'node_mode': NodeMode.DATA_INTERCHANGE_OPTIMIZED,  # Now a first-class NodeMode!
        'edge_mode': None
    }
    # To enable Graph Manager, add 'graph_manager': True to any model
    # Example:
    # {
    #     'name': 'Graph-Powered',
    #     'description': 'HASH_MAP + ADJ_LIST with Graph Manager',
    #     'node_mode': NodeMode.HASH_MAP,
    #     'edge_mode': EdgeMode.ADJ_LIST,
    #     'graph_manager': True  # Only specify when True
    # }
]

# Format configuration (not used in this benchmark)
TEST_CONFIG_FORMATS = []

# Operations configuration (not used in this benchmark)
TEST_CONFIG_OPERATIONS = []

# Legacy aliases for backward compatibility
TESTS = TEST_CONFIG_SIZE
MODELS = TEST_CONFIG_MODELS


class DynamicDatabase(BaseDatabase):
    """Dynamically configured database from MODELS configuration"""
    
    def __init__(self, model_config: dict):
        """
        Initialize database from model configuration.
        
        Args:
            model_config: Dictionary with name, node_mode, edge_mode, graph_manager
        """
        if model_config.get('graph_manager') is None:
            super().__init__(
                name=model_config['name'],
                node_mode=model_config['node_mode'],
                edge_mode=model_config.get('edge_mode')
            )
        else:
            graph_opt = GraphOptimization.OFF if not model_config.get('graph_manager') else GraphOptimization.FULL
            
            super().__init__(
                name=model_config['name'],
                node_mode=model_config['node_mode'],
                edge_mode=model_config.get('edge_mode'),
                graph_optimization=graph_opt
            )
        self.description = model_config.get('description', '')
    
    def get_description(self) -> str:
        """Get database description"""
        return self.description


class ClassicBenchmark:
    """Benchmark runner for configured database models"""
    
    def __init__(self, total_entities: int = 1000):
        """
        Initialize benchmark.
        
        Args:
            total_entities: Total number of entities (users + posts + comments)
                          Examples: 1000 (1K), 10000 (10K), 100000 (100K)
        """
        self.total_entities = total_entities
        self.databases = [DynamicDatabase(model) for model in MODELS]
        self.results = {}
        
        # Calculate scale factor for display (1K = 1x, 10K = 10x, 100K = 100x)
        self.scale_factor = total_entities // 1000
        
        # Entity distribution (50% users, 30% posts, 20% comments)
        self.num_users = int(total_entities * 0.5)
        self.num_posts = int(total_entities * 0.3)
        self.num_comments = int(total_entities * 0.2)
        
        # Relationships scale with users (2x number of users)
        self.num_relationships = self.num_users * 2
        
        # Operations scale with total entities (10% of users)
        self.num_read_ops = max(100, int(self.num_users * 0.1))
        self.num_update_users = int(self.num_users * 0.5)
        self.num_update_posts = int(self.num_posts * 0.5)
        self.num_update_comments = int(self.num_comments * 0.5)
        
    def run_benchmark(self, db: BaseDatabase) -> Dict[str, Any]:
        """Run complete benchmark on a single database"""
        print(f"\n{'='*80}")
        print(f"Benchmarking: {db.name} ({self.total_entities} entities)")
        print(f"{'='*80}")
        print(db.get_description())
        
        metrics = BenchmarkMetrics()
        user_ids = []
        post_ids = []
        comment_ids = []
        
        # Phase 1: Insert operations
        print(f"\n[Phase 1: Insert {self.num_users + self.num_posts + self.num_comments} entities + {self.num_relationships} relationships]")
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
        print(f"[Phase 2: Read {self.num_read_ops * 3} entities]")
        with metrics.measure("read"):
            for _ in range(self.num_read_ops):
                db.get_user(random.choice(user_ids))
                db.get_post(random.choice(post_ids))
                db.get_comment(random.choice(comment_ids))
        
        # Phase 3: Update operations
        print(f"[Phase 3: Update {self.num_update_users + self.num_update_posts + self.num_update_comments} entities]")
        with metrics.measure("update"):
            for i in range(self.num_update_users):
                db.update_user(user_ids[i], {'bio': f'Updated {i}'})
            for i in range(self.num_update_posts):
                db.update_post(post_ids[i], {'likes_count': i})
            for i in range(self.num_update_comments):
                db.update_comment(comment_ids[i], {'content': f'Updated {i}'})
        
        # Phase 4: Relationship queries
        print(f"[Phase 4: Query {self.num_read_ops * 2} relationships]")
        with metrics.measure("relationships"):
            for _ in range(self.num_read_ops):
                db.get_followers(random.choice(user_ids))
                db.get_following(random.choice(user_ids))
        
        total_time = metrics.get_total_time()
        peak_memory = metrics.get_peak_memory()
        
        print(f"\n[Results: {total_time:.2f}ms, {peak_memory:.1f}MB]")
        
        # Handle both NodeMode enum and preset strings
        node_mode_name = db.node_mode if isinstance(db.node_mode, str) else db.node_mode.name
        
        return {
            'database': db.name,
            'node_mode': node_mode_name,
            'edge_mode': db.edge_mode.name if db.edge_mode else 'None',
            'total_entities': self.total_entities,
            'scale': f'{self.scale_factor}x',
            'total_time_ms': total_time,
            'peak_memory_mb': peak_memory,
            'metrics': metrics.get_metrics(),
            'stats': db.get_stats()
        }
    
    def run_all(self):
        """Run benchmarks on all databases"""
        print(f"\n{'='*80}")
        print(f"CLASSIC DATABASE BENCHMARK - {self.total_entities:,} ENTITIES")
        print(f"{'='*80}")
        print(f"\nConfiguration:")
        print(f"  Total Entities: {self.total_entities:,}")
        print(f"  Distribution: {self.num_users:,} users, {self.num_posts:,} posts, {self.num_comments:,} comments")
        print(f"  Relationships: {self.num_relationships:,}")
        print(f"  Models to test: {len(self.databases)}")
        print(f"\nModels:")
        for i, db in enumerate(self.databases, 1):
            edge_name = db.edge_mode.name if db.edge_mode else 'None'
            graph_status = 'ON' if db.graph_optimization != GraphOptimization.OFF else 'OFF'
            node_mode_name = db.node_mode if isinstance(db.node_mode, str) else db.node_mode.name
            print(f"  {i}. {db.name}: {node_mode_name} + {edge_name} (Graph: {graph_status})")
        
        for db in self.databases:
            try:
                result = self.run_benchmark(db)
                self.results[db.name] = result
            except Exception as e:
                print(f"\n[ERROR] {db.name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Results are stored in self.results for later combination
        # Individual scale results saved by run_all_tests()
    
    def generate_report(self):
        """Generate markdown report"""
        output_dir = Path(__file__).parent
        md_file = output_dir / "RESULTS.md"
        
        # Combine all scale results if multiple exist
        all_results = {}
        for scale in [1, 10]:
            json_file = output_dir / f"results_{scale}x.json"
            if json_file.exists():
                with open(json_file, encoding='utf-8') as f:
                    all_results[f'{scale}x'] = json.load(f)
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Classic Database Benchmark Results\n\n")
            f.write("## Overview\n\n")
            f.write("Benchmarking 6 predefined database configurations:\n")
            f.write("- Read-Optimized: HASH_MAP + None\n")
            f.write("- Write-Optimized: LSM_TREE + DYNAMIC_ADJ_LIST\n")
            f.write("- Memory-Efficient: B_TREE + CSR\n")
            f.write("- Query-Optimized: TREE_GRAPH_HYBRID + WEIGHTED_GRAPH\n")
            f.write("- Persistence-Optimized: B_PLUS_TREE + EDGE_PROPERTY_STORE\n")
            f.write("- XWData-Optimized: HASH_MAP + None (DATA_INTERCHANGE)\n\n")
            
            for scale_name, results in all_results.items():
                f.write(f"## Results - {scale_name} Scale\n\n")
                f.write("| Rank | Database | Node Mode | Edge Mode | Time | Memory | Ops/sec |\n")
                f.write("|------|----------|-----------|-----------|------|--------|----------|\n")
                
                sorted_results = sorted(results.items(), key=lambda x: x[1].get('total_time_ms', float('inf')))
                
                for i, (name, data) in enumerate(sorted_results, 1):
                    node = data.get('node_mode', 'N/A')
                    edge = data.get('edge_mode', 'None')
                    time_ms = data.get('total_time_ms', 0)
                    memory = data.get('peak_memory_mb', 0)
                    ops_sec = (50000 / (time_ms / 1000)) if time_ms > 0 else 0
                    
                    medal = "*" if i == 1 else "" if i == 2 else "" if i == 3 else ""
                    f.write(f"| {i} {medal} | {name} | {node} | {edge} | {time_ms:.2f}ms | {memory:.1f}MB | {ops_sec:.0f} |\n")
                
                f.write("\n")
            
            f.write("## Key Findings\n\n")
            f.write("- **Fastest Overall**: Check rankings above\n")
            f.write("- **Most Memory Efficient**: Check memory column\n")
            f.write("- **Best for Production**: Query-Optimized or Write-Optimized\n")
            f.write("- **Best for xData**: XWData-Optimized\n\n")
            f.write("---\n\n")
            f.write("*Generated by Classic Database Benchmark*\n")
        
        print(f"Report generated: RESULTS.md")
    
    def generate_csv(self):
        """Generate combined CSV report with detailed metrics and summary for all scales"""
        output_dir = Path(__file__).parent
        
        # Combine all scale results if multiple exist
        all_results = {}
        for entities in [1000, 10000, 100000]:
            json_file = output_dir / f"results_{entities}.json"
            if json_file.exists():
                with open(json_file, encoding='utf-8') as f:
                    all_results[f'{entities}'] = json.load(f)
        
        # Always write to combined results.csv file
        csv_file = output_dir / "results.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['# Classic Database Benchmark Results - Combined'])
            writer.writerow([f'# All Available Scales: {", ".join([f"{k} entities" for k in all_results.keys()])}'])
            writer.writerow([])
            writer.writerow(['# Configuration per scale:'])
            for entities in [1000, 10000, 100000]:
                if str(entities) in all_results:
                    users = int(entities * 0.5)
                    posts = int(entities * 0.3)
                    comments = int(entities * 0.2)
                    relationships = users * 2
                    writer.writerow([f'#   {entities:,}: {users:,} users, {posts:,} posts, {comments:,} comments, {relationships:,} relationships'])
            writer.writerow([])
            
            for entities_str, results in all_results.items():
                writer.writerow([f'=== DETAILED RESULTS - {entities_str} Entities ==='])
                writer.writerow([])
                
                # Detailed results header
                writer.writerow([
                    'Rank', 'Database', 'Node Mode', 'Edge Mode', 
                    'Total Time (ms)', 'Peak Memory (MB)', 'Operations/sec',
                    'Insert Time (ms)', 'Insert Memory (MB)',
                    'Read Time (ms)', 'Read Memory (MB)',
                    'Update Time (ms)', 'Update Memory (MB)',
                    'Relationships Time (ms)', 'Relationships Memory (MB)'
                ])
                
                # Sort results by total time
                sorted_results = sorted(results.items(), key=lambda x: x[1].get('total_time_ms', float('inf')))
                
                for rank, (name, data) in enumerate(sorted_results, 1):
                    node = data.get('node_mode', 'N/A')
                    edge = data.get('edge_mode', 'None')
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
                        rank, name, node, edge,
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
                times = [r.get('total_time_ms', 0) for r in results.values()]
                memories = [r.get('peak_memory_mb', 0) for r in results.values()]
                
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Databases Tested', len(results)])
                writer.writerow(['Fastest Time (ms)', f'{min(times):.2f}'])
                writer.writerow(['Slowest Time (ms)', f'{max(times):.2f}'])
                writer.writerow(['Average Time (ms)', f'{sum(times)/len(times):.2f}'])
                writer.writerow(['Lowest Memory (MB)', f'{min(memories):.1f}'])
                writer.writerow(['Highest Memory (MB)', f'{max(memories):.1f}'])
                writer.writerow(['Average Memory (MB)', f'{sum(memories)/len(memories):.1f}'])
                writer.writerow(['Winner (Fastest)', sorted_results[0][0]])
                writer.writerow(['Memory Champion (Lowest)', min(results.items(), key=lambda x: x[1].get('peak_memory_mb', float('inf')))[0]])
                writer.writerow([])
        
        print(f"CSV report generated: results.csv (contains {len(all_results)} scale(s))")


def run_all_tests():
    """Run all tests defined in TESTS array and generate combined output files"""
    print(f"\n{'='*80}")
    print(f"CLASSIC DATABASE BENCHMARK - AUTO RUN")
    print(f"{'='*80}")
    print(f"\nTests to run: {', '.join([f'{t:,}' for t in TESTS])} entities")
    print(f"Total test runs: {len(TESTS)}")
    print(f"{'='*80}\n")
    
    # Store all results
    all_results = {}
    output_dir = Path(__file__).resolve().parent
    
    # Run each test
    for i, entities in enumerate(TESTS, 1):
        print(f"\n{'*'*80}")
        print(f"TEST {i}/{len(TESTS)}: {entities:,} entities")
        print(f"{'*'*80}")
        
        benchmark = ClassicBenchmark(total_entities=entities)
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
        print(f"   Please close the file and run again")
    
    # Generate combined CSV file
    csv_file = output_dir / f"results{timestamp}.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['# Classic Database Benchmark Results - Combined'])
            writer.writerow([f'# All Tests: {", ".join([f"{k} entities" for k in all_results.keys()])}'])
            writer.writerow([])
            writer.writerow(['# Configuration per test:'])
            for entities_str in all_results.keys():
                entities = int(entities_str)
                users = int(entities * 0.5)
                posts = int(entities * 0.3)
                comments = int(entities * 0.2)
                relationships = users * 2
                writer.writerow([f'#   {entities:,}: {users:,} users, {posts:,} posts, {comments:,} comments, {relationships:,} relationships'])
            writer.writerow([])
            
            # Write results for each test
            for entities_str, results in all_results.items():
                writer.writerow([f'=== DETAILED RESULTS - {entities_str} Entities ==='])
                writer.writerow([])
                
                # Detailed results header
                writer.writerow([
                    'Rank', 'Database', 'Node Mode', 'Edge Mode', 
                    'Total Time (ms)', 'Peak Memory (MB)', 'Operations/sec',
                    'Insert Time (ms)', 'Insert Memory (MB)',
                    'Read Time (ms)', 'Read Memory (MB)',
                    'Update Time (ms)', 'Update Memory (MB)',
                    'Relationships Time (ms)', 'Relationships Memory (MB)'
                ])
                
                # Sort results by total time
                sorted_results = sorted(results.items(), key=lambda x: x[1].get('total_time_ms', float('inf')))
                
                for rank, (name, data) in enumerate(sorted_results, 1):
                    node = data.get('node_mode', 'N/A')
                    edge = data.get('edge_mode', 'None')
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
                        rank, name, node, edge,
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
                times = [r.get('total_time_ms', 0) for r in results.values()]
                memories = [r.get('peak_memory_mb', 0) for r in results.values()]
                
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Databases Tested', len(results)])
                writer.writerow(['Fastest Time (ms)', f'{min(times):.2f}'])
                writer.writerow(['Slowest Time (ms)', f'{max(times):.2f}'])
                writer.writerow(['Average Time (ms)', f'{sum(times)/len(times):.2f}'])
                writer.writerow(['Lowest Memory (MB)', f'{min(memories):.1f}'])
                writer.writerow(['Highest Memory (MB)', f'{max(memories):.1f}'])
                writer.writerow(['Average Memory (MB)', f'{sum(memories)/len(memories):.1f}'])
                writer.writerow(['Winner (Fastest)', sorted_results[0][0]])
                writer.writerow(['Memory Champion (Lowest)', min(results.items(), key=lambda x: x[1].get('peak_memory_mb', float('inf')))[0]])
                writer.writerow([])
        
        print(f"✓ Combined CSV: {csv_file.name}")
    
    except PermissionError:
        print(f"⚠️  WARNING: Could not write {csv_file.name} - file is open in another program")
        print(f"   Please close the file in Excel/IDE and run again")
    
    print(f"\n{'='*80}")
    print(f"ALL BENCHMARKS COMPLETE")
    print(f"{'='*80}")
    print(f"\nFiles generated:")
    print(f"  ✓ results.json (combined JSON with all {len(TESTS)} tests)")
    print(f"  ✓ results.csv (combined CSV with all {len(TESTS)} tests)")
    print(f"\nTests completed: {', '.join([f'{t:,}' for t in TESTS])} entities")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Classic Database Benchmark')
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
        
        benchmark = ClassicBenchmark(total_entities=args.entities)
        benchmark.run_all()
        
        # Save individual results
        output_dir = Path(__file__).parent
        timestamp = datetime.now().strftime("_%y%m%d%H%M%S")
        json_file = output_dir / f"results_{args.entities}{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(benchmark.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK COMPLETE - {args.entities:,} ENTITIES")
        print(f"{'='*80}")
        print(f"\nFiles generated:")
        print(f"  - results_{args.entities}.json")


if __name__ == "__main__":
    main()

