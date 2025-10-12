# pyright: strict

from pathlib import Path

from ci.transparency.cwe.types.schema_evolution.errors import (
    SchemaBreakingChangeError,
    SchemaCompatibilityError,
    SchemaFreezeError,
    SchemaFreezeViolationError,
)


# --- Base freeze error ---------------------------------------------------------------

def test_schema_freeze_error_versions_rule_field_file_context() -> None:
    err = SchemaFreezeError(
        "freeze check failed",
        old_version="1.0",
        new_version="2.0",
        freeze_rule="no_removals",
        field_path="properties.id",
        file_path="schema.json",
    )
    s = str(err)
    assert "freeze check failed" in s
    # Validation context is emitted under "Context: ..."
    assert "Versions: 1.0 → 2.0" in s
    assert "Rule: no_removals" in s
    assert "Field: properties.id" in s
    assert "File: schema.json" in s


def test_schema_freeze_error_only_old_or_only_new_version() -> None:
    s_old = str(SchemaFreezeError("old only", old_version="1.1"))
    assert "Old: 1.1" in s_old

    s_new = str(SchemaFreezeError("new only", new_version="2.2"))
    assert "New: 2.2" in s_new


# --- Violation -----------------------------------------------------------------------

def test_schema_freeze_violation_includes_violation_and_affected_and_default_rule() -> None:
    err = SchemaFreezeViolationError(
        "violation",
        violation_type="enum_narrowed",
        affected_fields=["/id", "/name"],
        old_version="1.0",
        new_version="1.1",
        file_path=Path("evo.yaml"),
    )
    s = str(err)
    assert "violation" in s
    assert "Versions: 1.0 → 1.1" in s
    assert "Violation: enum_narrowed" in s
    assert "Affected: /id, /name" in s
    # default rule name in implementation
    assert "Rule: freeze_violation" in s
    assert "File: evo.yaml" in s


# --- Compatibility -------------------------------------------------------------------

def test_schema_compatibility_error_issue_and_backward_flag_and_default_rule() -> None:
    err = SchemaCompatibilityError(
        "compat failed",
        compatibility_issue="enum narrowed",
        backward_compatible=False,
        old_version="2.0",
        new_version="2.1",
        field_path="properties.kind",
        file_path="compat.json",
    )
    s = str(err)
    assert "compat failed" in s
    assert "Versions: 2.0 → 2.1" in s
    assert "Issue: enum narrowed" in s
    assert "Backward: No" in s
    assert "Rule: compatibility" in s
    assert "Field: properties.kind" in s
    assert "File: compat.json" in s


def test_schema_compatibility_error_backward_yes() -> None:
    s = str(SchemaCompatibilityError("ok-ish", backward_compatible=True))
    assert "Backward: Yes" in s


# --- Breaking change ----------------------------------------------------------------

def test_schema_breaking_change_error_includes_change_impact_description_and_default_rule() -> None:
    err = SchemaBreakingChangeError(
        "breaking",
        change_type="field_removed",
        change_description="Removed properties.details",
        impact_level="high",
        old_version="3.0",
        new_version="4.0",
        file_path="break.json",
    )
    s = str(err)
    assert "breaking" in s
    assert "Versions: 3.0 → 4.0" in s
    assert "Change: field_removed" in s
    assert "Impact: high" in s
    assert "Description: Removed properties.details" in s
    assert "Rule: breaking_change" in s
    assert "File: break.json" in s
