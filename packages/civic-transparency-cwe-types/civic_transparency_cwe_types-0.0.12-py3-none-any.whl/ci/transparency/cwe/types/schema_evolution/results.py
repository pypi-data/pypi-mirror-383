"""Schema evolution result types and composable operations.

This mirrors the Standards/CWE pattern: immutable dataclasses that compose
base building blocks (ValidationCounts, MessageCollection) and helper functions
that return *new* instances via dataclasses.replace.
"""

from dataclasses import dataclass, field, replace
from typing import cast

from ci.transparency.cwe.types.base.counts import ValidationCounts
from ci.transparency.cwe.types.base.messages import MessageCollection
from ci.transparency.cwe.types.base.result_helpers import with_message_methods

# ------------------------------------------------------------------------------------
# Diff structure
# ------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SchemaDiff:
    """Structural diff between two schema versions."""

    added: list[str] = field(default_factory=list[str])
    removed: list[str] = field(default_factory=list[str])
    changed: list[str] = field(default_factory=list[str])

    @property
    def added_count(self) -> int:  # convenience
        """Return the number of items added in the schema diff."""
        return len(self.added)

    @property
    def removed_count(self) -> int:
        """Return the number of items removed in the schema diff."""
        return len(self.removed)

    @property
    def changed_count(self) -> int:
        """Return the number of items changed in the schema diff."""
        return len(self.changed)

    @property
    def total_changes(self) -> int:
        """Return the total number of changes (added, removed, changed) in the schema diff."""
        return self.added_count + self.removed_count + self.changed_count


# ------------------------------------------------------------------------------------
# Evolution result (composition)
# ------------------------------------------------------------------------------------


@with_message_methods
@dataclass(frozen=True)
class SchemaEvolutionResult:
    """Aggregate result of a schema evolution (freeze/compatibility) check."""

    old_version: str | None = None
    new_version: str | None = None
    diff: SchemaDiff | None = None

    validation: ValidationCounts = field(default_factory=ValidationCounts)
    messages: MessageCollection = field(default_factory=MessageCollection)

    # Categorized findings (free-form strings you supply; paths, summaries, etc.)
    violations: list[str] = cast("list[str]", field(default_factory=list))
    breaking_changes: list[str] = cast("list[str]", field(default_factory=list))
    compatibility_issues: list[str] = cast("list[str]", field(default_factory=list))

    @property
    def is_successful(self) -> bool:
        """True if no validation failures and no error messages."""
        return self.validation.is_successful and not self.messages.has_errors

    @property
    def has_breaking_changes(self) -> bool:
        """Return True if there are any breaking changes recorded."""
        return bool(self.breaking_changes)

    @property
    def has_compat_issues(self) -> bool:
        """Return True if there are any compatibility issues recorded."""
        return bool(self.compatibility_issues)

    @property
    def violation_count(self) -> int:
        """Return the number of violations recorded in the schema evolution result."""
        return len(self.violations)

    @property
    def breaking_change_count(self) -> int:
        """Return the number of breaking changes recorded in the schema evolution result."""
        return len(self.breaking_changes)

    @property
    def compatibility_issue_count(self) -> int:
        """Return the number of compatibility issues recorded in the schema evolution result."""
        return len(self.compatibility_issues)

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "SchemaEvolutionResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "SchemaEvolutionResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "SchemaEvolutionResult":
        """Add info message (added by decorator)."""
        ...  # Overridden by decorator


# ------------------------------------------------------------------------------------
# Small composable helpers (same style as Standards/CWE)
# ------------------------------------------------------------------------------------


def _add_message(messages: MessageCollection, level: str, text: str) -> MessageCollection:
    if level == "error":
        return replace(messages, errors=messages.errors + [text])
    if level == "warning":
        return replace(messages, warnings=messages.warnings + [text])
    # default -> info
    return replace(messages, infos=messages.infos + [text])


def _inc_validation(
    counts: ValidationCounts, *, passed: int = 0, failed: int = 0
) -> ValidationCounts:
    return replace(
        counts,
        passed_count=counts.passed_count + passed,
        failed_count=counts.failed_count + failed,
    )


# ------------------------------------------------------------------------------------
# Public operations you can compose in your engine/flows
# ------------------------------------------------------------------------------------


