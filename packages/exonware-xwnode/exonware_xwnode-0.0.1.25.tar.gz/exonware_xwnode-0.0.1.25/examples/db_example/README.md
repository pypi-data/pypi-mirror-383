# Database Benchmarking Examples

Comprehensive benchmarking suite for testing xWNode database configurations.

## Structure

```
db_example/
├── common/                    # Shared utilities (schemas, metrics, base classes)
├── db_classic_mix/            # Test 6 predefined configs at 1x & 10x scales
├── db_exhaustive_mix/         # Test ALL NodeMode×EdgeMode combinations
├── db_graph_on_off/           # Compare Graph Manager ON vs OFF
└── db_files/                  # File serialization benchmark (top 5 models × all formats)
```

## Benchmarks

### 1. Classic Mix (`db_classic_mix/`)

Tests the 6 predefined, hand-tuned database configurations:
- **Read-Optimized**: HASH_MAP + None
- **Write-Optimized**: LSM_TREE + DYNAMIC_ADJ_LIST
- **Memory-Efficient**: B_TREE + CSR
- **Query-Optimized**: TREE_GRAPH_HYBRID + WEIGHTED_GRAPH
- **Persistence-Optimized**: B_PLUS_TREE + EDGE_PROPERTY_STORE
- **XWData-Optimized**: HASH_MAP + None (DATA_INTERCHANGE)

**Scales**:
- `--scale 1`: 1,000 total entities (500 users, 300 posts, 200 comments, 1000 relationships)
- `--scale 10`: 10,000 total entities (5000 users, 3000 posts, 2000 comments, 10000 relationships)

**Usage**:
```bash
cd db_classic_mix
python benchmark.py --scale 1    # Run 1x scale
python benchmark.py --scale 10   # Run 10x scale
```

**Output**: `RESULTS.md` with rankings and comparisons

---

### 2. Exhaustive Mix (`db_exhaustive_mix/`)

Tests **ALL** combinations of NodeMode × EdgeMode strategies.

**What it tests**:
- Every NodeMode (40+ strategies) × Every EdgeMode (18+ strategies + None)
- Total: 760+ unique configurations
- Dynamically discovers all available strategies at runtime

**Scales**:
- `--scale 1`: 400 entities (100 users, 60 posts, 40 comments, 200 relationships)
- `--scale 10`: 4,000 entities (1000 users, 600 posts, 400 comments, 2000 relationships)

**Usage**:
```bash
cd db_exhaustive_mix
python benchmark.py --scale 1    # Quick sweep (~15 min)
python benchmark.py --scale 10   # Production scale (~2-4 hours)
```

**Output**: `RESULTS.md` with top 20 fastest, memory efficient, and analysis

---

### 3. Graph ON/OFF (`db_graph_on_off/`)

Compares performance with Graph Manager **OFF** vs **ON (FULL)**.

**What it tests**:
- Runs exhaustive search TWICE per combination:
  1. **Graph Manager OFF**: Baseline O(n) dictionary iteration
  2. **Graph Manager ON**: O(1) indexed lookups with caching

**Key Metrics**:
- Overall speedup (ON vs OFF)
- Relationship query speedup (where Graph Manager helps most)
- Memory overhead of indexing

**Scales**:
- `--scale 1`: 400 entities
- `--scale 10`: 4,000 entities

**Usage**:
```bash
cd db_graph_on_off
python benchmark.py --scale 1    # Compare at 1x
python benchmark.py --scale 10   # Compare at 10x
```

**Output**: `RESULTS.md` with speedup analysis

---

### 4. File Serialization (`db_files/`)

Tests the **TOP 5 performers** from the 100,000 entity test across **ALL serialization formats**.

**What it tests**:
- Top 5 fastest models from `db_graph_on_off` 100k benchmark
- 9 serialization formats from xwsystem (JSON, YAML, MessagePack, Pickle, CBOR, BSON, CSV, TOML, XML)
- Total: 5 models × 9 formats = 45 configurations per test

**Operations tested**:
1. **File Size** - Measure serialized file size
2. **Write** - Write entire dataset to disk
3. **Read All** - Read entire dataset from disk
4. **Read Scattered** - Read random IDs (simulates random access)
5. **Search** - Search for specific records
6. **Soft Delete** - Mark records as deleted
7. **Hard Delete** - Remove deleted records

**Usage**:
```bash
cd db_files
python benchmark.py           # Run all tests (1k, 10k, 100k)
python benchmark.py 100000    # Run single test
```

**Output**: 
- `results.json` - Complete data for all tests
- `results.csv` - Summary table (easy to analyze in Excel)
- `output/` - All serialized files in various formats

**Key Questions Answered**:
- Which format is smallest? (File size)
- Which format is fastest? (Read/write speed)
- Which format handles random access best? (Scattered reads)
- Which format handles updates best? (Soft/hard delete)

---

## Common Module

The `common/` directory contains shared code used by all benchmarks:

- **`schema.py`**: Entity definitions (User, Post, Comment, Relationship) and data generators
- **`metrics.py`**: Time and memory measurement utilities
- **`base.py`**: BaseDatabase abstract class with CRUD operations
- **`db_configs.py`**: The 6 predefined database configurations
- **`utils.py`**: Strategy discovery and combination generation

**Import example**:
```python
from x0_common import (
    BenchmarkMetrics,
    generate_user, generate_post,
    get_all_predefined_databases
)
```

---

## Key Features

### ✅ Minimal Code Duplication
- All benchmarks share the same common utilities
- No repeated schema or metric code

### ✅ Dynamic Strategy Discovery
- Automatically detects all available NodeMode and EdgeMode strategies
- No hardcoded list - adapts as new strategies are added to xWNode

### ✅ Consistent Output Format
- All benchmarks generate `RESULTS.md` markdown reports
- All benchmarks save `results_Xx.json` for programmatic access
- Consistent ranking tables and analysis

### ✅ Multiple Scales
- Test at different complexities (1x, 10x)
- Discover how configurations scale with data size

---

## Quick Start

```bash
# Run all classic benchmarks
cd db_classic_mix
python benchmark.py --scale 1
python benchmark.py --scale 10

# Run exhaustive search (may take hours at 10x!)
cd ../db_exhaustive_mix
python benchmark.py --scale 1

# Compare graph manager impact
cd ../db_graph_on_off
python benchmark.py --scale 1

# Test file serialization across formats
cd ../db_files
python benchmark.py
```

---

## Results

Each benchmark generates:
1. **`results_1x.json`**: Raw data for 1x scale
2. **`results_10x.json`**: Raw data for 10x scale
3. **`RESULTS.md`**: Human-readable report with rankings and analysis

---

## Development Guidelines

When adding new strategies to xWNode:
- **No code changes needed** in `db_exhaustive_mix` or `db_graph_on_off` - they auto-discover!
- Update `db_classic_mix` only if you want to add a new predefined configuration
- All tests automatically pick up new strategies

---

**Company**: eXonware.com  
**Author**: Eng. Muhammad AlShehri  
**Email**: connect@exonware.com  
**Version**: 0.0.1  
**Date**: October 12, 2025
