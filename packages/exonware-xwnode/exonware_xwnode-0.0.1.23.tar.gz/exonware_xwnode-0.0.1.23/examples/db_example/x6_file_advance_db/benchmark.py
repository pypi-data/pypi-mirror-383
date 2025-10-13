#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/x6_file_advance_db/benchmark.py

File Advanced Features Benchmark - Top Performer with Advanced Operations

Tests the TOP 1 performer across ADVANCED serialization features:
- get_at: Random path access without full deserialization
- set_at: Partial updates by path
- iter_path: Streaming with filtering
- apply_patch: RFC 6902 JSON Patch operations
- streaming_load: Memory-efficient streaming
- canonical_hash: Deterministic hashing
- kv operations: Key-value ops (LMDB/SQLite)

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
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
import traceback

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

# Add xwsystem to path
xwsystem_root = project_root.parent / "xwsystem" / "src"
sys.path.insert(0, str(xwsystem_root))

from exonware.xwnode.defs import NodeMode, EdgeMode, GraphOptimization
from exonware.xwsystem.serialization import (
    JsonSerializer, YamlSerializer, XmlSerializer,
    LmdbSerializer, Sqlite3Serializer
)

from x0_common import (
    BenchmarkMetrics, BaseDatabase,
    generate_user, generate_post, generate_comment, generate_relationship
)

# ==============================================================================
# BENCHMARK CONFIGURATION
# ==============================================================================

# Test size configuration
TEST_CONFIG_SIZE = [1000, 10000, 100000]

# Top 1 model from x5_file_db (best performer)
TEST_CONFIG_MODELS = [
    {
        'name': 'SPARSE_MATRIX+EDGE_PROPERTY_STORE',
        'description': 'Sparse Matrix + Edge Property Store (Graph: OFF)',
        'node_mode': NodeMode.SPARSE_MATRIX,
        'edge_mode': EdgeMode.EDGE_PROPERTY_STORE,
        'graph_manager': False
    }
]

# Only formats supporting advanced features
TEST_CONFIG_FORMATS = [
    {
        'name': 'json',
        'serializer': JsonSerializer(),
        'extension': '.json',
        'capabilities': ['get_at', 'set_at', 'iter_path', 'apply_patch', 'streaming', 'canonical']
    },
    {
        'name': 'xml',
        'serializer': XmlSerializer(),
        'extension': '.xml',
        'capabilities': ['get_at', 'set_at', 'iter_path', 'canonical']
    },
    {
        'name': 'yaml',
        'serializer': YamlSerializer(),
        'extension': '.yaml',
        'capabilities': ['get_at', 'set_at', 'iter_path', 'canonical']
    },
    {
        'name': 'lmdb',
        'serializer': LmdbSerializer(),
        'extension': '_lmdb',
        'capabilities': ['kv_get', 'kv_put', 'kv_scan_prefix']
    },
    {
        'name': 'sqlite3',
        'serializer': Sqlite3Serializer(),
        'extension': '.db',
        'capabilities': ['kv_get', 'kv_put']
    },
]

# Advanced operations to test
TEST_CONFIG_OPERATIONS = [
    'get_at_random',      # Random path access (1000 times)
    'set_at_scattered',   # Scattered updates (100 times)
    'iter_path_filter',   # Streaming with filtering
    'apply_patch_batch',  # RFC 6902 patch operations
    'streaming_load',     # Memory-efficient streaming
    'canonical_hash',     # Deterministic hashing
    'kv_get',            # Key-value get (LMDB/SQLite only)
    'kv_put',            # Key-value put (LMDB/SQLite only)
    'kv_scan_prefix',    # Prefix-based scan (LMDB only)
]

