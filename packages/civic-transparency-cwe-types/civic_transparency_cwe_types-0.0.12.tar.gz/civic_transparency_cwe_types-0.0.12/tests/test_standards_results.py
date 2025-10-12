# pyright: strict

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from ci.transparency.cwe.types.standards.results import (
    StandardsLoadingResult,
    StandardsValidationResult,
    StandardsMappingResult,
    StandardsItemDict,
    add_standard,
    track_invalid_standards_file,
    track_skipped_standards_file,
    validate_standard,
    validate_standards_field,
    batch_validate_standards,
    analyze_mappings,
    add_mapping,
    get_standards_loading_summary,
    get_standards_validation_summary,
    get_mapping_summary,
)

# -------------------------------------------------------------------
# Helpers: minimal sample data
# -------------------------------------------------------------------

STD1_ID = "STD-1"
STD1: StandardsItemDict = {
    "id": STD1_ID,
    "name": "Standard One",
    "framework": "NIST",
    "version": "1.0",
    "controls": [
        {
            "id": "C1",
            "title": "Control 1",
            "mappings": [{"target_id": "CWE-79", "mapping_type": "cwe", "confidence": "high"}],
        },
        {"id": "C2", "title": "Control 2", "mappings": []},
    ],
}

STD2_ID = "STD-2"
STD2_INVALID_FOR_VALIDATION: StandardsItemDict = {
    "id": STD2_ID,
    "name": "",  # invalid / missing
    "framework": "ISO",
    "version": "2.0",
    "controls": [{"id": "I1", "mappings": [{"target_id": "CWE-9999", "mapping_type": "cwe"}]}],
}

STD2_FOR_MAPPING_ONLY: StandardsItemDict = {
    "id": STD2_ID,
    "name": "Standard Two",
    "framework": "ISO",
    "version": "2.0",
    "controls": [
        {"id": "I1", "mappings": [{"target_id": "CWE-9999", "mapping_type": "cwe"}]},
        {"id": "I2", "mappings": []},  # orphaned
    ],
}

# -------------------------------------------------------------------
# LoadingResult: add, duplicate, track files, summary
# -------------------------------------------------------------------

def test_loading_result_add_standard_and_duplicate_and_summary(tmp_path: Path) -> None:
    res = StandardsLoadingResult()

    # Add two unique standards
    res = add_standard(res, STD1_ID, STD1, file_path=tmp_path / "std1.yaml")
    res = add_standard(res, STD2_ID, STD2_FOR_MAPPING_ONLY, file_path=tmp_path / "std2.yaml")

    assert res.standards_count == 2
    assert res.loading.loaded_count == 2
    assert res.files.processed_file_count == 2
    assert res.frameworks.framework_stats.get("NIST") == 1
    assert res.frameworks.framework_stats.get("ISO") == 1
    assert STD1_ID in res.loaded_standard_ids and STD2_ID in res.loaded_standard_ids
    assert res.get_control_count() == 4  # C1, C2 from STD-1; I1, I2 from STD-2

    # Duplicate add for STD1 → warning + failed + duplicates
    res = add_standard(res, STD1_ID, STD1, file_path=tmp_path / "std1_dup.yaml")
    assert res.loading.failed_count == 1
    assert res.duplicates.duplicate_count == 1
    assert res.messages.has_warnings is True

    # Track invalid and skipped files
    res = track_invalid_standards_file(res, tmp_path / "bad.yaml", "parse error")
    res = track_skipped_standards_file(res, tmp_path / "skip.yaml", "disabled")

    assert res.files.failed_file_count == 1
    assert res.files.skipped_file_count == 1
    assert res.messages.has_errors is True  # invalid file added an error
    assert res.is_successful is False

    # Loading summary
    summary = get_standards_loading_summary(res)
    assert summary["standards_loaded"] == 2
    assert summary["successful_loads"] == 2
    assert summary["failed_loads"] == 2  # 1 dup + 1 invalid file
    assert summary["frameworks_detected"] == 2
    assert "NIST" in summary["frameworks"] and "ISO" in summary["frameworks"]
    assert summary["duplicate_ids"] == 1
    assert summary["processed_files"] == 2
    assert summary["failed_files"] == 1
    assert summary["skipped_files"] == 1
    assert isinstance(summary["success_rate_percent"], float)
    assert set(summary["loaded_standard_ids"]) == {STD1_ID, STD2_ID}
    assert summary["has_errors"] is True
    assert summary["has_warnings"] is True


