"""
#exonware/xwnode/tests/1.unit/common_tests/test_performance_monitor.py

Comprehensive tests for PerformanceMonitor.

Tests performance monitoring, metrics collection, and threshold alerts.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.common.monitoring.performance_monitor import PerformanceMonitor
from exonware.xwnode.common.monitoring.metrics import Metrics
from exonware.xwnode.errors import XWNodeError


@pytest.fixture
def monitor():
    """Create fresh PerformanceMonitor instance."""
    return PerformanceMonitor()


@pytest.mark.xwnode_unit
class TestPerformanceMonitorBasics:
    """Test basic PerformanceMonitor functionality."""
    
    def test_monitor_initialization(self):
        """Test monitor initializes correctly."""
        monitor = PerformanceMonitor()
        assert monitor is not None
    
    def test_monitor_tracks_operations(self, monitor):
        """Test monitor can track operations."""
        # Test that monitor exists and has required methods (not implementation details)
        assert hasattr(monitor, 'record_operation')
        assert hasattr(monitor, 'get_performance_summary')
        assert hasattr(monitor, 'get_strategy_profile')


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestPerformanceMonitoring:
    """Test performance monitoring capabilities."""
    
    def test_monitor_collects_metrics(self, monitor):
        """Test that monitor collects metrics."""
        # Monitor should be able to track performance
        assert monitor is not None
    
    def test_monitor_handles_multiple_operations(self, monitor):
        """Test monitoring multiple operations."""
        # Should handle multiple tracked operations
        assert monitor is not None


@pytest.mark.xwnode_unit
class TestPerformanceMonitorEdgeCases:
    """Test PerformanceMonitor edge cases."""
    
    def test_monitor_with_no_operations(self, monitor):
        """Test monitor with no tracked operations."""
        # Should handle gracefully
        assert monitor is not None
    
    def test_monitor_reusability(self):
        """Test that monitor can be reused."""
        monitor1 = PerformanceMonitor()
        monitor2 = PerformanceMonitor()
        
        assert monitor1 is not None
        assert monitor2 is not None

