"""Domain-neutral schema result types and operations using composition.

Immutable dataclasses for tracking schema loading and validation. Mirrors the
CWE/Standards shape (LoadingCounts, ValidationCounts, MessageCollection,
FileCollection, DuplicateCollection), so higher-level workflows can consume
a consistent interface.
"""

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, TypedDict, cast

from ci.transparency.cwe.types.base.collections import (
    DuplicateCollection,
    FileCollection,
)
from ci.transparency.cwe.types.base.counts import LoadingCounts, ValidationCounts
from ci.transparency.cwe.types.base.messages import MessageCollection
from ci.transparency.cwe.types.base.result_helpers import with_message_methods

# -------------------------
# Typed structures
# -------------------------


class SchemaDocumentDict(TypedDict, total=False):
    """Minimal shape of a single schema document."""

    id: str  # identifier or $id
    name: str  # human-readable name
    version: str  # version string
    content: dict[str, Any]  # parsed JSON/YAML schema root
    source_path: str  # stored as string for JSON compatibility


type SchemasDict = dict[str, SchemaDocumentDict]
type ValidationResultsDict = dict[str, bool]
type ValidationDetailsDict = dict[str, list[str]]
type SeverityCountsDict = dict[str, int]
type LoadingSummaryDict = dict[str, Any]
type ValidationSummaryDict = dict[str, Any]


# -------------------------
# Core results
# -------------------------


@with_message_methods
@dataclass(frozen=True)
class SchemaLoadingResult:
    """Result of loading/parsing schema documents (batch-friendly)."""

    schemas: SchemasDict = cast("SchemasDict", field(default_factory=dict))
    loading: LoadingCounts = field(default_factory=LoadingCounts)
    messages: MessageCollection = field(default_factory=MessageCollection)
    files: FileCollection = field(default_factory=FileCollection)
    duplicates: DuplicateCollection = field(default_factory=DuplicateCollection)

    @property
    def schema_count(self) -> int:
        """Return the number of loaded schemas."""
        return len(self.schemas)

    @property
    def is_successful(self) -> bool:
        """Return True if loading was successful and there are no error messages.

        Returns
        -------
        bool
            True if loading was successful and there are no error messages, False otherwise.
        """
        return self.loading.is_successful and not self.messages.has_errors

    @property
    def loaded_schema_ids(self) -> list[str]:
        """Return a sorted list of loaded schema IDs."""
        return sorted(self.schemas.keys())

    def get_schema(self, schema_id: str) -> SchemaDocumentDict | None:
        """Return the schema document for the given schema_id, or None if not found.

        Parameters
        ----------
        schema_id : str
            The identifier of the schema to retrieve.

        Returns
        -------
        SchemaDocumentDict or None
            The schema document if found, otherwise None.
        """
        return self.schemas.get(schema_id)

    def has_schema(self, schema_id: str) -> bool:
        """Check if a schema with the given ID exists in the loaded schemas.

        Parameters
        ----------
        schema_id : str
            The identifier of the schema to check.

        Returns
        -------
        bool
            True if the schema exists, False otherwise.
        """
        return schema_id in self.schemas

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "SchemaLoadingResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "SchemaLoadingResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "SchemaLoadingResult":
        """Add info message (added by decorator)."""
        ...  # Overridden by decorator


