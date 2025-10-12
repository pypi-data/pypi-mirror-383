"""CWE schema error types using enhanced base classes.

Domain-specific error hierarchy for CWE schema operations. Each error inherits
from exactly one enhanced base error class and leverages the flexible context
system for schema-specific information.

Design principles:
    - Single inheritance: each error extends exactly one base error class
    - Context-rich: uses the flexible context system for schema details
    - Consistent: maintains uniform error formatting across all errors
    - Minimal: leverages base class functionality rather than duplicating code

Usage patterns:
    - File operations → FileError, LoadingError, ParsingError
    - Validation operations → ValidationError
    - General schema operations → BaseTransparencyError

Typical usage:
    from ci.transparency.cwe.types.cwe.schema import CweSchemaValidationError

    raise CweSchemaValidationError(
        "Schema validation failed",
        schema_name="cwe-v2.0",
        field_path="relationships[0].id",
        file_path="cwe-79.yaml"
    )
    # Output: "Schema validation failed | Schema: cwe-v2.0 | Field: relationships[0].id | File: cwe-79.yaml"
"""

from pathlib import Path
from typing import Any

from ci.transparency.cwe.types.base.errors import (
    BaseTransparencyError,
    FileError,
    LoadingError,
    ParsingError,
    ValidationError,
)

# ============================================================================
# CWE schema loading error types (file-based operations)
# ============================================================================


class CweSchemaLoadingError(LoadingError):
    """CWE schema loading operation failed."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE schema loading error.

        Args:
            message: The error message
            schema_name: Optional name of the schema
            schema_version: Optional version of the schema
            file_path: Optional file path where the error occurred
            **kwargs: Additional context passed to base class
        """
        # Combine schema name and version for the schema_name context
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        super().__init__(
            message,
            file_path=file_path,
            schema_name=combined_schema,
            **kwargs,
        )


class CweSchemaNotFoundError(LoadingError):
    """CWE schema file could not be found."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE schema not found error."""
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        super().__init__(
            message,
            file_path=file_path,
            schema_name=combined_schema,
            **kwargs,
        )


class CweSchemaParsingError(ParsingError):
    """CWE schema file could not be parsed as valid JSON/YAML."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        parser_type: str | None = None,
        parse_details: str | None = None,
        line_number: int | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE schema parsing error."""
        # Combine schema name and version for schema context
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        # Let base ParsingError handle parser context building
        super().__init__(
            message,
            file_path=file_path,
            parser_type=parser_type,
            line_number=line_number,
            parse_details=parse_details,
            schema_name=combined_schema,  # Schema-specific context
            **kwargs,
        )


class CweSchemaFormatError(FileError):
    """CWE schema format is invalid or malformed."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        format_issue: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE schema format error.

        Args:
            message: The format error message
            schema_name: Optional name of the schema
            schema_version: Optional version of the schema
            format_issue: Optional description of the format issue
            file_path: Optional file path with the format issue
            **kwargs: Additional context passed to base class
        """
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        super().__init__(
            message,
            file_path=file_path,
            schema_name=combined_schema,
            validation_context=f"Issue: {format_issue}" if format_issue else None,
            **kwargs,
        )


class CweSchemaVersionError(FileError):
    """CWE schema version is not supported or invalid."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        supported_versions: list[str] | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE schema version error.

        Args:
            message: The version error message
            schema_name: Optional name of the schema
            schema_version: Optional version that was found
            supported_versions: Optional list of supported versions
            file_path: Optional file path with the version issue
            **kwargs: Additional context passed to base class
        """
        # Use error_code for version info
        error_code: str | None = schema_version

        # Build validation context with supported versions
        validation_context: str | None = None
        if supported_versions:
            supported: str = ", ".join(supported_versions)
            validation_context = f"Supported: {supported}"

        super().__init__(
            message,
            file_path=file_path,
            schema_name=schema_name,
            error_code=error_code,
            validation_context=validation_context,
            **kwargs,
        )


# ============================================================================
# CWE schema validation error types
# ============================================================================


class CweSchemaValidationError(ValidationError):
    """Base CWE schema validation error."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        field_path: str | None = None,
        validation_rule: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE schema validation error.

        Args:
            message: The validation error message
            schema_name: Optional name of the schema
            schema_version: Optional version of the schema
            field_path: Optional path to the field that failed
            validation_rule: Optional validation rule that failed
            **kwargs: Additional context passed to base class
        """
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        super().__init__(
            message,
            schema_name=combined_schema,
            field_path=field_path,
            validation_rule=validation_rule,
            **kwargs,
        )


