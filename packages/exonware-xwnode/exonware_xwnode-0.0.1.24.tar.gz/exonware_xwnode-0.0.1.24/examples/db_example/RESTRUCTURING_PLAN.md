# Database Example Restructuring Plan

## Overview

Complete restructuring of the db_example benchmarks with new organization and advanced serialization features.

## Folder Structure (Completed ✓)

```
db_example/
├── common/                    # Shared utilities (kept as-is for Python imports)
├── basic_db/                  # NEW: Simple node-only benchmarks
├── classic_db/                # Renamed from db_classic_mix (node+edge configs)
├── extensive_db/              # Renamed from db_exhaustive_mix
├── db_graph_on_off/           # Kept as-is (Graph Manager comparison)
├── file_db/                   # Renamed from db_files (top 5 models × formats)
└── file_advance_db/           # NEW: Top 1 model × advanced features
```

## Changes Summary

### 1. Folder Renaming (✓ Completed)
- `common` → kept as-is (Python import compatibility)
- `db_classic_mix` → `classic_db`
- `db_exhaustive_mix` → `extensive_db`
- `db_files` → `file_db`

### 2. New Benchmarks to Create

#### A. `basic_db/` - Tables Without Edges
**Purpose**: Test simple node-only storage (no relationships)

**Models** (only NodeModes, no EdgeModes):
```python
TEST_CONFIG_MODELS = [
    {'name': 'HASH_MAP', 'node_mode': NodeMode.HASH_MAP, 'edge_mode': None},
    {'name': 'B_TREE', 'node_mode': NodeMode.B_TREE, 'edge_mode': None},
    {'name': 'LSM_TREE', 'node_mode': NodeMode.LSM_TREE, 'edge_mode': None},
    {'name': 'SKIP_LIST', 'node_mode': NodeMode.SKIP_LIST, 'edge_mode': None},
    {'name': 'ARRAY_LIST', 'node_mode': NodeMode.ARRAY_LIST, 'edge_mode': None},
]
```

**Operations**: Insert, Read, Update (NO relationship queries)

#### B. `file_advance_db/` - Advanced Serialization Features
**Purpose**: Test xwsystem's unique advanced features

**Model**: Only top 1 performer from `file_db` (SPARSE_MATRIX+EDGE_PROPERTY_STORE)

**Formats**: Only formats supporting advanced features
```python
TEST_CONFIG_FORMATS = [
    {'name': 'json', 'capabilities': ['get_at', 'set_at', 'patch', 'stream']},
    {'name': 'xml', 'capabilities': ['get_at', 'set_at', 'xpath']},
    {'name': 'yaml', 'capabilities': ['get_at', 'set_at']},
    {'name': 'lmdb', 'capabilities': ['kv_ops', 'prefix_scan']},
    {'name': 'sqlite3', 'capabilities': ['kv_ops', 'sql_query']},
]
```

**Operations**:
```python
TEST_CONFIG_OPERATIONS = [
    'get_at_random',        # 1000 random path accesses (JSON: /users/123/name)
    'set_at_scattered',     # Update 100 scattered nodes by path
    'iter_path_filter',     # Stream with filtering (JSON: users.item where name starts with 'user_1')
    'apply_patch_batch',    # Apply RFC 6902 patch operations
    'streaming_load',       # Memory-efficient streaming (ijson for JSON)
    'canonical_hash',       # Deterministic hashing for caching
    'kv_get',              # Direct key access (LMDB/SQLite only)
    'kv_put',              # Direct key write (LMDB/SQLite only)
    'kv_scan_prefix',      # Prefix-based scanning (LMDB/SQLite only)
]
```

### 3. Configuration Updates

#### classic_db - Tables WITHOUT Edges Only
```python
TEST_CONFIG_MODELS = [
    {'name': 'Read-Optimized', 'node_mode': NodeMode.HASH_MAP, 'edge_mode': None},
    {'name': 'XWData-Optimized', 'node_mode': NodeMode.DATA_INTERCHANGE_OPTIMIZED, 'edge_mode': None},
    # Remove all models with EdgeModes
]
```

#### extensive_db - Keep All Combinations
No changes needed - already tests all NodeMode × EdgeMode combinations

