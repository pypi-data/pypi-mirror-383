"""CWE schema result types for loading and validation using composition.

Domain-specific result holders used by CWE schema loading/parsing and
CWE instance-vs-schema validation. Built using composition of base building blocks
for clean separation of concerns.

Design principles:
    - Composition-based: uses base building blocks for reusable functionality
    - Consistent shape across loading and validation operations
    - Minimal memory footprint with frozen dataclasses
    - Type-safe: follows Python 3.12+ and pyright strict conventions
    - Friendly to functional updates and transformations

Core CWE schema results:
    - CweSchemaLoadingResult: Outcome of loading/parsing CWE schemas
    - CweSchemaValidationResult: Outcome of validating CWE data against a schema
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
from ci.transparency.cwe.types.base.schema import SchemaCollection

# ============================================================================
# Typed structures for CWE schema data
# ============================================================================


class CweSchemaItemDict(TypedDict, total=False):
    """Typed structure for CWE schema data."""

    schema_name: str
    schema_version: str
    schema_content: dict[str, Any]
    source_path: str


type CweSchemaDataDict = dict[str, CweSchemaItemDict]
type LoadingSummaryDict = dict[str, Any]
type ValidationSummaryDict = dict[str, Any]

# ============================================================================
# Core result dataclasses using composition
# ============================================================================


@with_message_methods
@dataclass(frozen=True)
class CweSchemaLoadingResult:
    """Result of loading/parsing CWE schemas using composition.

    Composes base building blocks for clean separation of concerns.

    Attributes
    ----------
    schemas : CweSchemaDataDict
        Dictionary of loaded CWE schema data.
    loading : LoadingCounts
        Statistics about loading success and failures.
    messages : MessageCollection
        Collection of error, warning, and info messages.
    files : FileCollection
        Tracking of processed, failed, and skipped files.
    schema_metadata : SchemaCollection
        Schema-specific metadata and file type tracking.
    duplicates : DuplicateCollection
        Tracking of duplicate schema IDs and their associated files.
    """

    schemas: CweSchemaDataDict = cast("CweSchemaDataDict", field(default_factory=dict))
    loading: LoadingCounts = field(default_factory=LoadingCounts)
    messages: MessageCollection = field(default_factory=MessageCollection)
    files: FileCollection = field(default_factory=FileCollection)
    schema_metadata: SchemaCollection = field(default_factory=SchemaCollection)
    duplicates: DuplicateCollection = field(default_factory=DuplicateCollection)

    @property
    def schema_count(self) -> int:
        """Return the number of schemas loaded."""
        return len(self.schemas)

    @property
    def is_successful(self) -> bool:
        """Return True if loading is successful and there are no error messages."""
        return self.loading.is_successful and not self.messages.has_errors

    @property
    def loaded_schema_ids(self) -> list[str]:
        """All loaded schema IDs (sorted for stable output)."""
        return sorted(self.schemas.keys())

    @property
    def schema_name(self) -> str | None:
        """Schema name from metadata."""
        return self.schema_metadata.schema_name

    @property
    def schema_version(self) -> str | None:
        """Schema version from metadata."""
        return self.schema_metadata.schema_version

    def get_schema(self, schema_id: str) -> CweSchemaItemDict | None:
        """Get schema data by ID."""
        return self.schemas.get(schema_id)

    def has_schema(self, schema_id: str) -> bool:
        """Check if a schema ID was loaded."""
        return schema_id in self.schemas

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "CweSchemaLoadingResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "CweSchemaLoadingResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "CweSchemaLoadingResult":
        """Add info message (added by decorator)."""
        ...  # Overridden by decorator


@with_message_methods
@dataclass(frozen=True)
class CweSchemaValidationResult:
    """Result of validating CWE data against a schema using composition.

    Attributes
    ----------
    validation : ValidationCounts
        Statistics about validation success and failures.
    messages : MessageCollection
        Collection of error, warning, and info messages.
    schema_metadata : SchemaCollection
        Schema-specific metadata.
    cwe_id : str | None
        CWE identifier being validated.
    field_path : str | None
        Path to the field being validated.
    is_schema_valid : bool
        Whether the validation passed.
    """

    validation: ValidationCounts = field(default_factory=ValidationCounts)
    messages: MessageCollection = field(default_factory=MessageCollection)
    schema_metadata: SchemaCollection = field(default_factory=SchemaCollection)
    cwe_id: str | None = None
    field_path: str | None = None
    is_schema_valid: bool = False

    @property
    def is_successful(self) -> bool:
        """Return True if validation is successful and there are no error messages."""
        return (
            self.is_schema_valid and self.validation.is_successful and not self.messages.has_errors
        )

    @property
    def schema_name(self) -> str | None:
        """Schema name from metadata."""
        return self.schema_metadata.schema_name

    @property
    def schema_version(self) -> str | None:
        """Schema version from metadata."""
        return self.schema_metadata.schema_version

    @property
    def validation_target(self) -> str:
        """Get a description of what was validated."""
        if self.cwe_id and self.field_path:
            return f"{self.cwe_id}.{self.field_path}"
        if self.cwe_id:
            return self.cwe_id
        if self.field_path:
            return f"field: {self.field_path}"
        return "unknown target"

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "CweSchemaValidationResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "CweSchemaValidationResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "CweSchemaValidationResult":
        """Add info message (added by decorator)."""
        ...  # Overridden by decorator


# ============================================================================
# Composition helper functions for immutable updates
# ============================================================================


def _add_message(messages: MessageCollection, level: str, message: str) -> MessageCollection:
    """Add a message to the message collection."""
    if level == "error":
        new_errors = messages.errors + [message]
        return replace(messages, errors=new_errors)
    if level == "warning":
        new_warnings = messages.warnings + [message]
        return replace(messages, warnings=new_warnings)
    if level == "info":
        new_infos = messages.infos + [message]
        return replace(messages, infos=new_infos)
    # Default to info for unknown levels
    new_infos = messages.infos + [message]
    return replace(messages, infos=new_infos)


def _increment_loading_counts(
    counts: LoadingCounts, *, succeeded: int = 0, failed: int = 0
) -> LoadingCounts:
    """Increment loading counts."""
    return replace(
        counts,
        loaded_count=counts.loaded_count + succeeded,
        failed_count=counts.failed_count + failed,
    )


def _increment_validation_counts(
    counts: ValidationCounts, *, passed: int = 0, failed: int = 0
) -> ValidationCounts:
    """Increment validation counts."""
    return replace(
        counts, passed_count=counts.passed_count + passed, failed_count=counts.failed_count + failed
    )


def _add_processed_file(files: FileCollection, file_path: Path) -> FileCollection:
    """Add a processed file."""
    new_processed = files.processed_files + [file_path]
    return replace(files, processed_files=new_processed)


def _add_failed_file(files: FileCollection, file_path: Path) -> FileCollection:
    """Add a failed file."""
    new_failed = files.failed_files + [file_path]
    return replace(files, failed_files=new_failed)


def _add_skipped_file(files: FileCollection, file_path: Path) -> FileCollection:
    """Add a skipped file."""
    new_skipped = files.skipped_files + [file_path]
    return replace(files, skipped_files=new_skipped)


def _add_file_type(schema_metadata: SchemaCollection, file_type: str) -> SchemaCollection:
    """Add or increment a file type count."""
    return schema_metadata.add_file_type(file_type)


def _add_duplicate(
    duplicates: DuplicateCollection, item_id: str, file_path: Path
) -> DuplicateCollection:
    """Add a duplicate ID with its file path."""
    new_duplicate_ids = {**duplicates.duplicate_ids}
    current_paths = new_duplicate_ids.get(item_id, [])
    new_duplicate_ids[item_id] = current_paths + [file_path]
    return replace(duplicates, duplicate_ids=new_duplicate_ids)


# ============================================================================
# CWE schema loading operations
# ============================================================================


def add_cwe_schema(
    result: CweSchemaLoadingResult,
    schema_id: str,
    schema_data: CweSchemaItemDict,
    *,
    file_path: Path | None = None,
) -> CweSchemaLoadingResult:
    """Add successfully loaded CWE schema to the result."""
    # Check for duplicates
    if schema_id in result.schemas:
        if file_path is not None:
            new_duplicates = _add_duplicate(result.duplicates, schema_id, file_path)
            result = replace(result, duplicates=new_duplicates)

        new_messages = _add_message(
            result.messages, "warning", f"Duplicate schema ID found: {schema_id}"
        )
        new_loading = _increment_loading_counts(result.loading, failed=1)
        return replace(result, messages=new_messages, loading=new_loading)

    # Add the schema
    new_schemas = {**result.schemas, schema_id: schema_data}
    new_messages = _add_message(
        result.messages,
        "info",
        f"Loaded schema {schema_id}: {schema_data.get('schema_name', 'unnamed')}",
    )

    # Update file tracking if file_path provided
    new_files = result.files
    new_schema_metadata = result.schema_metadata
    if file_path is not None:
        new_files = _add_processed_file(result.files, file_path)
        # Extract and track file type
        file_type = file_path.suffix.lower() if file_path.suffix else "unknown"
        new_schema_metadata = _add_file_type(result.schema_metadata, file_type)

    new_loading = _increment_loading_counts(result.loading, succeeded=1)

    return replace(
        result,
        schemas=new_schemas,
        files=new_files,
        schema_metadata=new_schema_metadata,
        loading=new_loading,
        messages=new_messages,
    )


def track_invalid_schema_file(
    result: CweSchemaLoadingResult, file_path: Path, reason: str
) -> CweSchemaLoadingResult:
    """Track an invalid CWE schema file."""
    new_messages = _add_message(
        result.messages, "error", f"Invalid schema file {file_path}: {reason}"
    )
    new_files = _add_failed_file(result.files, file_path)
    new_loading = _increment_loading_counts(result.loading, failed=1)
    return replace(result, messages=new_messages, files=new_files, loading=new_loading)


def track_skipped_schema_file(
    result: CweSchemaLoadingResult,
    file_path: Path,
    reason: str,
) -> CweSchemaLoadingResult:
    """Track a skipped CWE schema file."""
    new_messages = _add_message(
        result.messages, "info", f"Skipped schema file {file_path}: {reason}"
    )
    new_files = _add_skipped_file(result.files, file_path)
    return replace(result, messages=new_messages, files=new_files)


def set_schema_metadata(
    result: CweSchemaLoadingResult,
    schema_name: str | None,
    schema_version: str | None,
) -> CweSchemaLoadingResult:
    """Set schema metadata for the loading result."""
    new_schema_metadata = result.schema_metadata.with_metadata(schema_name, schema_version)
    return replace(result, schema_metadata=new_schema_metadata)


# ============================================================================
# CWE schema validation operations
# ============================================================================


def create_successful_validation(
    *,
    schema_name: str | None = None,
    schema_version: str | None = None,
    cwe_id: str | None = None,
    field_path: str | None = None,
    info_message: str | None = None,
) -> CweSchemaValidationResult:
    """Create a successful validation result."""
    schema_metadata = SchemaCollection().with_metadata(schema_name, schema_version)
    validation = _increment_validation_counts(ValidationCounts(), passed=1)

    messages = MessageCollection()
    if info_message:
        messages = _add_message(messages, "info", info_message)

    return CweSchemaValidationResult(
        validation=validation,
        messages=messages,
        schema_metadata=schema_metadata,
        cwe_id=cwe_id,
        field_path=field_path,
        is_schema_valid=True,
    )


def create_failed_validation(
    *,
    error_messages: list[str] | None = None,
    warning_messages: list[str] | None = None,
    schema_name: str | None = None,
    schema_version: str | None = None,
    cwe_id: str | None = None,
    field_path: str | None = None,
) -> CweSchemaValidationResult:
    """Create a failed validation result."""
    schema_metadata = SchemaCollection().with_metadata(schema_name, schema_version)
    validation = _increment_validation_counts(ValidationCounts(), failed=1)

    messages = MessageCollection()
    if error_messages:
        for error in error_messages:
            messages = _add_message(messages, "error", error)
    if warning_messages:
        for warning in warning_messages:
            messages = _add_message(messages, "warning", warning)

    return CweSchemaValidationResult(
        validation=validation,
        messages=messages,
        schema_metadata=schema_metadata,
        cwe_id=cwe_id,
        field_path=field_path,
        is_schema_valid=False,
    )


def add_validation_error(
    result: CweSchemaValidationResult,
    error_message: str,
) -> CweSchemaValidationResult:
    """Add an error to the validation result."""
    new_messages = _add_message(result.messages, "error", error_message)
    new_validation = _increment_validation_counts(result.validation, failed=1)
    return replace(
        result,
        messages=new_messages,
        validation=new_validation,
        is_schema_valid=False,
    )


def add_validation_warning(
    result: CweSchemaValidationResult,
    warning_message: str,
) -> CweSchemaValidationResult:
    """Add a warning to the validation result."""
    new_messages = _add_message(result.messages, "warning", warning_message)
    return replace(result, messages=new_messages)


# ============================================================================
# Analysis and reporting
# ============================================================================


def get_cwe_schema_loading_summary(result: CweSchemaLoadingResult) -> LoadingSummaryDict:
    """Generate CWE schema loading summary."""
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
        "schema_name": result.schema_name,
        "schema_version": result.schema_version,
        "file_types": dict(result.schema_metadata.file_type_stats),
        "file_type_count": result.schema_metadata.file_type_count,
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
        "error_count": result.messages.error_count,
        "warning_count": result.messages.warning_count,
    }


def get_cwe_schema_validation_summary(result: CweSchemaValidationResult) -> ValidationSummaryDict:
    """Generate CWE schema validation summary."""
    return {
        "is_valid": result.is_schema_valid,
        "validation_passed": result.validation.passed_count,
        "validation_failed": result.validation.failed_count,
        "schema_name": result.schema_name,
        "schema_version": result.schema_version,
        "cwe_id": result.cwe_id,
        "field_path": result.field_path,
        "validation_target": result.validation_target,
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
        "error_count": result.messages.error_count,
        "warning_count": result.messages.warning_count,
        "errors": result.messages.errors,
        "warnings": result.messages.warnings,
    }


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Types
    "CweSchemaLoadingResult",
    "CweSchemaValidationResult",
    "CweSchemaItemDict",
    "CweSchemaDataDict",
    "LoadingSummaryDict",
    "ValidationSummaryDict",
    # Base collections
    "SchemaCollection",
    # Loading operations
    "add_cwe_schema",
    "track_invalid_schema_file",
    "track_skipped_schema_file",
    "set_schema_metadata",
    # Validation operations
    "create_successful_validation",
    "create_failed_validation",
    "add_validation_error",
    "add_validation_warning",
    # Summary functions
    "get_cwe_schema_loading_summary",
    "get_cwe_schema_validation_summary",
]
