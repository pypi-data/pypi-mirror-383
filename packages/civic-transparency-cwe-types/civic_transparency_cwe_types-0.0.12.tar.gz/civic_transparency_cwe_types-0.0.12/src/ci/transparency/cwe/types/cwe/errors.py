"""CWE domain error types using enhanced base classes.

Domain-specific error hierarchy for CWE operations. Each error inherits from
exactly one enhanced base error class and leverages the flexible context system
for CWE-specific information.

Design principles:
    - Single inheritance: each error extends exactly one base error class
    - Context-rich: uses the flexible context system for CWE details
    - Consistent: maintains uniform error formatting across all errors
    - Minimal: leverages base class functionality rather than duplicating code

Usage patterns:
    - File operations → FileError, LoadingError, ParsingError
    - Validation operations → ValidationError
    - Processing operations → OperationError
    - General operations → BaseTransparencyError

Typical usage:
    from ci.transparency.cwe.types.cwe import CweValidationError

    raise CweValidationError(
        "Field validation failed",
        item_id="CWE-79",
        field_path="relationships[0].id",
        validation_rule="required_field",
        file_path="cwe-79.yaml"
    )
    # Output: "Field validation failed | Item: CWE-79 | Field: relationships[0].id | Rule: required_field | File: cwe-79.yaml"
"""

from pathlib import Path
from typing import Any

from ci.transparency.cwe.types.base.errors import (
    BaseTransparencyError,
    FileError,
    LoadingError,
    OperationError,
    ParsingError,
    ValidationError,
)

# ============================================================================
# CWE loading error types (file-based operations)
# ============================================================================


class CweLoadingError(LoadingError):
    """Base CWE loading error."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        category: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE loading error.

        Args:
            message: The error message
            cwe_id: Optional CWE identifier (e.g., "CWE-79")
            category: Optional CWE category
            file_path: Optional file path where the error occurred
            **kwargs: Additional context passed to base class
        """
        super().__init__(
            message,
            file_path=file_path,
            item_id=cwe_id,
            validation_context=f"Category: {category}" if category else None,
            **kwargs,
        )


class CweFileNotFoundError(LoadingError):
    """CWE definition file could not be found."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE file not found error."""
        super().__init__(
            message,
            file_path=file_path,
            item_id=cwe_id,
            **kwargs,
        )


class CweParsingError(ParsingError):
    """CWE definition file could not be parsed."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        parser_type: str | None = None,
        line_number: int | None = None,
        parse_details: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE parsing error."""
        super().__init__(
            message,
            file_path=file_path,
            parser_type=parser_type,
            line_number=line_number,
            parse_details=parse_details,
            item_id=cwe_id,  # CWE-specific context
            **kwargs,
        )


class CweDuplicateError(LoadingError):
    """Duplicate CWE ID detected during loading."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        existing_file: Path | str | None = None,
        duplicate_file: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE duplicate error.

        Args:
            message: The duplicate error message
            cwe_id: Optional CWE identifier that's duplicated
            existing_file: Optional path to the existing CWE file
            duplicate_file: Optional path to the duplicate CWE file
            **kwargs: Additional context passed to base class
        """
        # Build validation context with file paths
        context_parts: list[str] = []
        if existing_file:
            context_parts.append(f"Existing: {existing_file}")
        if duplicate_file:
            context_parts.append(f"Duplicate: {duplicate_file}")

        validation_context: str | None = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            file_path=duplicate_file,
            item_id=cwe_id,
            validation_context=validation_context,
            **kwargs,
        )


class CweInvalidFormatError(FileError):
    """CWE definition format is invalid or unsupported."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        expected_format: str | None = None,
        detected_format: str | None = None,
        format_issue: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE invalid format error.

        Args:
            message: The format error message
            cwe_id: Optional CWE identifier
            expected_format: Optional expected format (e.g., "YAML")
            detected_format: Optional detected format
            format_issue: Optional description of the format issue
            file_path: Optional file path with format issue
            **kwargs: Additional context passed to base class
        """
        # Build validation context with format details
        context_parts: list[str] = []
        if expected_format:
            context_parts.append(f"Expected: {expected_format}")
        if detected_format:
            context_parts.append(f"Detected: {detected_format}")
        if format_issue:
            context_parts.append(f"Issue: {format_issue}")

        validation_context: str | None = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            file_path=file_path,
            item_id=cwe_id,
            validation_context=validation_context,
            **kwargs,
        )


