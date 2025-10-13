#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/db_files/benchmark.py

File Serialization Benchmark - Top Performers Across Formats

Tests the TOP 5 performers from 100k entity test across ALL serialization formats.
Measures file size, read/write performance, search, and delete operations.

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
    JsonSerializer, YamlSerializer, MsgPackSerializer, 
    PickleSerializer, CborSerializer, BsonSerializer,
    ParquetSerializer, CsvSerializer, TomlSerializer,
    XmlSerializer
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

# Top 5 models from 100k entity test (Graph Manager ON/OFF benchmark)
# These are the fastest performers from the exhaustive benchmark
TEST_CONFIG_MODELS = [
    {
        'name': 'SPARSE_MATRIX+EDGE_PROPERTY_STORE+GraphOFF',
        'description': 'Sparse Matrix + Edge Property Store (Graph: OFF)',
        'node_mode': NodeMode.SPARSE_MATRIX,
        'edge_mode': EdgeMode.EDGE_PROPERTY_STORE,
        'graph_manager': False
    },
    {
        'name': 'ART+HYPEREDGE_SET+GraphOFF',
        'description': 'ART + Hyperedge Set (Graph: OFF)',
        'node_mode': NodeMode.ART,
        'edge_mode': EdgeMode.HYPEREDGE_SET,
        'graph_manager': False
    },
    {
        'name': 'ADJACENCY_LIST+DYNAMIC_ADJ_LIST+GraphOFF',
        'description': 'Adjacency List + Dynamic Adj List (Graph: OFF)',
        'node_mode': NodeMode.ADJACENCY_LIST,
        'edge_mode': EdgeMode.DYNAMIC_ADJ_LIST,
        'graph_manager': False
    },
    {
        'name': 'SPARSE_MATRIX+FLOW_NETWORK+GraphOFF',
        'description': 'Sparse Matrix + Flow Network (Graph: OFF)',
        'node_mode': NodeMode.SPARSE_MATRIX,
        'edge_mode': EdgeMode.FLOW_NETWORK,
        'graph_manager': False
    },
    {
        'name': 'ADJACENCY_LIST+EDGE_LIST+GraphOFF',
        'description': 'Adjacency List + Edge List (Graph: OFF)',
        'node_mode': NodeMode.ADJACENCY_LIST,
        'edge_mode': EdgeMode.EDGE_LIST,
        'graph_manager': False
    }
]

# Serialization formats to test (using xwsystem)
TEST_CONFIG_FORMATS = [
    {'name': 'json', 'serializer': JsonSerializer(), 'extension': '.json'},
    {'name': 'yaml', 'serializer': YamlSerializer(), 'extension': '.yaml'},
    {'name': 'msgpack', 'serializer': MsgPackSerializer(), 'extension': '.msgpack'},
    {'name': 'pickle', 'serializer': PickleSerializer(), 'extension': '.pickle'},
    {'name': 'cbor', 'serializer': CborSerializer(), 'extension': '.cbor'},
    {'name': 'bson', 'serializer': BsonSerializer(), 'extension': '.bson'},
    {'name': 'csv', 'serializer': CsvSerializer(), 'extension': '.csv'},
    {'name': 'toml', 'serializer': TomlSerializer(), 'extension': '.toml'},
    {'name': 'xml', 'serializer': XmlSerializer(), 'extension': '.xml'},
]

