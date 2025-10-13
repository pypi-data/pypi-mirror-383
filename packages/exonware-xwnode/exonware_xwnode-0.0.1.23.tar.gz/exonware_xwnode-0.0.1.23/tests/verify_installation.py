#!/usr/bin/env python3
"""
#exonware/xwnode/tests/verify_installation.py

Installation verification script for xwnode

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025

Usage:
    python tests/verify_installation.py
"""

import sys
from pathlib import Path


def verify_import():
    """Verify that xwnode can be imported."""
    print("Verifying imports...")
    
    try:
        # Test main import
        import exonware.xwnode
        print("  exonware.xwnode imported successfully")
        
        # Test convenience import  
        import xwnode
        print("  xwnode convenience import works")
        
        # Test version information
        assert hasattr(exonware.xwnode, '__version__')
        assert hasattr(exonware.xwnode, '__author__')
        assert hasattr(exonware.xwnode, '__email__')
        assert hasattr(exonware.xwnode, '__company__')
        print(f"  Version: {exonware.xwnode.__version__}")
        
        return True
    except ImportError as e:
        print(f"  Import Error: {e}")
        return False


def verify_basic_functionality():
    """Verify basic xwnode functionality."""
    print("\nVerifying basic functionality...")
    
    try:
        from exonware.xwnode import XWNode
        
        # Test creating node from dict
        node = XWNode.from_native({'key1': 'value1', 'key2': 'value2'})
        assert node is not None
        print("  Node creation from dict works")
        
        # Test to_native conversion
        data = node.to_native()
        assert data == {'key1': 'value1', 'key2': 'value2'}
        print("  to_native() conversion works")
        
        # Test basic operations
        assert len(node) == 2
        print("  Basic operations work")
        
        return True
    except Exception as e:
        print(f"  Functionality Error: {e}")
        return False


def verify_dependencies():
    """Verify that required dependencies are installed."""
    print("\nVerifying dependencies...")
    
    try:
        # Check for pytest (development dependency)
        import pytest
        print(f"  pytest {pytest.__version__} installed")
        
        # Add other dependency checks as needed
        return True
    except ImportError as e:
        print(f"  Optional dependency not available: {e}")
        return True  # Dependencies are optional for basic usage


def verify_installation():
    """Verify that the library is properly installed and working."""
    print("Verifying xwnode installation...")
    print("=" * 60)
    
    # Add src to Python path for testing
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Run all verification checks
    import_ok = verify_import()
    functionality_ok = verify_basic_functionality()
    dependencies_ok = verify_dependencies()
    
    print("\n" + "=" * 60)
    
    if import_ok and functionality_ok and dependencies_ok:
        print("SUCCESS! exonware.xwnode is ready to use!")
        print("You have access to all xwnode features!")
        return True
    else:
        print("FAILED! Some verification checks did not pass.")
        print("Make sure you've installed the package: pip install exonware-xwnode")
        return False


def main():
    """Main verification function."""
    success = verify_installation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