class CweMissingFieldError(LoadingError):
    """Required CWE field is missing from definition."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        field_name: str | None = None,
        required_fields: list[str] | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE missing field error.

        Args:
            message: The missing field error message
            cwe_id: Optional CWE identifier
            field_name: Optional name of the missing field
            required_fields: Optional list of all required fields
            file_path: Optional file path with missing field
            **kwargs: Additional context passed to base class
        """
        # Build validation context with field requirements
        context_parts: list[str] = []
        if required_fields:
            required: str = ", ".join(required_fields)
            context_parts.append(f"Required: {required}")

        validation_context: str | None = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            file_path=file_path,
            item_id=cwe_id,
            field_path=field_name,
            validation_context=validation_context,
            **kwargs,
        )


# ============================================================================
# CWE validation error types
# ============================================================================


class CweValidationError(ValidationError):
    """Base CWE validation error."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        category: str | None = None,
        validation_type: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE validation error.

        Args:
            message: The validation error message
            cwe_id: Optional CWE identifier
            category: Optional CWE category
            validation_type: Optional type of validation
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        # Build validation context with category and type
        context_parts: list[str] = []
        if category:
            context_parts.append(f"Category: {category}")
        if validation_type:
            context_parts.append(f"Type: {validation_type}")

        validation_context: str | None = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=cwe_id,
            file_path=file_path,
            validation_context=validation_context,
            **kwargs,
        )


class CweFieldValidationError(ValidationError):
    """CWE field-level validation failed."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        field_name: str | None = None,
        field_value: str | None = None,
        validation_rule: str | None = None,
        expected_value: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE field validation error.

        Args:
            message: The field validation error message
            cwe_id: Optional CWE identifier
            field_name: Optional name of the field that failed validation
            field_value: Optional actual value of the field
            validation_rule: Optional validation rule that was violated
            expected_value: Optional expected value for the field
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        # Build validation context with field details
        context_parts: list[str] = []
        if field_value is not None:
            context_parts.append(f"Value: {field_value}")
        if expected_value:
            context_parts.append(f"Expected: {expected_value}")

        validation_context: str | None = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=cwe_id,
            field_path=field_name,
            validation_rule=validation_rule,
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


class CweSchemaValidationError(ValidationError):
    """CWE schema validation failed."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        schema_name: str | None = None,
        schema_version: str | None = None,
        field_path: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE schema validation error.

        Args:
            message: The schema validation error message
            cwe_id: Optional CWE identifier
            schema_name: Optional name of the schema
            schema_version: Optional version of the schema
            field_path: Optional path to the field that failed
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        # Combine schema name and version
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        super().__init__(
            message,
            item_id=cwe_id,
            schema_name=combined_schema,
            field_path=field_path,
            file_path=file_path,
            **kwargs,
        )


class CweConstraintViolationError(ValidationError):
    """CWE constraint validation failed."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        category: str | None = None,
        constraint_name: str | None = None,
        constraint_value: str | None = None,
        actual_value: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE constraint violation error.

        Args:
            message: The constraint violation error message
            cwe_id: Optional CWE identifier
            category: Optional CWE category
            constraint_name: Optional name of the constraint
            constraint_value: Optional expected constraint value
            actual_value: Optional actual value that violated the constraint
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        # Build validation context with constraint details
        context_parts: list[str] = []
        if category:
            context_parts.append(f"Category: {category}")
        if constraint_name:
            context_parts.append(f"Constraint: {constraint_name}")
        if constraint_value:
            context_parts.append(f"Expected: {constraint_value}")
        if actual_value:
            context_parts.append(f"Actual: {actual_value}")

        validation_context: str | None = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=cwe_id,
            validation_rule="constraint",
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


# ============================================================================
# CWE relationship error types
# ============================================================================