#### file_db - Top 5 from extensive_db
```python
# Based on 100k entity results from extensive_db
TEST_CONFIG_MODELS = [
    {'name': 'SPARSE_MATRIX+EDGE_PROPERTY_STORE', ...},  # Rank 1
    {'name': 'ART+HYPEREDGE_SET', ...},                   # Rank 2
    {'name': 'ADJACENCY_LIST+DYNAMIC_ADJ_LIST', ...},    # Rank 3
    {'name': 'SPARSE_MATRIX+FLOW_NETWORK', ...},         # Rank 4
    {'name': 'ADJACENCY_LIST+EDGE_LIST', ...},           # Rank 5
]
```

## xwsystem Serialization Examples

### Structure
```
xwsystem/examples/serialization_example/
├── common/                        # Shared utilities
│   ├── __init__.py
│   ├── data_generator.py         # Sample data generation
│   └── test_helpers.py           # Common test functions
├── 1.basic_formats/              # Basic serialization
│   ├── json_example.py
│   ├── yaml_example.py
│   ├── xml_example.py
│   ├── msgpack_example.py
│   ├── pickle_example.py
│   └── README.md
├── 2.path_access/                # Path-based partial access
│   ├── json_pointer.py           # get_at, set_at with JSON Pointer
│   ├── xpath_demo.py             # XML XPath queries
│   ├── dot_notation.py           # YAML dot notation
│   └── README.md
├── 3.streaming/                  # Streaming operations
│   ├── large_json_stream.py      # ijson streaming
│   ├── iter_path_demo.py         # Path-based iteration
│   └── README.md
├── 4.patching/                   # JSON Patch operations
│   ├── rfc6902_patch.py          # JSON Patch (RFC 6902)
│   ├── rfc7386_merge.py          # JSON Merge Patch (RFC 7386)
│   └── README.md
├── 5.key_value/                  # Database-backed serializers
│   ├── lmdb_demo.py              # LMDB key-value operations
│   ├── sqlite_demo.py            # SQLite operations
│   └── README.md
├── 6.canonical/                  # Canonical serialization
│   ├── hash_stable.py            # Stable hashing
│   ├── canonicalize_demo.py      # Canonical representation
│   └── README.md
└── README.md                     # Main documentation
```

### Example Code Templates

#### 1.basic_formats/json_example.py
```python
"""Basic JSON serialization example"""
from exonware.xwsystem.serialization import JsonSerializer

def main():
    serializer = JsonSerializer()
    
    # Sample data
    data = {
        'users': [
            {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
            {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
        ]
    }
    
    # Serialize
    json_str = serializer.dumps(data)
    print(f"Serialized: {json_str[:100]}...")
    
    # Deserialize
    loaded = serializer.loads(json_str)
    print(f"Loaded: {loaded['users'][0]['name']}")
    
    # File operations
    serializer.save_file('data.json', data)
    loaded_from_file = serializer.load_file('data.json')
    print(f"From file: {loaded_from_file['users'][1]['name']}")

if __name__ == "__main__":
    main()
```

#### 2.path_access/json_pointer.py
```python
"""JSON Pointer path access example"""
from exonware.xwsystem.serialization import JsonSerializer

def main():
    serializer = JsonSerializer()
    
    data_json = '''
    {
        "users": [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25}
        ]
    }
    '''
    
    # Get value at path WITHOUT full deserialization
    name = serializer.get_at(data_json, "/users/0/name")
    print(f"User 0 name: {name}")  # Alice
    
    # Set value at path WITHOUT full deserialization
    updated = serializer.set_at(data_json, "/users/1/age", 26)
    print(f"Updated Bob's age to 26")
    
    # Iterate over path matches
    for user in serializer.iter_path(data_json, "users.item"):
        print(f"User: {user['name']}")
    
    print("\n✓ Path access allows working with specific nodes without loading entire file!")
    print("  This is HUGE for large files - update single record in 10GB JSON!")

if __name__ == "__main__":
    main()
```

#### 3.streaming/large_json_stream.py
```python
"""Streaming JSON processing for large files"""
from exonware.xwsystem.serialization import JsonSerializer

def main():
    serializer = JsonSerializer()
    
    # Simulate large JSON file
    large_data = {
        'users': [{'id': i, 'name': f'User{i}'} for i in range(10000)]
    }
    
    # Save to file
    serializer.save_file('large.json', large_data)
    
    # Stream process WITHOUT loading entire file into memory
    print("Streaming users (memory-efficient):")
    count = 0
    for user in serializer.iter_path('large.json', 'users.item'):
        if count < 5:  # Show first 5
            print(f"  {user['name']}")
        count += 1
    print(f"  ... processed {count} users total")
    
    print("\n✓ Streamed 10,000 users without loading entire file!")
    print("  Can process files larger than RAM!")

if __name__ == "__main__":
    main()
```

