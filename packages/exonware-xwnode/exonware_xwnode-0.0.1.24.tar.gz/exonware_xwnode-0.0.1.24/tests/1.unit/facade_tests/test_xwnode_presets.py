"""
#exonware/xwnode/tests/1.unit/facade_tests/test_xwnode_presets.py

Comprehensive tests for XWNode A+ Usability Presets.

Tests all 12+ presets:
- DATA_INTERCHANGE_OPTIMIZED
- SOCIAL_GRAPH
- ANALYTICS
- SEARCH_ENGINE
- TIME_SERIES
- SPATIAL_MAP
- ML_DATASET
- etc.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import (
    get_preset, list_presets, USABILITY_PRESETS,
    NodeMode, EdgeMode
)


# ============================================================================
# PRESET AVAILABILITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_usability
class TestUsabilityPresetsAvailability:
    """Test that all A+ usability presets are available."""
    
    def test_all_presets_defined(self):
        """Test that all expected presets are defined."""
        expected_presets = [
            'DATA_INTERCHANGE_OPTIMIZED',
            'DEFAULT',
            'PURE_TREE',
            'TREE_GRAPH_MIX',
            'FAST_LOOKUP',
            'PERFORMANCE_OPTIMIZED',
            'MEMORY_EFFICIENT',
            'SOCIAL_GRAPH',
            'ANALYTICS',
            'SEARCH_ENGINE',
            'TIME_SERIES',
            'SPATIAL_MAP',
            'ML_DATASET',
        ]
        
        available_presets = list_presets()
        
        for preset_name in expected_presets:
            assert preset_name in available_presets, f"Preset {preset_name} not found"
    
    def test_get_preset_returns_config(self):
        """Test get_preset returns valid configuration."""
        config = get_preset('DATA_INTERCHANGE_OPTIMIZED')
        
        assert config is not None
        assert config.node_mode is not None
        assert config.description != ""
    
    def test_invalid_preset_raises_error(self):
        """Test that invalid preset name raises clear error."""
        with pytest.raises(ValueError, match="Unknown preset"):
            get_preset('INVALID_PRESET_NAME')


# ============================================================================
# PRESET CONFIGURATION TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_usability
class TestPresetsConfiguration:
    """Test preset configurations are valid."""
    
    @pytest.mark.parametrize("preset_name", [
        'DATA_INTERCHANGE_OPTIMIZED',
        'SOCIAL_GRAPH',
        'ANALYTICS',
        'SEARCH_ENGINE',
        'TIME_SERIES',
        'SPATIAL_MAP',
    ])
    def test_preset_has_valid_node_mode(self, preset_name):
        """Test each preset has valid node mode."""
        config = get_preset(preset_name)
        
        assert isinstance(config.node_mode, NodeMode)
    
    @pytest.mark.parametrize("preset_name", [
        'DATA_INTERCHANGE_OPTIMIZED',
        'SOCIAL_GRAPH',
        'ANALYTICS',
    ])
    def test_preset_has_description(self, preset_name):
        """Test each preset has meaningful description."""
        config = get_preset(preset_name)
        
        assert config.description is not None
        assert len(config.description) > 10
    
    def test_data_interchange_optimized_config(self):
        """Test DATA_INTERCHANGE_OPTIMIZED preset configuration."""
        config = get_preset('DATA_INTERCHANGE_OPTIMIZED')
        
        assert config.node_mode == NodeMode.HASH_MAP
        assert config.edge_mode is None  # No edges for efficiency
        assert config.performance_class == 'maximum_efficiency'
        assert 'graph_operations' in config.disabled_features
    
    def test_social_graph_config(self):
        """Test SOCIAL_GRAPH preset configuration."""
        config = get_preset('SOCIAL_GRAPH')
        
        assert config.node_mode == NodeMode.TREE_GRAPH_HYBRID
        assert config.edge_mode == EdgeMode.ADJ_LIST
        assert config.performance_class == 'graph_optimized'
    
    def test_analytics_config(self):
        """Test ANALYTICS preset configuration."""
        config = get_preset('ANALYTICS')
        
        assert config.node_mode == NodeMode.ORDERED_MAP_BALANCED
        assert config.edge_mode == EdgeMode.EDGE_PROPERTY_STORE
        assert config.performance_class == 'analytics_optimized'


# ============================================================================
# PRESET USAGE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_usability
class TestPresetUsage:
    """Test using presets with XWNode."""
    
    def test_list_presets_returns_all(self):
        """Test list_presets returns all available presets."""
        presets = list_presets()
        
        assert isinstance(presets, list)
        assert len(presets) >= 12  # At least 12 presets
        assert 'DATA_INTERCHANGE_OPTIMIZED' in presets
        assert 'SOCIAL_GRAPH' in presets
    
    def test_preset_configuration_is_usable(self):
        """Test that preset configurations can be used."""
        config = get_preset('DEFAULT')
        
        # Configuration should have all required attributes
        assert hasattr(config, 'node_mode')
        assert hasattr(config, 'edge_mode')
        assert hasattr(config, 'description')
        assert hasattr(config, 'performance_class')


# ============================================================================
# PRESET METADATA TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_usability
class TestPresetMetadata:
    """Test preset metadata and documentation."""
    
    def test_all_presets_have_performance_class(self):
        """Test all presets specify performance class."""
        for preset_name in list_presets():
            config = get_preset(preset_name)
            assert config.performance_class is not None
            assert len(config.performance_class) > 0
    
    def test_all_presets_have_node_mode(self):
        """Test all presets specify node mode."""
        for preset_name in list_presets():
            config = get_preset(preset_name)
            assert config.node_mode is not None
            assert isinstance(config.node_mode, NodeMode)
    
    def test_preset_disabled_features_is_list(self):
        """Test disabled_features is always a list."""
        for preset_name in list_presets():
            config = get_preset(preset_name)
            assert isinstance(config.disabled_features, list)
    
    def test_preset_internal_config_is_dict(self):
        """Test internal_config is always a dict."""
        for preset_name in list_presets():
            config = get_preset(preset_name)
            assert isinstance(config.internal_config, dict)

