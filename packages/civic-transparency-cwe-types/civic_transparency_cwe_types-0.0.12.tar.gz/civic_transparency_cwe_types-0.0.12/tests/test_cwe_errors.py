# pyright: strict

from pathlib import Path

from ci.transparency.cwe.types.cwe.errors import (
    CweCircularRelationshipError,
    CweConfigurationError,
    CweConstraintViolationError,
    CweDuplicateError,
    CweFieldValidationError,
    CweFileNotFoundError,
    CweIntegrityError,
    CweInvalidFormatError,
    CweInvalidReferenceError,
    CweLoadingError,
    CweMissingFieldError,
    CweOrphanedError,
    CweParsingError,
    CweProcessingError,
    CweRelationshipError,
    CweSchemaValidationError,
    CweValidationError,
)


# --- Loading / File-based ------------------------------------------------------------

def test_cwe_loading_error_sets_item_and_optional_category_context() -> None:
    err = CweLoadingError("load failed", cwe_id="CWE-79", category="Injection", file_path="cwe-79.yaml")
    s = str(err)
    assert "load failed" in s
    assert "Item: CWE-79" in s
    assert "File: cwe-79.yaml" in s
    assert "Category: Injection" in s  # via validation_context


def test_cwe_file_not_found_error_sets_item_and_file() -> None:
    file_path = Path("defs/cwe-20.yaml")
    err = CweFileNotFoundError("missing", cwe_id="CWE-20", file_path=file_path)
    s = str(err)
    assert "missing" in s
    assert "Item: CWE-20" in s
    assert f"File: {file_path}" in s


def test_cwe_parsing_error_accumulates_parser_line_and_details() -> None:
    file_path = Path("cwe-94.yaml")

    err = CweParsingError(
        "parse error",
        cwe_id="CWE-94",
        parser_type="YAML",
        line_number=42,
        parse_details="unexpected indent",
        file_path=file_path,
    )
    s = str(err)
    assert "parse error" in s
    assert "Item: CWE-94" in s
    assert f"File: {file_path}" in s
    # validation_context pieces
    assert "Parser: YAML" in s
    assert "Line: 42" in s
    assert "Details: unexpected indent" in s


def test_cwe_duplicate_error_context_and_file_choice() -> None:
    existing_file = Path("defs/cwe-200.yaml")
    duplicate_file = Path("incoming/cwe-200.yaml")

    err = CweDuplicateError(
        "duplicate",
        cwe_id="CWE-200",
        existing_file=existing_file,
        duplicate_file=duplicate_file,
    )
    s = str(err)
    # file_path should be duplicate_file according to implementation
    assert f"File: {duplicate_file}" in s
    assert "Item: CWE-200" in s
    assert f"Existing: {existing_file}" in s
    assert f"Duplicate: {duplicate_file}" in s


def test_cwe_invalid_format_error_expected_detected_issue() -> None:
    err = CweInvalidFormatError(
        "bad format",
        cwe_id="CWE-522",
        expected_format="YAML",
        detected_format="JSON",
        format_issue="top-level array not allowed",
        file_path="cwe-522.json",
    )
    s = str(err)
    assert "bad format" in s
    assert "Item: CWE-522" in s
    assert "File: cwe-522.json" in s
    assert "Expected: YAML" in s
    assert "Detected: JSON" in s
    assert "Issue: top-level array not allowed" in s


def test_cwe_missing_field_error_field_and_required_list() -> None:
    err = CweMissingFieldError(
        "missing field",
        cwe_id="CWE-89",
        field_name="name",
        required_fields=["name", "description"],
        file_path=Path("cwe-89.yaml"),
    )
    s = str(err)
    assert "Item: CWE-89" in s
    assert "File: cwe-89.yaml" in s
    assert "Field: name" in s
    assert "Required: name, description" in s


# --- Validation family ---------------------------------------------------------------

def test_cwe_validation_error_category_and_type_context() -> None:
    err = CweValidationError(
        "validation failed",
        cwe_id="CWE-79",
        category="Injection",
        validation_type="structure",
        file_path="cwe-79.yaml",
    )
    s = str(err)
    assert "Item: CWE-79" in s
    assert "File: cwe-79.yaml" in s
    assert "Category: Injection" in s
    assert "Type: structure" in s


def test_cwe_field_validation_error_details_and_rule() -> None:
    err = CweFieldValidationError(
        "field invalid",
        cwe_id="CWE-22",
        field_name="relationships[0].id",
        field_value="CWE-???",
        expected_value="CWE-\\d+",
        validation_rule="regex",
        file_path="cwe-22.yaml",
    )
    s = str(err)
    assert "Item: CWE-22" in s
    assert "File: cwe-22.yaml" in s
    assert "Field: relationships[0].id" in s
    assert "Rule: regex" in s
    assert "Value: CWE-???" in s
    assert "Expected: CWE-\\d+" in s


