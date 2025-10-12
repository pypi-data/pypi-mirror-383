# pyright: strict

from pathlib import Path

from ci.transparency.cwe.types.standards.errors import (
    StandardsConfigurationError,
    StandardsConstraintViolationError,
    StandardsDuplicateMappingError,
    StandardsFieldValidationError,
    StandardsFileNotFoundError,
    StandardsFormatError,
    StandardsIntegrityError,
    StandardsInvalidFormatError,
    StandardsInvalidMappingError,
    StandardsLoadingError,
    StandardsMappingError,
    StandardsMissingFieldError,
    StandardsParsingError,
    StandardsProcessingError,
    StandardsValidationError,
)


# --- Loading / File-based ------------------------------------------------------------

def test_standards_loading_error_sets_item_and_framework_context() -> None:
    err = StandardsLoadingError(
        "load failed",
        standard_id="NIST-SP-800-53",
        framework="NIST",
        file_path="nist.yaml",
    )
    s = str(err)
    assert "load failed" in s
    assert "Item: NIST-SP-800-53" in s
    assert "File: nist.yaml" in s
    assert "Framework: NIST" in s  # via validation_context


def test_standards_file_not_found_error_sets_item_and_file() -> None:
    err = StandardsFileNotFoundError("missing", standard_id="ISO-27001", file_path="iso.yaml")
    s = str(err)
    assert "missing" in s
    assert "Item: ISO-27001" in s
    assert "File: iso.yaml" in s


def test_standards_parsing_error_accumulates_parser_line_and_details() -> None:
    err = StandardsParsingError(
        "parse error",
        standard_id="CIS-1.0",
        parser_type="YAML",
        line_number=7,
        parse_details="invalid indentation",
        file_path="cis.yaml",
    )
    s = str(err)
    assert "parse error" in s
    assert "Item: CIS-1.0" in s
    assert "File: cis.yaml" in s
    assert "Parser: YAML" in s
    assert "Line: 7" in s
    assert "Details: invalid indentation" in s


def test_standards_invalid_format_error_expected_detected_issue() -> None:
    err = StandardsInvalidFormatError(
        "bad format",
        standard_id="CSA-STAR",
        detected_format="CSV",
        supported_formats=["YAML", "JSON"],
        format_issue="no headers",
        file_path="csa.csv",
    )
    s = str(err)
    assert "bad format" in s
    assert "Item: CSA-STAR" in s
    assert "File: csa.csv" in s
    assert "Detected: CSV" in s
    assert "Supported: YAML, JSON" in s
    assert "Issue: no headers" in s


def test_standards_missing_field_error_field_and_required_list() -> None:
    err = StandardsMissingFieldError(
        "missing field",
        standard_id="PCI-DSS",
        field_name="name",
        required_fields=["id", "name"],
        file_path=Path("pci.yaml"),
    )
    s = str(err)
    assert "Item: PCI-DSS" in s
    assert "File: pci.yaml" in s
    assert "Field: name" in s
    assert "Required: id, name" in s


# --- Validation family ---------------------------------------------------------------

def test_standards_validation_error_framework_and_type_context() -> None:
    err = StandardsValidationError(
        "validation failed",
        standard_id="NIST-CSF",
        framework="NIST",
        validation_type="structure",
        file_path="csf.yaml",
    )
    s = str(err)
    assert "Item: NIST-CSF" in s
    assert "File: csf.yaml" in s
    assert "Framework: NIST" in s
    assert "Type: structure" in s


def test_standards_field_validation_error_details_and_rule() -> None:
    err = StandardsFieldValidationError(
        "field invalid",
        standard_id="SOC2",
        field_name="controls[0].id",
        field_value="",
        expected_value="CTRL-\\d+",
        validation_rule="regex",
        file_path="soc2.yaml",
    )
    s = str(err)
    assert "Item: SOC2" in s
    assert "File: soc2.yaml" in s
    assert "Field: controls[0].id" in s
    assert "Rule: regex" in s
    assert "Value: " in s
    assert "Expected: CTRL-\\d+" in s


