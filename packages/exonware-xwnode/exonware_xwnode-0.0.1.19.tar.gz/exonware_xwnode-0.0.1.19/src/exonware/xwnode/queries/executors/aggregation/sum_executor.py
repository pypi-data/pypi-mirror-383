#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/aggregation/sum_executor.py

SUM Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.19
Generation Date: 09-Oct-2025
"""

from typing import Any, Dict, List
from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..defs import OperationType

class SumExecutor(AUniversalOperationExecutor):
    """
    SUM operation executor.
    
    Computes sum of numeric values
    
    Capability: Universal
    Operation Type: AGGREGATION
    """
    
    OPERATION_NAME = "SUM"
    OPERATION_TYPE = OperationType.AGGREGATION
    SUPPORTED_NODE_TYPES = []  # Universal
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute SUM operation."""
        params = action.params
        node = context.node
        
        result_data = self._execute_sum(node, params, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'operation': self.OPERATION_NAME}
        )
    
    def _execute_sum(self, node: Any, params: Dict, context: ExecutionContext) -> Dict:
        """Execute sum logic."""
        # Implementation here
        return {'result': 'SUM executed', 'params': params}
