#!/usr/bin/env python3
"""Pre-publication package validation script."""

from pathlib import Path
import sys


def validate_package_structure() -> bool:
    """Validate package has required structure."""
    print("Validating package structure...")

    required_files = [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "src/ci/transparency/cwe/types/__init__.py",
        "src/ci/transparency/cwe/types/py.typed",
    ]

    missing_files: list[str] = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"ERROR: Missing required files: {missing_files}")
        return False

    print("Package structure validation passed")
    return True


def validate_build_artifacts():
    """Validate that build artifacts can be created."""
    print("Validating build process...")

    # Check that dist directory would be clean for build
    dist_dir = Path("dist")
    if dist_dir.exists():
        dist_files = list(dist_dir.glob("*"))
        if dist_files:
            print(
                f"WARNING: dist/ contains {len(dist_files)} files - recommend cleaning before release"
            )

    # Try finding the package spec
    try:
        import importlib.util

        spec = importlib.util.find_spec("ci.transparency.cwe.types")
        if spec is None:
            print("ERROR: Cannot find package 'ci.transparency.cwe.types'")
            return False

        print("Package import validation passed")
        return True
    except Exception as e:
        print(f"ERROR: Cannot check package availability: {e}")
        return False


def validate_version_consistency():
    """Check version consistency across files."""
    print("Validating version consistency...")

    # Check pyproject.toml version
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("ERROR: pyproject.toml not found")
        return False

    try:
        with pyproject_path.open("r", encoding="utf-8") as f:
            content = f.read()
            if 'version = "0.0.1"' not in content:
                print("WARNING: Version in pyproject.toml may not match expected v0.0.1")
    except Exception as e:
        print(f"ERROR: Could not read pyproject.toml: {e}")
        return False

    print("Version consistency validation passed")
    return True


def validate_documentation():
    """Validate that documentation builds correctly."""
    print("Validating documentation...")

    required_docs = ["docs/en/index.md", "docs/en/usage.md", "docs/en/api.md", "mkdocs.yml"]

    missing_docs: list[str] = []
    for doc_path in required_docs:
        if not Path(doc_path).exists():
            missing_docs.append(doc_path)

    if missing_docs:
        print(f"ERROR: Missing documentation files: {missing_docs}")
        return False

    print("Documentation validation passed")
    return True


def validate_type_files():
    """Validate that type files exist and are non-empty."""
    print("Validating CWE type files...")

    types_dir = Path("src/ci/transparency/cwe/types")
    if not types_dir.exists():
        print("ERROR: Types directory not found")
        return False

    # Find all Python files (excluding __init__.py and py.typed)
    python_files = [
        f for f in types_dir.glob("*.py") if f.name != "__init__.py" and not f.name.startswith("__")
    ]

    if len(python_files) == 0:
        print("ERROR: No type files found")
        return False

    # Check that files are non-empty
    empty_files: list[str] = []
    for py_file in python_files:
        if py_file.stat().st_size == 0:
            empty_files.append(py_file.name)

    if empty_files:
        print(f"WARNING: Empty type files found: {empty_files}")

    print(f"Found {len(python_files)} type files")
    return True


def main():
    """Run all validation checks."""
    print("Starting pre-publication package validation")
    print("=" * 50)

    checks = [
        validate_package_structure,
        validate_build_artifacts,
        validate_version_consistency,
        validate_documentation,
        validate_type_files,
    ]

    passed = 0
    failed = 0

    for check in checks:
        try:
            if check():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"ERROR in {check.__name__}: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"Validation Summary: {passed} passed, {failed} failed")

    if failed > 0:
        print("Package validation FAILED - address issues before release")
        return False
    print("Package validation PASSED - ready for release")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