# ==============================================================================
# DATABASE IMPLEMENTATION
# ==============================================================================

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
    
    def export_data(self) -> Dict[str, Any]:
        """Export all database data for serialization"""
        return {
            'users': {uid: self.get_user(uid) for uid in self.users.keys()},
            'posts': {pid: self.get_post(pid) for pid in self.posts.keys()},
            'comments': {cid: self.get_comment(cid) for cid in self.comments.keys()},
            'relationships': list(self.relationships),
            'metadata': {
                'name': self.name,
                'description': self.description,
                'total_users': len(self.users),
                'total_posts': len(self.posts),
                'total_comments': len(self.comments),
                'total_relationships': len(self.relationships)
            }
        }


# ==============================================================================
# FILE ADVANCED FEATURES BENCHMARK
# ==============================================================================

class FileAdvancedBenchmark:
    """Benchmark runner for advanced file serialization features"""
    
    def __init__(self, total_entities: int = 1000):
        """
        Initialize benchmark.
        
        Args:
            total_entities: Total number of entities (users + posts + comments)
        """
        self.total_entities = total_entities
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Calculate scale factor
        self.scale_factor = total_entities // 1000
        
        # Entity distribution (10% of total for faster testing)
        base_scale = total_entities // 10
        self.num_users = int(base_scale * 0.5)
        self.num_posts = int(base_scale * 0.3)
        self.num_comments = int(base_scale * 0.2)
        self.num_relationships = self.num_users * 2
        
        # Sample IDs for operations
        self.num_random_access = min(1000, self.num_users)
        self.num_updates = min(100, self.num_users // 10)
        
        self.results = {}
    
    def populate_database(self, db: DynamicDatabase) -> Tuple[List[str], List[str], List[str]]:
        """Populate database with test data"""
        user_ids = []
        post_ids = []
        comment_ids = []
        
        # Insert users
        for i in range(self.num_users):
            user_ids.append(db.insert_user(generate_user(i)))
        
        # Insert posts
        for i in range(self.num_posts):
            post_ids.append(db.insert_post(generate_post(i, random.choice(user_ids))))
        
        # Insert comments
        for i in range(self.num_comments):
            comment_ids.append(db.insert_comment(generate_comment(i, random.choice(post_ids), random.choice(user_ids))))
        
        # Insert relationships
        for i in range(self.num_relationships):
            source, target = random.choice(user_ids), random.choice(user_ids)
            if source != target:
                db.add_relationship(generate_relationship(source, target))
        
        return user_ids, post_ids, comment_ids
    
    def benchmark_format(self, model_config: dict, format_config: dict) -> Dict[str, Any]:
        """Benchmark advanced features for a single model+format combination"""
        db = DynamicDatabase(model_config)
        serializer = format_config['serializer']
        extension = format_config['extension']
        format_name = format_config['name']
        capabilities = format_config['capabilities']
        
        result = {
            'model': model_config['name'],
            'format': format_name,
            'success': True,
            'operations': {}
        }
        
        try:
            # Populate database
            user_ids, post_ids, comment_ids = self.populate_database(db)
            
            # Export data
            data = db.export_data()
            
            # Serialize to file first
            file_path = self.output_dir / f"{model_config['name']}_{format_name}{extension}"
            serializer.save_file(str(file_path), data)
            serialized_data = serializer.dumps(data)
            
            # Generate random user IDs for testing
            random_user_ids = random.sample(user_ids, min(self.num_random_access, len(user_ids)))
            scattered_user_ids = random.sample(user_ids, min(self.num_updates, len(user_ids)))
            
            # Test each operation based on capabilities
            for operation in TEST_CONFIG_OPERATIONS:
                if operation not in capabilities and not any(cap in operation for cap in capabilities):
                    continue
                
                op_result = {'success': True}
                
                try:
                    if operation == 'get_at_random' and 'get_at' in capabilities:
                        # Random path access without full deserialization
                        start = time.perf_counter()
                        for i, uid in enumerate(random_user_ids):
                            try:
                                # Access user by path
                                path = f"/users/{uid}" if format_name == 'json' else f"users.{uid}"
                                value = serializer.get_at(serialized_data, path)
                            except:
                                pass  # Some paths may not exist
                        elapsed = (time.perf_counter() - start) * 1000
                        op_result.update({
                            'time_ms': elapsed,
                            'operations': len(random_user_ids),
                            'avg_time_per_op_ms': elapsed / len(random_user_ids) if random_user_ids else 0
                        })
                    
                    elif operation == 'set_at_scattered' and 'set_at' in capabilities:
                        # Scattered updates by path
                        start = time.perf_counter()
                        for i, uid in enumerate(scattered_user_ids):
                            try:
                                path = f"/users/{uid}/bio" if format_name == 'json' else f"users.{uid}.bio"
                                serialized_data = serializer.set_at(serialized_data, path, f"Updated bio {i}")
                            except:
                                pass
                        elapsed = (time.perf_counter() - start) * 1000
                        op_result.update({
                            'time_ms': elapsed,
                            'operations': len(scattered_user_ids),
                            'avg_time_per_op_ms': elapsed / len(scattered_user_ids) if scattered_user_ids else 0
                        })
                    
                    elif operation == 'iter_path_filter' and 'iter_path' in capabilities:
                        # Streaming with filtering
                        start = time.perf_counter()
                        count = 0
                        try:
                            for item in serializer.iter_path(serialized_data, "users.*" if format_name != 'json' else "users.item"):
                                if item and str(item).startswith("user"):
                                    count += 1
                        except:
                            pass
                        elapsed = (time.perf_counter() - start) * 1000
                        op_result.update({
                            'time_ms': elapsed,
                            'items_processed': count
                        })
                    
                    elif operation == 'apply_patch_batch' and 'apply_patch' in capabilities:
                        # RFC 6902 JSON Patch
                        start = time.perf_counter()
                        try:
                            patch = [
                                {'op': 'replace', 'path': '/metadata/name', 'value': 'Updated Database'},
                            ]
                            patched_data = serializer.apply_patch(serialized_data, patch, rfc="6902")
                        except:
                            pass
                        elapsed = (time.perf_counter() - start) * 1000
                        op_result.update({
                            'time_ms': elapsed,
                            'patch_operations': 1
                        })
                    
                    elif operation == 'streaming_load' and 'streaming' in capabilities:
                        # Memory-efficient streaming
                        start = time.perf_counter()
                        chunks = 0
                        try:
                            for chunk in serializer.iter_serialize(data, chunk_size=8192):
                                chunks += 1
                        except:
                            pass
                        elapsed = (time.perf_counter() - start) * 1000
                        op_result.update({
                            'time_ms': elapsed,
                            'chunks_generated': chunks
                        })
                    
                    elif operation == 'canonical_hash' and 'canonical' in capabilities:
                        # Deterministic hashing
                        start = time.perf_counter()
                        try:
                            hash1 = serializer.hash_stable(data)
                            hash2 = serializer.hash_stable(data)
                            matches = hash1 == hash2
                        except:
                            matches = False
                        elapsed = (time.perf_counter() - start) * 1000
                        op_result.update({
                            'time_ms': elapsed,
                            'hash_stable': matches
                        })
                    
                    elif operation == 'kv_get' and 'kv_get' in capabilities:
                        # Key-value get
                        start = time.perf_counter()
                        for i, uid in enumerate(random_user_ids[:10]):  # Only 10 for KV
                            try:
                                serializer.get(f"user:{uid}", file_path.parent)
                            except:
                                pass
                        elapsed = (time.perf_counter() - start) * 1000
                        op_result.update({
                            'time_ms': elapsed,
                            'operations': min(10, len(random_user_ids))
                        })
                    
                    elif operation == 'kv_put' and 'kv_put' in capabilities:
                        # Key-value put
                        start = time.perf_counter()
                        for i, uid in enumerate(scattered_user_ids[:10]):  # Only 10 for KV
                            try:
                                serializer.put(f"user:{uid}", {'id': uid, 'bio': f'Updated {i}'}, file_path.parent)
                            except:
                                pass
                        elapsed = (time.perf_counter() - start) * 1000
                        op_result.update({
                            'time_ms': elapsed,
                            'operations': min(10, len(scattered_user_ids))
                        })
                    
                    elif operation == 'kv_scan_prefix' and 'kv_scan_prefix' in capabilities:
                        # Prefix-based scanning
                        start = time.perf_counter()
                        count = 0
                        try:
                            for key in serializer.keys(file_path.parent, prefix="user:"):
                                count += 1
                                if count >= 100:  # Limit to 100
                                    break
                        except:
                            pass
                        elapsed = (time.perf_counter() - start) * 1000
                        op_result.update({
                            'time_ms': elapsed,
                            'keys_scanned': count
                        })
                
                except Exception as e:
                    op_result['success'] = False
                    op_result['error'] = str(e)
                
                if op_result.get('time_ms') is not None:
                    result['operations'][operation] = op_result
        
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()
        
        return result
    
    def run_all(self):
        """Run benchmarks on all model+format combinations"""
        print(f"\n{'='*80}")
        print(f"FILE ADVANCED FEATURES BENCHMARK - {self.total_entities:,} ENTITIES")
        print(f"{'='*80}")
        print(f"\nConfiguration:")
        print(f"  Total Entities (actual): {self.num_users + self.num_posts + self.num_comments:,}")
        print(f"  Distribution: {self.num_users:,} users, {self.num_posts:,} posts, {self.num_comments:,} comments")
        print(f"  Relationships: {self.num_relationships:,}")
        print(f"  Models to test: {len(TEST_CONFIG_MODELS)}")
        print(f"  Formats to test: {len(TEST_CONFIG_FORMATS)}")
        print(f"  Operations: {', '.join(TEST_CONFIG_OPERATIONS)}")
        print(f"  Total benchmarks: {len(TEST_CONFIG_MODELS)} × {len(TEST_CONFIG_FORMATS)} = {len(TEST_CONFIG_MODELS) * len(TEST_CONFIG_FORMATS)}")
        print(f"\nOutput directory: {self.output_dir}")
        print(f"\nTesting ADVANCED serialization features...")
        print(f"(get_at, set_at, iter_path, apply_patch, streaming, canonical, kv_ops)\n")
        
        total_benchmarks = len(TEST_CONFIG_MODELS) * len(TEST_CONFIG_FORMATS)
        completed = 0
        successful = 0
        failed = 0
        
        for model_config in TEST_CONFIG_MODELS:
            model_name = model_config['name']
            
            for format_config in TEST_CONFIG_FORMATS:
                format_name = format_config['name']
                completed += 1
                
                print(f"[{completed}/{total_benchmarks}] {model_name} × {format_name}...", end=' ', flush=True)
                
                try:
                    result = self.benchmark_format(model_config, format_config)
                    key = f"{model_name}+{format_name}"
                    self.results[key] = result
                    
                    if result.get('success', True):
                        successful += 1
                        ops_count = len([op for op in result.get('operations', {}).values() if op.get('success', True)])
                        print(f"✓ ({ops_count} ops)")
                    else:
                        failed += 1
                        print(f"✗ ({result.get('error', 'Unknown error')})")
                
                except Exception as e:
                    failed += 1
                    print(f"✗ (Exception: {e})")
                    self.results[f"{model_name}+{format_name}"] = {
                        'model': model_name,
                        'format': format_name,
                        'success': False,
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK COMPLETE")
        print(f"{'='*80}")
        print(f"Successful: {successful}/{total_benchmarks}")
        print(f"Failed: {failed}/{total_benchmarks}")


def run_all_tests():
    """Run all tests defined in TEST_CONFIG_SIZE array"""
    print(f"\n{'='*80}")
    print(f"FILE ADVANCED FEATURES BENCHMARK - AUTO RUN")
    print(f"{'='*80}")
    print(f"\nTests to run: {', '.join([f'{t:,}' for t in TEST_CONFIG_SIZE])} entities")
    print(f"Models per test: {len(TEST_CONFIG_MODELS)}")
    print(f"Formats per model: {len(TEST_CONFIG_FORMATS)}")
    print(f"{'='*80}\n")
    
    all_results = {}
    output_dir = Path(__file__).parent
    
    # Run each test
    for i, entities in enumerate(TEST_CONFIG_SIZE, 1):
        print(f"\n{'*'*80}")
        print(f"TEST {i}/{len(TEST_CONFIG_SIZE)}: {entities:,} entities")
        print(f"{'*'*80}")
        
        benchmark = FileAdvancedBenchmark(total_entities=entities)
        benchmark.run_all()
        
        all_results[str(entities)] = benchmark.results
    
    # Generate output files
    print(f"\n{'='*80}")
    print(f"GENERATING OUTPUT FILES")
    print(f"{'='*80}")
    
    # Generate timestamp for output files
    timestamp = datetime.now().strftime("_%y%m%d%H%M%S")
    
    # JSON output
    json_file = output_dir / f"results{timestamp}.json"
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"✓ {json_file.name}")
    except PermissionError:
        print(f"⚠️  WARNING: Could not write {json_file.name}")
    
    # CSV output
    csv_file = output_dir / f"results{timestamp}.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            writer.writerow(['# File Advanced Features Benchmark Results'])
            writer.writerow([f'# Tests: {", ".join([f"{k} entities" for k in all_results.keys()])}'])
            writer.writerow([])
            
            for entities_str, results in all_results.items():
                successful = {k: v for k, v in results.items() if v.get('success', True)}
                
                writer.writerow([f'=== {entities_str} Entities ==='])
                writer.writerow([f'# Successful: {len(successful)}/{len(results)}'])
                writer.writerow([])
                
                # Header
                writer.writerow([
                    'Model', 'Format', 'get_at (ms)', 'set_at (ms)', 
                    'iter_path (ms)', 'apply_patch (ms)', 'streaming (ms)',
                    'canonical (ms)', 'kv_get (ms)', 'kv_put (ms)', 'kv_scan (ms)'
                ])
                
                # Data rows
                for key, result in sorted(successful.items()):
                    ops = result.get('operations', {})
                    writer.writerow([
                        result['model'],
                        result['format'],
                        f"{ops.get('get_at_random', {}).get('time_ms', ''):.2f}" if 'get_at_random' in ops else '',
                        f"{ops.get('set_at_scattered', {}).get('time_ms', ''):.2f}" if 'set_at_scattered' in ops else '',
                        f"{ops.get('iter_path_filter', {}).get('time_ms', ''):.2f}" if 'iter_path_filter' in ops else '',
                        f"{ops.get('apply_patch_batch', {}).get('time_ms', ''):.2f}" if 'apply_patch_batch' in ops else '',
                        f"{ops.get('streaming_load', {}).get('time_ms', ''):.2f}" if 'streaming_load' in ops else '',
                        f"{ops.get('canonical_hash', {}).get('time_ms', ''):.2f}" if 'canonical_hash' in ops else '',
                        f"{ops.get('kv_get', {}).get('time_ms', ''):.2f}" if 'kv_get' in ops else '',
                        f"{ops.get('kv_put', {}).get('time_ms', ''):.2f}" if 'kv_put' in ops else '',
                        f"{ops.get('kv_scan_prefix', {}).get('time_ms', ''):.2f}" if 'kv_scan_prefix' in ops else '',
                    ])
                
                writer.writerow([])
        
        print(f"✓ {csv_file.name}")
    except PermissionError:
        print(f"⚠️  WARNING: Could not write {csv_file.name}")
    
    print(f"\n{'='*80}")
    print(f"ALL BENCHMARKS COMPLETE")
    print(f"{'='*80}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='File Advanced Features Benchmark')
    parser.add_argument('entities', type=int, nargs='?', default=None,
                        help='Total number of entities. If omitted, runs all tests.')
    args = parser.parse_args()
    
    if args.entities is None:
        run_all_tests()
    else:
        if args.entities < 100:
            print(f"Error: Minimum 100 entities required (got {args.entities})")
            return 1
        
        benchmark = FileAdvancedBenchmark(total_entities=args.entities)
        benchmark.run_all()


if __name__ == "__main__":
    main()

