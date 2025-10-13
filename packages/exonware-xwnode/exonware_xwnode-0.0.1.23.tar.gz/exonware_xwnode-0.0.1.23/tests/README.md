# xwnode Test Suite

**Company:** eXonware.com  
**Author:** Eng. Muhammad AlShehri  
**Email:** connect@exonware.com  
**Version:** 0.0.1  
**Generation Date:** 11-Oct-2025

---

## Overview

Comprehensive test suite for xwnode library following **GUIDELINES_TEST.md** standards with a **four-layer hierarchical testing strategy**.

### Testing Philosophy: The 80/20 Rule

- **20% Core tests** cover **80% of critical functionality** (fast, high-value)
- **Unit tests** verify individual components in isolation
- **Integration tests** validate cross-module scenarios
- **Advance tests** validate production excellence (v1.0.0+)

## Quick Start

```bash
# Run all tests (hierarchical execution)
python tests/runner.py

# Run specific layer
python tests/runner.py --core          # Fast, high-value tests (< 30s)
python tests/runner.py --unit          # Component tests (all modules)
python tests/runner.py --integration   # End-to-end scenarios
python tests/runner.py --advance       # Production excellence (v1.0.0+)

# Run specific priority (advance tests)
python tests/runner.py --security      # Priority #1
python tests/runner.py --usability     # Priority #2
python tests/runner.py --maintainability  # Priority #3
python tests/runner.py --performance   # Priority #4
python tests/runner.py --extensibility    # Priority #5
```

## Directory Structure

```
tests/
├── runner.py                   # Main orchestrator (calls all layer runners)
├── conftest.py                 # Shared fixtures for all layers
├── verify_installation.py      # Installation verification
├── README.md                   # This file
│
├── 0.core/                     # Layer 0: Core Tests (20% for 80% value)
│   ├── runner.py               # Core test runner
│   ├── conftest.py             # Core-specific fixtures
│   ├── data/                   # Test data
│   │   ├── inputs/
│   │   ├── expected/
│   │   └── fixtures/
│   ├── test_all_node_strategies.py  # Comprehensive node tests (47 tests)
│   ├── test_all_edge_strategies.py  # Comprehensive edge tests (34 tests)
│   └── ...                     # Other core tests
│
├── 1.unit/                     # Layer 1: Unit Tests (mirrors src structure)
│   ├── runner.py               # Unit test orchestrator
│   ├── conftest.py             # Unit-specific fixtures
│   ├── nodes_tests/            # Mirrors src/exonware/xwnode/nodes/
│   │   ├── runner.py
│   │   ├── conftest.py
│   │   └── strategies_tests/
│   │       ├── runner.py
│   │       └── test_*.py
│   ├── edges_tests/            # Mirrors src/exonware/xwnode/edges/
│   │   ├── runner.py
│   │   └── strategies_tests/
│   ├── common_tests/           # Mirrors src/exonware/xwnode/common/
│   │   └── runner.py
│   └── facade_tests/           # Mirrors src/exonware/xwnode/facade.py
│       └── runner.py
│
├── 2.integration/              # Layer 2: Integration Tests
│   ├── runner.py               # Integration test runner
│   ├── conftest.py             # Integration-specific fixtures
│   └── test_*.py               # Scenario-based tests
│
└── 3.advance/                  # Layer 3: Advance Tests (v1.0.0+)
    ├── runner.py               # Advance test runner
    ├── conftest.py             # Advance-specific fixtures
    ├── test_security.py        # Priority #1: Security excellence
    ├── test_usability.py       # Priority #2: Usability excellence
    ├── test_maintainability.py # Priority #3: Maintainability excellence
    ├── test_performance.py     # Priority #4: Performance excellence
    └── test_extensibility.py   # Priority #5: Extensibility excellence
```

## Hierarchical Runner Architecture

