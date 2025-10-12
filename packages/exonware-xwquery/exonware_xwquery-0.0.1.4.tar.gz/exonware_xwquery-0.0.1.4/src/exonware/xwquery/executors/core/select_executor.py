#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/core/select_executor.py

SELECT Operation Executor

Implements SELECT operation execution on all node types.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.4
Generation Date: 08-Oct-2025
"""

from typing import Any, List, Dict, Optional
from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..defs import OperationCapability
from ....nodes.strategies.contracts import NodeType


class SelectExecutor(AUniversalOperationExecutor):
    """
    SELECT operation executor - Universal operation.
    
    Works on all node types (LINEAR, TREE, GRAPH, MATRIX).
    Retrieves and projects data from nodes.
    """
    
    OPERATION_NAME = "SELECT"
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """
        Execute SELECT operation.
        
        Supports:
        - Column projection
        - Star (*) selection
        - Expressions and aliases
        - Adapts to different node types
        """
        # Extract parameters
        fields = action.params.get('fields', ['*'])
        columns = action.params.get('columns', fields)  # Support both
        table_name = action.params.get('from') or action.params.get('path')
        
        # Get the actual data source
        if table_name:
            # Get data from node at the specified path
            source = context.node.get(table_name) if hasattr(context.node, 'get') else context.node
        else:
            source = context.node
        
        # Get WHERE condition to apply BEFORE column projection
        where_condition = action.params.get('where')
        
        # Get node type
        node_type = self._get_node_type(context.node)
        
        # Route to appropriate handler based on node type
        # Pass where_condition to apply filtering before projection
        if node_type == NodeType.LINEAR:
            data = self._select_from_linear(source, columns, context, where_condition)
        elif node_type == NodeType.TREE:
            data = self._select_from_tree(source, columns, context, where_condition)
        elif node_type == NodeType.GRAPH:
            data = self._select_from_graph(source, columns, context, where_condition)
        elif node_type == NodeType.MATRIX:
            data = self._select_from_matrix(source, columns, context, where_condition)
        else:  # HYBRID
            data = self._select_from_tree(source, columns, context, where_condition)  # Default to tree
        
        return ExecutionResult(
            data=data,
            affected_count=len(data) if isinstance(data, list) else 1
        )
    
    def _get_node_type(self, node: Any) -> NodeType:
        """Get node's strategy type."""
        if hasattr(node, '_strategy') and hasattr(node._strategy, 'STRATEGY_TYPE'):
            return node._strategy.STRATEGY_TYPE
        elif hasattr(node, 'STRATEGY_TYPE'):
            return node.STRATEGY_TYPE
        return NodeType.TREE  # Default
    
    def _select_from_linear(self, source: Any, columns: List[str], context: ExecutionContext, where_condition: Optional[Dict] = None) -> List[Dict]:
        """Select from linear node (list-like)."""
        results = []
        
        # Iterate through linear structure
        if hasattr(source, 'items'):
            for key, value in source.items():
                row_dict = {'key': key, 'value': value} if not isinstance(value, dict) else value
                
                # Apply WHERE filter first
                if where_condition and not self._matches_condition(row_dict, where_condition):
                    continue
                
                if columns == ['*']:
                    results.append(row_dict)
                else:
                    row = self._project_columns(row_dict, columns)
                    if row is not None:
                        results.append(row)
        
        return results
    
    def _select_from_tree(self, source: Any, columns: List[str], context: ExecutionContext, where_condition: Optional[Dict] = None) -> List[Dict]:
        """Select from tree node (key-value map)."""
        results = []
        
        # Handle list of records (most common case)
        if isinstance(source, list):
            for item in source:
                if isinstance(item, dict):
                    # Apply WHERE filter FIRST (before column projection)
                    if where_condition and not self._matches_condition(item, where_condition):
                        continue
                    
                    # Then project columns
                    if columns == ['*'] or columns == [' *'] or '*' in columns:
                        results.append(item)
                    else:
                        row = self._project_columns(item, columns)
                        if row is not None:
                            results.append(row)
                else:
                    results.append({'value': item})
        
        # Handle tree structure (dict)
        elif hasattr(source, 'items'):
            for key, value in source.items():
                if columns == ['*']:
                    results.append({'key': key, 'value': value})
                else:
                    row = self._project_columns(value, columns)
                    if row is not None:
                        results.append(row)
        
        return results
    
    def _select_from_graph(self, source: Any, columns: List[str], context: ExecutionContext, where_condition: Optional[Dict] = None) -> List[Dict]:
        """Select from graph node."""
        # For graphs, return nodes
        results = []
        
        if hasattr(source, 'items'):
            for key, value in source.items():
                row_dict = {'node_id': key, 'node_data': value}
                
                # Apply WHERE filter first
                if where_condition and not self._matches_condition(row_dict, where_condition):
                    continue
                
                if columns == ['*']:
                    results.append(row_dict)
                else:
                    row = self._project_columns(value, columns)
                    if row is not None:
                        row['node_id'] = key
                        results.append(row)
        
        return results
    
    def _select_from_matrix(self, source: Any, columns: List[str], context: ExecutionContext, where_condition: Optional[Dict] = None) -> List[Dict]:
        """Select from matrix node."""
        results = []
        
        # Iterate through matrix
        if hasattr(source, 'items'):
            for key, value in source.items():
                row_dict = {'position': key, 'value': value} if not isinstance(value, dict) else value
                
                # Apply WHERE filter first
                if where_condition and not self._matches_condition(row_dict, where_condition):
                    continue
                
                if columns == ['*']:
                    results.append(row_dict)
                else:
                    row = self._project_columns(row_dict, columns)
                    if row is not None:
                        results.append(row)
        
        return results
    
    def _project_columns(self, value: Any, columns: List[str]) -> Optional[Dict]:
        """Project specific columns from a value."""
        if not isinstance(value, dict):
            return {'value': value}
        
        projected = {}
        for col in columns:
            if col in value:
                projected[col] = value[col]
        
        return projected if projected else None
    
    def _matches_condition(self, row: Dict, condition: Dict[str, Any]) -> bool:
        """Check if a single row matches a WHERE condition."""
        if not condition or not isinstance(row, dict):
            return True
        
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        if not field or not operator:
            return True
        
        row_value = row.get(field)
        if row_value is None:
            return False
        
        # Apply operator
        try:
            if operator == '>':
                return row_value > value
            elif operator == '<':
                return row_value < value
            elif operator == '>=':
                return row_value >= value
            elif operator == '<=':
                return row_value <= value
            elif operator == '=' or operator == '==':
                return row_value == value
            elif operator == '!=' or operator == '<>':
                return row_value != value
            elif operator == 'LIKE':
                return str(value).lower() in str(row_value).lower()
            elif operator == 'IN':
                return row_value in value
        except (TypeError, AttributeError):
            return False
        
        return False
    
    def _apply_where_filter(self, data: List[Dict], condition: Dict[str, Any]) -> List[Dict]:
        """Apply WHERE filter to data (legacy, prefer filtering in select methods)."""
        if not condition:
            return data
        
        return [row for row in data if self._matches_condition(row, condition)]


__all__ = ['SelectExecutor']
