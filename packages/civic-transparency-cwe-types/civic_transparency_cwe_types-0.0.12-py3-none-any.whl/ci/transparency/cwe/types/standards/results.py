"""Standards domain result types and operations using composition.

Immutable dataclasses for tracking standards loading, validation, and
mapping analysis operations. Built using composition of base building blocks
for clean separation of concerns.

Core types:
    - StandardsLoadingResult: Tracks standards definition loading with framework detection
    - StandardsValidationResult: Tracks standards validation with field and constraint checks
    - StandardsMappingResult: Tracks standards mapping validation and analysis

Key operations:
    - add_standard: Add successfully loaded standards definition
    - validate_standard: Validate standards data with field checks
    - analyze_mappings: Analyze standards mappings for consistency

Design principles:
    - Immutable: uses dataclasses.replace for all modifications
    - Composition-based: uses base building blocks for reusable functionality
    - Standards-specific: tailored for standards definition requirements and patterns
    - Type-safe: follows Python 3.12+ and pyright strict conventions
"""

from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, TypedDict, cast

from ci.transparency.cwe.types.base.collections import (
    DuplicateCollection,
    FileCollection,
    FrameworkCollection,
    ReferenceCollection,
)
from ci.transparency.cwe.types.base.counts import LoadingCounts, ValidationCounts
from ci.transparency.cwe.types.base.messages import MessageCollection
from ci.transparency.cwe.types.base.result_helpers import with_message_methods

# ============================================================================
# Typed structures for standards data
# ============================================================================


class StandardsMappingDict(TypedDict, total=False):
    """Typed structure for standards mapping data."""

    target_id: str
    mapping_type: str
    confidence: str


class StandardsControlDict(TypedDict, total=False):
    """Typed structure for standards control data."""

    id: str
    title: str
    description: str
    mappings: list[StandardsMappingDict]


class StandardsItemDict(TypedDict, total=False):
    """Typed structure for standards data."""

    id: str
    name: str
    framework: str
    version: str
    controls: list[StandardsControlDict]


type StandardsDataDict = dict[str, StandardsItemDict]
type ValidationResultsDict = dict[str, bool]
type ValidationDetailsDict = dict[str, list[str]]
type SeverityCountsDict = dict[str, int]
type MappingResultsDict = dict[str, list[str]]
type MappingTypesDict = dict[str, int]

type ErrorSummaryDict = dict[str, Any]
type LoadingSummaryDict = dict[str, Any]
type ValidationSummaryDict = dict[str, Any]
type MappingSummaryDict = dict[str, Any]


# ============================================================================
# Core result dataclasses using composition
# ============================================================================


