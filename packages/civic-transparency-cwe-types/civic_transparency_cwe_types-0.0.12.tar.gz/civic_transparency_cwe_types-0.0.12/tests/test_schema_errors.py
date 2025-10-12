from pathlib import Path

from ci.transparency.cwe.types.schema.errors import (
    SchemaError,
    SchemaLoadingError,
    SchemaNotFoundError,
    SchemaParsingError,
    SchemaVersionError,
    SchemaFormatError,
    SchemaValidationError,
    SchemaDataValidationError,
    SchemaFieldValidationError,
    SchemaConstraintError,
    SchemaReferenceError,
    SchemaCircularReferenceError,
)


def test_schema_error_base_context_parts():
    e = SchemaError("boom", schema_name="core", schema_version="2.0", file_path=Path("x.json"))
    parts = e.get_context_parts()
    # Context should include "Schema: core-2.0" (or similar) and the base file context
    assert any("Schema: core-2.0" in p for p in parts)


def test_loading_subclasses_add_details():
    e1 = SchemaNotFoundError("missing", schema_name="core")
    assert isinstance(e1, SchemaLoadingError)

    e2 = SchemaParsingError("parse", parse_error="unexpected token", schema_version="1.1")
    parts2 = e2.get_context_parts()
    # Changed from "Parse Error:" to "Details:" to match base ParsingError format
    assert any("Details: unexpected token" in p for p in parts2)
    assert any("Schema: 1.1" in p for p in parts2)

    e3 = SchemaVersionError("bad version", schema_version="9.9", supported_versions=["1.0", "2.0"])
    parts3 = e3.get_context_parts()
    assert any("Supported: 1.0, 2.0" in p for p in parts3)

    e4 = SchemaFormatError("format", format_issue="invalid $id")
    parts4 = e4.get_context_parts()
    assert any("Issue: invalid $id" in p for p in parts4)


def test_validation_subclasses_add_details():
    e1 = SchemaValidationError("val fail", schema_name="core", schema_version="2.0")
    assert isinstance(e1, SchemaError)

    e2 = SchemaDataValidationError(
        "type mismatch",
        validation_path="items[0].id",
        expected_type="string",
        actual_value="42",
        schema_name="core",
    )
    parts2 = e2.get_context_parts()
    assert any("Field: items[0].id" in p for p in parts2)
    assert any("Expected: string" in p for p in parts2)
    assert any("Actual: 42" in p for p in parts2)

    e3 = SchemaFieldValidationError(
        "constraint",
        field_name="id",
        field_path="items[0].id",
        constraint_type="required",
    )
    parts3 = e3.get_context_parts()
    assert any("Field: items[0].id" in p for p in parts3)
    assert any("Constraint: required" in p for p in parts3)

    e4 = SchemaConstraintError(
        "violated",
        constraint_name="$ref",
        constraint_value="valid uri",
        violated_rule="must be absolute",
    )
    parts4 = e4.get_context_parts()
    assert any("Constraint: $ref" in p for p in parts4)
    assert any("Expected: valid uri" in p for p in parts4)
    assert any("Rule: must be absolute" in p for p in parts4)

    e5 = SchemaReferenceError("ref missing", reference_path="#/$defs/x", reference_target="defs/x")
    parts5 = e5.get_context_parts()
    assert any("Reference: #/$defs/x" in p for p in parts5)
    assert any("Target: defs/x" in p for p in parts5)

    e6 = SchemaCircularReferenceError("cycle", reference_chain=["A", "B", "C"])
    parts6 = e6.get_context_parts()
    assert any("Chain: A → B → C" in p for p in parts6)
