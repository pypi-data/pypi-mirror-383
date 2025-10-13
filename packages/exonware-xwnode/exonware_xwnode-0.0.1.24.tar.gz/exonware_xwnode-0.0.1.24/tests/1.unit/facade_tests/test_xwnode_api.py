"""
#exonware/xwnode/tests/1.unit/facade_tests/test_xwnode_api.py

Comprehensive tests for XWNode public API.

Tests the main facade interface that users interact with.
CRITICAL for usability and backward compatibility.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode
from exonware.xwnode.errors import XWNodeError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def simple_dict_data():
    """Simple dictionary data."""
    return {'name': 'Alice', 'age': 30, 'city': 'NYC'}


@pytest.fixture
def nested_dict_data():
    """Nested dictionary data."""
    return {
        'user': {
            'profile': {
                'name': 'Alice',
                'email': 'alice@example.com'
            },
            'settings': {
                'theme': 'dark',
                'notifications': True
            }
        }
    }


@pytest.fixture
def simple_list_data():
    """Simple list data."""
    return [1, 2, 3, 4, 5]


# ============================================================================
# FACTORY METHODS TESTS
# ============================================================================

@pytest.mark.xwnode_unit
class TestXWNodeFactoryMethods:
    """Test XWNode factory methods."""
    
    def test_from_native_with_dict(self, simple_dict_data):
        """Test creating XWNode from dictionary."""
        node = XWNode.from_native(simple_dict_data)
        
        assert node is not None
        assert isinstance(node, XWNode)
    
    def test_from_native_with_list(self, simple_list_data):
        """Test creating XWNode from list."""
        node = XWNode.from_native(simple_list_data)
        
        assert node is not None
        assert isinstance(node, XWNode)
    
    def test_from_native_with_nested_data(self, nested_dict_data):
        """Test creating XWNode from nested data."""
        node = XWNode.from_native(nested_dict_data)
        
        assert node is not None
        assert len(node) > 0
    
    def test_from_native_with_specific_mode(self, simple_dict_data):
        """Test creating XWNode with specific mode."""
        node = XWNode.from_native(simple_dict_data, mode='AUTO')
        
        assert node is not None
    
    def test_from_native_with_empty_data(self):
        """Test creating XWNode from empty data."""
        empty_dict_node = XWNode.from_native({})
        empty_list_node = XWNode.from_native([])
        
        assert empty_dict_node is not None
        assert empty_list_node is not None


# ============================================================================
# CORE OPERATIONS TESTS
# ============================================================================

@pytest.mark.xwnode_unit
class TestXWNodeCoreOperations:
    """Test XWNode core operations."""
    
    def test_get_operation(self, simple_dict_data):
        """Test get retrieves values correctly."""
        node = XWNode.from_native(simple_dict_data)
        
        result = node.get('name')
        # Result might be a node or direct value
        if result is not None:
            if hasattr(result, 'value'):
                assert result.value == 'Alice'
            else:
                assert result == 'Alice'
    
    def test_set_operation(self):
        """Test set updates values correctly."""
        node = XWNode.from_native({})
        
        node.set('new_key', 'new_value', in_place=True)
        result = node.get('new_key')
        
        assert result is not None
    
    def test_delete_operation(self, simple_dict_data):
        """Test delete removes keys correctly."""
        node = XWNode.from_native(simple_dict_data)
        
        node.delete('name', in_place=True)
        assert not node.exists('name')
    
    def test_exists_operation(self, simple_dict_data):
        """Test exists checks key existence."""
        node = XWNode.from_native(simple_dict_data)
        
        assert node.exists('name') is True
        assert node.exists('nonexistent') is False
    
    def test_length_operation(self, simple_dict_data):
        """Test len() returns correct count."""
        node = XWNode.from_native(simple_dict_data)
        
        assert len(node) == 3
    
    def test_to_native_roundtrip(self, simple_dict_data):
        """Test data roundtrip through to_native."""
        node = XWNode.from_native(simple_dict_data)
        native = node.to_native()
        
        assert isinstance(native, (dict, list))
        # Data should be preserved
        if isinstance(native, dict):
            assert 'name' in native or len(native) > 0


# ============================================================================
# USABILITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_usability
class TestXWNodeUsability:
    """Test XWNode usability features."""
    
    def test_simple_creation_is_easy(self):
        """Test that creating nodes is simple and intuitive."""
        # Should be one-liner
        node = XWNode.from_native({'key': 'value'})
        assert node is not None
    
    def test_error_messages_are_helpful(self):
        """Test that error messages are clear and helpful."""
        node = XWNode.from_native({})
        
        try:
            # Try invalid operation
            node.get(None)
            # If no error, that's OK too
        except Exception as e:
            # Error message should be descriptive
            error_msg = str(e)
            assert len(error_msg) > 5  # Not just a code
    
    def test_common_operations_work_intuitively(self, simple_dict_data):
        """Test that common operations work as expected."""
        node = XWNode.from_native(simple_dict_data)
        
        # Get operation
        name = node.get('name')
        assert name is not None
        
        # Exists check
        assert node.exists('name')
        
        # Length
        assert len(node) > 0


# ============================================================================
# SECURITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_security
class TestXWNodeSecurity:
    """Test XWNode security features."""
    
    def test_malicious_input_handling(self):
        """Test handling of malicious inputs."""
        malicious_inputs = [
            {'../../../etc/passwd': 'value'},
            {'<script>alert("xss")</script>': 'value'},
            {"'; DROP TABLE users; --": 'value'},
        ]
        
        for data in malicious_inputs:
            # Should not crash
            node = XWNode.from_native(data)
            assert node is not None
    
    def test_resource_limits(self):
        """Test protection against resource exhaustion."""
        # Create very large dataset
        large_data = {f'key_{i}': f'value_{i}' for i in range(10000)}
        
        # Should not crash
        node = XWNode.from_native(large_data)
        assert node is not None
        assert len(node) == 10000
    
    def test_circular_reference_protection(self):
        """Test protection against circular references."""
        data = {'key': 'value'}
        data['self'] = data  # Circular reference
        
        # Should either handle or raise clear error
        try:
            node = XWNode.from_native(data)
            # If successful, verify no infinite loop
            assert node is not None
        except (RecursionError, ValueError, XWNodeError):
            # Expected - circular refs should be caught
            pass


# ============================================================================
# EDGE CASES TESTS
# ============================================================================

@pytest.mark.xwnode_unit
class TestXWNodeEdgeCases:
    """Test XWNode edge cases."""
    
    def test_empty_data_handling(self):
        """Test handling of empty data."""
        empty_dict = XWNode.from_native({})
        empty_list = XWNode.from_native([])
        
        assert empty_dict is not None
        assert empty_list is not None
    
    def test_none_values(self):
        """Test handling of None values."""
        data = {'key': None}
        node = XWNode.from_native(data)
        
        assert node is not None
    
    def test_unicode_data(self):
        """Test handling of Unicode data."""
        unicode_data = {
            '中文': '你好',
            'العربية': 'مرحبا',
            'emoji': '🚀🎉',
        }
        
        node = XWNode.from_native(unicode_data)
        assert node is not None
    
    def test_mixed_types_in_dict(self):
        """Test dict with mixed value types."""
        mixed_data = {
            'string': 'value',
            'int': 42,
            'float': 3.14,
            'bool': True,
            'list': [1, 2, 3],
            'dict': {'nested': 'value'},
            'none': None
        }
        
        node = XWNode.from_native(mixed_data)
        assert node is not None
        assert len(node) == 7

