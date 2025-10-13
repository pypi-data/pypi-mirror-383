#!/usr/bin/env python3
"""
10x Complexity Benchmark Runner

Runs benchmarks with 10x the scale:
- 5000 Users (vs 500)
- 3000 Posts (vs 300)  
- 2000 Comments (vs 200)
- 10000 Relationships (vs 1000)

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


# 10x SCALE CONFIGURATION
NUM_USERS = 5000
NUM_POSTS = 3000
NUM_COMMENTS = 2000
NUM_RELATIONSHIPS = 10000

# Operations scale
NUM_READ_OPS = 1000  # 10x
NUM_UPDATE_USERS = 2500  # 10x (50% of users)
NUM_UPDATE_POSTS = 1500  # 10x (50% of posts)
NUM_UPDATE_COMMENTS = 1000  # 10x (50% of comments)
NUM_SOFT_DELETE = 500  # 10x
NUM_SEARCHES = 100  # 10x
NUM_LIST_BY_USER = 500  # 10x
NUM_LIST_BY_POST = 500  # 10x
NUM_QUERY_FOLLOWERS = 500  # 10x
NUM_QUERY_FOLLOWING = 500  # 10x
NUM_HARD_DELETE_COMMENT = 100  # 10x
NUM_HARD_DELETE_POST = 100  # 10x
NUM_HARD_DELETE_USER = 100  # 10x


class Benchmark10xRunner:
    """Runs 10x complexity benchmarks"""
    
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
        """Run complete 10x benchmark on a single database"""
        print(f"\n{'='*80}")
        print(f"Benchmarking (10x): {db.name}")
        print(f"{'='*80}")
        print(db.get_description())
        print()
        
        metrics = BenchmarkMetrics()
        
        # Track entity IDs for later operations
        user_ids = []
        post_ids = []
        comment_ids = []
        
        # ========================================================================
        # PHASE 1: INSERT OPERATIONS (10x)
        # ========================================================================
        print("[Phase 1: Insert Operations - 10x Scale]")
        
        print(f"   Inserting {NUM_USERS} users...")
        with metrics.measure("insert_user"):
            for i in range(NUM_USERS):
                user = generate_user(i)
                user_id = db.insert_user(user)
                user_ids.append(user_id)
        
        print(f"   Inserting {NUM_POSTS} posts...")
        with metrics.measure("insert_post"):
            for i in range(NUM_POSTS):
                user_id = random.choice(user_ids)
                post = generate_post(i, user_id)
                post_id = db.insert_post(post)
                post_ids.append(post_id)
        
        print(f"   Inserting {NUM_COMMENTS} comments...")
        with metrics.measure("insert_comment"):
            for i in range(NUM_COMMENTS):
                post_id = random.choice(post_ids)
                user_id = random.choice(user_ids)
                comment = generate_comment(i, post_id, user_id)
                comment_id = db.insert_comment(comment)
                comment_ids.append(comment_id)
        
        print(f"   Inserting {NUM_RELATIONSHIPS} relationships...")
        with metrics.measure("insert_relationship"):
            for i in range(NUM_RELATIONSHIPS):
                source_id = random.choice(user_ids)
                target_id = random.choice(user_ids)
                if source_id != target_id:
                    rel = generate_relationship(source_id, target_id, "follows")
                    db.add_relationship(rel)
        
        # ========================================================================
        # PHASE 2: READ OPERATIONS (10x)
        # ========================================================================
        print(f"\n[Phase 2: Read Operations - {NUM_READ_OPS} operations]")
        
        print(f"   Reading {NUM_READ_OPS} random users...")
        with metrics.measure("read_user"):
            for _ in range(NUM_READ_OPS):
                user_id = random.choice(user_ids)
                db.get_user(user_id)
        
        print(f"   Reading {NUM_READ_OPS} random posts...")
        with metrics.measure("read_post"):
            for _ in range(NUM_READ_OPS):
                post_id = random.choice(post_ids)
                db.get_post(post_id)
        
        print(f"   Reading {NUM_READ_OPS} random comments...")
        with metrics.measure("read_comment"):
            for _ in range(NUM_READ_OPS):
                comment_id = random.choice(comment_ids)
                db.get_comment(comment_id)
        
        # ========================================================================
        # PHASE 3: UPDATE OPERATIONS (10x)
        # ========================================================================
        print(f"\n[Phase 3: Update Operations - 50% of entities]")
        
        print(f"   Updating {NUM_UPDATE_USERS} users...")
        with metrics.measure("update_user"):
            for i in range(NUM_UPDATE_USERS):
                user_id = user_ids[i]
                db.update_user(user_id, {'bio': f'Updated bio {i}'})
        
        print(f"   Updating {NUM_UPDATE_POSTS} posts...")
        with metrics.measure("update_post"):
            for i in range(NUM_UPDATE_POSTS):
                post_id = post_ids[i]
                db.update_post(post_id, {'likes_count': i * 10})
        
        print(f"   Updating {NUM_UPDATE_COMMENTS} comments...")
        with metrics.measure("update_comment"):
            for i in range(NUM_UPDATE_COMMENTS):
                comment_id = comment_ids[i]
                db.update_comment(comment_id, {'content': f'Updated comment {i}'})
        
        # ========================================================================
        # PHASE 4: SOFT DELETE OPERATIONS (10x)
        # ========================================================================
        print(f"\n[Phase 4: Soft Delete Operations]")
        
        print(f"   Soft deleting {NUM_SOFT_DELETE} comments...")
        with metrics.measure("soft_delete_comment"):
            for i in range(NUM_SOFT_DELETE):
                comment_id = comment_ids[i]
                db.soft_delete_comment(comment_id)
        
        # ========================================================================
        # PHASE 5: SEARCH OPERATIONS (10x)
        # ========================================================================
        print(f"\n[Phase 5: Search Operations]")
        
        print(f"   Searching users {NUM_SEARCHES} times...")
        with metrics.measure("search_users"):
            for i in range(NUM_SEARCHES):
                db.search_users(f"user_{i}")
        
        # ========================================================================
        # PHASE 6: LIST OPERATIONS (10x)
        # ========================================================================
        print(f"\n[Phase 6: List Operations]")
        
        print(f"   Listing posts by user {NUM_LIST_BY_USER} times...")
        with metrics.measure("list_posts_by_user"):
            for i in range(NUM_LIST_BY_USER):
                user_id = random.choice(user_ids)
                db.list_posts_by_user(user_id)
        
        print(f"   Listing comments by post {NUM_LIST_BY_POST} times...")
        with metrics.measure("list_comments_by_post"):
            for i in range(NUM_LIST_BY_POST):
                post_id = random.choice(post_ids)
                db.list_comments_by_post(post_id)
        
        print(f"   Listing all users...")
        with metrics.measure("list_all_users"):
            db.list_all_users()
        
        # ========================================================================
        # PHASE 7: RELATIONSHIP OPERATIONS (10x)
        # ========================================================================
        print(f"\n[Phase 7: Relationship Operations]")
        
        print(f"   Querying followers {NUM_QUERY_FOLLOWERS} times...")
        with metrics.measure("query_followers"):
            for i in range(NUM_QUERY_FOLLOWERS):
                user_id = random.choice(user_ids)
                db.get_followers(user_id)
        
        print(f"   Querying following {NUM_QUERY_FOLLOWING} times...")
        with metrics.measure("query_following"):
            for i in range(NUM_QUERY_FOLLOWING):
                user_id = random.choice(user_ids)
                db.get_following(user_id)
        
        # ========================================================================
        # PHASE 8: HARD DELETE OPERATIONS (10x)
        # ========================================================================
        print(f"\n[Phase 8: Hard Delete Operations]")
        
        print(f"   Hard deleting {NUM_HARD_DELETE_COMMENT} comments...")
        with metrics.measure("hard_delete_comment"):
            for i in range(NUM_HARD_DELETE_COMMENT):
                comment_id = comment_ids[NUM_SOFT_DELETE + i]
                db.delete_comment(comment_id)
        
        print(f"   Hard deleting {NUM_HARD_DELETE_POST} posts...")
        with metrics.measure("hard_delete_post"):
            for i in range(NUM_HARD_DELETE_POST):
                post_id = post_ids[i]
                db.delete_post(post_id)
        
        print(f"   Hard deleting {NUM_HARD_DELETE_USER} users...")
        with metrics.measure("hard_delete_user"):
            for i in range(NUM_HARD_DELETE_USER):
                user_id = user_ids[i]
                db.delete_user(user_id)
        
        # ========================================================================
        # RESULTS
        # ========================================================================
        print("\n[Benchmark Complete!]")
        
        metrics.print_summary(f"10x Benchmark Results: {db.name}")
        
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
        """Run 10x benchmarks on all database types"""
        print("\n" + "="*80)
        print("Entity Database Performance Benchmark - 10x COMPLEXITY")
        print("="*80)
        print("\nConfiguration:")
        print(f"  - Total Entities: {NUM_USERS + NUM_POSTS + NUM_COMMENTS}")
        print(f"    - Users: {NUM_USERS}")
        print(f"    - Posts: {NUM_POSTS}")
        print(f"    - Comments: {NUM_COMMENTS}")
        print(f"  - Total Relationships: {NUM_RELATIONSHIPS}")
        print(f"  - Total Operations: ~50,000+")
        print("  - Operations: Insert, Read, Update, Soft Delete, Hard Delete, Search, List")
        print("  - Database Types: 6")
        
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
        
        # Save results
        results_file = Path(__file__).parent / "benchmark_results_10x.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
        
        # Generate comparison report
        self.generate_comparison_report()
    
    def generate_comparison_report(self):
        """Generate comparison report"""
        output_file = Path(__file__).parent / "BENCHMARK_RESULTS_10X.md"
        
        with open(output_file, 'w') as f:
            f.write("# Entity Database Benchmark Results - 10x COMPLEXITY\n\n")
            f.write("## Configuration\n\n")
            f.write(f"- **Total Entities:** {NUM_USERS + NUM_POSTS + NUM_COMMENTS}\n")
            f.write(f"  - Users: {NUM_USERS}\n")
            f.write(f"  - Posts: {NUM_POSTS}\n")
            f.write(f"  - Comments: {NUM_COMMENTS}\n")
            f.write(f"- **Total Relationships:** {NUM_RELATIONSHIPS}\n")
            f.write("- **Total Operations:** ~50,000+\n")
            f.write("- **Scale:** 10x compared to base benchmark\n\n")
            
            f.write("## Results Summary\n\n")
            f.write("| DB Type | Node Mode | Edge Mode | Total Time | Memory | Ops/sec |\n")
            f.write("|---------|-----------|-----------|------------|--------|---------|\n")
            
            sorted_results = sorted(
                [(name, data) for name, data in self.results.items() if 'error' not in data],
                key=lambda x: x[1].get('total_time_ms', float('inf'))
            )
            
            for name, data in sorted_results:
                node_mode = data.get('node_mode', 'N/A')
                edge_mode = data.get('edge_mode', 'None')
                total_time = data.get('total_time_ms', 0)
                memory = data.get('peak_memory_mb', 0)
                ops_per_sec = (50000 / (total_time / 1000)) if total_time > 0 else 0
                f.write(f"| {name} | {node_mode} | {edge_mode} | {total_time:.2f}ms | {memory:.2f}MB | {ops_per_sec:.0f} |\n")
        
        print(f"10x Comparison report generated: {output_file}")


def main():
    """Main entry point"""
    runner = Benchmark10xRunner()
    runner.run_all_benchmarks()
    
    print("\n" + "="*80)
    print("10x BENCHMARK COMPLETE!")
    print("="*80)
    print("\nGenerated Files:")
    print("  - benchmark_results_10x.json")
    print("  - BENCHMARK_RESULTS_10X.md")


if __name__ == "__main__":
    main()

