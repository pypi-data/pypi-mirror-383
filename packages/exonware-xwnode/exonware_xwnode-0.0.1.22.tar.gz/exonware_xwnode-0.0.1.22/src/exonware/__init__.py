"""
exonware package - Enterprise-grade Python framework ecosystem

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.22
Generation Date: 2025-01-03

This is a namespace package allowing multiple exonware subpackages
to coexist (xwsystem, xwnode, xwdata, etc.)
"""

# Make this a namespace package - DO NOT set __path__
# This allows both exonware.xwsystem and exonware.xwnode to coexist
__path__ = __import__('pkgutil').extend_path(__path__, __name__)

__version__ = '0.0.1'
__author__ = 'Eng. Muhammad AlShehri'
__email__ = 'connect@exonware.com'
__company__ = 'eXonware.com'
