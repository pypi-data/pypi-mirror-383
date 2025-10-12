#!/usr/bin/env python3
"""Generate and display coverage summary."""

from pathlib import Path
import sys


def run_coverage():
    """Run coverage and display summary."""
    print("Generating coverage summary...")

    # Check if coverage.xml exists
    coverage_file = Path("coverage.xml")
    if not coverage_file.exists():
        print("Warning: coverage.xml not found, coverage may not have run")

    # Import coverage to avoid subprocess security warnings
    try:
        import coverage

        # Load and report coverage data
        cov = coverage.Coverage()
        cov.load()

        print("Coverage Report:")
        print("=" * 50)

        # Generate the report directly
        cov.report(show_missing=True)

        # Generate XML for CI systems
        cov.xml_report()
        print("Coverage XML generated for CI")

    except ImportError:
        print("Error: Coverage module not available for direct import")
        return False
    except Exception as e:
        print(f"Error: Coverage processing failed: {e}")
        return False

    return True


if __name__ == "__main__":
    success = run_coverage()
    if not success:
        sys.exit(1)