@with_message_methods
@dataclass(frozen=True)
class StandardsLoadingResult:
    """Represents the result of loading standards data using composition.

    Composes base building blocks for clean separation of concerns.

    Attributes
    ----------
    standards : StandardsDataDict
        Dictionary of loaded standards data.
    loading : LoadingCounts
        Statistics about loading success and failures.
    messages : MessageCollection
        Collection of error, warning, and info messages.
    files : FileCollection
        Tracking of processed, failed, and skipped files.
    frameworks : FrameworkCollection
        Statistics for frameworks encountered.
    duplicates : DuplicateCollection
        Tracking of duplicate IDs and their associated files.
    _format_breakdown : dict[str, int]
        Tracks format usage breakdown.
    """

    standards: StandardsDataDict = cast("StandardsDataDict", field(default_factory=dict))
    loading: LoadingCounts = field(default_factory=LoadingCounts)
    messages: MessageCollection = field(default_factory=MessageCollection)
    files: FileCollection = field(default_factory=FileCollection)
    frameworks: FrameworkCollection = field(default_factory=FrameworkCollection)
    duplicates: DuplicateCollection = field(default_factory=DuplicateCollection)
    _format_breakdown: dict[str, int] = field(default_factory=lambda: {})

    @property
    def standards_count(self) -> int:
        """Return the number of standards loaded."""
        return len(self.standards)

    @property
    def is_successful(self) -> bool:
        """Return True if loading is successful and there are no error messages."""
        return self.loading.is_successful and not self.messages.has_errors

    @property
    def loaded_standard_ids(self) -> list[str]:
        """All loaded standard IDs (sorted for stable output)."""
        return sorted(self.standards.keys())

    def get_standard(self, standard_id: str) -> StandardsItemDict | None:
        """Get standards data by ID."""
        return self.standards.get(standard_id)

    def has_standard(self, standard_id: str) -> bool:
        """Check if a standards ID was loaded."""
        return standard_id in self.standards

    def get_standards_by_framework(self, framework: str) -> StandardsDataDict:
        """Return all standards loaded for a given framework.

        Parameters
        ----------
        framework : str
            The framework name to filter standards by.

        Returns
        -------
        StandardsDataDict
            Dictionary of standards data filtered by the specified framework.
        """
        out: StandardsDataDict = {}
        for standard_id, standards_data in self.standards.items():
            fw_obj = standards_data.get("framework")
            fw: str | None = fw_obj if isinstance(fw_obj, str) else None
            if fw == framework:
                out[standard_id] = standards_data
        return out

    def get_control_count(self) -> int:
        """Get total number of controls across all standards."""
        total_controls = 0
        for standards_data in self.standards.values():
            controls = standards_data.get("controls", [])
            total_controls += len(controls)
        return total_controls

    def add_format_info(self, format_version: str) -> "StandardsLoadingResult":
        """Track format usage."""
        if not hasattr(self, "_format_breakdown"):
            object.__setattr__(self, "_format_breakdown", {})
        self._format_breakdown[format_version] = self._format_breakdown.get(format_version, 0) + 1
        return self

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "StandardsLoadingResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "StandardsLoadingResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "StandardsLoadingResult":
        """Add info message (added by decorator)."""
        ...  # Overridden by decorator


@with_message_methods
@dataclass(frozen=True)
class StandardsValidationResult:
    """Represents the result of validating standards data using composition.

    Attributes
    ----------
    validation_results : ValidationResultsDict
        Dictionary of validation results for each standards item.
    validation : ValidationCounts
        Statistics about validation success and failures.
    messages : MessageCollection
        Collection of error, warning, and info messages.
    field_errors : list[str]
        Field-level validation errors.
    validation_details : ValidationDetailsDict
        Detailed validation errors per standard.
    severity_counts : SeverityCountsDict
        Count of issues by severity level.
    control_validation_count : int
        Number of controls validated.
    coverage_stats : dict[str, Any] | None
        Optional coverage statistics (filled by higher-level validators).
    frameworks_checked : frozenset[str]
        Framework identifiers observed during validation (for completeness analysis).
    """

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
    control_validation_count: int = 0

    # fields commonly accessed by catalog-side validators/reporters
    coverage_stats: dict[str, Any] | None = None
    frameworks_checked: frozenset[str] = field(default_factory=lambda: frozenset[str]())

    # -------------------------------
    # Convenience properties & views
    # -------------------------------

    @property
    def validated_count(self) -> int:
        """Return the number of items that have been validated."""
        return len(self.validation_results)

    @property
    def is_successful(self) -> bool:
        """Return True if validation is successful and there are no error messages."""
        return self.validation.is_successful and not self.messages.has_errors

    @property
    def is_valid(self) -> bool:
        """Alias used by some callers; equivalent to is_successful."""
        return self.is_successful

    @property
    def validation_rate(self) -> float:
        """Validation success rate (0.0 to 1.0)."""
        if not self.validation_results:
            return 1.0
        passed = sum(self.validation_results.values())
        return passed / len(self.validation_results)

    @property
    def field_error_count(self) -> int:
        """Number of field-level validation errors."""
        return len(self.field_errors)

    @property
    def has_field_errors(self) -> bool:
        """True if any field-level validation errors occurred."""
        return bool(self.field_errors)

    # surface message lists directly (some callers expect these on the result)
    @property
    def error_messages(self) -> list[str]:
        """Errors collected during validation (proxy to messages.errors)."""
        return getattr(self.messages, "errors", [])

    @property
    def warning_messages(self) -> list[str]:
        """Warnings collected during validation (proxy to messages.warnings)."""
        return getattr(self.messages, "warnings", [])

    @property
    def info_messages(self) -> list[str]:
        """Infos collected during validation (proxy to messages.infos)."""
        return getattr(self.messages, "infos", [])

    def get_failed_standards(self) -> list[str]:
        """Get list of standards IDs that failed validation."""
        return [std_id for std_id, result in self.validation_results.items() if not result]

    def get_passed_standards(self) -> list[str]:
        """Get list of standards IDs that passed validation."""
        return [std_id for std_id, result in self.validation_results.items() if result]

    def get_validation_errors(self, standard_id: str) -> list[str]:
        """Get validation errors for a specific standard."""
        return self.validation_details.get(standard_id, [])

    def get_standards_summary(self) -> dict[str, Any]:
        """Small summary consumed by reporting utilities."""
        return {
            "infos": len(self.info_messages),
            "warnings": len(self.warning_messages),
            "errors": len(self.error_messages),
            "frameworks_checked": sorted(self.frameworks_checked),
            "validated": self.validated_count,
            "validation_rate": self.validation_rate,
        }

    # -------------------------------
    # Immutable helper methods
    # -------------------------------

    def with_coverage(self, stats: dict[str, Any]) -> "StandardsValidationResult":
        """Return a new result with coverage_stats set."""
        return replace(self, coverage_stats=stats)

    def with_frameworks(self, frameworks: Iterable[str]) -> "StandardsValidationResult":
        """Return a new result with frameworks merged in (as a frozenset)."""
        return replace(self, frameworks_checked=self.frameworks_checked.union(set(frameworks)))

    def with_field_error(self, message: str) -> "StandardsValidationResult":
        """Return a new result with one additional field-level error."""
        return replace(self, field_errors=[*self.field_errors, message])

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "StandardsValidationResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "StandardsValidationResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "StandardsValidationResult":
        """Add info message (added by decorator)."""
        ...  # Overridden by decorator


