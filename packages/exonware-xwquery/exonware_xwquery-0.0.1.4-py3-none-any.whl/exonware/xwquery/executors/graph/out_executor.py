#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/graph/out_executor.py

OUT Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.4
Generation Date: 09-Oct-2025
"""

from typing import Any, Dict, List
from ..base import AOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..defs import OperationType
from ....nodes.strategies.contracts import NodeType

class OutExecutor(AOperationExecutor):
    """
    OUT operation executor.
    
    Outbound graph traversal
    
    Capability: GRAPH, TREE, HYBRID only
    Operation Type: GRAPH
    """
    
    OPERATION_NAME = "OUT"
    OPERATION_TYPE = OperationType.GRAPH
    SUPPORTED_NODE_TYPES = [NodeType.GRAPH, NodeType.TREE, NodeType.HYBRID]
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute OUT operation."""
        params = action.params
        node = context.node
        
        result_data = self._execute_out(node, params, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'operation': self.OPERATION_NAME}
        )
    
    def _execute_out(self, node: Any, params: Dict, context: ExecutionContext) -> Dict:
        """Execute out logic."""
        # Implementation here
        return {'result': 'OUT executed', 'params': params}
