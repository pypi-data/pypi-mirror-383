"""CWE domain result types and operations using composition."""

from collections import defaultdict
from dataclasses import dataclass, field, replace
from pathlib import Path
import re
from typing import Any, Literal, TypedDict, cast

from ci.transparency.cwe.types.base.collections import (
    CategoryCollection,
    DuplicateCollection,
    FileCollection,
    ReferenceCollection,
    RelationshipDepthsDict,
    RelationshipMapDict,
    RelationshipTypesDict,
)
from ci.transparency.cwe.types.base.counts import LoadingCounts, ValidationCounts
from ci.transparency.cwe.types.base.messages import MessageCollection
from ci.transparency.cwe.types.base.result_helpers import with_message_methods

# ============================================================================
# Typed structures for CWE data
# ============================================================================

type RelationshipType = Literal[
    "related",  # string-only fallback
    "parent",
    "child",
    "variant",
    "requires",
    "causes",
    "consequence",
    "unknown",  # escape hatch
]


class CweRelationshipDict(TypedDict, total=False):
    """Typed structure for CWE relationship data."""

    cwe_id: str
    type: RelationshipType
    description: str


type CweRelationshipLike = CweRelationshipDict | str
type CweDataDict = dict[str, CweItemDict]
type ValidationResultsDict = dict[str, bool]
type ValidationDetailsDict = dict[str, list[str]]
type SeverityCountsDict = dict[str, int]
type ErrorSummaryDict = dict[str, Any]
type LoadingSummaryDict = dict[str, Any]
type ValidationSummaryDict = dict[str, Any]
type RelationshipStatisticsDict = dict[str, Any]
type RelationshipSummaryDict = dict[str, Any]


class CweItemDict(TypedDict, total=False):
    """Minimal shape of a single CWE record (extend as needed)."""

    id: str
    name: str
    description: str
    category: str
    relationships: list[CweRelationshipLike]
    source_path: str  # store as str for JSON-compat; convert to Path at edges


# ============================================================================
# Core result dataclasses using composition
# ============================================================================


@with_message_methods
@dataclass(frozen=True)
class CweLoadingResult:
    """Represents the result of loading CWE data using composition.

    Composes base building blocks for clean separation of concerns.

    Attributes
    ----------
    cwes : CweDataDict
        Dictionary of loaded CWE data.
    loading : LoadingCounts
        Statistics about loading success and failures.
    messages : MessageCollection
        Collection of error, warning, and info messages.
    files : FileCollection
        Tracking of processed, failed, and skipped files.
    categories : CategoryCollection
        Statistics for categories encountered.
    duplicates : DuplicateCollection
        Tracking of duplicate IDs and their associated files.
    """

    cwes: CweDataDict = cast("CweDataDict", field(default_factory=dict))
    loading: LoadingCounts = field(default_factory=LoadingCounts)
    messages: MessageCollection = field(default_factory=MessageCollection)
    files: FileCollection = field(default_factory=FileCollection)
    categories: CategoryCollection = field(default_factory=CategoryCollection)
    duplicates: DuplicateCollection = field(default_factory=DuplicateCollection)

    @property
    def cwe_count(self) -> int:
        """Return the number of CWEs loaded."""
        return len(self.cwes)

    @property
    def is_successful(self) -> bool:
        """Return True if loading is successful and there are no error messages."""
        return self.loading.is_successful and not self.messages.has_errors

    @property
    def loaded_cwe_ids(self) -> list[str]:
        """All loaded CWE IDs (sorted for stable output)."""
        return sorted(self.cwes.keys())

    def get_cwe(self, cwe_id: str) -> CweItemDict | None:
        """Get CWE data by ID."""
        return self.cwes.get(cwe_id)

    def has_cwe(self, cwe_id: str) -> bool:
        """Check if a CWE ID was loaded."""
        return cwe_id in self.cwes

    def get_cwes_by_category(self, category: str) -> CweDataDict:
        """Get CWEs filtered by category."""
        return {
            cwe_id: cwe_data
            for cwe_id, cwe_data in self.cwes.items()
            if cwe_data.get("category") == category
        }

    def search_cwes(self, search_term: str) -> CweDataDict:
        """Search CWEs by name or description."""
        search_lower = search_term.lower()
        return {
            cwe_id: cwe_data
            for cwe_id, cwe_data in self.cwes.items()
            if (
                search_lower in cwe_data.get("name", "").lower()
                or search_lower in cwe_data.get("description", "").lower()
            )
        }

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "CweLoadingResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "CweLoadingResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "CweLoadingResult":
        """Add info message (added by decorator)."""
        ...  # Overridden by decorator


