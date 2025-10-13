"""
#exonware/xwnode/tests/2.integration/conftest.py

Integration test fixtures - Real wiring with ephemeral resources.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from pathlib import Path


@pytest.fixture
def integration_data_dir():
    """Get the integration test data directory."""
    return Path(__file__).parent / "resources"


@pytest.fixture(scope="session")
def integration_temp_dir(tmp_path_factory):
    """Create a temporary directory for integration tests (session-scoped)."""
    return tmp_path_factory.mktemp("integration_tests")

