#!/usr/bin/env python3
"""
xwquery - Universal Query Language for Python

This module provides the main public API for the xwquery library,
implementing a universal query language that works across all data structures.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.4
Generation Date: October 11, 2025
"""

from .version import __version__, get_version, get_version_info

# Core query components
from .strategies.xwquery import XWQueryScriptStrategy
from .executors.engine import ExecutionEngine
from .executors.contracts import (
    Action,
    ExecutionContext,
    ExecutionResult,
    IOperationExecutor
)
from .executors.registry import get_operation_registry, register_operation
from .executors.capability_checker import check_operation_compatibility

# Query strategies (format converters)
from .strategies.sql import SQLStrategy
from .strategies.graphql import GraphQLStrategy
from .strategies.cypher import CypherStrategy
from .strategies.sparql import SPARQLStrategy

# Parsers
from .parsers.sql_param_extractor import SQLParamExtractor


class XWQuery:
    """
    Main facade for XWQuery - Universal Query Language for Python.
    
    This class provides a clean, simple API for querying any data structure
    with SQL-like syntax and converting between multiple query formats.
    """
    
    def __init__(self):
        """Initialize XWQuery with execution engine."""
        self._engine = ExecutionEngine()
        self._parser = XWQueryScriptStrategy()
    
    @staticmethod
    def execute(query: str, data: any, **kwargs) -> ExecutionResult:
        """
        Execute a query on data.
        
        Args:
            query: XWQuery script string
            data: Target data to query (can be node, dict, list, etc.)
            **kwargs: Additional execution options
            
        Returns:
            ExecutionResult with query results
            
        Example:
            >>> data = {'users': [{'name': 'Alice', 'age': 30}]}
            >>> result = XWQuery.execute("SELECT * FROM users WHERE age > 25", data)
            >>> print(result.data)
        """
        from exonware.xwnode import XWNode
        
        # Convert data to node if needed
        if not hasattr(data, '_strategy'):
            node = XWNode.from_native(data)
        else:
            node = data
        
        # Execute query
        engine = ExecutionEngine()
        return engine.execute(query, node, **kwargs)
    
    @staticmethod
    def parse(query: str, source_format: str = 'xwquery') -> XWQueryScriptStrategy:
        """
        Parse a query string into actions tree.
        
        Args:
            query: Query string
            source_format: Query format ('xwquery', 'sql', 'graphql', etc.)
            
        Returns:
            XWQueryScriptStrategy with parsed actions tree
            
        Example:
            >>> parsed = XWQuery.parse("SELECT * FROM users")
            >>> actions_tree = parsed.get_actions_tree()
        """
        parser = XWQueryScriptStrategy()
        
        if source_format.lower() == 'xwquery':
            return parser.parse_script(query)
        else:
            return parser.from_format(query, source_format)
    
    @staticmethod
    def convert(query: str, from_format: str = 'sql', to_format: str = 'xwquery') -> str:
        """
        Convert query from one format to another.
        
        Args:
            query: Query string
            from_format: Source format ('sql', 'graphql', 'cypher', etc.)
            to_format: Target format ('xwquery', 'mongodb', 'sparql', etc.)
            
        Returns:
            Converted query string
            
        Example:
            >>> sql = "SELECT * FROM users WHERE age > 25"
            >>> graphql = XWQuery.convert(sql, from_format='sql', to_format='graphql')
        """
        # Parse to intermediate representation
        parser = XWQueryScriptStrategy()
        parsed = parser.from_format(query, from_format)
        
        # Convert to target format
        if to_format.lower() == 'xwquery':
            # Return XWQuery script
            return parsed.to_format('xwquery')
        else:
            return parsed.to_format(to_format)
    
    @staticmethod
    def validate(query: str, format: str = 'xwquery') -> bool:
        """
        Validate query syntax.
        
        Args:
            query: Query string
            format: Query format ('xwquery', 'sql', etc.)
            
        Returns:
            True if valid, False otherwise
            
        Example:
            >>> XWQuery.validate("SELECT * FROM users")
            True
        """
        try:
            parser = XWQueryScriptStrategy()
            if format.lower() == 'xwquery':
                return parser.validate_query(query)
            else:
                # Try to parse from format
                parser.from_format(query, format)
                return True
        except Exception:
            return False
    
    @staticmethod
    def get_supported_formats() -> list:
        """
        Get list of supported query formats.
        
        Returns:
            List of supported format names
            
        Example:
            >>> formats = XWQuery.get_supported_formats()
            >>> print(formats)
            ['xwquery', 'sql', 'graphql', 'cypher', 'sparql', ...]
        """
        return [
            'xwquery', 'sql', 'graphql', 'cypher', 'sparql', 'gremlin',
            'mongodb', 'cql', 'n1ql', 'elasticsearch', 'promql', 'flux',
            'logql', 'kql', 'jq', 'jmespath', 'jsoniq', 'xpath', 'xquery',
            'datalog', 'linq', 'hiveql', 'pig', 'partiql', 'gql'
        ]
    
    @staticmethod
    def get_supported_operations() -> list:
        """
        Get list of supported operations.
        
        Returns:
            List of operation names
            
        Example:
            >>> operations = XWQuery.get_supported_operations()
            >>> print(operations)
            ['SELECT', 'INSERT', 'UPDATE', 'DELETE', ...]
        """
        parser = XWQueryScriptStrategy()
        return parser.get_supported_operations()
    
    @staticmethod
    def get_operation_registry():
        """Get the global operation registry."""
        return get_operation_registry()


# Convenience functions
def execute(query: str, data: any, **kwargs) -> ExecutionResult:
    """Execute query on data - convenience function."""
    return XWQuery.execute(query, data, **kwargs)


def parse(query: str, source_format: str = 'xwquery') -> XWQueryScriptStrategy:
    """Parse query string - convenience function."""
    return XWQuery.parse(query, source_format)


def convert(query: str, from_format: str = 'sql', to_format: str = 'xwquery') -> str:
    """Convert query between formats - convenience function."""
    return XWQuery.convert(query, from_format, to_format)


def validate(query: str, format: str = 'xwquery') -> bool:
    """Validate query syntax - convenience function."""
    return XWQuery.validate(query, format)


__all__ = [
    # Version
    '__version__',
    'get_version',
    'get_version_info',
    
    # Main facade
    'XWQuery',
    
    # Convenience functions
    'execute',
    'parse',
    'convert',
    'validate',
    
    # Core components
    'XWQueryScriptStrategy',
    'ExecutionEngine',
    'Action',
    'ExecutionContext',
    'ExecutionResult',
    'IOperationExecutor',
    
    # Registry
    'get_operation_registry',
    'register_operation',
    'check_operation_compatibility',
    
    # Query strategies
    'SQLStrategy',
    'GraphQLStrategy',
    'CypherStrategy',
    'SPARQLStrategy',
    
    # Parsers
    'SQLParamExtractor',
]

