"""
#exonware/xwnode/src/exonware/xwnode/common/graph/errors.py

Graph-specific error classes.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
Generation Date: 11-Oct-2025
"""

from ...errors import XWNodeError


class XWGraphError(XWNodeError):
    """Base error for graph operations."""
    pass


class XWGraphSecurityError(XWGraphError):
    """Security violation in graph operations."""
    pass


class XWGraphEntityNotFoundError(XWGraphError):
    """Entity not found in graph."""
    pass


class XWGraphRelationshipNotFoundError(XWGraphError):
    """Relationship not found in graph."""
    pass


class XWGraphCycleDetectedError(XWGraphError):
    """Cycle detected in graph traversal."""
    pass


class XWGraphInvalidOperationError(XWGraphError):
    """Invalid graph operation."""
    pass