def test_loading_result_is_frozen() -> None:
    res = StandardsLoadingResult()
    with pytest.raises(FrozenInstanceError):
        setattr(res, "standards", {})

# -------------------------------------------------------------------
# ValidationResult: single/field/batch, summary
# -------------------------------------------------------------------

def test_validation_result_single_and_field_and_summary() -> None:
    res = StandardsValidationResult()

    # One valid, one invalid
    res = validate_standard(res, STD1_ID, STD1)
    res = validate_standard(res, STD2_ID, STD2_INVALID_FOR_VALIDATION)

    assert res.validated_count == 2
    assert res.validation.passed_count == 1
    assert res.validation.failed_count == 1
    assert res.control_validation_count == 2 + 1  # STD1: 2 controls, STD2: 1 control
    assert set(res.get_failed_standards()) == {STD2_ID}
    assert set(res.get_passed_standards()) == {STD1_ID}
    assert res.messages.has_errors is True  # invalid standard adds error message

    # Field validation: one fail (None), one pass (non-None)
    res = validate_standards_field(res, STD1_ID, "name", None, "required")
    res = validate_standards_field(res, STD1_ID, "name", "ok", "required")
    assert res.field_error_count >= 1
    assert res.has_field_errors is True

    # Batch validate one more (re-validating STD1 is fine; counts accumulate)
    res = batch_validate_standards(res, {STD1_ID: STD1})
    assert res.validated_count == 2 or res.validated_count == 3  # depending on overwrite semantics; dict keys may overwrite

    # Validation summary
    summary = get_standards_validation_summary(res)
    assert summary["standards_validated"] == res.validated_count
    assert summary["validation_passed"] == res.validation.passed_count
    assert summary["validation_failed"] == res.validation.failed_count
    assert summary["field_errors"] == res.field_error_count
    assert summary["controls_validated"] == res.control_validation_count
    assert isinstance(summary["success_rate_percent"], float)
    assert isinstance(summary["validation_rate"], float)
    assert set(summary["failed_standards"]).issubset({STD2_ID})
    assert set(summary["passed_standards"]).issubset({STD1_ID})
    assert "has_errors" in summary and "has_warnings" in summary


def test_validation_result_is_frozen() -> None:
    res = StandardsValidationResult()
    with pytest.raises(FrozenInstanceError):
        setattr(res, "validation_results", {})

# -------------------------------------------------------------------
# MappingResult: analyze, add_mapping, summary
# -------------------------------------------------------------------

def test_mapping_result_analyze_and_add_mapping_and_summary() -> None:
    res = StandardsMappingResult()

    standards_dict = {STD1_ID: STD1, STD2_ID: STD2_FOR_MAPPING_ONLY}
    # Only CWE-79 is valid; CWE-9999 will be invalid → 1 invalid mapping
    res = analyze_mappings(res, standards_dict, valid_targets={"CWE-79"})

    # mapping_results should include STD-1 mappings; STD-2 has a mapping to an invalid target,
    # so it's recorded but flagged as invalid in references.invalid_references.
    assert STD1_ID in res.mapping_results
    assert "CWE-79" in res.mapping_results[STD1_ID]
    assert len(res.references.invalid_references) == 1
    assert any("STD-2:" in s and "CWE-9999" in s for s in res.references.invalid_references)

    # Orphaned controls should include STD-1:C2 and STD-2:I2
    assert "STD-1:C2" in res.references.orphaned_items
    assert "STD-2:I2" in res.references.orphaned_items

    # Validation counts updated by analyze_mappings
    assert res.validation.passed_count + res.validation.failed_count >= 2

    # Add an extra mapping via helper (increments mapping_types)
    res = add_mapping(res, "STD-X", "CWE-20", mapping_type="cwe")
    assert "STD-X" in res.mapping_results
    assert "cwe" in res.mapping_types and res.mapping_types["cwe"] >= 1

    # Summary
    summary = get_mapping_summary(res)
    assert summary["total_mappings"] == res.total_mappings_count
    assert summary["mapped_standards"] == len(res.mapping_results)
    assert summary["has_duplicate_mappings"] == res.has_duplicate_mappings
    assert "invalid_mappings" in summary and "orphaned_controls" in summary
    assert isinstance(summary["mapping_coverage_rate"], float)
    assert "mapping_types" in summary
    assert "has_errors" in summary and "has_warnings" in summary


def test_mapping_result_is_frozen() -> None:
    res = StandardsMappingResult()
    with pytest.raises(FrozenInstanceError):
        setattr(res, "mapping_results", {})
