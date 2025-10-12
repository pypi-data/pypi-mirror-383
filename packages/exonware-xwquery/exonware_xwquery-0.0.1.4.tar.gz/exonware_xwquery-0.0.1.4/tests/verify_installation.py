#!/usr/bin/env python3
"""
Verify xwquery installation.

This script verifies that xwquery is properly installed and can be imported.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 11, 2025
"""

import sys
from pathlib import Path

# Add src to path for development testing
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def verify_installation():
    """Verify xwquery installation."""
    print("Verifying xwquery installation...\n")
    
    try:
        # Test import from exonware.xwquery
        from exonware.xwquery import (
            __version__,
            XWQuery,
            execute,
            parse,
            convert,
            validate
        )
        print(f"SUCCESS: Imported exonware.xwquery v{__version__}")
        
        # Test convenience import
        import xwquery
        print(f"SUCCESS: Imported xwquery convenience module v{xwquery.__version__}")
        
        # Test basic functionality
        print("\nTesting basic functionality...")
        
        # Test validation
        is_valid = XWQuery.validate("SELECT * FROM users")
        print(f"  Validation: {'PASS' if is_valid else 'FAIL'}")
        
        # Test supported formats
        formats = XWQuery.get_supported_formats()
        print(f"  Supported formats: {len(formats)} formats")
        
        # Test supported operations
        operations = XWQuery.get_supported_operations()
        print(f"  Supported operations: {len(operations)} operations")
        
        print("\n" + "="*50)
        print("SUCCESS! xwquery is ready to use!")
        print("="*50)
        print(f"\nVersion: {__version__}")
        print(f"Package: exonware-xwquery")
        print(f"Import: from exonware.xwquery import *")
        print(f"Alias: import xwquery")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to verify installation")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)

