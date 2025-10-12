# pyright: strict

from dataclasses import FrozenInstanceError

import pytest

from ci.transparency.cwe.types.schema_evolution.results import (
    SchemaDiff,
    SchemaEvolutionResult,
    get_schema_evolution_summary,
    mark_check_passed,
    record_breaking_change,
    record_compat_issue,
    record_violation,
    set_diff,
    set_versions,
)


# --- SchemaDiff ----------------------------------------------------------------------

def test_schema_diff_counts() -> None:
    diff = SchemaDiff(added=["/a"], removed=["/b", "/c"], changed=["/x"])
    assert diff.added_count == 1
    assert diff.removed_count == 2
    assert diff.changed_count == 1
    assert diff.total_changes == 4


# --- Evolution result: set versions, set diff, immutability --------------------------

def test_schema_evolution_set_versions_and_diff_adds_info_message() -> None:
    res = SchemaEvolutionResult()

    res = set_versions(res, old_version="1.0", new_version="2.0")
    assert res.old_version == "1.0"
    assert res.new_version == "2.0"

    base_info = res.messages.info_count
    res = set_diff(res, SchemaDiff(added=["/n"], removed=[], changed=["/t"]))
    # An info message like "Diff computed: +1 / -0 / ~1" is added
    assert res.messages.info_count == base_info + 1
    assert res.diff is not None
    assert res.diff.added == ["/n"]
    assert res.diff.changed == ["/t"]


def test_schema_evolution_is_frozen() -> None:
    res = SchemaEvolutionResult()
    with pytest.raises(FrozenInstanceError):
        setattr(res, "old_version", "x")  # noqa: PLW2901


# --- Record events: violations, breaking changes, compat issues, pass increments -----

def test_schema_evolution_record_violation_and_breaking_and_compat_and_pass() -> None:
    res = SchemaEvolutionResult()

    # Start with a passing check increment
    res = mark_check_passed(res, message="pre-check ok")
    assert res.validation.passed_count == 1
    assert res.messages.info_count >= 1

    # Violation -> error + failed++
    res = record_violation(res, "removed field /id")
    assert res.validation.failed_count == 1
    assert res.messages.has_errors is True
    assert "removed field /id" in res.violations

    # Breaking change -> error + failed++
    res = record_breaking_change(res, "type changed at /value")
    assert res.validation.failed_count == 2
    assert "type changed at /value" in res.breaking_changes
    assert res.has_breaking_changes is True

    # Compatibility issue (warning by default; does not increment failed)
    res = record_compat_issue(res, "enum narrowed at /kind")
    assert res.messages.has_warnings is True
    assert res.validation.failed_count == 2
    assert "enum narrowed at /kind" in res.compatibility_issues
    assert res.has_compat_issues is True

    # Compatibility issue hardened to failure
    res = record_compat_issue(res, "strict incompat at /mode", treat_as_failure=True)
    assert res.validation.failed_count == 3
    # still tracked in compatibility_issues
    assert any("strict incompat at /mode" in m for m in res.compatibility_issues)

    # With failures and errors, not successful
    assert res.is_successful is False


# --- Summary -------------------------------------------------------------------------

def test_schema_evolution_summary_shape_and_values() -> None:
    res = SchemaEvolutionResult()
    res = set_versions(res, old_version="1.0", new_version="2.0")
    res = set_diff(res, SchemaDiff(added=["/a"], removed=["/b"], changed=["/c", "/d"]))

    res = mark_check_passed(res, "rule-ok")
    res = record_violation(res, "bad /b")
    res = record_breaking_change(res, "removed /b")
    res = record_compat_issue(res, "narrowed /x")  # warning
    res = record_compat_issue(res, "strict /y", treat_as_failure=True)  # error

    summary = get_schema_evolution_summary(res)

    # Versions & diff counts
    assert summary["old_version"] == "1.0"
    assert summary["new_version"] == "2.0"
    assert summary["added"] == 1
    assert summary["removed"] == 1
    assert summary["changed"] == 2
    assert summary["total_changes"] == 4

    # Buckets and counts
    assert int(str(summary["violation_count"])) >= 1
    assert int(str(summary["breaking_change_count"])) >= 1
    assert int(str(summary["compatibility_issue_count"])) >= 2

    # Validation counters and flags
    assert int(str(summary["validation_passed"])) >= 1
    assert int(str(summary["validation_failed"])) >= 1
    assert isinstance(summary["success_rate_percent"], float)
    assert summary["is_successful"] is False

    # Message flags
    assert summary["has_errors"] is True
    assert summary["has_warnings"] is True
