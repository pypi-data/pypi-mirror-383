from pathlib import Path

from ci.transparency.cwe.types.base.errors import (
    AbortedError,
    BaseTransparencyError,
    ConfigurationError,
    FileError,
    LoadingError,
    NetworkError,
    OperationError,
    ParsingError,
    ResourceError,
    TransparencyTimeoutError,
    ValidationError,
)

# --- BaseTransparencyError ------------------------------------------------------------

def test_base_transparency_error_minimal_has_message_only() -> None:
    err = BaseTransparencyError("boom")
    s = str(err)
    assert s == "boom"
    # No unintended attributes in output
    assert "Phase:" not in s
    assert "Operation:" not in s
    assert "Progress:" not in s
    assert "File:" not in s
    assert "Schema:" not in s
    assert "Reason:" not in s
    assert "Code:" not in s


def test_base_transparency_error_full_context_and_ordering() -> None:
    # Use Path object for cross-platform compatibility
    test_file_path = Path("data/file.json")

    err = BaseTransparencyError(
        "failed",
        # operation identification
        phase_name="validate",
        stage="cleanup",
        operation="ingest-ignored-when-phase-present",
        # progress
        processed_count=150,
        total_count=500,
        batch_size=64,
        # resource
        resource_type="cpu",
        timeout_seconds=30.0,
        elapsed_seconds=12.34,
        limit_reached="rate-limit",
        resource_usage="85%",
        # file/item
        file_path=test_file_path,
        item_id="CWE-123",
        # validation
        validation_context="cross-check",
        validation_rule="no-dup-id",
        schema_name="cwe.schema.json",
        field_path="items[0].id",
        # flow
        abort_reason="user abort",
        error_code="E42",
    )
    s = str(err)

    # Must include all parts - use platform-appropriate path separators
    wanted = [
        "failed",
        "Phase: validate",          # operation identification
        "Stage: cleanup",
        "Progress: 150/500",        # progress
        "Batch Size: 64",
        "Resource: cpu",            # resource
        "Timeout: 30.0s",
        "Elapsed: 12.3s",           # one decimal place
        "Limit: rate-limit",
        "Usage: 85%",
        f"File: {test_file_path}",  # Use actual path representation
        "Item: CWE-123",
        "Schema: cwe.schema.json",  # validation
        "Rule: no-dup-id",
        "Field: items[0].id",
        "Context: cross-check",
        "Reason: user abort",       # flow
        "Code: E42",
    ]
    for part in wanted:
        assert part in s

    # Check relative ordering: operation -> progress -> resource -> file/item -> validation -> flow
    idx = [
        s.index("Phase: "),
        s.index("Progress:"),
        s.index("Resource:"),
        s.index("File:"),
        s.index("Schema:"),
        s.index("Reason:"),
    ]
    assert idx == sorted(idx)


# --- OperationError ------------------------------------------------------------------

def test_operation_error_formats_progress_and_batch() -> None:
    err = OperationError(
        "op failed",
        operation="ingest",
        processed_count=3,
        total_count=10,
        batch_size=2,
        stage="processing",
    )
    s = str(err)
    # Phase not set -> Operation should appear
    assert "Operation: ingest" in s
    assert "Stage: processing" in s
    assert "Progress: 3/10" in s
    assert "Batch Size: 2" in s


# --- ResourceError -------------------------------------------------------------------

def test_resource_error_formats_timing_and_resource() -> None:
    err = ResourceError(
        "timeout-ish",
        resource_type="network",
        timeout_seconds=5.0,
        elapsed_seconds=1.234,
        limit_reached="socket cap",
        resource_usage="connections=50",
    )
    s = str(err)
    assert "Resource: network" in s
    assert "Timeout: 5.0s" in s
    assert "Elapsed: 1.2s" in s  # rounded to one decimal
    assert "Limit: socket cap" in s
    assert "Usage: connections=50" in s


# --- ValidationError -----------------------------------------------------------------

def test_validation_error_formats_validation_context() -> None:
    err = ValidationError(
        "bad field",
        validation_context="range check",
        validation_rule=">= 0",
        schema_name="schema.json",
        field_path="data.value",
    )
    s = str(err)
    assert "Schema: schema.json" in s
    assert "Rule: >= 0" in s
    assert "Field: data.value" in s
    assert "Context: range check" in s


# --- FileError and derived ------------------------------------------------------------

def test_file_error_coerces_str_path_to_Path() -> None:
    err = FileError("io", file_path="x/y/z.json")

    # Check that the path was converted to Path and has correct parts
    assert isinstance(err.file_path, Path)
    assert err.file_path.parts[-3:] == ("x", "y", "z.json")  # Check path components

    # Check string representation contains the path (with platform separators)
    expected_path_str = str(Path("x/y/z.json"))
    assert f"File: {expected_path_str}" in str(err)


def test_loading_error_inherits_file_context() -> None:
    file_path = Path("a/b.json")
    err = LoadingError("could not load", file_path=file_path)
    s = str(err)
    assert "could not load" in s
    assert f"File: {file_path}" in s


def test_parsing_error_pushes_parser_into_validation_context() -> None:
    err = ParsingError("parse", file_path="f.json", parser_type="JSON")
    s = str(err)
    assert "File: f.json" in s
    # Injected as validation_context with prefix "Parser: "
    assert "Context: Parser: JSON" in s


# --- Configuration / Timeout / Abort / Network --------------------------------------

def test_configuration_error_uses_item_id_for_config_key_and_file_path() -> None:
    err = ConfigurationError("bad config", config_key="workers", config_file="conf.toml")
    s = str(err)
    assert err.item_id == "workers"
    assert str(err.file_path).endswith("conf.toml")
    assert "Item: workers" in s
    assert "File: conf.toml" in s


def test_transparency_timeout_error_includes_operation_and_timing() -> None:
    err = TransparencyTimeoutError("t/o", timeout_seconds=9.0, elapsed_seconds=9.1, operation="fetch")
    s = str(err)
    assert "Operation: fetch" in s
    assert "Timeout: 9.0s" in s
    assert "Elapsed: 9.1s" in s


def test_aborted_error_with_reason() -> None:
    err = AbortedError("stop", abort_reason="user-request")
    s = str(err)
    assert "stop" in s
    assert "Reason: user-request" in s


def test_network_error_sets_url_to_item_id_and_status_to_code() -> None:
    err = NetworkError("net fail", url="https://ex", status_code=503)
    s = str(err)
    # stored in BaseTransparencyError.item_id and error_code (string)
    assert err.item_id == "https://ex"
    assert err.error_code == "503"
    assert "Item: https://ex" in s
    assert "Code: 503" in s
