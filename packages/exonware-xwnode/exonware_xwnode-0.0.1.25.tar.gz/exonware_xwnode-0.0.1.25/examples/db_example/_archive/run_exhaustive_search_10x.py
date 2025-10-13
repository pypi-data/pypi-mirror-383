#!/usr/bin/env python3
"""
Exhaustive Strategy Search Benchmark - 10x COMPLEXITY

Dynamically tests ALL 760 combinations at 10x scale to find the TRUE champion at production scale!

This will test:
- Every NodeMode (40 strategies)
- Every EdgeMode (18 strategies) + None
- Total combinations: 760 configurations
- At 10x complexity: 5000 users, 3000 posts, 2000 comments, 10000 relationships

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
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from exonware.xwnode.defs import NodeMode, EdgeMode
from benchmark_utils import BenchmarkMetrics
from shared_schema import (
    generate_user, generate_post, generate_comment, generate_relationship
)
from base_database import BaseDatabase


# ============================================================================
# 10x SCALE CONFIGURATION
# ============================================================================

NUM_USERS = 5000
NUM_POSTS = 3000
NUM_COMMENTS = 2000
NUM_RELATIONSHIPS = 10000
NUM_READ_OPS = 1000
NUM_UPDATE_USERS = 2500
NUM_UPDATE_POSTS = 1500
NUM_UPDATE_COMMENTS = 1000


# ============================================================================
# PREDICTION BEFORE RUNNING (10x Scale)
# ============================================================================

PREDICTIONS_10X = {
    "10x_scale": {
        "winner": "B_TREE + ADJ_LIST",
        "reason": "B_TREE cache hits dominate at scale, ADJ_LIST is sparse-efficient",
        "estimated_time_ms": 350.0,
        "estimated_memory_mb": 230.0
    },
    "dark_horse": {
        "winner": "CUCKOO_HASH + CSR",
        "reason": "1x champion might scale well, CSR compression helps",
        "estimated_time_ms": 340.0
    },
    "wildcard": {
        "winner": "LSM_TREE + DYNAMIC_ADJ_LIST",
        "reason": "Write-optimized should dominate with 20K inserts",
        "estimated_time_ms": 330.0
    }
}


# ============================================================================
# DYNAMIC DATABASE GENERATOR
# ============================================================================

@dataclass
class StrategyCombo:
    """Represents a node+edge strategy combination"""
    node_mode: NodeMode
    edge_mode: Optional[EdgeMode]
    name: str
    
    def __str__(self):
        edge_str = self.edge_mode.name if self.edge_mode else "None"
        return f"{self.node_mode.name}+{edge_str}"


class DynamicDatabase(BaseDatabase):
    """Dynamically configured database for testing any strategy combination"""
    
    def __init__(self, combo: StrategyCombo):
        super().__init__(
            name=str(combo),
            node_mode=combo.node_mode,
            edge_mode=combo.edge_mode
        )
        self.combo = combo
    
    def get_description(self) -> str:
        return f"10x Dynamic: {self.combo.node_mode.name} + {self.combo.edge_mode.name if self.combo.edge_mode else 'None'}"


# ============================================================================
# EXHAUSTIVE SEARCH RUNNER - 10x SCALE
# ============================================================================

class ExhaustiveSearch10xRunner:
    """Tests all possible node+edge combinations at 10x scale"""
    
    def __init__(self):
        self.results = {}
        self.combinations = self._generate_combinations()
        
        print("\n" + "="*80)
        print("EXHAUSTIVE STRATEGY SEARCH - 10x COMPLEXITY FULL SWEEP")
        print("="*80)
        print(f"\nTotal Combinations to Test: {len(self.combinations)}")
        print(f"Scale: 10x (5000 users, 3000 posts, 2000 comments, 10000 relationships)")
        print(f"\nThis will test EVERY possible combination at PRODUCTION SCALE:")
        print(f"  - All {len([m for m in NodeMode if m != NodeMode.AUTO])} Node Strategies")
        print(f"  - All {len([m for m in EdgeMode if m != EdgeMode.AUTO])} Edge Strategies + None")
        print(f"  - Total: {len(self.combinations)} unique configurations")
        print(f"\nEstimated time: 2-4 HOURS for complete sweep")
        print(f"Philosophy: LET THE DATA SPEAK AT SCALE!")
        
        # Print predictions
        print("\n" + "="*80)
        print("PREDICTIONS (10x Scale):")
        print("="*80)
        for key, pred in PREDICTIONS_10X.items():
            print(f"\n{key.replace('_', ' ').title()}:")
            print(f"  Winner: {pred['winner']}")
            print(f"  Reason: {pred['reason']}")
            if 'estimated_time_ms' in pred:
                print(f"  Estimated Time: {pred['estimated_time_ms']}ms")
            if 'estimated_memory_mb' in pred:
                print(f"  Estimated Memory: {pred['estimated_memory_mb']}MB")
        print("="*80)
    
    def _generate_combinations(self) -> List[StrategyCombo]:
        """Generate all valid node+edge combinations"""
        combinations = []
        
        # Get ALL node modes (complete sweep)
        node_modes = [mode for mode in NodeMode if mode != NodeMode.AUTO]
        
        # Get ALL edge modes + None (complete sweep)
        edge_modes = [None] + [mode for mode in EdgeMode if mode != EdgeMode.AUTO]
        
        # Generate ALL combinations - TRUST THE DATA AT SCALE!
        for node_mode in node_modes:
            for edge_mode in edge_modes:
                combo = StrategyCombo(
                    node_mode=node_mode,
                    edge_mode=edge_mode,
                    name=f"{node_mode.name}+{edge_mode.name if edge_mode else 'None'}"
                )
                combinations.append(combo)
        
        return combinations
    
    def run_10x_benchmark(self, db: DynamicDatabase) -> Dict[str, Any]:
        """Run 10x scale benchmark on a single configuration"""
        metrics = BenchmarkMetrics()
        
        user_ids = []
        post_ids = []
        comment_ids = []
        
        try:
            # Insert operations - 10x scale
            with metrics.measure("insert"):
                for i in range(NUM_USERS):
                    user_id = db.insert_user(generate_user(i))
                    user_ids.append(user_id)
                
                for i in range(NUM_POSTS):
                    user_id = random.choice(user_ids)
                    post_id = db.insert_post(generate_post(i, user_id))
                    post_ids.append(post_id)
                
                for i in range(NUM_COMMENTS):
                    post_id = random.choice(post_ids)
                    user_id = random.choice(user_ids)
                    comment_id = db.insert_comment(generate_comment(i, post_id, user_id))
                    comment_ids.append(comment_id)
                
                for i in range(NUM_RELATIONSHIPS):
                    source_id = random.choice(user_ids)
                    target_id = random.choice(user_ids)
                    if source_id != target_id:
                        db.add_relationship(generate_relationship(source_id, target_id))
            
            # Read operations - 10x scale
            with metrics.measure("read"):
                for _ in range(NUM_READ_OPS):
                    db.get_user(random.choice(user_ids))
                    db.get_post(random.choice(post_ids))
                    db.get_comment(random.choice(comment_ids))
            
            # Update operations - 10x scale
            with metrics.measure("update"):
                for i in range(NUM_UPDATE_USERS):
                    db.update_user(user_ids[i], {'bio': f'Updated {i}'})
                
                for i in range(NUM_UPDATE_POSTS):
                    db.update_post(post_ids[i], {'likes_count': i})
                
                for i in range(NUM_UPDATE_COMMENTS):
                    db.update_comment(comment_ids[i], {'content': f'Updated {i}'})
            
            # Relationship queries - 10x scale
            with metrics.measure("relationships"):
                for _ in range(500):
                    db.get_followers(random.choice(user_ids))
                    db.get_following(random.choice(user_ids))
            
            total_time = metrics.get_total_time()
            peak_memory = metrics.get_peak_memory()
            
            return {
                'combo': str(db.combo),
                'node_mode': db.combo.node_mode.name,
                'edge_mode': db.combo.edge_mode.name if db.combo.edge_mode else 'None',
                'total_time_ms': total_time,
                'peak_memory_mb': peak_memory,
                'success': True,
                'metrics': metrics.get_metrics()
            }
            
        except Exception as e:
            return {
                'combo': str(db.combo),
                'node_mode': db.combo.node_mode.name,
                'edge_mode': db.combo.edge_mode.name if db.combo.edge_mode else 'None',
                'total_time_ms': float('inf'),
                'peak_memory_mb': float('inf'),
                'success': False,
                'error': str(e)
            }
    
    def run_exhaustive_search(self):
        """Run 10x benchmark on all combinations"""
        print(f"\nStarting 10x EXHAUSTIVE SEARCH across {len(self.combinations)} combinations...")
        print("This will take 2-4 HOURS - go get coffee!")
        print("Progress reports every 25 combinations...\n")
        
        results = []
        successful = 0
        failed = 0
        
        for i, combo in enumerate(self.combinations):
            # Progress indicator (every 25 for detailed tracking)
            if (i + 1) % 25 == 0:
                success_rate = (successful / (i + 1)) * 100
                if results:
                    current_leader = min(results, key=lambda x: x.get('total_time_ms', float('inf')) if x.get('success') else float('inf'))
                    if current_leader.get('success'):
                        print(f"Progress: {i+1}/{len(self.combinations)} ({(i+1)/len(self.combinations)*100:.1f}%) | "
                              f"Success: {success_rate:.1f}% | "
                              f"Leader: {current_leader['combo']} @ {current_leader['total_time_ms']:.0f}ms")
                else:
                    print(f"Progress: {i+1}/{len(self.combinations)} ({(i+1)/len(self.combinations)*100:.1f}%)")
            
            try:
                db = DynamicDatabase(combo)
                result = self.run_10x_benchmark(db)
                results.append(result)
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"  [SKIP] {combo.name}: {e}")
                failed += 1
                results.append({
                    'combo': str(combo),
                    'node_mode': combo.node_mode.name,
                    'edge_mode': combo.edge_mode.name if combo.edge_mode else 'None',
                    'success': False,
                    'error': str(e)
                })
        
        print(f"\n10x SWEEP COMPLETE: {successful} successful, {failed} failed\n")
        
        # Sort by total time (successful only)
        successful_results = [r for r in results if r['success']]
        successful_results.sort(key=lambda x: x['total_time_ms'])
        
        # Save all results
        output_file = Path(__file__).parent / "exhaustive_search_results_10x.json"
        with open(output_file, 'w') as f:
            json.dump({
                'scale': '10x',
                'predictions': PREDICTIONS_10X,
                'total_tested': len(self.combinations),
                'successful': successful,
                'failed': failed,
                'results': successful_results
            }, f, indent=2)
        
        print(f"Results saved to: {output_file}")
        
        # Generate report
        self.generate_report(successful_results)
        
        return successful_results
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """Generate markdown report with 10x winners"""
        output_file = Path(__file__).parent / "EXHAUSTIVE_SEARCH_RESULTS_10X.md"
        
        with open(output_file, 'w') as f:
            f.write("# Exhaustive Strategy Search Results - 10x COMPLEXITY\n\n")
            f.write("## Test Configuration\n\n")
            f.write(f"- **Total Combinations Tested:** {len(results)}\n")
            f.write(f"- **Scale:** 10x complexity\n")
            f.write(f"- **Dataset:** {NUM_USERS} users, {NUM_POSTS} posts, {NUM_COMMENTS} comments, {NUM_RELATIONSHIPS} relationships\n")
            f.write(f"- **Total Entities:** {NUM_USERS + NUM_POSTS + NUM_COMMENTS + NUM_RELATIONSHIPS}\n")
            f.write(f"- **Operations:** Insert, Read ({NUM_READ_OPS}), Update ({NUM_UPDATE_USERS + NUM_UPDATE_POSTS + NUM_UPDATE_COMMENTS}), Relationship queries (1000)\n\n")
            
            f.write("## Predictions (10x Scale)\n\n")
            for key, pred in PREDICTIONS_10X.items():
                f.write(f"### {key.replace('_', ' ').title()}\n")
                f.write(f"- **Predicted Winner:** {pred['winner']}\n")
                f.write(f"- **Reasoning:** {pred['reason']}\n")
                if 'estimated_time_ms' in pred:
                    f.write(f"- **Estimated Time:** {pred['estimated_time_ms']}ms\n")
                f.write("\n")
            
            f.write("## Top 20 Fastest Configurations\n\n")
            f.write("| Rank | Configuration | Node Mode | Edge Mode | Total Time | Memory | Ops/sec |\n")
            f.write("|------|---------------|-----------|-----------|------------|--------|----------|\n")
            
            for i, result in enumerate(results[:20], 1):
                combo = result['combo']
                node = result['node_mode']
                edge = result['edge_mode']
                total = result['total_time_ms']
                memory = result['peak_memory_mb']
                ops_per_sec = (50000 / (total / 1000)) if total > 0 else 0
                
                medal = "[1st]" if i == 1 else "[2nd]" if i == 2 else "[3rd]" if i == 3 else ""
                f.write(f"| {i} {medal} | {combo} | {node} | {edge} | {total:.2f}ms | {memory:.1f}MB | {ops_per_sec:.0f} |\n")
            
            f.write("\n## Top 20 Most Memory Efficient\n\n")
            memory_sorted = sorted(results, key=lambda x: x['peak_memory_mb'])
            f.write("| Rank | Configuration | Node Mode | Edge Mode | Memory | Total Time |\n")
            f.write("|------|---------------|-----------|-----------|--------|------------|\n")
            
            for i, result in enumerate(memory_sorted[:20], 1):
                combo = result['combo']
                node = result['node_mode']
                edge = result['edge_mode']
                memory = result['peak_memory_mb']
                total = result['total_time_ms']
                f.write(f"| {i} | {combo} | {node} | {edge} | {memory:.1f}MB | {total:.2f}ms |\n")
            
            f.write("\n## Prediction Accuracy\n\n")
            
            # Check if predictions match
            winner = results[0]
            predicted = PREDICTIONS_10X['10x_scale']['winner']
            actual_winner = winner['combo']
            
            f.write(f"**Predicted Winner:** {predicted}\n")
            f.write(f"**Actual Winner:** {actual_winner}\n")
            
            if predicted in actual_winner:
                f.write(f"**Prediction Status:** CORRECT!\n\n")
            else:
                f.write(f"**Prediction Status:** INCORRECT\n\n")
                f.write(f"**Why the difference:**\n")
                f.write(f"- Predicted: {PREDICTIONS_10X['10x_scale']['reason']}\n")
                f.write(f"- Actual winner scaled differently than expected\n\n")
            
            f.write("## Strategy Analysis\n\n")
            
            # Group by node mode
            f.write("### Best Edge Mode for Each Node Mode\n\n")
            f.write("| Node Mode | Best Edge Mode | Time | Memory | Ops/sec |\n")
            f.write("|-----------|----------------|------|--------|----------|\n")
            
            node_best = {}
            for result in results:
                node = result['node_mode']
                if node not in node_best or result['total_time_ms'] < node_best[node]['total_time_ms']:
                    node_best[node] = result
            
            for node, result in sorted(node_best.items(), key=lambda x: x[1]['total_time_ms'])[:40]:
                edge = result['edge_mode']
                time = result['total_time_ms']
                memory = result['peak_memory_mb']
                ops_sec = (50000 / (time / 1000)) if time > 0 else 0
                f.write(f"| {node} | {edge} | {time:.2f}ms | {memory:.1f}MB | {ops_sec:.0f} |\n")
            
            f.write("\n## Key Findings\n\n")
            
            # Analyze patterns
            edge_none_results = [r for r in results if r['edge_mode'] == 'None']
            edge_some_results = [r for r in results if r['edge_mode'] != 'None']
            
            if edge_none_results and edge_some_results:
                avg_none = sum(r['total_time_ms'] for r in edge_none_results) / len(edge_none_results)
                avg_some = sum(r['total_time_ms'] for r in edge_some_results) / len(edge_some_results)
                
                f.write(f"1. **Edge Storage Impact at 10x Scale:**\n")
                f.write(f"   - Average time with No Edges: {avg_none:.2f}ms\n")
                f.write(f"   - Average time with Edges: {avg_some:.2f}ms\n")
                f.write(f"   - Overhead: {((avg_some/avg_none - 1) * 100):.1f}%\n\n")
            
            # Top node modes
            node_times = {}
            for result in results:
                node = result['node_mode']
                if node not in node_times:
                    node_times[node] = []
                node_times[node].append(result['total_time_ms'])
            
            node_avgs = {node: sum(times)/len(times) for node, times in node_times.items()}
            top_nodes = sorted(node_avgs.items(), key=lambda x: x[1])[:10]
            
            f.write(f"2. **Top 10 Node Modes at 10x Scale (Average Performance):**\n")
            for i, (node, avg_time) in enumerate(top_nodes, 1):
                count = len(node_times[node])
                ops_sec = (50000 / (avg_time / 1000)) if avg_time > 0 else 0
                f.write(f"   {i}. {node}: {avg_time:.2f}ms average ({ops_sec:.0f} ops/sec, {count} edge combos)\n")
            
            # Top edge modes
            edge_times = {}
            for result in results:
                edge = result['edge_mode']
                if edge not in edge_times:
                    edge_times[edge] = []
                edge_times[edge].append(result['total_time_ms'])
            
            edge_avgs = {edge: sum(times)/len(times) for edge, times in edge_times.items()}
            top_edges = sorted(edge_avgs.items(), key=lambda x: x[1])[:10]
            
            f.write(f"\n3. **Top 10 Edge Modes at 10x Scale (Average Performance):**\n")
            for i, (edge, avg_time) in enumerate(top_edges, 1):
                count = len(edge_times[edge])
                ops_sec = (50000 / (avg_time / 1000)) if avg_time > 0 else 0
                f.write(f"   {i}. {edge}: {avg_time:.2f}ms average ({ops_sec:.0f} ops/sec, {count} node combos)\n")
            
            f.write(f"\n4. **Champion at 10x Scale:** {results[0]['combo']}\n")
            f.write(f"   - Time: {results[0]['total_time_ms']:.2f}ms\n")
            f.write(f"   - Memory: {results[0]['peak_memory_mb']:.1f}MB\n")
            f.write(f"   - Throughput: {(50000 / (results[0]['total_time_ms'] / 1000)):.0f} ops/sec\n\n")
            
            f.write(f"\n## Bottom 20 Slowest Configurations\n\n")
            f.write("| Rank | Configuration | Node Mode | Edge Mode | Total Time | Memory |\n")
            f.write("|------|---------------|-----------|-----------|------------|--------|\n")
            
            for i, result in enumerate(results[-20:], len(results)-19):
                combo = result['combo']
                node = result['node_mode']
                edge = result['edge_mode']
                total = result['total_time_ms']
                memory = result['peak_memory_mb']
                f.write(f"| {i} | {combo} | {node} | {edge} | {total:.2f}ms | {memory:.1f}MB |\n")
            
            f.write(f"\n## Complete Statistics (10x Scale)\n\n")
            f.write(f"- **Total Configurations Tested:** {len(results)}\n")
            f.write(f"- **Fastest:** {results[0]['combo']} at {results[0]['total_time_ms']:.2f}ms\n")
            f.write(f"- **Slowest:** {results[-1]['combo']} at {results[-1]['total_time_ms']:.2f}ms\n")
            f.write(f"- **Performance Range:** {results[-1]['total_time_ms'] - results[0]['total_time_ms']:.2f}ms\n")
            f.write(f"- **Speed Difference:** {((results[-1]['total_time_ms'] / results[0]['total_time_ms']) - 1) * 100:.1f}% slower (slowest vs fastest)\n\n")
            
            f.write("## Comparison with 1x Scale Winner\n\n")
            f.write("**1x Scale Champion:** CUCKOO_HASH + CSR (1.60ms)\n")
            f.write(f"**10x Scale Champion:** {results[0]['combo']} ({results[0]['total_time_ms']:.2f}ms)\n\n")
            
            # Find CUCKOO_HASH+CSR in 10x results
            cuckoo_csr_10x = next((r for r in results if r['combo'] == 'CUCKOO_HASH+CSR'), None)
            if cuckoo_csr_10x:
                scaling_factor = cuckoo_csr_10x['total_time_ms'] / 1.60
                rank_10x = results.index(cuckoo_csr_10x) + 1
                f.write(f"**CUCKOO_HASH + CSR at 10x:**\n")
                f.write(f"- Rank: {rank_10x}/{len(results)}\n")
                f.write(f"- Time: {cuckoo_csr_10x['total_time_ms']:.2f}ms\n")
                f.write(f"- Scaling: {scaling_factor:.1f}x (for 10x data)\n")
                f.write(f"- Still champion? {'YES!' if rank_10x == 1 else f'No - dropped to rank {rank_10x}'}\n\n")
            
        print(f"10x Report generated: {output_file}")


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("EXHAUSTIVE STRATEGY SEARCH - 10x COMPLEXITY")
    print("="*80)
    print("\nThis test will find the OPTIMAL configuration at PRODUCTION SCALE")
    print("by testing ALL 760 configurations with 10x data complexity.")
    print("\nPhilosophy: SCALE CHANGES EVERYTHING - TEST AT PRODUCTION SIZE!")
    print("\nWARNING: This will take 2-4 HOURS to complete!")
    print("         Grab coffee, lunch, or a nap!")
    
    runner = ExhaustiveSearch10xRunner()
    results = runner.run_exhaustive_search()
    
    print("\n" + "="*80)
    print("10x EXHAUSTIVE SEARCH COMPLETE!")
    print("="*80)
    
    if results:
        winner = results[0]
        print(f"\n[10x CHAMPION]: {winner['combo']}")
        print(f"   Time: {winner['total_time_ms']:.2f}ms")
        print(f"   Memory: {winner['peak_memory_mb']:.1f}MB")
        print(f"   Throughput: {(50000 / (winner['total_time_ms'] / 1000)):.0f} ops/sec")
        print(f"\nPrediction Check:")
        print(f"   Predicted: {PREDICTIONS_10X['10x_scale']['winner']}")
        print(f"   Actual: {winner['combo']}")
        if PREDICTIONS_10X['10x_scale']['winner'] in winner['combo']:
            print(f"   Status: [CORRECT] PREDICTION WAS RIGHT!")
        else:
            print(f"   Status: [WRONG] But we found the truth!")
    
    print("\nGenerated Files:")
    print("  - exhaustive_search_results_10x.json")
    print("  - EXHAUSTIVE_SEARCH_RESULTS_10X.md")
    print("\nThe ultimate truth has been revealed! Trust the data! 🎯")


if __name__ == "__main__":
    main()

