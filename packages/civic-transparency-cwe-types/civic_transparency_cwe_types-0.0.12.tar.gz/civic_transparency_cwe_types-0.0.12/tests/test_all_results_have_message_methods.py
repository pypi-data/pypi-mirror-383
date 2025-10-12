# tests/test_all_results_have_message_methods.py
# pyright: strict

import ast
import inspect
from typing import Any

import pytest

# Import ALL Result classes that should have message methods
from ci.transparency.cwe.types.cwe.results import (
    CweLoadingResult,
    CweRelationshipResult,
    CweValidationResult,
)
from ci.transparency.cwe.types.cwe.schema.results import (
    CweSchemaLoadingResult,
    CweSchemaValidationResult,
)
from ci.transparency.cwe.types.schema.results import (
    SchemaLoadingResult,
    SchemaValidationResult,
)
from ci.transparency.cwe.types.schema_evolution.results import (
    SchemaEvolutionResult,
)
from ci.transparency.cwe.types.standards.results import (
    StandardsLoadingResult,
    StandardsMappingResult,
    StandardsValidationResult,
)

# Explicit list of all Result classes with messages
ALL_RESULT_CLASSES: list[type[Any]] = [
    # CWE (3)
    CweLoadingResult,
    CweValidationResult,
    CweRelationshipResult,
    # CWE Schema (2)
    CweSchemaLoadingResult,
    CweSchemaValidationResult,
    # Generic Schema (2)
    SchemaLoadingResult,
    SchemaValidationResult,
    # Schema Evolution (1)
    SchemaEvolutionResult,
    # Standards (3)
    StandardsLoadingResult,
    StandardsValidationResult,
    StandardsMappingResult,
]


def _has_decorator(cls: type[Any], decorator_name: str) -> bool:
    """Check if class has @with_message_methods decorator in source."""
    try:
        source_file = inspect.getfile(cls)
        with open(source_file) as f:
            source = f.read()

        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == cls.__name__:
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == decorator_name:
                        return True
                    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                        if decorator.func.id == decorator_name:
                            return True
        return False
    except Exception:
        return False


