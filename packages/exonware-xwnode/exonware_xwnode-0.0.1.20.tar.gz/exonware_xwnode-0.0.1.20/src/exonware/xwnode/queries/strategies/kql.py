#!/usr/bin/env python3
"""
KQL Query Strategy

This module implements the KQL query strategy for Kusto Query Language operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.20
Generation Date: January 2, 2025
"""

from typing import Any, Dict, List, Optional
from .base import AStructuredQueryStrategy
from ...errors import XWNodeValueError
from ...contracts import QueryMode, QueryTrait


class KQLStrategy(AStructuredQueryStrategy):
    """KQL query strategy for Kusto Query Language operations."""
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.KQL
        self._traits = QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL | QueryTrait.BATCH
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute KQL query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid KQL query: {query}")
        return {"result": "KQL query executed", "query": query}
    
    def validate_query(self, query: str) -> bool:
        """Validate KQL query syntax."""
        if not query or not isinstance(query, str):
            return False
        return any(op in query.upper() for op in ["TABLE", "WHERE", "PROJECT", "SUMMARIZE", "JOIN"])
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get KQL query execution plan."""
        return {
            "query_type": "KQL",
            "complexity": "MEDIUM",
            "estimated_cost": 90
        }
    
    def select_query(self, table: str, columns: List[str], where_clause: str = None) -> Any:
        """Execute SELECT query."""
        return self.execute(f"{table} | project {', '.join(columns)}")
    
    def insert_query(self, table: str, data: Dict[str, Any]) -> Any:
        """Execute INSERT query."""
        return self.execute(f"INSERT INTO {table} VALUES {data}")
    
    def update_query(self, table: str, data: Dict[str, Any], where_clause: str = None) -> Any:
        """Execute UPDATE query."""
        return self.execute(f"UPDATE {table} SET {data}")
    
    def delete_query(self, table: str, where_clause: str = None) -> Any:
        """Execute DELETE query."""
        return self.execute(f"DELETE FROM {table}")
    
    def join_query(self, tables: List[str], join_conditions: List[str]) -> Any:
        """Execute JOIN query."""
        return self.execute(f"{tables[0]} | join {tables[1]}")
    
    def aggregate_query(self, table: str, functions: List[str], group_by: List[str] = None) -> Any:
        """Execute aggregate query."""
        return self.execute(f"{table} | summarize {', '.join(functions)}")
