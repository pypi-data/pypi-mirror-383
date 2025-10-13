# Integration Tests (Layer 2)

**Purpose:** Cross-module scenario tests - Validate real-world flows with actual wiring.

**Target Runtime:** < 15 minutes total

## What Belongs Here

- End-to-end workflows
- Cross-module interactions
- Real wiring with ephemeral resources
- Scenario-based tests
- External service integration (with cleanup)
- Multi-component orchestration

## What Doesn't Belong Here

- Single component tests (use 1.unit)
- Fast smoke tests (use 0.core)
- Production excellence validation (use 3.advance)

## Current Tests

- `test_end_to_end.py` - Complete workflow tests
- `test_installation_modes.py` - Installation scenario tests
- `test_xwnode_xwsystem_lazy_serialization.py` - Cross-library integration
- `test_xwquery_script_end_to_end.py` - Query execution integration

## Running Integration Tests

```bash
# Via main orchestrator
python tests/runner.py --integration

# Directly
python tests/2.integration/runner.py

# With pytest
pytest tests/2.integration/ -m xwnode_integration
```

## Test Guidelines

- Real wiring with ephemeral resources (Docker, local services)
- Comprehensive cleanup/teardown
- May use network/disk I/O
- Test realistic scenarios
- Use integration-specific fixtures
- Proper resource management

## Resources

Integration tests may use:
- Docker containers (docker-compose.yml)
- Local databases (with cleanup)
- Mock API servers
- Temporary file systems
- External service mocks

## Markers

Integration tests should use:
```python
@pytest.mark.xwnode_integration
```

## Success Criteria

- ✅ All tests pass (≥ 95%)
- ✅ Total runtime < 15 minutes
- ✅ Flakiness < 2%
- ✅ Proper cleanup (no resource leaks)
- ✅ Realistic scenarios covered