class CweSchemaConstraintError(ValidationError):
    """CWE schema constraint validation failed."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        constraint_name: str | None = None,
        constraint_value: str | None = None,
        violated_rule: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE schema constraint error.

        Args:
            message: The constraint error message
            schema_name: Optional name of the schema
            schema_version: Optional version of the schema
            constraint_name: Optional name of the constraint
            constraint_value: Optional expected constraint value
            violated_rule: Optional description of the violated rule
            **kwargs: Additional context passed to base class
        """
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        # Build validation context with constraint details
        context_parts: list[str] = []
        if constraint_name:
            context_parts.append(f"Constraint: {constraint_name}")
        if constraint_value:
            context_parts.append(f"Expected: {constraint_value}")
        if violated_rule:
            context_parts.append(f"Rule: {violated_rule}")

        validation_context: str | None = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            schema_name=combined_schema,
            validation_context=validation_context,
            **kwargs,
        )


class CweSchemaDataValidationError(ValidationError):
    """CWE data validation against schema failed."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        validation_path: str | None = None,
        expected_type: str | None = None,
        actual_value: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE data validation error.

        Args:
            message: The validation error message
            schema_name: Optional name of the schema
            schema_version: Optional version of the schema
            validation_path: Optional path to the field that failed validation
            expected_type: Optional expected type or format
            actual_value: Optional actual value that failed validation
            **kwargs: Additional context passed to base class
        """
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        # Build validation context with type/value details
        context_parts: list[str] = []
        if expected_type:
            context_parts.append(f"Expected: {expected_type}")
        if actual_value:
            context_parts.append(f"Actual: {actual_value}")

        validation_context: str | None = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            schema_name=combined_schema,
            field_path=validation_path,
            validation_context=validation_context,
            **kwargs,
        )


class CweSchemaFieldValidationError(ValidationError):
    """CWE field-level validation against schema failed."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        field_name: str | None = None,
        field_path: str | None = None,
        constraint_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE field validation error.

        Args:
            message: The field validation error message
            schema_name: Optional name of the schema
            schema_version: Optional version of the schema
            field_name: Optional name of the field
            field_path: Optional full path to the field (e.g., "relationships[0].id")
            constraint_type: Optional type of constraint that failed
            **kwargs: Additional context passed to base class
        """
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        # Use field_path if available, otherwise field_name
        final_field_path: str | None = field_path or field_name

        super().__init__(
            message,
            schema_name=combined_schema,
            field_path=final_field_path,
            validation_rule=constraint_type,
            **kwargs,
        )


class CweSchemaCircularReferenceError(ValidationError):
    """CWE schema contains circular references."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        reference_chain: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE schema circular reference error.

        Args:
            message: The circular reference error message
            schema_name: Optional name of the schema
            schema_version: Optional version of the schema
            reference_chain: Optional chain of references that form the cycle
            **kwargs: Additional context passed to base class
        """
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        # Build validation context with reference chain
        validation_context: str | None = None
        if reference_chain:
            chain: str = " → ".join(reference_chain)
            validation_context = f"Chain: {chain}"

        super().__init__(
            message,
            schema_name=combined_schema,
            validation_rule="circular_reference",
            validation_context=validation_context,
            **kwargs,
        )


class CweSchemaReferenceError(ValidationError):
    """CWE schema reference could not be resolved."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        reference_path: str | None = None,
        reference_target: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CWE schema reference error.

        Args:
            message: The reference error message
            schema_name: Optional name of the schema
            schema_version: Optional version of the schema
            reference_path: Optional path to the unresolved reference
            reference_target: Optional target of the reference
            **kwargs: Additional context passed to base class
        """
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        # Build validation context with reference details
        context_parts: list[str] = []
        if reference_path:
            context_parts.append(f"Reference: {reference_path}")
        if reference_target:
            context_parts.append(f"Target: {reference_target}")

        validation_context: str | None = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            schema_name=combined_schema,
            validation_rule="reference_resolution",
            validation_context=validation_context,
            **kwargs,
        )


# ============================================================================
# General CWE schema error (for operations that don't fit other categories)
# ============================================================================


class CweSchemaError(BaseTransparencyError):
    """General CWE schema error for operations that don't fit specific categories."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        schema_version: str | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize general CWE schema error.

        Args:
            message: The error message
            schema_name: Optional name of the schema
            schema_version: Optional version of the schema
            operation: Optional operation being performed
            **kwargs: Additional context passed to base class
        """
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name

        super().__init__(
            message,
            schema_name=combined_schema,
            operation=operation,
            **kwargs,
        )


# ============================================================================
# Public API (alphabetical)
# ============================================================================

__all__ = [
    "CweSchemaCircularReferenceError",
    "CweSchemaConstraintError",
    "CweSchemaDataValidationError",
    "CweSchemaError",
    "CweSchemaFieldValidationError",
    "CweSchemaFormatError",
    "CweSchemaLoadingError",
    "CweSchemaNotFoundError",
    "CweSchemaParsingError",
    "CweSchemaReferenceError",
    "CweSchemaValidationError",
    "CweSchemaVersionError",
]
