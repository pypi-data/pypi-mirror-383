# tests/test_cwe_schema.py
from pathlib import Path


from ci.transparency.cwe.types.cwe.schema.results import (
    CweSchemaItemDict,
    CweSchemaLoadingResult,
    CweSchemaValidationResult,
    add_cwe_schema,
    add_validation_error,
    add_validation_warning,
    create_failed_validation,
    create_successful_validation,
    get_cwe_schema_loading_summary,
    get_cwe_schema_validation_summary,
    set_schema_metadata,
    track_invalid_schema_file,
    track_skipped_schema_file,
)


def test_loading_add_and_summary_file_types():
    result = CweSchemaLoadingResult()

    # attach schema metadata first
    result = set_schema_metadata(result, schema_name="core", schema_version="1.0")

    # add two schemas with different file types
    s1: CweSchemaItemDict = {
        "schema_name": "core",
        "schema_version": "1.0",
        "schema_content": {"type": "object"},
        "source_path": "schemas/core.json",
    }
    s2: CweSchemaItemDict = {
        "schema_name": "mappings",
        "schema_version": "1.0",
        "schema_content": {"type": "object"},
        "source_path": "schemas/mappings.yaml",
    }

    result = add_cwe_schema(result, "core@1.0", s1, file_path=Path("schemas/core.json"))
    result = add_cwe_schema(result, "mappings@1.0", s2, file_path=Path("schemas/mappings.yaml"))

    # basic properties
    assert result.schema_count == 2
    assert result.is_successful is True
    assert result.schema_name == "core"
    assert result.schema_version == "1.0"
    assert result.loaded_schema_ids == ["core@1.0", "mappings@1.0"]

    # summary view
    summary = get_cwe_schema_loading_summary(result)
    assert summary["schemas_loaded"] == 2
    assert summary["successful_loads"] == 2
    assert summary["failed_loads"] == 0
    assert summary["schema_name"] == "core"
    assert summary["schema_version"] == "1.0"

    # file type tracking (suffixes include the dot)
    file_types = summary["file_types"]
    assert file_types[".json"] == 1
    assert file_types[".yaml"] == 1
    assert summary["file_type_count"] == 2

    # processed/failed/skipped
    assert summary["processed_files"] == 2
    assert summary["failed_files"] == 0
    assert summary["skipped_files"] == 0

    # messages
    assert summary["has_errors"] is False
    assert summary["has_warnings"] is False
    assert summary["error_count"] == 0
    assert summary["warning_count"] == 0


def test_loading_duplicate_and_invalid_and_skipped_counts():
    result = CweSchemaLoadingResult()

    schema: CweSchemaItemDict = {
        "schema_name": "core",
        "schema_version": "1.0",
        "schema_content": {"type": "object"},
        "source_path": "schemas/core.json",
    }

    # first add succeeds
    result = add_cwe_schema(result, "core@1.0", schema, file_path=Path("schemas/core.json"))
    # duplicate add should be tracked as failed load + warning
    result = add_cwe_schema(result, "core@1.0", schema, file_path=Path("schemas/core.json"))

    # invalid file and skipped file tracking
    result = track_invalid_schema_file(result, Path("schemas/bad.json"), "malformed")
    result = track_skipped_schema_file(result, Path("schemas/skip.json"), "filtered")

    summary = get_cwe_schema_loading_summary(result)

    assert summary["schemas_loaded"] == 1  # only one unique schema in map
    assert summary["successful_loads"] == 1
    assert summary["failed_loads"] >= 1  # at least the duplicate
    assert summary["failed_files"] == 1
    assert summary["skipped_files"] == 1

    # we did create at least one warning/error message
    assert summary["has_warnings"] is True or summary["has_errors"] is True


def test_validation_success_helpers_and_summary():
    ok = create_successful_validation(
        schema_name="core",
        schema_version="1.0",
        cwe_id="CWE-79",
        field_path="description",
        info_message="looks good",
    )
    assert isinstance(ok, CweSchemaValidationResult)
    assert ok.is_schema_valid is True
    assert ok.validation.passed_count == 1
    assert ok.validation.failed_count == 0
    assert ok.schema_name == "core"
    assert ok.schema_version == "1.0"
    assert ok.validation_target == "CWE-79.description"
    assert ok.messages.has_errors is False
    assert ok.messages.has_warnings is False
    assert "looks good" in ok.messages.infos

    summary = get_cwe_schema_validation_summary(ok)
    assert summary["is_valid"] is True
    assert summary["validation_passed"] == 1
    assert summary["validation_failed"] == 0
    assert summary["schema_name"] == "core"
    assert summary["schema_version"] == "1.0"
    assert summary["validation_target"] == "CWE-79.description"
    assert summary["has_errors"] is False
    assert summary["has_warnings"] is False
    assert summary["errors"] == []
    assert "looks good" in summary["warnings"] or summary["warnings"] == []  # warnings may be empty


def test_validation_failure_helpers_and_summary():
    err = create_failed_validation(
        error_messages=["missing required field: id"],
        warning_messages=["deprecated field: foo"],
        schema_name="core",
        schema_version="1.0",
        cwe_id="CWE-120",
    )
    assert err.is_schema_valid is False
    assert err.validation.passed_count == 0
    assert err.validation.failed_count == 1
    assert err.schema_name == "core"
    assert err.schema_version == "1.0"
    assert err.validation_target == "CWE-120"
    assert err.messages.has_errors is True
    assert err.messages.has_warnings is True

    summary = get_cwe_schema_validation_summary(err)
    assert summary["is_valid"] is False
    assert summary["validation_failed"] == 1
    assert "missing required field: id" in summary["errors"]
    assert "deprecated field: foo" in summary["warnings"]


def test_validation_mutation_helpers():
    ok = create_successful_validation(
        schema_name="core",
        schema_version="1.0",
        cwe_id="CWE-352",
    )
    # add a warning (doesn't change pass/fail counts)
    warned = add_validation_warning(ok, "minor: extra whitespace")
    assert warned.is_schema_valid is True
    assert warned.validation.passed_count == 1
    assert warned.validation.failed_count == 0
    assert warned.messages.has_warnings is True

    # add an error -> flips overall validity and increments failed count
    failed = add_validation_error(warned, "invalid type at path: details[0]")
    assert failed.is_schema_valid is False
    assert failed.validation.passed_count == 1  # unchanged
    assert failed.validation.failed_count == 1
    assert failed.messages.has_errors is True

    summary = get_cwe_schema_validation_summary(failed)
    assert summary["is_valid"] is False
    assert "invalid type at path: details[0]" in summary["errors"]