@with_message_methods
@dataclass(frozen=True)
class StandardsMappingResult:
    """Result from standards mapping validation and analysis using composition.

    Tracks standards mapping consistency, invalid references detection,
    and mapping statistics analysis.

    Attributes
    ----------
    validation : ValidationCounts
        Statistics about mapping validation.
    messages : MessageCollection
        Collection of error, warning, and info messages.
    references : ReferenceCollection
        Tracking of references between standards and targets.
    mapping_results : MappingResultsDict
        Mapping of standards IDs to their target IDs.
    mapping_types : MappingTypesDict
        Count of mapping types.
    duplicate_mappings : list[str]
        Duplicate mappings detected.
    """

    validation: ValidationCounts = field(default_factory=ValidationCounts)
    messages: MessageCollection = field(default_factory=MessageCollection)
    references: ReferenceCollection = field(default_factory=ReferenceCollection)
    mapping_results: MappingResultsDict = cast("MappingResultsDict", field(default_factory=dict))
    mapping_types: MappingTypesDict = cast("MappingTypesDict", field(default_factory=dict))
    duplicate_mappings: list[str] = cast("list[str]", field(default_factory=list))

    @property
    def total_mappings_count(self) -> int:
        """Total number of mappings tracked."""
        return sum(len(targets) for targets in self.mapping_results.values())

    @property
    def duplicate_mapping_count(self) -> int:
        """Number of duplicate mappings detected."""
        return len(self.duplicate_mappings)

    @property
    def is_successful(self) -> bool:
        """Return True if mapping analysis is successful."""
        return self.validation.is_successful and not self.messages.has_errors

    @property
    def is_valid(self) -> bool:
        """Alias used by some callers; equivalent to is_successful."""
        return self.is_successful

    @property
    def has_duplicate_mappings(self) -> bool:
        """True if duplicate mappings were detected."""
        return bool(self.duplicate_mappings)

    # --- Message proxies for ergonomic access (match StandardsValidationResult) ---
    @property
    def error_messages(self) -> list[str]:
        """Errors collected during mapping analysis (proxy to messages.errors)."""
        return getattr(self.messages, "errors", [])

    @property
    def warning_messages(self) -> list[str]:
        """Warnings collected during mapping analysis (proxy to messages.warnings)."""
        return getattr(self.messages, "warnings", [])

    @property
    def info_messages(self) -> list[str]:
        """Infos collected during mapping analysis (proxy to messages.infos)."""
        return getattr(self.messages, "infos", [])

    def get_mappings(self, standard_id: str) -> list[str]:
        """Get all mappings for a specific standard."""
        return self.mapping_results.get(standard_id, [])

    def get_mapping_coverage_rate(self) -> float:
        """Calculate mapping coverage rate."""
        total_items = len(self.mapping_results) + self.references.orphaned_item_count
        if total_items == 0:
            return 1.0
        return len(self.mapping_results) / total_items

    # --- Immutable helpers (keep frozen dataclass semantics) ---
    def with_mapping(
        self, standard_id: str, target_id: str, *, mapping_type: str = "mapped"
    ) -> "StandardsMappingResult":
        """Return a new result with one additional mapping and type count updated."""
        current = self.mapping_results.get(standard_id, [])
        new_results = {**self.mapping_results, standard_id: [*current, target_id]}
        new_types = {
            **self.mapping_types,
            mapping_type: self.mapping_types.get(mapping_type, 0) + 1,
        }
        return replace(self, mapping_results=new_results, mapping_types=new_types)

    def with_mappings(
        self, standard_id: str, target_ids: Iterable[str], *, mapping_type: str = "mapped"
    ) -> "StandardsMappingResult":
        """Return a new result with multiple mappings added."""
        current = self.mapping_results.get(standard_id, [])
        targets = list(target_ids)
        new_results = {**self.mapping_results, standard_id: [*current, *targets]}
        new_types = {
            **self.mapping_types,
            mapping_type: self.mapping_types.get(mapping_type, 0) + len(targets),
        }
        return replace(self, mapping_results=new_results, mapping_types=new_types)

    def with_duplicate(self, mapping_id: str) -> "StandardsMappingResult":
        """Return a new result with one duplicate mapping recorded."""
        return replace(self, duplicate_mappings=[*self.duplicate_mappings, mapping_id])

    def with_references(self, refs: ReferenceCollection) -> "StandardsMappingResult":
        """Return a new result with the references collection replaced."""
        return replace(self, references=refs)

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "StandardsMappingResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "StandardsMappingResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "StandardsMappingResult":
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