@with_message_methods
@dataclass(frozen=True)
class SchemaValidationResult:
    """Result of validating instances/documents against schemas."""

    validation_results: ValidationResultsDict = cast(
        "ValidationResultsDict", field(default_factory=dict)
    )
    validation: ValidationCounts = field(default_factory=ValidationCounts)
    messages: MessageCollection = field(default_factory=MessageCollection)
    field_errors: list[str] = cast("list[str]", field(default_factory=list))
    validation_details: ValidationDetailsDict = cast(
        "ValidationDetailsDict", field(default_factory=dict)
    )
    severity_counts: SeverityCountsDict = cast("SeverityCountsDict", field(default_factory=dict))

    @property
    def validated_count(self) -> int:
        """Return the number of validated schemas."""
        return len(self.validation_results)

    @property
    def is_successful(self) -> bool:
        """Return True if validation was successful and there are no error messages.

        Returns
        -------
        bool
            True if validation was successful and there are no error messages, False otherwise.
        """
        return self.validation.is_successful and not self.messages.has_errors

    @property
    def validation_rate(self) -> float:
        """Return the rate of successful validations as a float between 0 and 1.

        Returns
        -------
        float
            The fraction of schemas that passed validation.
        """
        if not self.validation_results:
            return 1.0
        passed = sum(self.validation_results.values())
        return passed / len(self.validation_results)

    def get_failed(self) -> list[str]:
        """Return a list of schema IDs that failed validation.

        Returns
        -------
        list[str]
            List of schema IDs where validation did not pass.
        """
        return [sid for sid, ok in self.validation_results.items() if not ok]

    def get_passed(self) -> list[str]:
        """Return a list of schema IDs that passed validation.

        Returns
        -------
        list[str]
            List of schema IDs where validation passed.
        """
        return [sid for sid, ok in self.validation_results.items() if ok]

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "SchemaValidationResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "SchemaValidationResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "SchemaValidationResult":
        """Add info message (added by decorator)."""
        ...  # Overridden by decorator


# -------------------------
# Composition helpers
# -------------------------


def add_message(messages: MessageCollection, level: str, message: str) -> MessageCollection:
    """Immutable message append."""
    if level == "error":
        return replace(messages, errors=messages.errors + [message])
    if level == "warning":
        return replace(messages, warnings=messages.warnings + [message])
    # default to info
    return replace(messages, infos=messages.infos + [message])


def increment_loading(counts: LoadingCounts, *, ok: int = 0, failed: int = 0) -> LoadingCounts:
    """Increment the loading counts immutably by the specified ok and failed values.

    Parameters
    ----------
    counts : LoadingCounts
        The current loading counts.
    ok : int, optional
        Number of successful loads to add (default is 0).
    failed : int, optional
        Number of failed loads to add (default is 0).

    Returns
    -------
    LoadingCounts
        A new LoadingCounts instance with updated counts.
    """
    return replace(
        counts,
        loaded_count=counts.loaded_count + ok,
        failed_count=counts.failed_count + failed,
    )


def increment_validation(
    counts: ValidationCounts, *, passed: int = 0, failed: int = 0
) -> ValidationCounts:
    """Increment the validation counts immutably by the specified passed and failed values.

    Parameters
    ----------
    counts : ValidationCounts
        The current validation counts.
    passed : int, optional
        Number of successful validations to add (default is 0).
    failed : int, optional
        Number of failed validations to add (default is 0).

    Returns
    -------
    ValidationCounts
        A new ValidationCounts instance with updated counts.
    """
    return replace(
        counts,
        passed_count=counts.passed_count + passed,
        failed_count=counts.failed_count + failed,
    )


def add_processed_file(files: FileCollection, file_path: Path) -> FileCollection:
    """Add a processed file to the FileCollection in an immutable fashion.

    Parameters
    ----------
    files : FileCollection
        The current collection of files.
    file_path : Path
        The path of the file to add as processed.

    Returns
    -------
    FileCollection
        A new FileCollection with the processed file added.
    """
    return replace(files, processed_files=files.processed_files + [file_path])


def add_failed_file(files: FileCollection, file_path: Path) -> FileCollection:
    """Add a failed file to the FileCollection in an immutable fashion.

    Parameters
    ----------
    files : FileCollection
        The current collection of files.
    file_path : Path
        The path of the file to add as failed.

    Returns
    -------
    FileCollection
        A new FileCollection with the failed file added.
    """
    return replace(files, failed_files=files.failed_files + [file_path])


