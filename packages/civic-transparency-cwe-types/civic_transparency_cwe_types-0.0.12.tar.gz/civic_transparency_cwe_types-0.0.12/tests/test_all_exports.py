# tests/test_all_exports.py
# pyright: strict

"""Test that __all__ exports are complete and accurate in all modules."""

import importlib
import inspect
from pathlib import Path
from typing import Any

import pytest


def _get_package_root() -> Path:
    """Get the package root directory."""
    return Path(__file__).parent.parent / "src" / "ci" / "transparency" / "cwe" / "types"


def _get_all_modules() -> list[str]:
    """Find all Python modules in the package (excluding __init__.py)."""
    package_root = _get_package_root()
    modules: list[str] = []

    for py_file in package_root.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        # Convert path to module name
        rel_path = py_file.relative_to(package_root.parent.parent.parent.parent)
        module_name = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
        modules.append(module_name)

    return sorted(modules)


def _get_public_names(module: Any) -> set[str]:
    """Get all public names (classes, functions, constants) defined in a module."""
    public_names: set[str] = set()

    for name in dir(module):
        # Skip private/magic names
        if name.startswith("_"):
            continue

        obj = getattr(module, name)

        # Skip TypeVars - they're implementation details, not public API
        if type(obj).__name__ == "TypeVar":
            continue

        # Only include items defined in this module
        if hasattr(obj, "__module__") and obj.__module__ == module.__name__:
            public_names.add(name)
        # Include constants/variables that don't have __module__
        elif not inspect.ismodule(obj) and not hasattr(obj, "__module__"):
            public_names.add(name)

    return public_names


def _check_module_all(module_name: str) -> tuple[bool, str]:
    """
    Check if a module's __all__ is complete and accurate.

    Returns (is_valid, message)
    """
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        return False, f"Could not import: {e}"

    # Check if __all__ exists
    if not hasattr(module, "__all__"):
        # Get public names to report what should be there
        public_names = _get_public_names(module)
        if public_names:
            return False, (
                f"Missing __all__ declaration\n"
                f"  Public names found: {sorted(public_names)}"
            )
        else:
            # No public names, so no __all__ needed
            return True, "No public exports (OK)"

    all_exports = set(module.__all__)
    public_names = _get_public_names(module)

    # Check for names in __all__ that don't exist
    missing_names = all_exports - public_names - set(dir(module))
    if missing_names:
        return False, (
            f"__all__ contains non-existent names: {sorted(missing_names)}"
        )

    # Check for names in __all__ that exist but are private
    for name in all_exports:
        if name.startswith("_"):
            return False, f"__all__ contains private name: {name}"

    # Check for public names not in __all__
    missing_from_all = public_names - all_exports
    if missing_from_all:
        return False, (
            f"Public names not in __all__: {sorted(missing_from_all)}\n"
            f"  Current __all__: {sorted(all_exports)}"
        )

    # Check for duplicates in __all__
    if len(all_exports) != len(module.__all__):
        from collections import Counter
        counts: Counter[str] = Counter(module.__all__)
        duplicates = [name for name, count in counts.items() if count > 1]
        return False, f"__all__ contains duplicates: {duplicates}"

    return True, f"OK ({len(all_exports)} exports)"


def test_all_module_exports_are_complete() -> None:
    """
    Verify that every module has complete and accurate __all__ declarations.

    This ensures:
    1. All public classes/functions are in __all__
    2. No private names are in __all__
    3. No non-existent names are in __all__
    4. No duplicates in __all__
    """
    modules = _get_all_modules()

    if not modules:
        pytest.skip("No modules found to test")

    failures: list[str] = []
    successes: list[str] = []

    for module_name in modules:
        is_valid, message = _check_module_all(module_name)

        if is_valid:
            successes.append(f"✓ {module_name}: {message}")
        else:
            failures.append(f"✗ {module_name}:\n    {message}")

    # Print summary
    print(f"\n{'='*70}")
    print(f"Checked {len(modules)} modules")
    print(f"{'='*70}")

    if successes:
        print(f"\nPassed ({len(successes)}):")
        for success in successes:
            print(f"  {success}")

    if failures:
        print(f"\nFailed ({len(failures)}):")
        for failure in failures:
            print(f"  {failure}")
        print(f"{'='*70}\n")

        pytest.fail(
            f"\n\n{len(failures)} module(s) have incomplete or incorrect __all__ declarations.\n"
            f"See details above.\n\n"
            f"To fix:\n"
            f"1. Add missing public names to __all__\n"
            f"2. Remove non-existent names from __all__\n"
            f"3. Remove private names (starting with _) from __all__\n"
            f"4. Ensure __all__ is at the bottom of the file\n"
        )


@pytest.mark.parametrize(
    "module_name",
    [
        "ci.transparency.cwe.types.cwe.results",
        "ci.transparency.cwe.types.cwe.schema.results",
        "ci.transparency.cwe.types.schema.results",
        "ci.transparency.cwe.types.schema_evolution.results",
        "ci.transparency.cwe.types.standards.results",
        "ci.transparency.cwe.types.base.messages",
    ],
)
def test_key_modules_have_all(module_name: str) -> None:
    """Test that key modules have __all__ declarations."""
    module = importlib.import_module(module_name)

    assert hasattr(module, "__all__"), (
        f"{module_name} is missing __all__ declaration.\n"
        f"This is a key module and should explicitly declare its public API."
    )

    assert len(module.__all__) > 0, (
        f"{module_name} has empty __all__.\n"
        f"If there are no public exports, remove __all__ entirely."
    )


def test_all_lists_are_sorted() -> None:
    """
    Verify that __all__ lists are sorted alphabetically OR use clear grouping comments.

    We allow grouped __all__ with comments (preferred for large exports) or
    simple alphabetical sorting (fine for small exports).
    """
    modules = _get_all_modules()
    issues: list[str] = []

    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            if not hasattr(module, "__all__"):
                continue

            # Check if the __all__ has grouping comments by inspecting source
            source_file = inspect.getfile(module)
            with open(source_file) as f:
                source = f.read()

            # Look for __all__ section in source
            all_section = None
            in_all = False
            lines: list[str] = []
            for line in source.split('\n'):
                if '__all__ = [' in line or '__all__=[' in line:
                    in_all = True
                if in_all:
                    lines.append(line)
                    if ']' in line and in_all:
                        all_section = '\n'.join(lines)
                        break

            # If source has comments in __all__ section, allow grouping
            if all_section and '#' in all_section:
                # Has comments/grouping - this is fine, skip sorting check
                continue

            # No comments, should be sorted
            if list(module.__all__) != sorted(module.__all__):
                issues.append(
                    f"{module_name}:\n"
                    f"  No grouping comments found, but __all__ is not sorted.\n"
                    f"  Either:\n"
                    f"    1. Add grouping comments (recommended for clarity)\n"
                    f"    2. Sort alphabetically\n"
                    f"  Current: {module.__all__}\n"
                    f"  Sorted:  {sorted(module.__all__)}"
                )
        except (ImportError, OSError):
            continue

    if issues:
        pytest.fail(
            f"\n\n{len(issues)} module(s) have __all__ that should be organized:\n\n"
            + "\n\n".join(issues) +
            "\n\nGrouped __all__ with comments is preferred for readability!"
        )