def _add_framework(frameworks: FrameworkCollection, framework: str) -> FrameworkCollection:
    """Add or increment a framework count."""
    # Assuming FrameworkCollection has a public method 'add_framework'
    return frameworks.add_framework(framework)


def _add_duplicate(
    duplicates: DuplicateCollection, item_id: str, file_path: Path
) -> DuplicateCollection:
    """Add a duplicate ID with its file path."""
    new_duplicate_ids = {**duplicates.duplicate_ids}
    current_paths = new_duplicate_ids.get(item_id, [])
    new_duplicate_ids[item_id] = current_paths + [file_path]
    return replace(duplicates, duplicate_ids=new_duplicate_ids)


# ============================================================================
# Standards loading operations
# ============================================================================


def add_standard(
    result: StandardsLoadingResult,
    standard_id: str,
    standards_data: StandardsItemDict,
    *,
    file_path: Path | None = None,
) -> StandardsLoadingResult:
    """Add successfully loaded standards to the result."""
    # Check for duplicates
    if standard_id in result.standards:
        if file_path is not None:
            new_duplicates = _add_duplicate(result.duplicates, standard_id, file_path)
            result = replace(result, duplicates=new_duplicates)

        new_messages = _add_message(
            result.messages, "warning", f"Duplicate standards ID found: {standard_id}"
        )
        new_loading = _increment_loading_counts(result.loading, failed=1)
        return replace(result, messages=new_messages, loading=new_loading)

    # Update framework statistics
    framework = str(standards_data.get("framework", "unknown"))
    new_frameworks = _add_framework(result.frameworks, framework)

    # Add the standards
    new_standards = {**result.standards, standard_id: standards_data}
    new_messages = _add_message(
        result.messages,
        "info",
        f"Loaded standard {standard_id}: {standards_data.get('name', 'unnamed')}",
    )

    # Update file tracking if file_path provided
    new_files = result.files
    if file_path is not None:
        new_files = _add_processed_file(result.files, file_path)

    new_loading = _increment_loading_counts(result.loading, succeeded=1)

    return replace(
        result,
        standards=new_standards,
        frameworks=new_frameworks,
        files=new_files,
        loading=new_loading,
        messages=new_messages,
    )