### Main Orchestrator
`tests/runner.py` calls sub-runners in sequence:
```
tests/runner.py (main)
├─→ tests/0.core/runner.py
├─→ tests/1.unit/runner.py
│   ├─→ tests/1.unit/nodes_tests/runner.py
│   │   └─→ tests/1.unit/nodes_tests/strategies_tests/runner.py
│   ├─→ tests/1.unit/edges_tests/runner.py
│   ├─→ tests/1.unit/common_tests/runner.py
│   └─→ tests/1.unit/facade_tests/runner.py
├─→ tests/2.integration/runner.py
└─→ tests/3.advance/runner.py (v1.0.0+)
```

## Test Markers

All tests use consistent markers for categorization:

```python
@pytest.mark.xwnode_core          # Core functionality tests
@pytest.mark.xwnode_unit          # Unit tests
@pytest.mark.xwnode_integration   # Integration tests
@pytest.mark.xwnode_advance       # Advance tests (v1.0.0+)

# Priority markers (advance tests)
@pytest.mark.xwnode_security         # Priority #1
@pytest.mark.xwnode_usability        # Priority #2
@pytest.mark.xwnode_maintainability  # Priority #3
@pytest.mark.xwnode_performance      # Priority #4
@pytest.mark.xwnode_extensibility    # Priority #5

# Strategy-specific markers
@pytest.mark.xwnode_node_strategy    # Node strategy tests
@pytest.mark.xwnode_edge_strategy    # Edge strategy tests
```

## Running Tests with pytest

```bash
# Run all tests
pytest

# Run specific marker
pytest -m xwnode_core -q          # Core tests only
pytest -m xwnode_security -vv     # Security tests (Priority #1)

# Run specific file
pytest tests/0.core/test_all_node_strategies.py

# Run with keyword filter
pytest -k "hash_map"

# Stop on first failure
pytest -x

# Last failed tests
pytest --lf

# Generate coverage report
pytest --cov=exonware.xwnode --cov-report=html
```

## Test Quality Gates

### Performance Targets
- **Core (0.core):** < 30 seconds total
- **Unit (1.unit):** < 5 minutes total
- **Integration (2.integration):** < 15 minutes total
- **Advance (3.advance):** < 30 minutes total (v1.0.0+)

### Coverage Targets
- **Core libraries:** ≥ 85% coverage
- **Critical modules:** ≥ 90% coverage
- **Security modules:** ≥ 95% coverage

### Success Criteria
- **Pre-v1.0.0:** All core + unit + integration tests pass (100%)
- **v1.0.0+:** All advance tests pass (100%), all 5 priorities validated

## Current Status

**Test Results:**
- ✅ 47 Node Strategy Tests: 100% PASSING
- ✅ 34 Edge Strategy Tests: 100% PASSING
- ✅ Total: 81 comprehensive tests PASSING

## For Developers

### Adding New Tests

**1. Determine appropriate layer:**
- **Core:** Critical path, fast (< 1s per test), high value
- **Unit:** Isolated component test, mirrors source structure
- **Integration:** Cross-module scenario, real wiring
- **Advance:** Production excellence validation (v1.0.0+)

**2. Place in correct directory:**
- Unit tests mirror source: `tests/1.unit/module_name_tests/`
- Add to appropriate layer directory

**3. Add proper markers:**
```python
@pytest.mark.xwnode_unit
def test_my_feature():
    """Test description."""
    pass
```

**4. Update/create module runner if needed**

### Running Individual Layers

```bash
# Run layer runners directly (faster iteration)
python tests/0.core/runner.py
python tests/1.unit/runner.py
python tests/2.integration/runner.py
python tests/3.advance/runner.py
```

## References

- **GUIDELINES_TEST.md:** Comprehensive testing standards
- **GUIDELINES_DEV.md:** Development philosophy and standards
- **pytest Documentation:** [https://docs.pytest.org](https://docs.pytest.org)

---

*This test suite follows eXonware production-grade testing standards for production-ready, maintainable, and extensible code.*