# File operations to test
TEST_CONFIG_OPERATIONS = [
    'file_size',        # Measure serialized file size
    'write',            # Write entire dataset
    'read_all',         # Read entire dataset
    'read_scattered',   # Read scattered IDs from middle
    'search',           # Search for specific records
    'soft_delete',      # Mark records as deleted
    'hard_delete',      # Actually remove records
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
    
    def import_data(self, data: Dict[str, Any]):
        """Import data back into database"""
        # Clear existing data
        self.users.clear()
        self.posts.clear()
        self.comments.clear()
        self.relationships.clear()
        
        # Import users
        for uid, user_data in data.get('users', {}).items():
            self.insert_user(user_data)
        
        # Import posts
        for pid, post_data in data.get('posts', {}).items():
            self.insert_post(post_data)
        
        # Import comments
        for cid, comment_data in data.get('comments', {}).items():
            self.insert_comment(comment_data)
        
        # Import relationships
        for rel in data.get('relationships', []):
            self.add_relationship(rel)


# ==============================================================================
# FILE SERIALIZATION BENCHMARK
# ==============================================================================

class FileSerializationBenchmark:
    """Benchmark runner for file serialization operations"""
    
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
        
        # Sample IDs for scattered reads (10% of users)
        self.num_scattered_reads = max(10, int(self.num_users * 0.1))
        
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
        """Benchmark a single model+format combination"""
        db = DynamicDatabase(model_config)
        serializer = format_config['serializer']
        extension = format_config['extension']
        format_name = format_config['name']
        
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
            
            # Generate scattered IDs for reads
            scattered_ids = random.sample(user_ids, min(self.num_scattered_reads, len(user_ids)))
            
            # Test each operation
            for operation in TEST_CONFIG_OPERATIONS:
                op_result = {'success': True}
                
                try:
                    if operation == 'file_size':
                        # Serialize and measure file size
                        start = time.perf_counter()
                        serialized = serializer.dumps(data)
                        elapsed = (time.perf_counter() - start) * 1000
                        
                        file_path = self.output_dir / f"{model_config['name']}_{format_name}{extension}"
                        with open(file_path, 'wb') as f:
                            f.write(serialized if isinstance(serialized, bytes) else serialized.encode())
                        
                        file_size = file_path.stat().st_size
                        op_result.update({
                            'time_ms': elapsed,
                            'file_size_bytes': file_size,
                            'file_size_mb': file_size / (1024 * 1024)
                        })
                    
                    elif operation == 'write':
                        # Write entire dataset
                        start = time.perf_counter()
                        file_path = self.output_dir / f"{model_config['name']}_{format_name}{extension}"
                        serializer.save_file(str(file_path), data)
                        elapsed = (time.perf_counter() - start) * 1000
                        op_result['time_ms'] = elapsed
                    
                    elif operation == 'read_all':
                        # Read entire dataset
                        file_path = self.output_dir / f"{model_config['name']}_{format_name}{extension}"
                        if file_path.exists():
                            start = time.perf_counter()
                            loaded_data = serializer.load_file(str(file_path))
                            elapsed = (time.perf_counter() - start) * 1000
                            op_result['time_ms'] = elapsed
                        else:
                            op_result['success'] = False
                            op_result['error'] = 'File not found'
                    
                    elif operation == 'read_scattered':
                        # Read scattered IDs (simulate random access)
                        file_path = self.output_dir / f"{model_config['name']}_{format_name}{extension}"
                        if file_path.exists():
                            start = time.perf_counter()
                            loaded_data = serializer.load_file(str(file_path))
                            users = loaded_data.get('users', {})
                            fetched = [users.get(uid) for uid in scattered_ids if uid in users]
                            elapsed = (time.perf_counter() - start) * 1000
                            op_result.update({
                                'time_ms': elapsed,
                                'ids_requested': len(scattered_ids),
                                'ids_found': len(fetched)
                            })
                        else:
                            op_result['success'] = False
                            op_result['error'] = 'File not found'
                    
                    elif operation == 'search':
                        # Search for records matching criteria
                        file_path = self.output_dir / f"{model_config['name']}_{format_name}{extension}"
                        if file_path.exists():
                            start = time.perf_counter()
                            loaded_data = serializer.load_file(str(file_path))
                            users = loaded_data.get('users', {})
                            # Search for users with specific criteria (e.g., username starts with 'user_1')
                            matches = [u for u in users.values() if u.get('username', '').startswith('user_1')]
                            elapsed = (time.perf_counter() - start) * 1000
                            op_result.update({
                                'time_ms': elapsed,
                                'matches_found': len(matches)
                            })
                        else:
                            op_result['success'] = False
                            op_result['error'] = 'File not found'
                    
                    elif operation == 'soft_delete':
                        # Mark records as deleted
                        file_path = self.output_dir / f"{model_config['name']}_{format_name}{extension}"
                        if file_path.exists():
                            start = time.perf_counter()
                            loaded_data = serializer.load_file(str(file_path))
                            users = loaded_data.get('users', {})
                            # Mark first 10% as deleted
                            delete_count = max(1, len(users) // 10)
                            for i, uid in enumerate(list(users.keys())[:delete_count]):
                                users[uid]['deleted'] = True
                            serializer.save_file(str(file_path), loaded_data)
                            elapsed = (time.perf_counter() - start) * 1000
                            op_result.update({
                                'time_ms': elapsed,
                                'records_marked': delete_count
                            })
                        else:
                            op_result['success'] = False
                            op_result['error'] = 'File not found'
                    
                    elif operation == 'hard_delete':
                        # Actually remove records
                        file_path = self.output_dir / f"{model_config['name']}_{format_name}{extension}"
                        if file_path.exists():
                            start = time.perf_counter()
                            loaded_data = serializer.load_file(str(file_path))
                            users = loaded_data.get('users', {})
                            # Delete marked records
                            original_count = len(users)
                            users = {uid: u for uid, u in users.items() if not u.get('deleted', False)}
                            loaded_data['users'] = users
                            serializer.save_file(str(file_path), loaded_data)
                            elapsed = (time.perf_counter() - start) * 1000
                            op_result.update({
                                'time_ms': elapsed,
                                'records_deleted': original_count - len(users),
                                'records_remaining': len(users)
                            })
                        else:
                            op_result['success'] = False
                            op_result['error'] = 'File not found'
                
                except Exception as e:
                    op_result['success'] = False
                    op_result['error'] = str(e)
                
                result['operations'][operation] = op_result
        
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()
        
        return result
    
    def run_all(self):
        """Run benchmarks on all model+format combinations"""
        print(f"\n{'='*80}")
        print(f"FILE SERIALIZATION BENCHMARK - {self.total_entities:,} ENTITIES")
        print(f"{'='*80}")
        print(f"\nConfiguration:")
        print(f"  Total Entities (actual): {self.num_users + self.num_posts + self.num_comments:,}")
        print(f"  Distribution: {self.num_users:,} users, {self.num_posts:,} posts, {self.num_comments:,} comments")
        print(f"  Relationships: {self.num_relationships:,}")
        print(f"  Models to test: {len(TEST_CONFIG_MODELS)}")
        print(f"  Formats to test: {len(TEST_CONFIG_FORMATS)}")
        print(f"  Operations per format: {len(TEST_CONFIG_OPERATIONS)}")
        print(f"  Total benchmarks: {len(TEST_CONFIG_MODELS)} × {len(TEST_CONFIG_FORMATS)} = {len(TEST_CONFIG_MODELS) * len(TEST_CONFIG_FORMATS)}")
        print(f"\nOutput directory: {self.output_dir}")
        print()
        
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
                        print("✓")
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
        
        # Show summary by format
        self.show_summary()
    
    def show_summary(self):
        """Show summary of results by format"""
        print(f"\n{'='*80}")
        print(f"SUMMARY BY FORMAT")
        print(f"{'='*80}\n")
        
        successful_results = {k: v for k, v in self.results.items() if v.get('success', True)}
        
        if not successful_results:
            print("No successful results to display.")
            return
        
        # Group by format
        by_format = {}
        for key, result in successful_results.items():
            format_name = result['format']
            if format_name not in by_format:
                by_format[format_name] = []
            by_format[format_name].append(result)
        
        # Display summary for each format
        for format_name in sorted(by_format.keys()):
            results = by_format[format_name]
            print(f"Format: {format_name.upper()}")
            print(f"  Tests: {len(results)}")
            
            # Average file size
            file_sizes = [r['operations']['file_size']['file_size_mb'] 
                         for r in results 
                         if 'file_size' in r['operations'] 
                         and r['operations']['file_size'].get('success', True)]
            if file_sizes:
                avg_size = sum(file_sizes) / len(file_sizes)
                print(f"  Avg File Size: {avg_size:.2f} MB")
            
            # Average write time
            write_times = [r['operations']['write']['time_ms'] 
                          for r in results 
                          if 'write' in r['operations'] 
                          and r['operations']['write'].get('success', True)]
            if write_times:
                avg_write = sum(write_times) / len(write_times)
                print(f"  Avg Write Time: {avg_write:.2f} ms")
            
            # Average read time
            read_times = [r['operations']['read_all']['time_ms'] 
                         for r in results 
                         if 'read_all' in r['operations'] 
                         and r['operations']['read_all'].get('success', True)]
            if read_times:
                avg_read = sum(read_times) / len(read_times)
                print(f"  Avg Read Time: {avg_read:.2f} ms")
            
            print()


def run_all_tests():
    """Run all tests defined in TEST_CONFIG_SIZE array"""
    print(f"\n{'='*80}")
    print(f"FILE SERIALIZATION BENCHMARK - AUTO RUN")
    print(f"{'='*80}")
    print(f"\nTests to run: {', '.join([f'{t:,}' for t in TEST_CONFIG_SIZE])} entities")
    print(f"Models per test: {len(TEST_CONFIG_MODELS)}")
    print(f"Formats per model: {len(TEST_CONFIG_FORMATS)}")
    print(f"Total benchmarks per test: {len(TEST_CONFIG_MODELS)} × {len(TEST_CONFIG_FORMATS)} = {len(TEST_CONFIG_MODELS) * len(TEST_CONFIG_FORMATS)}")
    print(f"Total benchmarks overall: {len(TEST_CONFIG_SIZE)} × {len(TEST_CONFIG_MODELS) * len(TEST_CONFIG_FORMATS)} = {len(TEST_CONFIG_SIZE) * len(TEST_CONFIG_MODELS) * len(TEST_CONFIG_FORMATS)}")
    print(f"{'='*80}\n")
    
    all_results = {}
    output_dir = Path(__file__).parent
    
    # Run each test
    for i, entities in enumerate(TEST_CONFIG_SIZE, 1):
        print(f"\n{'*'*80}")
        print(f"TEST {i}/{len(TEST_CONFIG_SIZE)}: {entities:,} entities")
        print(f"{'*'*80}")
        
        benchmark = FileSerializationBenchmark(total_entities=entities)
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
        print(f"⚠️  WARNING: Could not write {json_file.name} - file is open")
    
    # CSV output
    csv_file = output_dir / f"results{timestamp}.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            writer.writerow(['# File Serialization Benchmark Results - Combined'])
            writer.writerow([f'# Tests: {", ".join([f"{k} entities" for k in all_results.keys()])}'])
            writer.writerow([f'# Models: {len(TEST_CONFIG_MODELS)}, Formats: {len(TEST_CONFIG_FORMATS)}'])
            writer.writerow([])
            
            for entities_str, results in all_results.items():
                successful = {k: v for k, v in results.items() if v.get('success', True)}
                
                writer.writerow([f'=== {entities_str} Entities ==='])
                writer.writerow([f'# Successful: {len(successful)}/{len(results)}'])
                writer.writerow([])
                
                # Header
                writer.writerow([
                    'Model', 'Format', 
                    'File Size (MB)', 'Write (ms)', 'Read All (ms)', 
                    'Read Scattered (ms)', 'Search (ms)', 
                    'Soft Delete (ms)', 'Hard Delete (ms)'
                ])
                
                # Data rows
                for key, result in sorted(successful.items()):
                    ops = result.get('operations', {})
                    writer.writerow([
                        result['model'],
                        result['format'],
                        f"{ops.get('file_size', {}).get('file_size_mb', 0):.2f}",
                        f"{ops.get('write', {}).get('time_ms', 0):.2f}",
                        f"{ops.get('read_all', {}).get('time_ms', 0):.2f}",
                        f"{ops.get('read_scattered', {}).get('time_ms', 0):.2f}",
                        f"{ops.get('search', {}).get('time_ms', 0):.2f}",
                        f"{ops.get('soft_delete', {}).get('time_ms', 0):.2f}",
                        f"{ops.get('hard_delete', {}).get('time_ms', 0):.2f}"
                    ])
                
                writer.writerow([])
        
        print(f"✓ {csv_file.name}")
    except PermissionError:
        print(f"⚠️  WARNING: Could not write {csv_file.name} - file is open")
    
    print(f"\n{'='*80}")
    print(f"ALL BENCHMARKS COMPLETE")
    print(f"{'='*80}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='File Serialization Benchmark')
    parser.add_argument('entities', type=int, nargs='?', default=None,
                        help='Total number of entities. If omitted, runs all tests from TEST_CONFIG_SIZE.')
    args = parser.parse_args()
    
    if args.entities is None:
        run_all_tests()
    else:
        if args.entities < 100:
            print(f"Error: Minimum 100 entities required (got {args.entities})")
            return 1
        
        benchmark = FileSerializationBenchmark(total_entities=args.entities)
        benchmark.run_all()


if __name__ == "__main__":
    main()