def track_invalid_standards_file(
    result: StandardsLoadingResult, file_path: Path, reason: str
) -> StandardsLoadingResult:
    """Track an invalid standards file."""
    new_messages = _add_message(
        result.messages, "error", f"Invalid standards file {file_path}: {reason}"
    )
    new_files = _add_failed_file(result.files, file_path)
    new_loading = _increment_loading_counts(result.loading, failed=1)
    return replace(result, messages=new_messages, files=new_files, loading=new_loading)


def track_skipped_standards_file(
    result: StandardsLoadingResult,
    file_path: Path,
    reason: str,
) -> StandardsLoadingResult:
    """Track a skipped standards file."""
    new_messages = _add_message(
        result.messages, "info", f"Skipped standards file {file_path}: {reason}"
    )
    new_files = _add_skipped_file(result.files, file_path)
    return replace(result, messages=new_messages, files=new_files)


# ============================================================================
# Standards validation operations
# ============================================================================


def validate_standard(
    result: StandardsValidationResult,
    standard_id: str,
    standards_data: StandardsItemDict,
) -> StandardsValidationResult:
    """Validate a standards definition with comprehensive field validation."""
    errors: list[str] = []
    is_valid = True

    # Basic standards validation
    if not standards_data.get("id"):
        errors.append("Missing required field: id")
        is_valid = False

    if not standards_data.get("name"):
        errors.append("Missing required field: name")
        is_valid = False

    if not standards_data.get("framework"):
        errors.append("Missing recommended field: framework")

    # Validate controls if present
    control_count = 0
    if "controls" in standards_data:
        for control in standards_data["controls"]:
            # control is a StandardsControlDict
            if "id" in control and control["id"]:
                control_count += 1
            else:
                errors.append("Control missing ID")
                is_valid = False

    # Record validation result
    new_results = {**result.validation_results, standard_id: is_valid}
    new_details = {**result.validation_details}
    new_messages = result.messages

    if errors:
        new_details[standard_id] = errors
        new_messages = _add_message(
            new_messages, "error", f"Validation failed for {standard_id}: {len(errors)} issues"
        )

    new_validation = _increment_validation_counts(
        result.validation, passed=1 if is_valid else 0, failed=0 if is_valid else 1
    )

    return replace(
        result,
        validation_results=new_results,
        validation_details=new_details,
        validation=new_validation,
        messages=new_messages,
        control_validation_count=result.control_validation_count + control_count,
    )


def validate_standards_field(
    result: StandardsValidationResult,
    standard_id: str,
    field_path: str,
    field_value: Any,
    validation_rule: str,
) -> StandardsValidationResult:
    """Validate a specific standards field."""
    is_field_valid = field_value is not None

    if not is_field_valid:
        error_msg = f"Field validation failed for {standard_id}.{field_path}: {validation_rule}"
        new_messages = _add_message(result.messages, "error", error_msg)
        new_field_errors = result.field_errors + [f"{standard_id}.{field_path}"]
        new_validation = _increment_validation_counts(result.validation, failed=1)
        return replace(
            result, field_errors=new_field_errors, validation=new_validation, messages=new_messages
        )

    new_validation = _increment_validation_counts(result.validation, passed=1)
    return replace(result, validation=new_validation)