def test_cwe_schema_validation_error_combines_name_and_version() -> None:
    err = CweSchemaValidationError(
        "schema mismatch",
        cwe_id="CWE-451",
        schema_name="cwe.schema",
        schema_version="v2",
        field_path="data.items[0]",
        file_path="cwe-451.yaml",
    )
    s = str(err)
    assert "Item: CWE-451" in s
    assert "Schema: cwe.schema-v2" in s
    assert "Field: data.items[0]" in s
    assert "File: cwe-451.yaml" in s


def test_cwe_constraint_violation_error_context_and_rule() -> None:
    err = CweConstraintViolationError(
        "constraint failed",
        cwe_id="CWE-120",
        category="Buffer Errors",
        constraint_name="max_children",
        constraint_value="5",
        actual_value="8",
        file_path="cwe-120.yaml",
    )
    s = str(err)
    assert "Item: CWE-120" in s
    assert "File: cwe-120.yaml" in s
    assert "Category: Buffer Errors" in s
    assert "Constraint: max_children" in s
    assert "Expected: 5" in s
    assert "Actual: 8" in s
    assert "Rule: constraint" in s


# --- Relationship errors -------------------------------------------------------------

def test_cwe_relationship_error_context() -> None:
    err = CweRelationshipError(
        "relationship bad",
        cwe_id="CWE-10",
        related_cwe_id="CWE-11",
        relationship_type="child-of",
        relationship_direction="outbound",
        file_path="cwe-10.yaml",
    )
    s = str(err)
    assert "Item: CWE-10" in s
    assert "Related: CWE-11" in s
    assert "Type: child-of" in s
    assert "Direction: outbound" in s
    assert "Rule: relationship" in s
    assert "File: cwe-10.yaml" in s


def test_cwe_circular_relationship_error_chain() -> None:
    err = CweCircularRelationshipError(
        "cycle",
        cwe_id="CWE-1",
        relationship_chain=["CWE-1", "CWE-2", "CWE-3", "CWE-1"],
        file_path="defs.yaml",
    )
    s = str(err)
    assert "Item: CWE-1" in s
    assert "Rule: circular_relationship" in s
    assert "Chain: CWE-1 → CWE-2 → CWE-3 → CWE-1" in s
    assert "File: defs.yaml" in s


def test_cwe_orphaned_error_rule_and_category() -> None:
    err = CweOrphanedError("orphaned", cwe_id="CWE-333", category="Insecure", file_path="cwe-333.yaml")
    s = str(err)
    assert "Item: CWE-333" in s
    assert "Rule: orphaned" in s
    assert "Category: Insecure" in s
    assert "File: cwe-333.yaml" in s


def test_cwe_invalid_reference_error_related_and_source() -> None:
    err = CweInvalidReferenceError(
        "bad ref",
        cwe_id="CWE-7",
        related_cwe_id="CWE-9999",
        reference_source="relationships[2]",
        file_path="defs.yaml",
    )
    s = str(err)
    assert "Item: CWE-7" in s
    assert "Related: CWE-9999" in s
    assert "Source: relationships[2]" in s
    assert "Rule: invalid_reference" in s
    assert "File: defs.yaml" in s


# --- Processing / Config -------------------------------------------------------------

def test_cwe_processing_error_operation_and_progress() -> None:
    err = CweProcessingError("proc failed", operation="build-index", processed_count=12, total_count=100)
    s = str(err)
    assert "Operation: build-index" in s
    assert "Progress: 12/100" in s


def test_cwe_integrity_error_rule_and_details() -> None:
    err = CweIntegrityError(
        "integrity",
        cwe_id="CWE-500",
        integrity_check="hash",
        expected_value="abc",
        actual_value="xyz",
        file_path="cwe-500.yaml",
    )
    s = str(err)
    assert "Item: CWE-500" in s
    assert "Rule: integrity" in s
    assert "Check: hash" in s
    assert "Expected: abc" in s
    assert "Actual: xyz" in s
    assert "File: cwe-500.yaml" in s


def test_cwe_configuration_error_maps_fields() -> None:
    err = CweConfigurationError(
        "bad cfg",
        config_key="mode",
        config_value="invalid",
        valid_values=["fast", "full"],
    )
    s = str(err)
    # item_id <- config_key ; error_code <- config_value ; context shows valid values
    assert "Item: mode" in s
    assert "Code: invalid" in s
    assert "Valid: fast, full" in s
