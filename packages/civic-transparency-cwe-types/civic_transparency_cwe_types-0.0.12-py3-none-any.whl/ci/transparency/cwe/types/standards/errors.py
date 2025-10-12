"""Standards domain error types using enhanced base classes.

Domain-specific error hierarchy for standards operations. Each error inherits from
exactly one enhanced base error class and leverages the flexible context system
for standards-specific information.

Design principles:
    - Single inheritance: each error extends exactly one base error class
    - Context-rich: uses the flexible context system for standards details
    - Consistent: maintains uniform error formatting across all errors
    - Minimal: leverages base class functionality rather than duplicating code

Usage patterns:
    - File operations → FileError, LoadingError, ParsingError
    - Validation operations → ValidationError
    - Processing operations → OperationError
    - General operations → BaseTransparencyError

Typical usage:
    from ci.transparency.cwe.types.standards import StandardsValidationError

    raise StandardsValidationError(
        "Field validation failed",
        item_id="NIST-SP-800-53",
        field_path="controls[0].id",
        validation_rule="required_field",
        file_path="nist.yaml"
    )
    # Output: "Field validation failed | Item: NIST-SP-800-53 | Field: controls[0].id | Rule: required_field | File: nist.yaml"
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
# Standards loading error types (file-based operations)
# ============================================================================


class StandardsLoadingError(LoadingError):
    """Base standards loading error."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        framework: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards loading error.

        Args:
            message: The error message
            standard_id: Optional standard identifier (e.g., "NIST-SP-800-53")
            framework: Optional framework name (e.g., "NIST", "ISO")
            file_path: Optional file path where the error occurred
            **kwargs: Additional context passed to base class
        """
        super().__init__(
            message,
            file_path=file_path,
            item_id=standard_id,
            validation_context=f"Framework: {framework}" if framework else None,
            **kwargs,
        )


class StandardsFileNotFoundError(LoadingError):
    """Standards definition file could not be found."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards file not found error."""
        super().__init__(message, file_path=file_path, item_id=standard_id, **kwargs)


class StandardsParsingError(ParsingError):
    """Standards definition file could not be parsed."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        parser_type: str | None = None,
        line_number: int | None = None,
        parse_details: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize standards parsing error."""
        # Let base ParsingError handle parser context building
        super().__init__(
            message,
            file_path=file_path,
            parser_type=parser_type,
            line_number=line_number,
            parse_details=parse_details,
            item_id=standard_id,  # Standards-specific context
            **kwargs,
        )


class StandardsInvalidFormatError(FileError):
    """Standards definition format is invalid or unsupported."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        detected_format: str | None = None,
        supported_formats: list[str] | None = None,
        format_issue: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards invalid format error.

        Args:
            message: The format error message
            standard_id: Optional standard identifier
            detected_format: Optional detected format
            supported_formats: Optional list of supported formats
            format_issue: Optional description of the format issue
            file_path: Optional file path with format issue
            **kwargs: Additional context passed to base class
        """
        # Build validation context with format details
        context_parts: list[str] = []
        if detected_format:
            context_parts.append(f"Detected: {detected_format}")
        if supported_formats:
            supported = ", ".join(supported_formats)
            context_parts.append(f"Supported: {supported}")
        if format_issue:
            context_parts.append(f"Issue: {format_issue}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            file_path=file_path,
            item_id=standard_id,
            validation_context=validation_context,
            **kwargs,
        )


class StandardsMissingFieldError(LoadingError):
    """Required standards field is missing from definition."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        field_name: str | None = None,
        required_fields: list[str] | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards missing field error.

        Args:
            message: The missing field error message
            standard_id: Optional standard identifier
            field_name: Optional name of the missing field
            required_fields: Optional list of all required fields
            file_path: Optional file path with missing field
            **kwargs: Additional context passed to base class
        """
        # Build validation context with field requirements
        context_parts: list[str] = []
        if required_fields:
            required = ", ".join(required_fields)
            context_parts.append(f"Required: {required}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            file_path=file_path,
            item_id=standard_id,
            field_path=field_name,
            validation_context=validation_context,
            **kwargs,
        )


# ============================================================================
# Standards validation error types
# ============================================================================


class StandardsValidationError(ValidationError):
    """Base standards validation error."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        framework: str | None = None,
        validation_type: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards validation error.

        Args:
            message: The validation error message
            standard_id: Optional standard identifier
            framework: Optional framework name
            validation_type: Optional type of validation
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        # Build validation context with framework and type
        context_parts: list[str] = []
        if framework:
            context_parts.append(f"Framework: {framework}")
        if validation_type:
            context_parts.append(f"Type: {validation_type}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=standard_id,
            file_path=file_path,
            validation_context=validation_context,
            **kwargs,
        )


class StandardsFieldValidationError(ValidationError):
    """Standards field-level validation failed."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        field_name: str | None = None,
        field_value: str | None = None,
        validation_rule: str | None = None,
        expected_value: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards field validation error.

        Args:
            message: The field validation error message
            standard_id: Optional standard identifier
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

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=standard_id,
            field_path=field_name,
            validation_rule=validation_rule,
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


