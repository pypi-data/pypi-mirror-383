#!/usr/bin/env python3
"""
Test runner for xwquery.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 11, 2025
"""

import sys
import pytest
from pathlib import Path

def main():
    """Run tests with pytest."""
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src"))
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    # Build pytest arguments
    pytest_args = [
        str(project_root / "tests"),
        "-v",
        "--tb=short",
    ]
    
    # Add specific test types if requested
    if "--core" in args:
        pytest_args.append(str(project_root / "tests" / "core"))
        args.remove("--core")
    elif "--unit" in args:
        pytest_args.append(str(project_root / "tests" / "unit"))
        args.remove("--unit")
    elif "--integration" in args:
        pytest_args.append(str(project_root / "tests" / "integration"))
        args.remove("--integration")
    
    # Add remaining arguments
    pytest_args.extend(args)
    
    # Run pytest
    exit_code = pytest.main(pytest_args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