def set_versions(
    result: SchemaEvolutionResult, *, old_version: str | None, new_version: str | None
) -> SchemaEvolutionResult:
    """Set the old and new version identifiers in a SchemaEvolutionResult.

    Parameters
    ----------
    result : SchemaEvolutionResult
        The schema evolution result to update.
    old_version : str | None
        The old version identifier.
    new_version : str | None
        The new version identifier.

    Returns
    -------
    SchemaEvolutionResult
        A new SchemaEvolutionResult instance with updated version fields.
    """
    return replace(result, old_version=old_version, new_version=new_version)


def set_diff(result: SchemaEvolutionResult, diff: SchemaDiff) -> SchemaEvolutionResult:
    """Set the schema diff in a SchemaEvolutionResult and add an info message summarizing the diff counts.

    Parameters
    ----------
    result : SchemaEvolutionResult
        The schema evolution result to update.
    diff : SchemaDiff
        The schema diff to set.

    Returns
    -------
    SchemaEvolutionResult
        A new SchemaEvolutionResult instance with the updated diff and info message.
    """
    # Add a small info message summarizing counts
    msg = f"Diff computed: +{diff.added_count} / -{diff.removed_count} / ~{diff.changed_count}"
    return replace(result, diff=diff, messages=_add_message(result.messages, "info", msg))


def record_violation(
    result: SchemaEvolutionResult,
    message: str,
) -> SchemaEvolutionResult:
    """Record a freeze-rule violation (may or may not be breaking)."""
    new_msgs = _add_message(result.messages, "error", message)
    new_counts = _inc_validation(result.validation, failed=1)
    return replace(
        result, messages=new_msgs, validation=new_counts, violations=result.violations + [message]
    )


def record_breaking_change(
    result: SchemaEvolutionResult,
    message: str,
) -> SchemaEvolutionResult:
    """Record a breaking change; also a validation failure."""
    new_msgs = _add_message(result.messages, "error", message)
    new_counts = _inc_validation(result.validation, failed=1)
    return replace(
        result,
        messages=new_msgs,
        validation=new_counts,
        breaking_changes=result.breaking_changes + [message],
    )


def record_compat_issue(
    result: SchemaEvolutionResult,
    message: str,
    *,
    treat_as_failure: bool = False,
) -> SchemaEvolutionResult:
    """Record a compatibility issue. By default it's a warning; can be hardened."""
    level = "error" if treat_as_failure else "warning"
    new_msgs = _add_message(result.messages, level, message)
    new_counts = _inc_validation(result.validation, failed=1 if treat_as_failure else 0)
    return replace(
        result,
        messages=new_msgs,
        validation=new_counts,
        compatibility_issues=result.compatibility_issues + [message],
    )


def mark_check_passed(
    result: SchemaEvolutionResult, message: str | None = None
) -> SchemaEvolutionResult:
    """Increment 'passed' when a check succeeds."""
    new_counts = _inc_validation(result.validation, passed=1)
    new_msgs = _add_message(result.messages, "info", message) if message else result.messages
    return replace(result, validation=new_counts, messages=new_msgs)


# ------------------------------------------------------------------------------------
# Summary (shape mirrors standards-style summaries)
# ------------------------------------------------------------------------------------


def get_schema_evolution_summary(result: SchemaEvolutionResult) -> dict[str, object]:
    """Generate a summary dictionary of the schema evolution result.

    Parameters
    ----------
    result : SchemaEvolutionResult
        The schema evolution result to summarize.

    Returns
    -------
    dict[str, object]
        A dictionary containing summary statistics and details about the schema evolution.
    """
    added = removed = changed = total = 0
    if result.diff:
        added = result.diff.added_count
        removed = result.diff.removed_count
        changed = result.diff.changed_count
        total = result.diff.total_changes

    return {
        "old_version": result.old_version,
        "new_version": result.new_version,
        "added": added,
        "removed": removed,
        "changed": changed,
        "total_changes": total,
        "violations": list(result.violations),
        "breaking_changes": list(result.breaking_changes),
        "compatibility_issues": list(result.compatibility_issues),
        "violation_count": result.violation_count,
        "breaking_change_count": result.breaking_change_count,
        "compatibility_issue_count": result.compatibility_issue_count,
        "validation_passed": result.validation.passed_count,
        "validation_failed": result.validation.failed_count,
        "success_rate_percent": round(result.validation.pass_rate * 100, 2),
        "is_successful": result.is_successful,
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
    }


__all__ = [
    "SchemaDiff",
    "SchemaEvolutionResult",
    # Ops
    "set_versions",
    "set_diff",
    "record_violation",
    "record_breaking_change",
    "record_compat_issue",
    "mark_check_passed",
    "get_schema_evolution_summary",
]
