#!/usr/bin/env python3
"""
Unified Benchmark Runner

Executes all benchmark operations across all 5 database types and generates results.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 11, 2025
"""

import sys
import json
import random
from pathlib import Path
from typing import List, Dict, Any

# Add paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from benchmark_utils import BenchmarkMetrics
from shared_schema import (
    generate_user, generate_post, generate_comment, generate_relationship
)

# Import all database types
from db_type_read_optimized.config import ReadOptimizedDatabase
from db_type_write_optimized.config import WriteOptimizedDatabase
from db_type_memory_efficient.config import MemoryEfficientDatabase
from db_type_query_optimized.config import QueryOptimizedDatabase
from db_type_persistence_optimized.config import PersistenceOptimizedDatabase
from db_type_xwdata_optimized.config import XWDataOptimizedDatabase


class BenchmarkRunner:
    """Runs benchmarks across all database types"""
    
    def __init__(self):
        self.databases = [
            ReadOptimizedDatabase(),
            WriteOptimizedDatabase(),
            MemoryEfficientDatabase(),
            QueryOptimizedDatabase(),
            PersistenceOptimizedDatabase(),
            XWDataOptimizedDatabase()
        ]
        self.results = {}
    
    def run_benchmark(self, db) -> Dict[str, Any]:
        """Run complete benchmark on a single database"""
        print(f"\n{'='*80}")
        print(f"Benchmarking: {db.name}")
        print(f"{'='*80}")
        print(db.get_description())
        print()
        
        metrics = BenchmarkMetrics()
        
        # Track entity IDs for later operations
        user_ids = []
        post_ids = []
        comment_ids = []
        
        # ========================================================================
        # PHASE 1: INSERT OPERATIONS
        # ========================================================================
        print("[Phase 1: Insert Operations]")
        
        # Insert 500 Users
        print("   Inserting 500 users...")
        with metrics.measure("insert_user"):
            for i in range(500):
                user = generate_user(i)
                user_id = db.insert_user(user)
                user_ids.append(user_id)
        
        # Insert 300 Posts (distributed across users)
        print("   Inserting 300 posts...")
        with metrics.measure("insert_post"):
            for i in range(300):
                user_id = random.choice(user_ids)
                post = generate_post(i, user_id)
                post_id = db.insert_post(post)
                post_ids.append(post_id)
        
        # Insert 200 Comments (distributed across posts)
        print("   Inserting 200 comments...")
        with metrics.measure("insert_comment"):
            for i in range(200):
                post_id = random.choice(post_ids)
                user_id = random.choice(user_ids)
                comment = generate_comment(i, post_id, user_id)
                comment_id = db.insert_comment(comment)
                comment_ids.append(comment_id)
        
        # Insert 1000 Relationships (user follows)
        print("   Inserting 1000 relationships...")
        with metrics.measure("insert_relationship"):
            for i in range(1000):
                source_id = random.choice(user_ids)
                target_id = random.choice(user_ids)
                if source_id != target_id:
                    rel = generate_relationship(source_id, target_id, "follows")
                    db.add_relationship(rel)
        
        # ========================================================================
        # PHASE 2: READ OPERATIONS
        # ========================================================================
        print("\n[Phase 2: Read Operations]")
        
        # Read 100 random users
        print("   Reading 100 random users...")
        with metrics.measure("read_user"):
            for _ in range(100):
                user_id = random.choice(user_ids)
                db.get_user(user_id)
        
        # Read 100 random posts
        print("   Reading 100 random posts...")
        with metrics.measure("read_post"):
            for _ in range(100):
                post_id = random.choice(post_ids)
                db.get_post(post_id)
        
        # Read 100 random comments
        print("   Reading 100 random comments...")
        with metrics.measure("read_comment"):
            for _ in range(100):
                comment_id = random.choice(comment_ids)
                db.get_comment(comment_id)
        
        # ========================================================================
        # PHASE 3: UPDATE OPERATIONS
        # ========================================================================
        print("\n[Phase 3: Update Operations (50% of entities)]")
        
        # Update 250 users
        print("   Updating 250 users...")
        with metrics.measure("update_user"):
            for i in range(250):
                user_id = user_ids[i]
                db.update_user(user_id, {'bio': f'Updated bio {i}'})
        
        # Update 150 posts
        print("   Updating 150 posts...")
        with metrics.measure("update_post"):
            for i in range(150):
                post_id = post_ids[i]
                db.update_post(post_id, {'likes_count': i * 10})
        
        # Update 100 comments
        print("   Updating 100 comments...")
        with metrics.measure("update_comment"):
            for i in range(100):
                comment_id = comment_ids[i]
                db.update_comment(comment_id, {'content': f'Updated comment {i}'})
        
        # ========================================================================
        # PHASE 4: SOFT DELETE OPERATIONS
        # ========================================================================
        print("\n[Phase 4: Soft Delete Operations]")
        
        # Soft delete 50 comments
        print("   Soft deleting 50 comments...")
        with metrics.measure("soft_delete_comment"):
            for i in range(50):
                comment_id = comment_ids[i]
                db.soft_delete_comment(comment_id)
        
        # ========================================================================
        # PHASE 5: SEARCH OPERATIONS
        # ========================================================================
        print("\n[Phase 5: Search Operations]")
        
        # Search users by username
        print("   Searching users...")
        with metrics.measure("search_users"):
            for i in range(10):
                db.search_users(f"user_{i}")
        
        # ========================================================================
        # PHASE 6: LIST OPERATIONS
        # ========================================================================
        print("\n[Phase 6: List Operations]")
        
        # List posts by user
        print("   Listing posts by user...")
        with metrics.measure("list_posts_by_user"):
            for i in range(50):
                user_id = random.choice(user_ids)
                db.list_posts_by_user(user_id)
        
        # List comments by post
        print("   Listing comments by post...")
        with metrics.measure("list_comments_by_post"):
            for i in range(50):
                post_id = random.choice(post_ids)
                db.list_comments_by_post(post_id)
        
        # List all users
        print("   Listing all users...")
        with metrics.measure("list_all_users"):
            db.list_all_users()
        
        # ========================================================================
        # PHASE 7: RELATIONSHIP OPERATIONS
        # ========================================================================
        print("\n[Phase 7: Relationship Operations]")
        
        # Query followers
        print("   Querying followers...")
        with metrics.measure("query_followers"):
            for i in range(50):
                user_id = random.choice(user_ids)
                db.get_followers(user_id)
        
        # Query following
        print("   Querying following...")
        with metrics.measure("query_following"):
            for i in range(50):
                user_id = random.choice(user_ids)
                db.get_following(user_id)
        
        # ========================================================================
        # PHASE 8: HARD DELETE OPERATIONS
        # ========================================================================
        print("\n[Phase 8: Hard Delete Operations]")
        
        # Hard delete 10 comments
        print("   Hard deleting 10 comments...")
        with metrics.measure("hard_delete_comment"):
            for i in range(10):
                comment_id = comment_ids[50 + i]  # Delete different ones
                db.delete_comment(comment_id)
        
        # Hard delete 10 posts
        print("   Hard deleting 10 posts...")
        with metrics.measure("hard_delete_post"):
            for i in range(10):
                post_id = post_ids[i]
                db.delete_post(post_id)
        
        # Hard delete 10 users
        print("   Hard deleting 10 users...")
        with metrics.measure("hard_delete_user"):
            for i in range(10):
                user_id = user_ids[i]
                db.delete_user(user_id)
        
        # ========================================================================
        # RESULTS
        # ========================================================================
        print("\n[Benchmark Complete!]")
        
        metrics.print_summary(f"Benchmark Results: {db.name}")
        
        # Get database stats
        stats = db.get_stats()
        print(f"\n[Final Database Statistics:]")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        return {
            'database': db.name,
            'node_mode': stats['node_mode'],
            'edge_mode': stats['edge_mode'],
            'total_time_ms': metrics.get_total_time(),
            'peak_memory_mb': metrics.get_peak_memory(),
            'metrics': metrics.get_metrics(),
            'stats': stats
        }
    
    def run_all_benchmarks(self):
        """Run benchmarks on all database types"""
        print("\n" + "="*80)
        print("Entity Database Performance Benchmark")
        print("="*80)
        print("\nConfiguration:")
        print("  - Total Entities: 1000 (500 users, 300 posts, 200 comments)")
        print("  - Total Relationships: 1000 (user follows)")
        print("  - Operations: Insert, Read, Update, Soft Delete, Hard Delete, Search, List")
        print("  - Database Types: 6 (Read, Write, Memory, Query, Persistence, XWData)")
        
        for db in self.databases:
            try:
                result = self.run_benchmark(db)
                self.results[db.name] = result
            except Exception as e:
                print(f"\n[ERROR] Error benchmarking {db.name}: {e}")
                import traceback
                traceback.print_exc()
                self.results[db.name] = {
                    'error': str(e),
                    'database': db.name
                }
        
        # Save results to JSON
        results_file = Path(__file__).parent / "benchmark_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
        
        # Generate markdown report
        self.generate_markdown_report()
    
    def generate_markdown_report(self):
        """Generate BENCHMARK_RESULTS.md"""
        output_file = Path(__file__).parent / "BENCHMARK_RESULTS.md"
        
        with open(output_file, 'w') as f:
            f.write("# Entity Database Benchmark Results\n\n")
            f.write("## Configuration\n\n")
            f.write("- **Total Entities:** 1000 (500 users, 300 posts, 200 comments)\n")
            f.write("- **Total Relationships:** 1000 (user follows)\n")
            f.write("- **Operations:** Insert, View, Update (50%), Soft Delete, Hard Delete, Search, List\n")
            f.write("- **Database Types:** 6 (Read-Optimized, Write-Optimized, Memory-Efficient, Query-Optimized, Persistence-Optimized, XWData-Optimized)\n\n")
            
            f.write("## Results Summary\n\n")
            f.write("| DB Type | Node Mode | Edge Mode | Total Time | Memory | Best For |\n")
            f.write("|---------|-----------|-----------|------------|--------|----------|\n")
            
            # Sort by total time
            sorted_results = sorted(
                [(name, data) for name, data in self.results.items() if 'error' not in data],
                key=lambda x: x[1].get('total_time_ms', float('inf'))
            )
            
            best_for = {
                'Read-Optimized': 'Fast lookups',
                'Write-Optimized': 'High throughput',
                'Memory-Efficient': 'Large datasets',
                'Query-Optimized': 'Graph traversal',
                'Persistence-Optimized': 'Durability',
                'XWData-Optimized': 'Data interchange'
            }
            
            for name, data in sorted_results:
                node_mode = data.get('node_mode', 'N/A')
                edge_mode = data.get('edge_mode', 'None')
                total_time = data.get('total_time_ms', 0)
                memory = data.get('peak_memory_mb', 0)
                f.write(f"| {name} | {node_mode} | {edge_mode} | {total_time:.2f}ms | {memory:.2f}MB | {best_for.get(name, 'General')} |\n")
            
            # Detailed breakdown for each database
            f.write("\n## Detailed Performance Breakdown\n\n")
            
            for name, data in sorted_results:
                f.write(f"### {name} Database\n\n")
                f.write(f"**Configuration:**\n")
                f.write(f"- Node Strategy: `{data.get('node_mode', 'N/A')}`\n")
                f.write(f"- Edge Strategy: `{data.get('edge_mode', 'None')}`\n")
                f.write(f"- Total Time: {data.get('total_time_ms', 0):.2f} ms\n")
                f.write(f"- Peak Memory: {data.get('peak_memory_mb', 0):.2f} MB\n\n")
                
                f.write("**Operation Performance:**\n\n")
                f.write("| Operation | Count | Total Time | Avg Time | Min Time | Max Time |\n")
                f.write("|-----------|-------|------------|----------|----------|----------|\n")
                
                metrics = data.get('metrics', {})
                for op_name, op_data in metrics.items():
                    count = op_data.get('count', 0)
                    total = op_data.get('total_time_ms', 0)
                    avg = op_data.get('avg_time_ms', 0)
                    min_time = op_data.get('min_time_ms', 0)
                    max_time = op_data.get('max_time_ms', 0)
                    f.write(f"| {op_name} | {count} | {total:.2f}ms | {avg:.4f}ms | {min_time:.4f}ms | {max_time:.4f}ms |\n")
                
                f.write("\n")
            
            f.write("## Recommendations\n\n")
            f.write("Based on the benchmark results:\n\n")
            
            if sorted_results:
                fastest = sorted_results[0][0]
                f.write(f"- **Fastest Overall:** {fastest} - Best for latency-sensitive applications\n")
            
            # Find memory efficient
            memory_sorted = sorted(sorted_results, key=lambda x: x[1].get('peak_memory_mb', float('inf')))
            if memory_sorted:
                most_efficient = memory_sorted[0][0]
                f.write(f"- **Most Memory Efficient:** {most_efficient} - Best for large-scale deployments\n")
            
            f.write("\n")
            f.write("## Notes\n\n")
            f.write("- All benchmarks run on the same hardware and software environment\n")
            f.write("- Times are measured in milliseconds (ms)\n")
            f.write("- Memory is measured in megabytes (MB)\n")
            f.write("- Operations include all CRUD operations plus search and relationship queries\n")
        
        print(f"Markdown report generated: {output_file}")


def main():
    """Main entry point"""
    runner = BenchmarkRunner()
    runner.run_all_benchmarks()
    
    print("\n" + "="*80)
    print("ALL BENCHMARKS COMPLETE!")
    print("="*80)
    print("\nGenerated Files:")
    print("  - benchmark_results.json")
    print("  - BENCHMARK_RESULTS.md")
    print("\nCheck these files for detailed performance analysis.")


if __name__ == "__main__":
    main()

