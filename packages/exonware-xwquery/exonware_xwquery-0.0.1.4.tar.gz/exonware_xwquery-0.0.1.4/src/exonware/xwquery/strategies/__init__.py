"""
Query Strategies Package

This package contains all query strategy implementations organized by type:
- Linear queries (index-based, value-based)
- Tree queries (key-based, range queries)
- Graph queries (path queries, neighbor queries)

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.4
Generation Date: January 2, 2025
"""

from .base import AQueryStrategy
from .xwquery import XWQueryScriptStrategy
from .xwnode_executor import XWNodeQueryActionExecutor

__all__ = [
    'AQueryStrategy',
    'XWQueryScriptStrategy',
    'XWNodeQueryActionExecutor'
]
