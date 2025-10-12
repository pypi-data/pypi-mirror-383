#!/usr/bin/env python3
"""
Basic XWQuery tests.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 11, 2025
"""

import pytest
from exonware.xwquery import XWQuery, execute, parse, convert, validate


class TestXWQueryBasic:
    """Basic XWQuery functionality tests."""
    
    def test_import(self):
        """Test that XWQuery can be imported."""
        assert XWQuery is not None
    
    def test_validate_valid_query(self):
        """Test validating a valid query."""
        query = "SELECT * FROM users WHERE age > 25"
        assert validate(query) == True
    
    def test_validate_invalid_query(self):
        """Test validating an invalid query."""
        query = "INVALID QUERY SYNTAX"
        assert validate(query) == False
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = XWQuery.get_supported_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0
        assert 'sql' in formats
        assert 'graphql' in formats
        assert 'xwquery' in formats
    
    def test_get_supported_operations(self):
        """Test getting supported operations."""
        operations = XWQuery.get_supported_operations()
        assert isinstance(operations, list)
        assert len(operations) > 0
        assert 'SELECT' in operations
        assert 'INSERT' in operations
        assert 'UPDATE' in operations
        assert 'DELETE' in operations
    
    def test_parse_query(self):
        """Test parsing a query."""
        query = "SELECT * FROM users"
        parsed = parse(query)
        assert parsed is not None
        assert hasattr(parsed, 'get_actions_tree')


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_execute_function(self):
        """Test execute convenience function."""
        assert callable(execute)
    
    def test_parse_function(self):
        """Test parse convenience function."""
        assert callable(parse)
    
    def test_convert_function(self):
        """Test convert convenience function."""
        assert callable(convert)
    
    def test_validate_function(self):
        """Test validate convenience function."""
        assert callable(validate)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

