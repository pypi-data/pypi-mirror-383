# File Serialization Benchmark

## Overview

This benchmark tests the **TOP 5 performers** from the 100,000 entity test across **ALL serialization formats** available in xwsystem.

It measures file size, read/write performance, search operations, and deletion operations for each model+format combination.

## Configuration

All benchmark configuration is at the top of `benchmark.py`:

```python
# Test size configuration
TEST_CONFIG_SIZE = [1000, 10000, 100000]

# Top 5 models from 100k entity test
TEST_CONFIG_MODELS = [...]  # 5 top performers

# Serialization formats to test (xwsystem)
TEST_CONFIG_FORMATS = [...]  # json, yaml, msgpack, pickle, cbor, bson, csv, toml, xml

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
```

## Top 5 Models Tested

Based on 100,000 entity benchmark from `db_graph_on_off`:

1. **SPARSE_MATRIX + EDGE_PROPERTY_STORE** (Graph: OFF)
2. **ART + HYPEREDGE_SET** (Graph: OFF)
3. **ADJACENCY_LIST + DYNAMIC_ADJ_LIST** (Graph: OFF)
4. **SPARSE_MATRIX + FLOW_NETWORK** (Graph: OFF)
5. **ADJACENCY_LIST + EDGE_LIST** (Graph: OFF)

## Serialization Formats

Tests all major formats from xwsystem:

### Text Formats
- **JSON** - Standard web format, human-readable
- **YAML** - Configuration format, highly readable
- **TOML** - Modern config format
- **XML** - Enterprise standard
- **CSV** - Spreadsheet-friendly

### Binary Formats
- **MessagePack** - Fast binary JSON alternative
- **Pickle** - Python-native serialization
- **CBOR** - Compact binary format
- **BSON** - MongoDB-style binary JSON

## Operations Tested

### 1. File Size
Measures the serialized file size in bytes and MB for each format.

### 2. Write
Times writing the entire dataset to disk.

### 3. Read All
Times reading the entire dataset from disk.

### 4. Read Scattered
Times reading scattered IDs (10% of users) from the middle of the dataset - simulates random access patterns.

### 5. Search
Times searching for records matching criteria (e.g., username starts with 'user_1').

### 6. Soft Delete
Times marking records as deleted (adds 'deleted' flag to 10% of records).

### 7. Hard Delete
Times actually removing deleted records from the dataset.

## Usage

### Run All Tests
```bash
python benchmark.py
```

This runs all entity sizes (1k, 10k, 100k) across all 5 models and 9 formats.

Total benchmarks: **3 × 5 × 9 = 135 benchmarks**

### Run Single Test
```bash
python benchmark.py 100000
```

This runs only the 100,000 entity test.

## Output Files

### results.json
Complete JSON data for all tests with detailed metrics for each operation.

### results.csv
CSV file with summary data for easy analysis in Excel:
- Model name
- Format name
- File size (MB)
- Write time (ms)
- Read all time (ms)
- Read scattered time (ms)
- Search time (ms)
- Soft delete time (ms)
- Hard delete time (ms)

### output/ Directory
Contains all serialized files in various formats:
- `{MODEL_NAME}_{FORMAT}.{extension}`
- Example: `SPARSE_MATRIX+EDGE_PROPERTY_STORE+GraphOFF_json.json`

## Analysis Questions

This benchmark helps answer:

1. **Which format is smallest?** (File size comparison)
2. **Which format is fastest to write?** (Write performance)
3. **Which format is fastest to read?** (Read performance)
4. **Which format handles random access best?** (Scattered reads)
5. **Which format handles updates best?** (Soft/hard delete)
6. **Which format is best overall?** (Combined metrics)

## Expected Results

### File Size Winners
- **CBOR, MessagePack** - Most compact binary formats
- **CSV** - Efficient for tabular data but not hierarchical

### Write Speed Winners
- **Pickle** - Fastest Python-native serialization
- **MessagePack** - Very fast binary format

### Read Speed Winners
- **Pickle** - Fastest Python-native deserialization
- **JSON** - Well-optimized in Python

### Trade-offs
- **Text formats** (JSON, YAML, XML) - Larger but human-readable, debuggable
- **Binary formats** (Pickle, MessagePack, CBOR) - Smaller and faster but not human-readable
- **Specialized formats** (Parquet, CSV) - Great for specific use cases

## Integration with xwsystem

This benchmark demonstrates the power of xwsystem's unified serialization API:

```python
from exonware.xwsystem.serialization import JsonSerializer, MsgPackSerializer

# Same API for all formats
json_serializer = JsonSerializer()
msgpack_serializer = MsgPackSerializer()

# Save
json_serializer.save_file('data.json', data)
msgpack_serializer.save_file('data.msgpack', data)

# Load
data1 = json_serializer.load_file('data.json')
data2 = msgpack_serializer.load_file('data.msgpack')
```

**ONE import gets 30+ serialization formats with a consistent API!**

## Notes

- All benchmarks use the same data for fair comparison
- Scattered reads use the same random IDs across all formats
- File sizes include all metadata (users, posts, comments, relationships)
- Graph Manager is OFF for all top 5 models (they were fastest without it)

---

**Generated by xwnode benchmark suite**  
Company: eXonware.com  
Author: Eng. Muhammad AlShehri  
Version: 0.0.1