def batch_validate_standards(
    result: StandardsValidationResult,
    standards_dict: StandardsDataDict,
) -> StandardsValidationResult:
    """Validate multiple standards in batch."""
    for standard_id, standards_data in standards_dict.items():
        result = validate_standard(result, standard_id, standards_data)

    new_messages = _add_message(
        result.messages, "info", f"Batch validated {len(standards_dict)} standards"
    )
    return replace(result, messages=new_messages)


# ============================================================================
# Standards mapping operations
# ============================================================================
def _extract_control_id(control: StandardsControlDict, unknown_index: int) -> str:
    """Return a string control id or a stable 'unknown-{n}' fallback."""
    if "id" in control and control["id"]:
        return control["id"]
    return f"unknown-{unknown_index}"


def _collect_control_mappings(
    standard_id: str,
    control: StandardsControlDict,
    *,
    valid_targets: set[str] | None,
    mapping_types: MappingTypesDict,
    invalid_mappings: list[str],
    orphaned_controls: list[str],
) -> list[str]:
    """Collect target ids from a single control, updating counters and issues."""
    control_id = _extract_control_id(control, len(orphaned_controls))

    # Pull typed list of mappings
    mapping_items: list[StandardsMappingDict] = control.get("mappings", [])

    if not mapping_items:
        orphaned_controls.append(f"{standard_id}:{control_id}")
        return []

    collected: list[str] = []
    for mapping in mapping_items:
        # mapping is StandardsMappingDict by type
        target_id: str | None = mapping.get("target_id", None)
        mapping_type: str = mapping.get("mapping_type", "unknown")

        if target_id is None:
            continue

        collected.append(target_id)
        mapping_types[mapping_type] = mapping_types.get(mapping_type, 0) + 1

        if valid_targets and target_id not in valid_targets:
            invalid_mappings.append(f"{standard_id}:{control_id} → {target_id}")

    return collected


def _process_standard_mappings(
    standard_id: str,
    standards_data: StandardsItemDict,
    valid_targets: set[str] | None,
    mapping_types: MappingTypesDict,
    invalid_mappings: list[str],
    orphaned_controls: list[str],
) -> list[str]:
    """Process mappings for a single standard."""
    standard_mappings: list[str] = []

    if "controls" in standards_data:
        for control in standards_data["controls"]:
            standard_mappings.extend(
                _collect_control_mappings(
                    standard_id,
                    control,
                    valid_targets=valid_targets,
                    mapping_types=mapping_types,
                    invalid_mappings=invalid_mappings,
                    orphaned_controls=orphaned_controls,
                )
            )

    return standard_mappings


def analyze_mappings(
    result: StandardsMappingResult,
    standards_dict: StandardsDataDict,
    valid_targets: set[str] | None = None,
) -> StandardsMappingResult:
    """Analyze standards mappings for consistency and detect issues."""
    mapping_results: MappingResultsDict = {}
    mapping_types: MappingTypesDict = {}
    invalid_mappings: list[str] = []
    orphaned_controls: list[str] = []

    # Build mapping map
    for standard_id, standards_data in standards_dict.items():
        standard_mappings = _process_standard_mappings(
            standard_id,
            standards_data,
            valid_targets,
            mapping_types,
            invalid_mappings,
            orphaned_controls,
        )
        if standard_mappings:
            mapping_results[standard_id] = standard_mappings

    # Create reference collection
    new_references = ReferenceCollection(
        reference_map=mapping_results,
        invalid_references=invalid_mappings,
        orphaned_items=orphaned_controls,
    )

    # Update messages
    new_messages = _add_message(
        result.messages, "info", f"Analyzed mappings for {len(standards_dict)} standards"
    )
    if invalid_mappings:
        new_messages = _add_message(
            new_messages,
            "error",
            f"Found {len(invalid_mappings)} invalid mapping references",
        )

    new_validation = _increment_validation_counts(
        result.validation,
        passed=len(standards_dict) - len(invalid_mappings),
        failed=len(invalid_mappings),
    )

    return replace(
        result,
        references=new_references,
        mapping_results=mapping_results,
        mapping_types=mapping_types,
        validation=new_validation,
        messages=new_messages,
    )