def test_standards_constraint_violation_error_context_and_rule() -> None:
    err = StandardsConstraintViolationError(
        "constraint failed",
        standard_id="CSA-CCM",
        framework="CSA",
        constraint_name="max_controls",
        expected="100",
        actual="120",
        file_path="ccm.yaml",
    )
    s = str(err)
    assert "Item: CSA-CCM" in s
    assert "File: ccm.yaml" in s
    assert "Framework: CSA" in s
    assert "Constraint: max_controls" in s
    assert "Expected: 100" in s
    assert "Actual: 120" in s
    assert "Rule: constraint" in s


# --- Mapping errors ------------------------------------------------------------------

def test_standards_mapping_error_context() -> None:
    err = StandardsMappingError(
        "mapping bad",
        standard_id="NIST-SP-800-171",
        mapping_key="3.1.1",
        target_id="CWE-79",
        mapping_type="cwe",
        file_path="800-171.yaml",
    )
    s = str(err)
    assert "Item: NIST-SP-800-171" in s
    assert "Mapping: 3.1.1" in s
    assert "Target: CWE-79" in s
    assert "Type: cwe" in s
    assert "Rule: mapping" in s
    assert "File: 800-171.yaml" in s


def test_standards_invalid_mapping_error_related_and_source() -> None:
    err = StandardsInvalidMappingError(
        "bad ref",
        standard_id="NIST-PR",
        mapping_key="PR.AC-1",
        target_id="CWE-9999",
        reference_source="controls[5].mappings[0]",
        file_path="nist-pr.yaml",
    )
    s = str(err)
    assert "Item: NIST-PR" in s
    assert "Mapping: PR.AC-1" in s
    assert "Target: CWE-9999" in s
    assert "Source: controls[5].mappings[0]" in s
    assert "Rule: invalid_mapping" in s
    assert "File: nist-pr.yaml" in s


def test_standards_duplicate_mapping_error_context() -> None:
    err = StandardsDuplicateMappingError(
        "dup map",
        standard_id="ISO-27002",
        mapping_key="A.5.1.1",
        existing_target="CWE-20",
        duplicate_target="CWE-20",
        file_path="iso27002.yaml",
    )
    s = str(err)
    assert "Item: ISO-27002" in s
    assert "Mapping: A.5.1.1" in s
    assert "Existing: CWE-20" in s
    assert "Duplicate: CWE-20" in s
    assert "Rule: duplicate_mapping" in s
    assert "File: iso27002.yaml" in s


# --- Format / Processing / Integrity / Config ---------------------------------------

def test_standards_format_error_context() -> None:
    err = StandardsFormatError(
        "formatting",
        standard_id="NERC-CIP",
        format_type="export",
        export_template="xlsx",
        file_path="nerc.xlsx",
    )
    s = str(err)
    assert "Item: NERC-CIP" in s
    assert "Format: export" in s
    assert "Template: xlsx" in s
    assert "File: nerc.xlsx" in s


def test_standards_processing_error_operation_and_stage_and_progress() -> None:
    err = StandardsProcessingError(
        "proc failed",
        standard_id="HIPAA",
        operation="index",
        stage="processing",
        processed_count=12,
        file_path="hipaa.yaml",
    )
    s = str(err)
    assert "Operation: index" in s
    assert "Stage: processing" in s
    assert "Processed: 12" in s  # total_count not provided → "Processed: N"
    assert "Item: HIPAA" in s
    assert "File: hipaa.yaml" in s


def test_standards_integrity_error_rule_and_details() -> None:
    err = StandardsIntegrityError(
        "integrity",
        standard_id="SOC2",
        integrity_check="checksum",
        expected_value="abc",
        actual_value="xyz",
        file_path="soc2.yaml",
    )
    s = str(err)
    assert "Item: SOC2" in s
    assert "Rule: integrity" in s
    assert "Check: checksum" in s
    assert "Expected: abc" in s
    assert "Actual: xyz" in s
    assert "File: soc2.yaml" in s


def test_standards_configuration_error_maps_fields() -> None:
    err = StandardsConfigurationError(
        "bad cfg",
        config_key="mode",
        config_value="invalid",
        valid_values=["fast", "full"],
    )
    s = str(err)
    assert "Item: mode" in s
    assert "Code: invalid" in s
    assert "Valid: fast, full" in s