def _check_stub_methods(cls: type[Any]) -> dict[str, bool]:
    """Check if source has stub methods with correct return type annotations."""
    try:
        source_file = inspect.getfile(cls)
        with open(source_file) as f:
            source = f.read()

        tree = ast.parse(source)

        results = {
            "add_error": False,
            "add_warning": False,
            "add_info": False,
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == cls.__name__:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name in results:
                        # Check return annotation is the class name (as string)
                        if item.returns and isinstance(item.returns, ast.Constant):
                            if item.returns.value == cls.__name__:
                                results[item.name] = True

        return results
    except Exception:
        return {"add_error": False, "add_warning": False, "add_info": False}


def test_all_result_classes_have_decorator_and_stubs() -> None:
    """
    Verify ALL Result classes have @with_message_methods and correct stub methods.

    This test ensures we don't forget to add the decorator or stub methods
    when creating new Result classes, preventing pyright strict mode issues
    in client code.
    """
    failures: list[str] = []

    for cls in ALL_RESULT_CLASSES:
        class_name = cls.__name__
        source_file = inspect.getfile(cls)

        # Check 1: Has @with_message_methods decorator
        if not _has_decorator(cls, "with_message_methods"):
            failures.append(
                f"{class_name}: Missing @with_message_methods decorator\n"
                f"  File: {source_file}"
            )

        # Check 2: Has stub methods with correct return types
        stub_methods = _check_stub_methods(cls)
        for method, found in stub_methods.items():
            if not found:
                failures.append(
                    f"{class_name}: Missing stub method '{method}()' "
                    f"with return type '{class_name}'\n"
                    f"  File: {source_file}"
                )

        # Check 3: Methods exist at runtime (decorator worked)
        for method in ["add_error", "add_warning", "add_info"]:
            if not hasattr(cls, method):
                failures.append(
                    f"{class_name}: Method '{method}' not added by decorator at runtime"
                )

    if failures:
        failure_msg = "\n\n".join(failures)
        pytest.fail(
            f"\n\n{'='*70}\n"
            f"FAILED: {len(failures)} issue(s) found with Result classes\n"
            f"{'='*70}\n\n"
            f"{failure_msg}\n\n"
            f"{'='*70}\n"
            f"Requirements for all Result classes with MessageCollection:\n"
            f"{'='*70}\n"
            f"1. Add @with_message_methods decorator above @dataclass\n"
            f"2. Add these stub methods at the end of the class:\n\n"
            f'   def add_error(self, msg: str) -> "YourResultClass":\n'
            f'       """Add error message (added by decorator)."""\n'
            f"       ...  # Overridden by decorator\n\n"
            f'   def add_warning(self, msg: str) -> "YourResultClass":\n'
            f'       """Add warning message (added by decorator)."""\n'
            f"       ...  # Overridden by decorator\n\n"
            f'   def add_info(self, msg: str) -> "YourResultClass":\n'
            f'       """Add info message (added by decorator)."""\n'
            f"       ...  # Overridden by decorator\n"
        )


@pytest.mark.parametrize("result_class", ALL_RESULT_CLASSES)
def test_each_result_class_methods_work(result_class: type[Any]) -> None:
    """Test that each Result class's message methods work at runtime."""
    instance = result_class()

    # Runtime checks
    assert callable(instance.add_error), f"{result_class.__name__}.add_error not callable"
    assert callable(instance.add_warning), f"{result_class.__name__}.add_warning not callable"
    assert callable(instance.add_info), f"{result_class.__name__}.add_info not callable"

    # Test they return the correct type
    r1 = instance.add_error("test error")
    assert isinstance(r1, result_class), f"add_error should return {result_class.__name__}"

    r2 = instance.add_warning("test warning")
    assert isinstance(r2, result_class), f"add_warning should return {result_class.__name__}"

    r3 = instance.add_info("test info")
    assert isinstance(r3, result_class), f"add_info should return {result_class.__name__}"

    # Test immutability
    assert r1 is not instance, "Should return new instance (immutability)"


def test_pyright_type_checking_example() -> None:
    """
    Example showing pyright strict mode works correctly.

    This test itself verifies type checking works. If you're missing
    the stub methods, pyright --strict will fail on this test file.
    """
    # Pick one example - if this works, the pattern is correct
    result = CweLoadingResult()

    # These assignments will be checked by pyright in strict mode
    r1: CweLoadingResult = result.add_error("error")
    r2: CweLoadingResult = result.add_warning("warning")
    r3: CweLoadingResult = result.add_info("info")

    # Chaining should also work
    r4: CweLoadingResult = result.add_error("e1").add_warning("w1").add_info("i1")

    assert isinstance(r1, CweLoadingResult)
    assert isinstance(r2, CweLoadingResult)
    assert isinstance(r3, CweLoadingResult)
    assert isinstance(r4, CweLoadingResult)


def test_count_summary() -> None:
    """Display summary of all Result classes being tested."""
    # This is informational - helps developers know what's being tested
    print(f"\n{'='*70}")
    print(f"Testing {len(ALL_RESULT_CLASSES)} Result classes with MessageCollection:")
    print(f"{'='*70}")

    by_module: dict[str, list[str]] = {}
    for cls in ALL_RESULT_CLASSES:
        module = cls.__module__.split(".")[-2]  # Get the module name
        if module not in by_module:
            by_module[module] = []
        by_module[module].append(cls.__name__)

    for module, classes in sorted(by_module.items()):
        print(f"\n{module} ({len(classes)}):")
        for class_name in sorted(classes):
            print(f"  - {class_name}")

    print(f"\n{'='*70}")
    print(f"Total: {len(ALL_RESULT_CLASSES)} classes")
    print(f"{'='*70}\n")


def test_all_result_classes_are_in_list() -> None:
    """
    Verify that ALL_RESULT_CLASSES contains all classes with 'messages'.

    This catches if you added a Result class but forgot to add it to the list.
    """
    # Get all imported Result classes that have a 'messages' attribute
    import sys
    from ci.transparency.cwe.types.base.messages import MessageCollection

    discovered_classes: set[type[Any]] = set()

    # Check all modules we've imported
    for module_name, module in sys.modules.items():
        if module_name.startswith("ci.transparency.cwe.types") and ".results" in module_name:
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, "__annotations__")
                    and "messages" in attr.__annotations__
                    and attr.__annotations__["messages"] == MessageCollection
                ):
                    discovered_classes.add(attr)

    listed_classes = set(ALL_RESULT_CLASSES)

    # Check for missing classes
    missing_from_list = discovered_classes - listed_classes
    if missing_from_list:
        missing_names = [cls.__name__ for cls in missing_from_list]
        pytest.fail(
            f"Found {len(missing_from_list)} Result class(es) with 'messages' "
            f"not in ALL_RESULT_CLASSES:\n"
            f"  {', '.join(sorted(missing_names))}\n\n"
            f"Please add them to ALL_RESULT_CLASSES in this test file."
        )

    # Check for classes that shouldn't be in the list
    extra_in_list = listed_classes - discovered_classes
    if extra_in_list:
        extra_names = [cls.__name__ for cls in extra_in_list]
        pytest.fail(
            f"ALL_RESULT_CLASSES contains {len(extra_in_list)} class(es) "
            f"that don't have MessageCollection:\n"
            f"  {', '.join(sorted(extra_names))}\n\n"
            f"Please remove them from ALL_RESULT_CLASSES in this test file."
        )