def add_skipped_file(files: FileCollection, file_path: Path) -> FileCollection:
    """Add a skipped file to the FileCollection in an immutable fashion.

    Parameters
    ----------
    files : FileCollection
        The current collection of files.
    file_path : Path
        The path of the file to add as skipped.

    Returns
    -------
    FileCollection
        A new FileCollection with the skipped file added.
    """
    return replace(files, skipped_files=files.skipped_files + [file_path])


def add_duplicate(
    duplicates: DuplicateCollection, item_id: str, file_path: Path
) -> DuplicateCollection:
    """Add a duplicate item to the DuplicateCollection in an immutable fashion.

    Parameters
    ----------
    duplicates : DuplicateCollection
        The current collection of duplicates.
    item_id : str
        The identifier of the duplicate item.
    file_path : Path
        The path of the file where the duplicate was found.

    Returns
    -------
    DuplicateCollection
        A new DuplicateCollection with the duplicate item added.
    """
    m = {**duplicates.duplicate_ids}
    paths = m.get(item_id, [])
    m[item_id] = paths + [file_path]
    return replace(duplicates, duplicate_ids=m)


# -------------------------
# Loading operations
# -------------------------


def add_schema(
    result: SchemaLoadingResult,
    schema_id: str,
    schema_doc: SchemaDocumentDict,
    *,
    file_path: Path | None = None,
) -> SchemaLoadingResult:
    """Add a loaded schema (dedup, files, messages, counts)."""
    if schema_id in result.schemas:
        if file_path is not None:
            result = replace(
                result, duplicates=add_duplicate(result.duplicates, schema_id, file_path)
            )
        return replace(
            result,
            messages=add_message(result.messages, "warning", f"Duplicate schema ID: {schema_id}"),
            loading=increment_loading(result.loading, failed=1),
        )

    new_schemas = {**result.schemas, schema_id: schema_doc}
    new_files = result.files if file_path is None else add_processed_file(result.files, file_path)
    msg_name = schema_doc.get("name", "unnamed")

    return replace(
        result,
        schemas=new_schemas,
        files=new_files,
        loading=increment_loading(result.loading, ok=1),
        messages=add_message(result.messages, "info", f"Loaded schema {schema_id}: {msg_name}"),
    )


def track_invalid_schema_file(
    result: SchemaLoadingResult, file_path: Path, reason: str
) -> SchemaLoadingResult:
    """Record a file that failed to load as a schema."""
    return replace(
        result,
        messages=add_message(
            result.messages, "error", f"Invalid schema file {file_path}: {reason}"
        ),
        files=add_failed_file(result.files, file_path),
        loading=increment_loading(result.loading, failed=1),
    )


def track_skipped_schema_file(
    result: SchemaLoadingResult, file_path: Path, reason: str
) -> SchemaLoadingResult:
    """Record a file that was skipped during schema loading."""
    return replace(
        result,
        messages=add_message(result.messages, "info", f"Skipped schema file {file_path}: {reason}"),
        files=add_skipped_file(result.files, file_path),
    )


# -------------------------
# Validation operations
# -------------------------


def validate_schema_document(
    result: SchemaValidationResult,
    schema_id: str,
    schema_doc: SchemaDocumentDict,
) -> SchemaValidationResult:
    """Minimal structural checks (domain-neutral).

    Designed so engines that call jsonschema, fastjsonschema, etc. can still pipe their messages into the
    same result container.
    """
    errors: list[str] = []
    ok = True

    # require an id/name-ish and a dict content
    if "content" not in schema_doc:
        errors.append("Missing 'content' (expected dict)")
        ok = False

    if "name" not in schema_doc or not schema_doc["name"]:
        # recommended (not strictly required)
        errors.append("Missing recommended field: name")

    # update aggregates
    new_results = {**result.validation_results, schema_id: ok}
    new_details = {**result.validation_details}
    msgs = result.messages

    if errors:
        new_details[schema_id] = errors
        msgs = add_message(
            msgs, "error", f"Schema {schema_id} failed basic validation: {len(errors)} issues"
        )

    return replace(
        result,
        validation_results=new_results,
        validation_details=new_details,
        validation=increment_validation(
            result.validation, passed=1 if ok else 0, failed=0 if ok else 1
        ),
        messages=msgs,
    )