@with_message_methods
@dataclass(frozen=True)
class CweValidationResult:
    """Represents the result of validating CWE data using composition.

    Attributes
    ----------
    validation_results : ValidationResultsDict
        Dictionary of validation results for each CWE item.
    validation : ValidationCounts
        Statistics about validation success and failures.
    messages : MessageCollection
        Collection of error, warning, and info messages.
    field_errors : list[str]
        Field-level validation errors.
    validation_details : ValidationDetailsDict
        Detailed validation errors per CWE.
    severity_counts : SeverityCountsDict
        Count of issues by severity level.
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

    @property
    def validated_count(self) -> int:
        """Return the number of items that have been validated."""
        return len(self.validation_results)

    @property
    def is_successful(self) -> bool:
        """Return True if validation is successful and there are no error messages."""
        return self.validation.is_successful and not self.messages.has_errors

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

    def get_failed_cwes(self) -> list[str]:
        """Get list of CWE IDs that failed validation."""
        return [cwe_id for cwe_id, result in self.validation_results.items() if not result]

    def get_passed_cwes(self) -> list[str]:
        """Get list of CWE IDs that passed validation."""
        return [cwe_id for cwe_id, result in self.validation_results.items() if result]

    def get_validation_errors(self, cwe_id: str) -> list[str]:
        """Get validation errors for a specific CWE."""
        return self.validation_details.get(cwe_id, [])

    def get_most_common_errors(self, limit: int = 5) -> list[tuple[str, int]]:
        """Get most common validation errors."""
        error_counts: dict[str, int] = {}
        for errors in self.validation_details.values():
            for error in errors:
                error_counts[error] = error_counts.get(error, 0) + 1

        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_errors[:limit]

    def get_error_summary(self) -> ErrorSummaryDict:
        """Get comprehensive error summary."""
        return {
            "total_errors": sum(len(errors) for errors in self.validation_details.values()),
            "cwes_with_errors": len(
                [cwe for cwe, errors in self.validation_details.items() if errors]
            ),
            "most_common_errors": self.get_most_common_errors(),
            "severity_distribution": dict(self.severity_counts),
        }

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "CweValidationResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "CweValidationResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "CweValidationResult":
        """Add info message (added by decorator)."""
        ...  # Overridden by decorator


@with_message_methods
@dataclass(frozen=True)
class CweRelationshipResult:
    """Result from CWE relationship validation and analysis using composition.

    Tracks CWE relationship consistency, circular dependency detection,
    and relationship graph analysis.

    Attributes
    ----------
    validation : ValidationCounts
        Statistics about relationship validation.
    messages : MessageCollection
        Collection of error, warning, and info messages.
    references : ReferenceCollection
        Tracking of references between CWEs.
    relationship_depths : RelationshipDepthsDict
        Depth of each CWE in the relationship graph.
    relationship_types : RelationshipTypesDict
        Count of relationship types.
    circular_dependencies : list[str]
        CWEs involved in circular dependencies.
    """

    validation: ValidationCounts = field(default_factory=ValidationCounts)
    messages: MessageCollection = field(default_factory=MessageCollection)
    references: ReferenceCollection = field(default_factory=ReferenceCollection)
    relationship_depths: RelationshipDepthsDict = cast(
        "RelationshipDepthsDict", field(default_factory=dict)
    )
    relationship_types: RelationshipTypesDict = cast(
        "RelationshipTypesDict", field(default_factory=dict)
    )
    circular_dependencies: list[str] = cast("list[str]", field(default_factory=list))

    @property
    def circular_dependency_count(self) -> int:
        """Number of circular dependencies detected."""
        return len(self.circular_dependencies)

    @property
    def max_relationship_depth(self) -> int:
        """Maximum relationship depth in the graph."""
        return max(self.relationship_depths.values()) if self.relationship_depths else 0

    @property
    def is_successful(self) -> bool:
        """Return True if relationship analysis is successful."""
        return self.validation.is_successful and not self.messages.has_errors

    @property
    def has_circular_dependencies(self) -> bool:
        """True if circular dependencies were detected."""
        return bool(self.circular_dependencies)

    def get_relationships(self, cwe_id: str) -> list[str]:
        """Get all relationships for a specific CWE."""
        return self.references.reference_map.get(cwe_id, [])

    def get_relationship_depth(self, cwe_id: str) -> int:
        """Get relationship depth for a specific CWE."""
        return self.relationship_depths.get(cwe_id, 0)

    def get_related_cwes(self, cwe_id: str, max_depth: int = 1) -> set[str]:
        """Get all CWEs related to a given CWE up to max_depth."""
        related: set[str] = set()
        current_level: set[str] = {cwe_id}

        for _depth in range(max_depth):
            next_level: set[str] = set()
            for current_cwe in current_level:
                for related_cwe in self.get_relationships(current_cwe):
                    if related_cwe not in related and related_cwe != cwe_id:
                        related.add(related_cwe)
                        next_level.add(related_cwe)
            current_level = next_level
            if not current_level:
                break

        return related

    def find_relationship_path(self, from_cwe: str, to_cwe: str) -> list[str] | None:
        """Find shortest path between two CWEs."""
        return _find_shortest_path(self.references.reference_map, from_cwe, to_cwe)

    def get_relationship_statistics(self) -> RelationshipStatisticsDict:
        """Get comprehensive relationship statistics."""
        return {
            "total_relationships": self.references.total_references_count,
            "connected_cwes": len(self.references.reference_map),
            "orphaned_cwes": self.references.orphaned_item_count,
            "circular_dependencies": self.circular_dependency_count,
            "invalid_references": self.references.invalid_reference_count,
            "relationship_types": dict(self.relationship_types),
            "max_depth": self.max_relationship_depth,
            "avg_relationships_per_cwe": (
                self.references.total_references_count / len(self.references.reference_map)
                if self.references.reference_map
                else 0
            ),
        }

    # Type hints for decorator-added methods (overridden at runtime)
    def add_error(self, msg: str) -> "CweRelationshipResult":
        """Add error message (added by decorator)."""
        ...  # Overridden by decorator

    def add_warning(self, msg: str) -> "CweRelationshipResult":
        """Add warning message (added by decorator)."""
        ...  # Overridden by decorator

    def add_info(self, msg: str) -> "CweRelationshipResult":
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


def _add_category(categories: CategoryCollection, category: str) -> CategoryCollection:
    """Add or increment a category count."""
    new_stats = {**categories.category_stats}
    new_stats[category] = new_stats.get(category, 0) + 1
    return replace(categories, category_stats=new_stats)


def _add_duplicate(
    duplicates: DuplicateCollection, item_id: str, file_path: Path
) -> DuplicateCollection:
    """Add a duplicate ID with its file path."""
    new_duplicate_ids = {**duplicates.duplicate_ids}
    current_paths = new_duplicate_ids.get(item_id, [])
    new_duplicate_ids[item_id] = current_paths + [file_path]
    return replace(duplicates, duplicate_ids=new_duplicate_ids)


# ============================================================================
# CWE loading operations
# ============================================================================


def add_cwe(
    result: CweLoadingResult,
    cwe_id: str,
    cwe_data: CweItemDict,
    *,
    file_path: Path | None = None,
) -> CweLoadingResult:
    """Add successfully loaded CWE to the result."""
    # Check for duplicates
    if cwe_id in result.cwes:
        if file_path is not None:
            new_duplicates = _add_duplicate(result.duplicates, cwe_id, file_path)
            result = replace(result, duplicates=new_duplicates)

        new_messages = _add_message(result.messages, "warning", f"Duplicate CWE ID found: {cwe_id}")
        new_loading = _increment_loading_counts(result.loading, failed=1)
        return replace(result, messages=new_messages, loading=new_loading)

    # Update category statistics
    category = str(cwe_data.get("category", "unknown"))
    new_categories = _add_category(result.categories, category)

    # Add the CWE
    new_cwes = {**result.cwes, cwe_id: cwe_data}
    new_messages = _add_message(
        result.messages, "info", f"Loaded CWE {cwe_id}: {cwe_data.get('name', 'unnamed')}"
    )

    # Update file tracking if file_path provided
    new_files = result.files
    if file_path is not None:
        new_files = _add_processed_file(result.files, file_path)

    new_loading = _increment_loading_counts(result.loading, succeeded=1)

    return replace(
        result,
        cwes=new_cwes,
        categories=new_categories,
        files=new_files,
        loading=new_loading,
        messages=new_messages,
    )


def track_invalid_file(result: CweLoadingResult, file_path: Path, reason: str) -> CweLoadingResult:
    """Track an invalid CWE file."""
    new_messages = _add_message(result.messages, "error", f"Invalid CWE file {file_path}: {reason}")
    new_files = _add_failed_file(result.files, file_path)
    new_loading = _increment_loading_counts(result.loading, failed=1)
    return replace(result, messages=new_messages, files=new_files, loading=new_loading)


def track_skipped_cwe_file(
    result: CweLoadingResult,
    file_path: Path,
    reason: str,
) -> CweLoadingResult:
    """Track a skipped CWE file."""
    new_messages = _add_message(result.messages, "info", f"Skipped CWE file {file_path}: {reason}")
    new_files = _add_skipped_file(result.files, file_path)
    return replace(result, messages=new_messages, files=new_files)


# ============================================================================
# CWE validation operations
# ============================================================================


def validate_cwe(
    result: CweValidationResult,
    cwe_id: str,
    cwe_data: CweItemDict,
) -> CweValidationResult:
    """Validate a CWE definition with comprehensive field validation."""
    req_errors, req_sev = _validate_required_fields(cwe_data)
    opt_errors, opt_sev = _validate_optional_fields(cwe_data)
    rel_errors, rel_sev = _validate_relationships(cwe_data)

    errors = req_errors + opt_errors + rel_errors
    severity = _max_severity(req_sev, opt_sev, rel_sev)
    is_valid = not errors

    # Record validation result
    new_results = {**result.validation_results, cwe_id: is_valid}
    new_details = {**result.validation_details}
    new_severity_counts = {**result.severity_counts}
    new_messages = result.messages

    if errors:
        new_details[cwe_id] = errors
        new_severity_counts[severity] = new_severity_counts.get(severity, 0) + 1
        new_messages = _add_message(
            new_messages, "error", f"Validation failed for {cwe_id}: {len(errors)} issues"
        )

    new_validation = _increment_validation_counts(
        result.validation, passed=1 if is_valid else 0, failed=0 if is_valid else 1
    )

    return replace(
        result,
        validation_results=new_results,
        validation_details=new_details,
        severity_counts=new_severity_counts,
        validation=new_validation,
        messages=new_messages,
    )


def validate_cwe_field(
    result: CweValidationResult,
    cwe_id: str,
    field_path: str,
    field_value: Any,
    validation_rule: str,
) -> CweValidationResult:
    """Validate a specific CWE field."""
    is_field_valid = True
    error_msg = ""

    if field_value is None:
        is_field_valid = False
        error_msg = f"Field {field_path} is required but missing"
    elif isinstance(field_value, str) and len(field_value.strip()) == 0:
        is_field_valid = False
        error_msg = f"Field {field_path} cannot be empty"
    elif field_path == "id" and (
        not isinstance(field_value, str) or not _is_valid_cwe_id(field_value)
    ):
        is_field_valid = False
        error_msg = f"Field {field_path} has invalid CWE ID format"

    if not is_field_valid:
        full_error_msg = (
            f"Field validation failed for {cwe_id}.{field_path}: {error_msg} ({validation_rule})"
        )
        new_messages = _add_message(result.messages, "error", full_error_msg)
        new_field_errors = result.field_errors + [f"{cwe_id}.{field_path}"]
        new_validation = _increment_validation_counts(result.validation, failed=1)
        return replace(
            result, field_errors=new_field_errors, validation=new_validation, messages=new_messages
        )

    new_validation = _increment_validation_counts(result.validation, passed=1)
    return replace(result, validation=new_validation)


def batch_validate_cwes(
    result: CweValidationResult,
    cwe_dict: CweDataDict,
) -> CweValidationResult:
    """Validate multiple CWEs in batch."""
    for cwe_id, cwe_data in cwe_dict.items():
        result = validate_cwe(result, cwe_id, cwe_data)

    new_messages = _add_message(result.messages, "info", f"Batch validated {len(cwe_dict)} CWEs")
    return replace(result, messages=new_messages)


# ============================================================================
# CWE relationship operations
# ============================================================================


def _process_relationship_item(
    relationship: CweRelationshipLike,
    _relationship_types: RelationshipTypesDict,
) -> tuple[str | None, RelationshipType]:
    if isinstance(relationship, str):
        return relationship, "related"
    rid_obj = relationship.get("cwe_id")
    rtype_obj = relationship.get("type", "unknown")
    related_id: str | None = rid_obj if isinstance(rid_obj, str) else None
    rel_type: RelationshipType = rtype_obj
    return (related_id, rel_type) if related_id is not None else (None, "unknown")


def _build_relationship_map(
    cwe_dict: CweDataDict,
) -> tuple[RelationshipMapDict, RelationshipTypesDict, list[str], list[str]]:
    """Build relationship map and identify invalid references and orphaned items."""
    relationship_map: RelationshipMapDict = {}
    relationship_types: RelationshipTypesDict = {}
    invalid_references: list[str] = []
    orphaned_cwes: list[str] = []

    for cwe_id, cwe_data in cwe_dict.items():
        # Explicit type annotation for relationships
        relationships = cwe_data.get("relationships", [])
        related_ids: list[str] = []

        for relationship in relationships:
            related_id, rel_type = _process_relationship_item(relationship, relationship_types)

            if related_id:
                related_ids.append(related_id)
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1

                # Check if reference is valid
                if related_id not in cwe_dict:
                    invalid_references.append(f"{cwe_id} → {related_id}")

        if related_ids:
            relationship_map[cwe_id] = related_ids
        else:
            orphaned_cwes.append(cwe_id)

    return relationship_map, relationship_types, invalid_references, orphaned_cwes


def analyze_relationships(
    result: CweRelationshipResult,
    cwe_dict: CweDataDict,
) -> CweRelationshipResult:
    """Analyze CWE relationships for consistency and detect issues."""
    # Build relationship map and identify issues
    relationship_map, relationship_types, invalid_references, orphaned_cwes = (
        _build_relationship_map(cwe_dict)
    )

    # Create reference collection
    new_references = ReferenceCollection(
        reference_map=relationship_map,
        invalid_references=invalid_references,
        orphaned_items=orphaned_cwes,
    )

    # Detect circular dependencies
    circular_deps = _detect_circular_dependencies(relationship_map)

    # Calculate relationship depths
    relationship_depths: RelationshipDepthsDict = {}
    for cid in cwe_dict:
        relationship_depths[cid] = _calculate_relationship_depth(relationship_map, cid, set())

    # Update messages
    new_messages = _add_message(
        result.messages, "info", f"Analyzed relationships for {len(cwe_dict)} CWEs"
    )
    if circular_deps:
        new_messages = _add_message(
            new_messages, "warning", f"Found {len(circular_deps)} CWEs in circular dependencies"
        )
    if invalid_references:
        new_messages = _add_message(
            new_messages,
            "error",
            f"Found {len(invalid_references)} invalid relationship references",
        )

    new_validation = _increment_validation_counts(
        result.validation,
        passed=len(cwe_dict) - len(invalid_references),
        failed=len(invalid_references),
    )

    return replace(
        result,
        references=new_references,
        relationship_types=relationship_types,
        relationship_depths=relationship_depths,
        circular_dependencies=circular_deps,
        validation=new_validation,
        messages=new_messages,
    )


# ============================================================================
# Analysis and reporting
# ============================================================================


def get_cwe_loading_summary(result: CweLoadingResult) -> LoadingSummaryDict:
    """Generate CWE loading summary."""
    return {
        "cwes_loaded": result.cwe_count,
        "successful_loads": result.loading.loaded_count,
        "failed_loads": result.loading.failed_count,
        "duplicate_ids": result.duplicates.duplicate_count,
        "processed_files": result.files.processed_file_count,
        "failed_files": result.files.failed_file_count,
        "skipped_files": result.files.skipped_file_count,
        "success_rate_percent": round(result.loading.success_rate * 100, 2),
        "loaded_cwe_ids": result.loaded_cwe_ids,
        "categories": list(result.categories.category_stats.keys()),
        "category_distribution": dict(result.categories.category_stats),
        "most_common_category": result.categories.most_common_category,
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
        "error_count": result.messages.error_count,
        "warning_count": result.messages.warning_count,
    }


def get_cwe_validation_summary(result: CweValidationResult) -> ValidationSummaryDict:
    """Generate CWE validation summary."""
    return {
        "cwes_validated": result.validated_count,
        "validation_passed": result.validation.passed_count,
        "validation_failed": result.validation.failed_count,
        "field_errors": result.field_error_count,
        "success_rate_percent": round(result.validation.pass_rate * 100, 2),
        "validation_rate": round(result.validation_rate * 100, 2),
        "failed_cwes": result.get_failed_cwes(),
        "passed_cwes": result.get_passed_cwes(),
        "error_summary": result.get_error_summary(),
        "most_common_errors": result.get_most_common_errors(),
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
    }


def get_relationship_summary(result: CweRelationshipResult) -> RelationshipSummaryDict:
    """Generate CWE relationship summary."""
    stats = result.get_relationship_statistics()
    return {
        "total_relationships": result.references.total_references_count,
        "connected_cwes": len(result.references.reference_map),
        "relationship_types": dict(result.relationship_types),
        "circular_dependencies": result.circular_dependencies,
        "orphaned_cwes": result.references.orphaned_items,
        "invalid_references": result.references.invalid_references,
        "has_circular_dependencies": result.has_circular_dependencies,
        "has_orphaned_cwes": result.references.has_orphaned_items,
        "max_relationship_depth": result.max_relationship_depth,
        "relationship_statistics": stats,
        "invalid_reference_rate": (
            result.references.invalid_reference_count / result.references.total_references_count
            if result.references.total_references_count > 0
            else 0
        ),
        "has_errors": result.messages.has_errors,
        "has_warnings": result.messages.has_warnings,
    }


# ============================================================================
# Helpers (internal)
# ============================================================================


def _raise_severity(current: str, candidate: str) -> str:
    """Return the higher-severity label according to _severity_order()."""
    return max(current, candidate, key=_severity_order)


def _validate_required_fields(cwe_data: CweItemDict) -> tuple[list[str], str]:
    """Validate required CWE fields: id, name, description (recommended)."""
    errors: list[str] = []
    severity: str = "info"

    cid = cwe_data.get("id")
    if not cid:
        errors.append("Missing required field: id")
        severity = "error"
    elif not _is_valid_cwe_id(str(cid)):
        errors.append(f"Invalid CWE ID format: {cid}")
        severity = "error"

    name = cwe_data.get("name")
    if not name:
        errors.append("Missing required field: name")
        severity = "error"
    elif len(str(name)) < 3:
        errors.append("CWE name too short (minimum 3 characters)")
        severity = _raise_severity(severity, "warning")

    desc = cwe_data.get("description")
    if not desc:
        errors.append("Missing recommended field: description")
        severity = _raise_severity(severity, "warning")
    elif len(str(desc)) < 10:
        errors.append("Description too short (minimum 10 characters)")
        severity = _raise_severity(severity, "warning")

    return errors, severity


def _validate_optional_fields(cwe_data: CweItemDict) -> tuple[list[str], str]:
    """Validate optional-but-constrained fields: category."""
    errors: list[str] = []
    severity: str = "info"

    category = cwe_data.get("category")
    if category and not _is_valid_category(str(category)):
        errors.append(f"Invalid category: {category}")
        severity = _raise_severity(severity, "warning")

    return errors, severity


def _validate_relationships(cwe_data: CweItemDict) -> tuple[list[str], str]:
    """Validate relationships: presence of cwe_id and its format."""
    errors: list[str] = []
    severity: str = "info"

    rels = cwe_data.get("relationships")
    relationships: list[CweRelationshipLike] = rels if isinstance(rels, list) else []
    for i, rel in enumerate(relationships):
        if isinstance(rel, str):
            if not _is_valid_cwe_id(rel):
                errors.append(f"Relationship {i}: invalid cwe_id format")
                severity = _raise_severity(severity, "warning")
        else:
            # rel is CweRelationshipDict here
            rel_id_obj = rel.get("cwe_id")
            rel_id: str | None = rel_id_obj if isinstance(rel_id_obj, str) else None

            if not rel_id or rel_id.strip() == "":
                errors.append(f"Relationship {i}: missing cwe_id")
                severity = _raise_severity(severity, "warning")
            elif not _is_valid_cwe_id(rel_id):
                errors.append(f"Relationship {i}: invalid cwe_id format")
                severity = _raise_severity(severity, "warning")

    return errors, severity


def _max_severity(*labels: str) -> str:
    """Return the highest-severity label among the provided ones."""
    highest = "info"
    for lab in labels:
        highest = _raise_severity(highest, lab)
    return highest


def _detect_circular_dependencies(relationship_map: RelationshipMapDict) -> list[str]:
    """Detect circular dependencies in relationship map using DFS."""
    white, gray, black = 0, 1, 2
    color: dict[str, int] = defaultdict(lambda: white)
    circular_deps: set[str] = set()

    def dfs(node: str) -> bool:
        if color[node] == gray:
            return True
        if color[node] == black:
            return False

        color[node] = gray
        for neighbor in relationship_map.get(node, []):
            if dfs(neighbor):
                circular_deps.add(node)
                circular_deps.add(neighbor)
        color[node] = black
        return False

    for cwe_id in relationship_map:
        if color[cwe_id] == white:
            dfs(cwe_id)

    return list(circular_deps)


def _calculate_relationship_depth(
    relationship_map: RelationshipMapDict,
    cwe_id: str,
    visited: set[str],
) -> int:
    """Calculate relationship depth recursively with cycle detection."""
    if cwe_id in visited:
        return 0  # Circular dependency

    visited.add(cwe_id)
    relationships = relationship_map.get(cwe_id, [])
    if not relationships:
        return 1

    max_depth = 0
    for related_id in relationships:
        depth = _calculate_relationship_depth(relationship_map, related_id, visited.copy())
        max_depth = max(max_depth, depth)
    return max_depth + 1


def _find_shortest_path(
    relationship_map: RelationshipMapDict,
    start: str,
    end: str,
) -> list[str] | None:
    """Find shortest path between two CWEs using BFS."""
    if start == end:
        return [start]

    queue: list[tuple[str, list[str]]] = [(start, [start])]
    visited: set[str] = {start}

    while queue:
        current, path = queue.pop(0)
        for neighbor in relationship_map.get(current, []):
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None


def _is_valid_cwe_id(cwe_id: str) -> bool:
    """Validate CWE ID format."""
    pattern = r"^CWE-\d+$"
    return bool(re.match(pattern, cwe_id))


def _is_valid_category(category: str) -> bool:
    """Validate CWE category."""
    valid_categories = {
        "input_validation",
        "authentication",
        "authorization",
        "session_management",
        "cryptography",
        "error_handling",
        "code_quality",
        "race_conditions",
        "resource_management",
        "information_exposure",
        "injection",
        "path_traversal",
        "cross_site_scripting",
        "buffer_errors",
        "numeric_errors",
        "other",
    }
    return category.lower() in valid_categories


def _severity_order(severity: str) -> int:
    """Get severity order for comparison."""
    order = {"info": 0, "warning": 1, "error": 2}
    return order.get(severity, 0)


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Types
    "CweLoadingResult",
    "CweValidationResult",
    "CweRelationshipResult",
    "CweRelationshipDict",
    "CweRelationshipLike",
    "CweDataDict",
    "CweItemDict",
    "ValidationResultsDict",
    "ValidationDetailsDict",
    "SeverityCountsDict",
    "ErrorSummaryDict",
    "LoadingSummaryDict",
    "ValidationSummaryDict",
    "RelationshipStatisticsDict",
    "RelationshipSummaryDict",
    "RelationshipType",
    # Loading operations
    "add_cwe",
    "track_invalid_file",
    "track_skipped_cwe_file",
    # Validation operations
    "validate_cwe",
    "validate_cwe_field",
    "batch_validate_cwes",
    # Relationship operations
    "analyze_relationships",
    # Summary functions
    "get_cwe_loading_summary",
    "get_cwe_validation_summary",
    "get_relationship_summary",
]
