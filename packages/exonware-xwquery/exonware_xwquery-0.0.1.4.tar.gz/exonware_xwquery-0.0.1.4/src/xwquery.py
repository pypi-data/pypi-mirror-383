"""
Convenience module for importing xwquery.

This module provides a convenience import path: `import xwquery`
Instead of the full path: `from exonware.xwquery import *`

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.4
Generation Date: October 11, 2025
"""

# Import everything from the main package
from exonware.xwquery import *  # noqa: F401, F403

# Expose version for easy access
from exonware.xwquery.version import __version__

__all__ = ['__version__']

