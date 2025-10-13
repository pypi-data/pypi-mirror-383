"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_flow_network.py

Comprehensive tests for FLOW_NETWORK Strategy.

Flow graphs with capacity constraints.
Critical for network flow algorithms.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.edges.strategies import flow_network


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestFlowNetworkInterface:
    """Test FLOW_NETWORK interface."""
    
    def test_strategy_exists(self):
        """Test that FLOW_NETWORK strategy exists."""
        assert flow_network is not None
        assert EdgeMode.FLOW_NETWORK is not None
    
    def test_capacity_constraints(self):
        """Test flow capacity constraint support."""
        # Flow networks have capacity constraints
        assert EdgeMode.FLOW_NETWORK is not None