def record_schema_validation(
    result: SchemaValidationResult,
    schema_id: str,
    *,
    ok: bool,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
    infos: list[str] | None = None,
) -> SchemaValidationResult:
    """Adapt external validator messages and push them in here without re-validating content.

    If an external validator already produced messages, push them in here without re-validating content.
    """
    msgs = result.messages
    for m in errors or []:
        msgs = add_message(msgs, "error", f"{schema_id}: {m}")
    for m in warnings or []:
        msgs = add_message(msgs, "warning", f"{schema_id}: {m}")
    for m in infos or []:
        msgs = add_message(msgs, "info", f"{schema_id}: {m}")

    details = {**result.validation_details}
    if errors:
        details[schema_id] = details.get(schema_id, []) + errors

    return replace(
        result,
        validation_results={**result.validation_results, schema_id: ok},
        validation=increment_validation(
            result.validation, passed=1 if ok else 0, failed=0 if ok else 1
        ),
        messages=msgs,
        validation_details=details,
    )


# -------------------------
# Summaries
# -------------------------


def get_schema_loading_summary(result: SchemaLoadingResult) -> LoadingSummaryDict:
    """Generate a summary dictionary of schema loading results.

    Parameters
    ----------
    result : SchemaLoadingResult
        The result object containing schema loading details.

    Returns
    -------
    LoadingSummaryDict
        A dictionary summarizing loading statistics and outcomes.
    """
    return {
        "schemas_loaded": result.schema_count,
        "successful_loads": result.loading.loaded_count,
        "failed_loads": result.loading.failed_count,
        "duplicate_ids": result.duplicates.duplicate_count,
        "processed_files": result.files.processed_file_count,
        "failed_files": result.files.failed_file_count,
        "skipped_files": result.files.skipped_file_count,
        "success_rate_percent": round(result.loading.success_rate * 100, 2),
        "loaded_schema_ids": result.loaded_schema_ids,
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
        "error_count": result.messages.error_count,
        "warning_count": result.messages.warning_count,
    }


def get_schema_validation_summary(result: SchemaValidationResult) -> ValidationSummaryDict:
    """Generate a summary dictionary of schema validation results.

    Parameters
    ----------
    result : SchemaValidationResult
        The result object containing validation details.

    Returns
    -------
    ValidationSummaryDict
        A dictionary summarizing validation statistics and outcomes.
    """
    return {
        "schemas_validated": result.validated_count,
        "validation_passed": result.validation.passed_count,
        "validation_failed": result.validation.failed_count,
        "success_rate_percent": round(result.validation.pass_rate * 100, 2),
        "validation_rate": round(result.validation_rate * 100, 2),
        "failed": result.get_failed(),
        "passed": result.get_passed(),
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
    }


__all__ = [
    # Results
    "SchemaLoadingResult",
    "SchemaValidationResult",
    # Typed structures
    "SchemaDocumentDict",
    "SchemasDict",
    "ValidationResultsDict",
    "ValidationDetailsDict",
    "SeverityCountsDict",
    "LoadingSummaryDict",
    "ValidationSummaryDict",
    # Ops
    "add_schema",
    "track_invalid_schema_file",
    "track_skipped_schema_file",
    "validate_schema_document",
    "record_schema_validation",
    # Summaries
    "get_schema_loading_summary",
    "get_schema_validation_summary",
    # Helpers
    "add_message",
    "increment_loading",
    "increment_validation",
    "add_processed_file",
    "add_failed_file",
    "add_skipped_file",
    "add_duplicate",
]
