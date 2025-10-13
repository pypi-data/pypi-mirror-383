"""
#exonware/xwnode/tests/3.advance/conftest.py

Advance test fixtures - Production excellence validation.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest


@pytest.fixture
def advance_test_data():
    """Comprehensive test data for advance tests."""
    return {
        'security': {
            'malicious_inputs': [
                '../../../etc/passwd',
                '<script>alert("XSS")</script>',
                "' OR '1'='1",
                'null\x00byte'
            ]
        },
        'performance': {
            'large_dataset_size': 100000,
            'benchmark_iterations': 1000
        },
        'usability': {
            'common_use_cases': [
                'create_from_dict',
                'navigate_nested_path',
                'convert_to_native'
            ]
        }
    }