#### 4.patching/rfc6902_patch.py
```python
"""JSON Patch (RFC 6902) example"""
from exonware.xwsystem.serialization import JsonSerializer

def main():
    serializer = JsonSerializer()
    
    data_json = serializer.dumps({
        'users': [
            {'id': 1, 'name': 'Alice', 'status': 'active'},
            {'id': 2, 'name': 'Bob', 'status': 'inactive'}
        ]
    })
    
    # Define patch operations
    patch = [
        {'op': 'replace', 'path': '/users/1/status', 'value': 'active'},
        {'op': 'add', 'path': '/users/-', 'value': {'id': 3, 'name': 'Charlie', 'status': 'active'}},
        {'op': 'remove', 'path': '/users/0/status'}
    ]
    
    # Apply patch WITHOUT full deserialization
    patched = serializer.apply_patch(data_json, patch, rfc="6902")
    result = serializer.loads(patched)
    
    print("After patch:")
    for user in result['users']:
        print(f"  {user}")
    
    print("\n✓ Atomic patch operations - perfect for database-like updates!")

if __name__ == "__main__":
    main()
```

#### 5.key_value/lmdb_demo.py
```python
"""LMDB key-value operations example"""
from exonware.xwsystem.serialization import LmdbSerializer
from pathlib import Path

def main():
    serializer = LmdbSerializer(map_size=1024**3)  # 1GB
    
    db_path = Path("./lmdb_data")
    db_path.mkdir(exist_ok=True)
    
    # Put operations
    serializer.put("user:1", {'name': 'Alice', 'age': 30}, db_path)
    serializer.put("user:2", {'name': 'Bob', 'age': 25}, db_path)
    serializer.put("post:1", {'title': 'Hello', 'author_id': 1}, db_path)
    
    # Get operation
    user = serializer.get("user:1", db_path)
    print(f"User 1: {user}")
    
    # Scan with prefix
    print("\nAll users:")
    for key in serializer.keys(db_path, prefix="user:"):
        value = serializer.get(key, db_path)
        print(f"  {key}: {value}")
    
    serializer.close()
    
    print("\n✓ LMDB provides database-like operations on serialized data!")
    print("  Very fast reads through memory mapping!")

if __name__ == "__main__":
    main()
```

#### 6.canonical/hash_stable.py
```python
"""Stable hashing example"""
from exonware.xwsystem.serialization import JsonSerializer

def main():
    serializer = JsonSerializer()
    
    # Same data, different order
    data1 = {'b': 2, 'a': 1, 'c': 3}
    data2 = {'a': 1, 'c': 3, 'b': 2}
    
    # Canonical serialization ensures same output
    hash1 = serializer.hash_stable(data1)
    hash2 = serializer.hash_stable(data2)
    
    print(f"Data 1 hash: {hash1}")
    print(f"Data 2 hash: {hash2}")
    print(f"Hashes match: {hash1 == hash2}")
    
    # Use cases
    print("\n✓ Stable hashing enables:")
    print("  - Content-based caching")
    print("  - Deduplication")
    print("  - Version control")
    print("  - Integrity verification")

if __name__ == "__main__":
    main()
```

## Implementation Status

- ✓ Folder renaming completed
- ⏳ basic_db benchmark (pending)
- ⏳ file_advance_db benchmark (pending)  
- ⏳ Configuration updates (pending)
- ⏳ xwsystem serialization examples (pending)
- ⏳ Documentation updates (pending)

## Next Steps

1. Implement `basic_db/benchmark.py`
2. Implement `file_advance_db/benchmark.py`
3. Update `classic_db` models (remove edge modes)
4. Update `file_db` models (add top 5 from extensive_db)
5. Create `xwsystem/examples/serialization_example/` with all examples
6. Update all README files

## Key Benefits

### Database Benchmarks
- **Clearer organization**: basic → classic → extensive → file
- **Better coverage**: Separate testing of node-only vs node+edge configurations
- **Advanced features**: file_advance_db showcases xwsystem's unique capabilities

### Serialization Examples
- **Educational**: Shows all xwsystem features with practical examples
- **Progressive**: From basic to advanced features
- **Production-ready**: Code can be copied directly into projects

---

**Generated**: October 12, 2025  
**Author**: Eng. Muhammad AlShehri  
**Company**: eXonware.com