class CweRelationshipError(ValidationError):
    """CWE relationship validation failed."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        related_cwe_id: str | None = None,
        relationship_type: str | None = None,
        relationship_direction: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize CWE relationship error.

        Args:
            message: The relationship error message
            cwe_id: Optional source CWE identifier
            related_cwe_id: Optional ID of the related CWE
            relationship_type: Optional type of relationship
            relationship_direction: Optional direction
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        # Build validation context with relationship details
        context_parts: list[str] = []
        if related_cwe_id:
            context_parts.append(f"Related: {related_cwe_id}")
        if relationship_type:
            context_parts.append(f"Type: {relationship_type}")
        if relationship_direction:
            context_parts.append(f"Direction: {relationship_direction}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=cwe_id,
            validation_rule="relationship",
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


class CweCircularRelationshipError(ValidationError):
    """Circular CWE relationship detected."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        relationship_chain: list[str] | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize CWE circular relationship error.

        Args:
            message: The circular relationship error message
            cwe_id: Optional source CWE identifier
            relationship_chain: Optional chain of CWE IDs that form the cycle
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        # Build validation context with relationship chain
        validation_context = None
        if relationship_chain:
            chain = " → ".join(relationship_chain)
            validation_context = f"Chain: {chain}"

        super().__init__(
            message,
            item_id=cwe_id,
            validation_rule="circular_relationship",
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


class CweOrphanedError(ValidationError):
    """CWE has no valid relationships."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        category: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize CWE orphaned error.

        Args:
            message: The orphaned error message
            cwe_id: Optional CWE identifier that's orphaned
            category: Optional CWE category
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        super().__init__(
            message,
            item_id=cwe_id,
            validation_rule="orphaned",
            validation_context=f"Category: {category}" if category else None,
            file_path=file_path,
            **kwargs,
        )


class CweInvalidReferenceError(ValidationError):
    """CWE relationship references unknown CWE ID."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        related_cwe_id: str | None = None,
        reference_source: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize CWE invalid reference error.

        Args:
            message: The invalid reference error message
            cwe_id: Optional source CWE identifier
            related_cwe_id: Optional ID that couldn't be found
            reference_source: Optional source of the reference
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        # Build validation context with reference details
        context_parts: list[str] = []
        if related_cwe_id:
            context_parts.append(f"Related: {related_cwe_id}")
        if reference_source:
            context_parts.append(f"Source: {reference_source}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=cwe_id,
            validation_rule="invalid_reference",
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


# ============================================================================
# CWE processing error types
# ============================================================================


class CweProcessingError(OperationError):
    """CWE processing operation failed."""

    def __init__(
        self,
        message: str,
        *,
        operation: str | None = None,
        processed_count: int | None = None,
        total_count: int | None = None,
        **kwargs: Any,
    ):
        """Initialize CWE processing error.

        Args:
            message: The processing error message
            operation: Optional name of the operation being performed
            processed_count: Optional number of items processed before failure
            total_count: Optional total number of items to process
            **kwargs: Additional context passed to base class
        """
        super().__init__(
            message,
            operation=operation,
            processed_count=processed_count,
            total_count=total_count,
            **kwargs,
        )


class CweIntegrityError(ValidationError):
    """CWE data integrity violation."""

    def __init__(
        self,
        message: str,
        *,
        cwe_id: str | None = None,
        integrity_check: str | None = None,
        expected_value: str | None = None,
        actual_value: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize CWE integrity error.

        Args:
            message: The integrity error message
            cwe_id: Optional CWE identifier
            integrity_check: Optional name of the integrity check that failed
            expected_value: Optional expected value
            actual_value: Optional actual value found
            file_path: Optional file path being checked
            **kwargs: Additional context passed to base class
        """
        # Build validation context with integrity details
        context_parts: list[str] = []
        if integrity_check:
            context_parts.append(f"Check: {integrity_check}")
        if expected_value:
            context_parts.append(f"Expected: {expected_value}")
        if actual_value:
            context_parts.append(f"Actual: {actual_value}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=cwe_id,
            validation_rule="integrity",
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


class CweConfigurationError(BaseTransparencyError):
    """CWE configuration error."""

    def __init__(
        self,
        message: str,
        *,
        config_key: str | None = None,
        config_value: str | None = None,
        valid_values: list[str] | None = None,
        **kwargs: Any,
    ):
        """Initialize CWE configuration error.

        Args:
            message: The configuration error message
            config_key: Optional configuration key that caused the error
            config_value: Optional invalid configuration value
            valid_values: Optional list of valid configuration values
            **kwargs: Additional context passed to base class
        """
        # Build validation context with valid values
        validation_context = None
        if valid_values:
            valid_str = ", ".join(valid_values)
            validation_context = f"Valid: {valid_str}"

        super().__init__(
            message,
            item_id=config_key,
            validation_context=validation_context,
            error_code=config_value,
            **kwargs,
        )


# ============================================================================
# Public API (alphabetical)
# ============================================================================

__all__ = [
    "CweCircularRelationshipError",
    "CweConfigurationError",
    "CweConstraintViolationError",
    "CweDuplicateError",
    "CweFieldValidationError",
    "CweFileNotFoundError",
    "CweIntegrityError",
    "CweInvalidFormatError",
    "CweInvalidReferenceError",
    "CweLoadingError",
    "CweMissingFieldError",
    "CweOrphanedError",
    "CweParsingError",
    "CweProcessingError",
    "CweRelationshipError",
    "CweSchemaValidationError",
    "CweValidationError",
]