def add_mapping(
    result: StandardsMappingResult,
    standard_id: str,
    target_id: str,
    mapping_type: str = "mapped",
) -> StandardsMappingResult:
    """Add a mapping between a standard and target."""
    current_mappings = result.mapping_results.get(standard_id, [])
    new_items = current_mappings + [target_id]

    new_results = {**result.mapping_results, standard_id: new_items}
    new_types = {**result.mapping_types}
    new_types[mapping_type] = new_types.get(mapping_type, 0) + 1

    return replace(
        result,
        mapping_results=new_results,
        mapping_types=new_types,
    )


# ============================================================================
# Analysis and reporting
# ============================================================================


def get_standards_loading_summary(result: StandardsLoadingResult) -> LoadingSummaryDict:
    """Generate standards loading summary."""
    return {
        "standards_loaded": result.standards_count,
        "successful_loads": result.loading.loaded_count,
        "failed_loads": result.loading.failed_count,
        "frameworks_detected": result.frameworks.framework_count,
        "frameworks": dict(result.frameworks.framework_stats),
        "duplicate_ids": result.duplicates.duplicate_count,
        "processed_files": result.files.processed_file_count,
        "failed_files": result.files.failed_file_count,
        "skipped_files": result.files.skipped_file_count,
        "success_rate_percent": round(result.loading.success_rate * 100, 2),
        "loaded_standard_ids": result.loaded_standard_ids,
        "most_common_framework": result.frameworks.most_common_framework,
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
        "error_count": result.messages.error_count,
        "warning_count": result.messages.warning_count,
        "total_controls": result.get_control_count(),
    }


def get_standards_validation_summary(result: StandardsValidationResult) -> ValidationSummaryDict:
    """Generate standards validation summary."""
    return {
        "standards_validated": result.validated_count,
        "validation_passed": result.validation.passed_count,
        "validation_failed": result.validation.failed_count,
        "field_errors": result.field_error_count,
        "controls_validated": result.control_validation_count,
        "success_rate_percent": round(result.validation.pass_rate * 100, 2),
        "validation_rate": round(result.validation_rate * 100, 2),
        "failed_standards": result.get_failed_standards(),
        "passed_standards": result.get_passed_standards(),
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
    }


def get_mapping_summary(result: StandardsMappingResult) -> MappingSummaryDict:
    """Generate standards mapping summary."""
    return {
        "total_mappings": result.total_mappings_count,
        "mapped_standards": len(result.mapping_results),
        "mapping_types": dict(result.mapping_types),
        "duplicate_mappings": result.duplicate_mappings,
        "orphaned_controls": result.references.orphaned_items,
        "invalid_mappings": result.references.invalid_references,
        "has_duplicate_mappings": result.has_duplicate_mappings,
        "has_orphaned_controls": result.references.has_orphaned_items,
        "has_invalid_mappings": result.references.has_invalid_references,
        "mapping_coverage_rate": result.get_mapping_coverage_rate(),
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
    }


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Types
    "StandardsLoadingResult",
    "StandardsValidationResult",
    "StandardsMappingResult",
    "StandardsMappingDict",
    "StandardsControlDict",
    "StandardsItemDict",
    "StandardsDataDict",
    "ValidationResultsDict",
    "ValidationDetailsDict",
    "SeverityCountsDict",
    "MappingResultsDict",
    "MappingTypesDict",
    "ErrorSummaryDict",
    "LoadingSummaryDict",
    "ValidationSummaryDict",
    "MappingSummaryDict",
    # Base collections
    "FrameworkCollection",
    # Loading operations
    "add_standard",
    "track_invalid_standards_file",
    "track_skipped_standards_file",
    # Validation operations
    "validate_standard",
    "validate_standards_field",
    "batch_validate_standards",
    # Mapping operations
    "analyze_mappings",
    "add_mapping",
    # Summary functions
    "get_standards_loading_summary",
    "get_standards_validation_summary",
    "get_mapping_summary",
]
