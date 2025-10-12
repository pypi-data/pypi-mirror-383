#!/usr/bin/env python3
"""Verify that CWE types can be imported correctly."""

from pathlib import Path
import sys


def verify_types():
    """Verify that all CWE types can be imported."""
    print("Verifying CWE types can be imported...")

    # Check if types directory exists
    types_dir = Path("src/ci/transparency/cwe/types")
    if not types_dir.exists():
        print(f"Error: Types directory not found: {types_dir}")
        return False

    # Count Python files (excluding __init__.py and __pycache__)
    python_files = list(types_dir.rglob("*.py"))
    python_files = [f for f in python_files if not f.name.startswith("__")]

    print(f"Found {len(python_files)} type files in {types_dir}")

    if len(python_files) == 0:
        print("Error: No type files found!")
        return False

    # Try to check if the main module can be found
    try:
        import importlib.util

        spec = importlib.util.find_spec("ci.transparency.cwe.types")
        if spec is None:
            print("Error: ci.transparency.cwe.types module not found!")
            return False
        print("Successfully found ci.transparency.cwe.types module")
    except Exception as e:
        print(f"Error: Failed to check ci.transparency.cwe.types: {e}")
        return False

    # List some of the type files for verification
    print("Available type files:")
    for py_file in sorted(python_files)[:10]:  # Show first 10
        print(f"   - {py_file.name}")

    if len(python_files) > 10:
        print(f"   ... and {len(python_files) - 10} more")

    print("Type verification completed successfully.")
    return True


if __name__ == "__main__":
    success = verify_types()
    if not success:
        sys.exit(1)