class StandardsConstraintViolationError(ValidationError):
    """Standards constraint validation failed."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        framework: str | None = None,
        constraint_name: str | None = None,
        expected: str | None = None,
        actual: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards constraint violation error.

        Args:
            message: The constraint violation error message
            standard_id: Optional standard identifier
            framework: Optional framework name
            constraint_name: Optional name of the constraint
            expected: Optional expected constraint value
            actual: Optional actual value that violated the constraint
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        # Build validation context with constraint details
        context_parts: list[str] = []
        if framework:
            context_parts.append(f"Framework: {framework}")
        if constraint_name:
            context_parts.append(f"Constraint: {constraint_name}")
        if expected:
            context_parts.append(f"Expected: {expected}")
        if actual:
            context_parts.append(f"Actual: {actual}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=standard_id,
            validation_rule="constraint",
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


# ============================================================================
# Standards mapping error types
# ============================================================================


class StandardsMappingError(ValidationError):
    """Base standards mapping validation error."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        mapping_key: str | None = None,
        target_id: str | None = None,
        mapping_type: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards mapping error.

        Args:
            message: The mapping error message
            standard_id: Optional standard identifier
            mapping_key: Optional mapping key or control ID
            target_id: Optional target ID being mapped to (e.g., CWE ID)
            mapping_type: Optional type of mapping (e.g., "cwe", "control")
            file_path: Optional file path being processed
            **kwargs: Additional context passed to base class
        """
        # Build validation context with mapping details
        context_parts: list[str] = []
        if mapping_key:
            context_parts.append(f"Mapping: {mapping_key}")
        if target_id:
            context_parts.append(f"Target: {target_id}")
        if mapping_type:
            context_parts.append(f"Type: {mapping_type}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=standard_id,
            validation_rule="mapping",
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


class StandardsInvalidMappingError(ValidationError):
    """Standards mapping references unknown target ID."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        mapping_key: str | None = None,
        target_id: str | None = None,
        reference_source: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards invalid mapping error.

        Args:
            message: The invalid mapping error message
            standard_id: Optional standard identifier
            mapping_key: Optional mapping key that failed
            target_id: Optional target ID that couldn't be found
            reference_source: Optional source of the reference
            file_path: Optional file path being validated
            **kwargs: Additional context passed to base class
        """
        # Build validation context with reference details
        context_parts: list[str] = []
        if mapping_key:
            context_parts.append(f"Mapping: {mapping_key}")
        if target_id:
            context_parts.append(f"Target: {target_id}")
        if reference_source:
            context_parts.append(f"Source: {reference_source}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=standard_id,
            validation_rule="invalid_mapping",
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


class StandardsDuplicateMappingError(ValidationError):
    """Duplicate standards mapping detected."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        mapping_key: str | None = None,
        existing_target: str | None = None,
        duplicate_target: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards duplicate mapping error.

        Args:
            message: The duplicate mapping error message
            standard_id: Optional standard identifier
            mapping_key: Optional mapping key that's duplicated
            existing_target: Optional existing target ID
            duplicate_target: Optional duplicate target ID
            file_path: Optional file path being processed
            **kwargs: Additional context passed to base class
        """
        # Build validation context with duplicate details
        context_parts: list[str] = []
        if mapping_key:
            context_parts.append(f"Mapping: {mapping_key}")
        if existing_target:
            context_parts.append(f"Existing: {existing_target}")
        if duplicate_target:
            context_parts.append(f"Duplicate: {duplicate_target}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            item_id=standard_id,
            validation_rule="duplicate_mapping",
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


# ============================================================================
# Standards format error types
# ============================================================================


class StandardsFormatError(FileError):
    """Standards formatting/serialization problem."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        format_type: str | None = None,
        export_template: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards format error.

        Args:
            message: The format error message
            standard_id: Optional standard identifier
            format_type: Optional format type (e.g., "export", "template")
            export_template: Optional export template name
            file_path: Optional file path with format issue
            **kwargs: Additional context passed to base class
        """
        # Build validation context with format details
        context_parts: list[str] = []
        if format_type:
            context_parts.append(f"Format: {format_type}")
        if export_template:
            context_parts.append(f"Template: {export_template}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            file_path=file_path,
            item_id=standard_id,
            validation_context=validation_context,
            **kwargs,
        )


# ============================================================================
# Standards processing error types
# ============================================================================


class StandardsProcessingError(OperationError):
    """Standards processing operation failed."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        operation: str | None = None,
        stage: str | None = None,
        processed_count: int | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards processing error.

        Args:
            message: The processing error message
            standard_id: Optional standard identifier
            operation: Optional name of the operation being performed
            stage: Optional processing stage
            processed_count: Optional number of items processed before failure
            file_path: Optional file path being processed
            **kwargs: Additional context passed to base class
        """
        super().__init__(
            message,
            operation=operation,
            stage=stage,
            processed_count=processed_count,
            item_id=standard_id,
            file_path=file_path,
            **kwargs,
        )


class StandardsIntegrityError(ValidationError):
    """Standards data integrity violation."""

    def __init__(
        self,
        message: str,
        *,
        standard_id: str | None = None,
        integrity_check: str | None = None,
        expected_value: str | None = None,
        actual_value: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ):
        """Initialize standards integrity error.

        Args:
            message: The integrity error message
            standard_id: Optional standard identifier
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
            item_id=standard_id,
            validation_rule="integrity",
            validation_context=validation_context,
            file_path=file_path,
            **kwargs,
        )


class StandardsConfigurationError(BaseTransparencyError):
    """Standards configuration error."""

    def __init__(
        self,
        message: str,
        *,
        config_key: str | None = None,
        config_value: str | None = None,
        valid_values: list[str] | None = None,
        **kwargs: Any,
    ):
        """Initialize standards configuration error.

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
    "StandardsConfigurationError",
    "StandardsConstraintViolationError",
    "StandardsDuplicateMappingError",
    "StandardsFieldValidationError",
    "StandardsFileNotFoundError",
    "StandardsFormatError",
    "StandardsIntegrityError",
    "StandardsInvalidFormatError",
    "StandardsInvalidMappingError",
    "StandardsLoadingError",
    "StandardsMappingError",
    "StandardsMissingFieldError",
    "StandardsParsingError",
    "StandardsProcessingError",
    "StandardsValidationError",
]
