#!/usr/bin/env python3
"""
Exhaustive Strategy Search Benchmark

Dynamically tests ALL combinations of Node + Edge strategies to find the optimal configuration.

This will test:
- Every NodeMode (28 strategies)
- Every EdgeMode (16 strategies) + None
- Total combinations: 28 * 17 = 476 configurations!

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
# PREDICTION BEFORE RUNNING
# ============================================================================

PREDICTIONS = {
    "1x_scale": {
        "winner": "HASH_MAP + None",
        "reason": "O(1) lookups dominate small datasets, zero graph overhead",
        "estimated_time_ms": 11.5,
        "estimated_memory_mb": 205.0
    },
    "10x_scale": {
        "winner": "B_TREE + ADJ_LIST",
        "reason": "B_TREE cache hits increase, ADJ_LIST is sparse-efficient",
        "estimated_time_ms": 350.0,
        "estimated_memory_mb": 230.0
    },
    "dark_horse": {
        "winner": "LSM_TREE + None",
        "reason": "Write-optimized inserts + zero edge overhead",
        "estimated_time_ms": 360.0
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
        return f"Dynamic: {self.combo.node_mode.name} + {self.combo.edge_mode.name if self.combo.edge_mode else 'None'}"


# ============================================================================
# EXHAUSTIVE SEARCH RUNNER
# ============================================================================

class ExhaustiveSearchRunner:
    """Tests all possible node+edge combinations"""
    
    def __init__(self, quick_mode: bool = False):
        """
        Initialize exhaustive search.
        
        Args:
            quick_mode: If True, only test top candidates (faster)
        """
        self.quick_mode = quick_mode
        self.results = {}
        self.combinations = self._generate_combinations()
        
        print("\n" + "="*80)
        print("EXHAUSTIVE STRATEGY SEARCH - Finding Optimal Configuration")
        print("="*80)
        print(f"\nTotal Combinations to Test: {len(self.combinations)}")
        print(f"Quick Mode: {'Enabled (Top candidates)' if quick_mode else 'DISABLED - FULL 820 SWEEP!'}")
        print(f"\nThis will test EVERY possible combination:")
        print(f"  - All {len([m for m in NodeMode if m != NodeMode.AUTO])} Node Strategies")
        print(f"  - All {len([m for m in EdgeMode if m != EdgeMode.AUTO])} Edge Strategies + None")
        print(f"  - Total: {len(self.combinations)} unique configurations")
        
        # Print predictions
        print("\n" + "="*80)
        print("PREDICTIONS (Before Running):")
        print("="*80)
        for scale, pred in PREDICTIONS.items():
            print(f"\n{scale.replace('_', ' ').title()}:")
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
        
        # Get ALL node modes (complete sweep - trust the data!)
        node_modes = [mode for mode in NodeMode if mode != NodeMode.AUTO]
        
        # Get ALL edge modes + None (complete sweep)
        edge_modes = [None] + [mode for mode in EdgeMode if mode != EdgeMode.AUTO]
        
        # Generate ALL combinations - TRUST THE DATA!
        for node_mode in node_modes:
            for edge_mode in edge_modes:
                combo = StrategyCombo(
                    node_mode=node_mode,
                    edge_mode=edge_mode,
                    name=f"{node_mode.name}+{edge_mode.name if edge_mode else 'None'}"
                )
                combinations.append(combo)
        
        # If quick mode and not overridden, still use full search
        # User wants ALL 820 combinations tested!
        if self.quick_mode and not hasattr(self, '_force_full'):
            print("\n[INFO] Quick mode is on, but testing ALL combinations anyway!")
            print("       Use force_full=True to override and test all 820 configs")
        
        return combinations
    
    def run_quick_benchmark(self, db: DynamicDatabase) -> Dict[str, Any]:
        """Run a lightweight benchmark on a single configuration"""
        metrics = BenchmarkMetrics()
        
        # Use smaller dataset for speed
        num_users = 100
        num_posts = 60
        num_comments = 40
        num_relationships = 200
        
        user_ids = []
        post_ids = []
        comment_ids = []
        
        try:
            # Insert operations
            with metrics.measure("insert"):
                for i in range(num_users):
                    user_id = db.insert_user(generate_user(i))
                    user_ids.append(user_id)
                
                for i in range(num_posts):
                    user_id = random.choice(user_ids)
                    post_id = db.insert_post(generate_post(i, user_id))
                    post_ids.append(post_id)
                
                for i in range(num_comments):
                    post_id = random.choice(post_ids)
                    user_id = random.choice(user_ids)
                    comment_id = db.insert_comment(generate_comment(i, post_id, user_id))
                    comment_ids.append(comment_id)
                
                for i in range(num_relationships):
                    source_id = random.choice(user_ids)
                    target_id = random.choice(user_ids)
                    if source_id != target_id:
                        db.add_relationship(generate_relationship(source_id, target_id))
            
            # Read operations
            with metrics.measure("read"):
                for _ in range(20):
                    db.get_user(random.choice(user_ids))
                    db.get_post(random.choice(post_ids))
                    db.get_comment(random.choice(comment_ids))
            
            # Update operations
            with metrics.measure("update"):
                for i in range(10):
                    db.update_user(user_ids[i], {'bio': f'Updated {i}'})
                    db.update_post(post_ids[i], {'likes_count': i})
            
            # Relationship queries
            with metrics.measure("relationships"):
                for _ in range(10):
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
        """Run benchmark on all combinations"""
        print(f"\nStarting exhaustive search across {len(self.combinations)} combinations...")
        print("This may take a while...\n")
        
        results = []
        successful = 0
        failed = 0
        
        for i, combo in enumerate(self.combinations):
            # Progress indicator (every 50 for large sweeps)
            if (i + 1) % 50 == 0:
                success_rate = (successful / (i + 1)) * 100
                print(f"Progress: {i+1}/{len(self.combinations)} combinations tested... ({success_rate:.1f}% success rate)")
            
            try:
                db = DynamicDatabase(combo)
                result = self.run_quick_benchmark(db)
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
        
        print(f"\nCompleted: {successful} successful, {failed} failed\n")
        
        # Sort by total time (successful only)
        successful_results = [r for r in results if r['success']]
        successful_results.sort(key=lambda x: x['total_time_ms'])
        
        # Save all results
        output_file = Path(__file__).parent / "exhaustive_search_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                'predictions': PREDICTIONS,
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
        """Generate markdown report with winners"""
        output_file = Path(__file__).parent / "EXHAUSTIVE_SEARCH_RESULTS.md"
        
        with open(output_file, 'w') as f:
            f.write("# Exhaustive Strategy Search Results\n\n")
            f.write("## Test Configuration\n\n")
            f.write(f"- **Total Combinations Tested:** {len(self.combinations)}\n")
            f.write(f"- **Successful Tests:** {len(results)}\n")
            f.write(f"- **Quick Mode:** {'Enabled' if self.quick_mode else 'Disabled'}\n")
            f.write("- **Dataset:** 100 users, 60 posts, 40 comments, 200 relationships\n")
            f.write("- **Operations:** Insert, Read, Update, Relationship queries\n\n")
            
            f.write("## Predictions\n\n")
            for scale, pred in PREDICTIONS.items():
                f.write(f"### {scale.replace('_', ' ').title()}\n")
                f.write(f"- **Predicted Winner:** {pred['winner']}\n")
                f.write(f"- **Reasoning:** {pred['reason']}\n")
                if 'estimated_time_ms' in pred:
                    f.write(f"- **Estimated Time:** {pred['estimated_time_ms']}ms\n")
                f.write("\n")
            
            f.write("## Top 20 Fastest Configurations\n\n")
            f.write("| Rank | Configuration | Node Mode | Edge Mode | Total Time | Memory | Insert | Read | Update | Relations |\n")
            f.write("|------|---------------|-----------|-----------|------------|--------|--------|------|--------|----------|\n")
            
            for i, result in enumerate(results[:20], 1):
                combo = result['combo']
                node = result['node_mode']
                edge = result['edge_mode']
                total = result['total_time_ms']
                memory = result['peak_memory_mb']
                
                metrics = result.get('metrics', {})
                insert_time = metrics.get('insert', {}).get('total_time_ms', 0)
                read_time = metrics.get('read', {}).get('total_time_ms', 0)
                update_time = metrics.get('update', {}).get('total_time_ms', 0)
                rel_time = metrics.get('relationships', {}).get('total_time_ms', 0)
                
                medal = "[1st]" if i == 1 else "[2nd]" if i == 2 else "[3rd]" if i == 3 else ""
                f.write(f"| {i} {medal} | {combo} | {node} | {edge} | {total:.2f}ms | {memory:.1f}MB | {insert_time:.1f}ms | {read_time:.1f}ms | {update_time:.1f}ms | {rel_time:.1f}ms |\n")
            
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
            predicted_1x = PREDICTIONS['1x_scale']['winner']
            actual_winner = winner['combo']
            
            f.write(f"**Predicted Winner:** {predicted_1x}\n")
            f.write(f"**Actual Winner:** {actual_winner}\n")
            
            if predicted_1x in actual_winner:
                f.write(f"**Prediction Status:** CORRECT!\n\n")
            else:
                f.write(f"**Prediction Status:** INCORRECT\n\n")
                f.write(f"**Why the difference:**\n")
                f.write(f"- Predicted: {PREDICTIONS['1x_scale']['reason']}\n")
                f.write(f"- Actual winner may have optimizations we didn't account for\n\n")
            
            f.write("## Strategy Analysis\n\n")
            
            # Group by node mode
            f.write("### Best Edge Mode for Each Node Mode\n\n")
            f.write("| Node Mode | Best Edge Mode | Time | Memory |\n")
            f.write("|-----------|----------------|------|--------|\n")
            
            node_best = {}
            for result in results:
                node = result['node_mode']
                if node not in node_best or result['total_time_ms'] < node_best[node]['total_time_ms']:
                    node_best[node] = result
            
            for node, result in sorted(node_best.items(), key=lambda x: x[1]['total_time_ms']):
                edge = result['edge_mode']
                time = result['total_time_ms']
                memory = result['peak_memory_mb']
                f.write(f"| {node} | {edge} | {time:.2f}ms | {memory:.1f}MB |\n")
            
            f.write("\n## Key Findings\n\n")
            
            # Analyze patterns
            edge_none_results = [r for r in results if r['edge_mode'] == 'None']
            edge_some_results = [r for r in results if r['edge_mode'] != 'None']
            
            if edge_none_results and edge_some_results:
                avg_none = sum(r['total_time_ms'] for r in edge_none_results) / len(edge_none_results)
                avg_some = sum(r['total_time_ms'] for r in edge_some_results) / len(edge_some_results)
                
                f.write(f"1. **Edge Storage Impact:**\n")
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
            
            f.write(f"2. **Top 10 Node Modes (Average Performance Across All Edge Modes):**\n")
            for i, (node, avg_time) in enumerate(top_nodes, 1):
                count = len(node_times[node])
                f.write(f"   {i}. {node}: {avg_time:.2f}ms average ({count} edge combinations tested)\n")
            
            f.write(f"\n3. **Fastest Configuration:** {results[0]['combo']}\n")
            f.write(f"   - Time: {results[0]['total_time_ms']:.2f}ms\n")
            f.write(f"   - Memory: {results[0]['peak_memory_mb']:.1f}MB\n\n")
            
            # Top edge modes
            edge_times = {}
            for result in results:
                edge = result['edge_mode']
                if edge not in edge_times:
                    edge_times[edge] = []
                edge_times[edge].append(result['total_time_ms'])
            
            edge_avgs = {edge: sum(times)/len(times) for edge, times in edge_times.items()}
            top_edges = sorted(edge_avgs.items(), key=lambda x: x[1])[:10]
            
            f.write(f"4. **Top 10 Edge Modes (Average Performance Across All Node Modes):**\n")
            for i, (edge, avg_time) in enumerate(top_edges, 1):
                count = len(edge_times[edge])
                f.write(f"   {i}. {edge}: {avg_time:.2f}ms average ({count} node combinations tested)\n")
            
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
            
            f.write(f"\n## Complete Statistics\n\n")
            f.write(f"- **Total Configurations Tested:** {len(results)}\n")
            f.write(f"- **Fastest:** {results[0]['combo']} at {results[0]['total_time_ms']:.2f}ms\n")
            f.write(f"- **Slowest:** {results[-1]['combo']} at {results[-1]['total_time_ms']:.2f}ms\n")
            f.write(f"- **Performance Range:** {results[-1]['total_time_ms'] - results[0]['total_time_ms']:.2f}ms\n")
            f.write(f"- **Speed Difference:** {((results[-1]['total_time_ms'] / results[0]['total_time_ms']) - 1) * 100:.1f}% slower (slowest vs fastest)\n")
            
        print(f"Report generated: {output_file}")


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("EXHAUSTIVE STRATEGY SEARCH - FULL 820 COMBINATION SWEEP")
    print("="*80)
    print("\nThis test will find the OPTIMAL node+edge strategy combination")
    print("by testing ALL 820 possible configurations.")
    print("\nPhilosophy: NEVER TRUST INTUITION - TRUST THE DATA!")
    print("\nEstimated time: ~15-20 minutes for complete sweep")
    print("(Testing every NodeMode × EdgeMode combination)")
    
    # FULL SEARCH - No quick mode!
    quick_mode = False
    
    runner = ExhaustiveSearchRunner(quick_mode=quick_mode)
    results = runner.run_exhaustive_search()
    
    print("\n" + "="*80)
    print("EXHAUSTIVE SEARCH COMPLETE!")
    print("="*80)
    
    if results:
        winner = results[0]
        print(f"\n[WINNER]: {winner['combo']}")
        print(f"   Time: {winner['total_time_ms']:.2f}ms")
        print(f"   Memory: {winner['peak_memory_mb']:.1f}MB")
        print(f"\nPrediction Check:")
        print(f"   Predicted: {PREDICTIONS['1x_scale']['winner']}")
        print(f"   Actual: {winner['combo']}")
        if PREDICTIONS['1x_scale']['winner'] in winner['combo']:
            print(f"   Status: [CORRECT] PREDICTION WAS RIGHT!")
        else:
            print(f"   Status: [WRONG] Prediction was incorrect, but we found something better!")
    
    print("\nGenerated Files:")
    print("  - exhaustive_search_results.json")
    print("  - EXHAUSTIVE_SEARCH_RESULTS.md")


if __name__ == "__main__":
    main()

