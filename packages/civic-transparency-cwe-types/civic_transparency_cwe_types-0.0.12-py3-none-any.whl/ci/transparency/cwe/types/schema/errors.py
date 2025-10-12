"""Domain-neutral schema error types.

Lightweight hierarchy that adds schema context (name/version/path) on top
of base loading/validation errors. Keeps __slots__ for low overhead and
reuses your BaseLoadingError formatting contract.
"""

from pathlib import Path
from typing import Any

from ci.transparency.cwe.types.base.errors import LoadingError, ParsingError


class SchemaError(LoadingError):
    """Base exception for schema operations with schema context."""

    __slots__ = ("schema_name", "schema_version")

    def __init__(
        self,
        message: str,
        schema_name: str | None = None,
        schema_version: str | None = None,
        file_path: Path | None = None,
    ):
        """Initialize SchemaError.

        Args:
            message (str): Error message.
            schema_name (str | None): Name of the schema.
            schema_version (str | None): Version of the schema.
            file_path (Path | None): Path to the schema file.
        """
        super().__init__(message)
        self.schema_name = schema_name
        self.schema_version = schema_version

    def get_context_parts(self) -> list[str]:
        """Return a list of context parts describing the schema error.

        Includes schema name and version if available.
        """
        parts = super().get_context_parts()
        if self.schema_name:
            parts.insert(
                0,
                f"Schema: {self.schema_name}-{self.schema_version}"
                if self.schema_version
                else f"Schema: {self.schema_name}",
            )
        elif self.schema_version:
            parts.insert(0, f"Version: {self.schema_version}")
        return parts


# -------------------------
# Loading / format errors
# -------------------------


class SchemaLoadingError(SchemaError):
    """Schema loading/parsing/format failures."""


class SchemaNotFoundError(SchemaLoadingError):
    """Schema file/resource could not be found."""


class SchemaParsingError(ParsingError):
    """Schema could not be parsed as valid JSON/YAML."""

    def __init__(
        self,
        message: str,
        *,
        parse_error: str | None = None,
        schema_name: str | None = None,
        schema_version: str | None = None,
        file_path: Path | str | None = None,
        parser_type: str | None = None,
        line_number: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize schema parsing error."""
        # Combine schema name and version - handle all combinations
        combined_schema: str | None = None
        if schema_name and schema_version:
            combined_schema = f"{schema_name}-{schema_version}"
        elif schema_name:
            combined_schema = schema_name
        elif schema_version:  # NEW: Handle version-only case
            combined_schema = schema_version

        super().__init__(
            message,
            file_path=file_path,
            parser_type=parser_type,
            line_number=line_number,
            parse_details=parse_error,
            schema_name=combined_schema,
            **kwargs,
        )


class SchemaVersionError(SchemaLoadingError):
    """Schema version is not supported or invalid."""

    __slots__ = ("encountered_version", "supported_versions")

    def __init__(
        self,
        message: str,
        schema_version: str | None = None,
        supported_versions: list[str] | None = None,
        schema_name: str | None = None,
        file_path: Path | None = None,
    ):
        """Initialize SchemaVersionError.

        Args:
            message (str): Error message.
            schema_version (str | None): The encountered schema version.
            supported_versions (list[str] | None): List of supported schema versions.
            schema_name (str | None): Name of the schema.
            file_path (Path | None): Path to the schema file.
        """
        super().__init__(message, schema_name, schema_version, file_path)
        self.encountered_version = schema_version
        self.supported_versions = supported_versions or []

    def get_context_parts(self) -> list[str]:
        """Return a list of context parts describing the schema version error.

        Includes supported versions if available.
        """
        parts = super().get_context_parts()
        if self.supported_versions:
            parts.append(f"Supported: {', '.join(self.supported_versions)}")
        return parts


class SchemaFormatError(SchemaLoadingError):
    """Schema format is invalid or malformed."""

    __slots__ = ("format_issue",)

    def __init__(
        self,
        message: str,
        format_issue: str | None = None,
        schema_name: str | None = None,
        schema_version: str | None = None,
        file_path: Path | None = None,
    ):
        """Initialize SchemaFormatError.

        Args:
            message (str): Error message.
            format_issue (str | None): Description of the format issue.
            schema_name (str | None): Name of the schema.
            schema_version (str | None): Version of the schema.
            file_path (Path | None): Path to the schema file.
        """
        super().__init__(message, schema_name, schema_version, file_path)
        self.format_issue = format_issue

    def get_context_parts(self) -> list[str]:
        """Return a list of context parts describing the schema format error.

        Includes format issue details if available.
        """
        parts = super().get_context_parts()
        if self.format_issue:
            parts.append(f"Issue: {self.format_issue}")
        return parts


# -------------------------
# Instance-vs-schema errors
# -------------------------


class SchemaValidationError(SchemaError):
    """Base instance validation error against a schema."""


class SchemaDataValidationError(SchemaValidationError):
    """Instance data validation against schema failed."""

    __slots__ = ("validation_path", "expected_type", "actual_value")

    def __init__(
        self,
        message: str,
        validation_path: str | None = None,
        expected_type: str | None = None,
        actual_value: str | None = None,
        schema_name: str | None = None,
        schema_version: str | None = None,
    ):
        """Initialize SchemaDataValidationError.

        Args:
            message (str): Error message.
            validation_path (str | None): Path to the field being validated.
            expected_type (str | None): Expected type for the field.
            actual_value (str | None): Actual value encountered.
            schema_name (str | None): Name of the schema.
            schema_version (str | None): Version of the schema.
        """
        super().__init__(message, schema_name, schema_version)
        self.validation_path = validation_path
        self.expected_type = expected_type
        self.actual_value = actual_value

    def get_context_parts(self) -> list[str]:
        """Return a list of context parts describing the data validation error.

        Returns
        -------
        list[str]
            List of context strings including validation path, expected type, and actual value if available.
        """
        parts = super().get_context_parts()
        if self.validation_path:
            parts.append(f"Field: {self.validation_path}")
        if self.expected_type:
            parts.append(f"Expected: {self.expected_type}")
        if self.actual_value:
            parts.append(f"Actual: {self.actual_value}")
        return parts


class SchemaFieldValidationError(SchemaValidationError):
    """Field-level validation against schema failed."""

    __slots__ = ("field_name", "field_path", "constraint_type")

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        field_path: str | None = None,
        constraint_type: str | None = None,
        schema_name: str | None = None,
        schema_version: str | None = None,
    ):
        """Initialize SchemaFieldValidationError.

        Args:
            message (str): Error message.
            field_name (str | None): Name of the field.
            field_path (str | None): Path to the field.
            constraint_type (str | None): Type of constraint violated.
            schema_name (str | None): Name of the schema.
            schema_version (str | None): Version of the schema.
        """
        super().__init__(message, schema_name, schema_version)
        self.field_name = field_name
        self.field_path = field_path
        self.constraint_type = constraint_type

    def get_context_parts(self) -> list[str]:
        """Return a list of context parts describing the field validation error.

        Includes field path, field name, and constraint type if available.
        """
        parts = super().get_context_parts()
        if self.field_path:
            parts.append(f"Field: {self.field_path}")
        elif self.field_name:
            parts.append(f"Field: {self.field_name}")
        if self.constraint_type:
            parts.append(f"Constraint: {self.constraint_type}")
        return parts


class SchemaConstraintError(SchemaValidationError):
    """Schema constraint validation failed."""

    __slots__ = ("constraint_name", "constraint_value", "violated_rule")

    def __init__(
        self,
        message: str,
        constraint_name: str | None = None,
        constraint_value: str | None = None,
        violated_rule: str | None = None,
        schema_name: str | None = None,
        schema_version: str | None = None,
    ):
        """Initialize SchemaConstraintError.

        Args:
            message (str): Error message.
            constraint_name (str | None): Name of the constraint.
            constraint_value (str | None): Expected value of the constraint.
            violated_rule (str | None): Rule that was violated.
            schema_name (str | None): Name of the schema.
            schema_version (str | None): Version of the schema.
        """
        super().__init__(message, schema_name, schema_version)
        self.constraint_name = constraint_name
        self.constraint_value = constraint_value
        self.violated_rule = violated_rule

    def get_context_parts(self) -> list[str]:
        """Return a list of context parts describing the constraint error.

        Includes constraint name, expected value, and violated rule if available.
        """
        parts = super().get_context_parts()
        if self.constraint_name:
            parts.append(f"Constraint: {self.constraint_name}")
        if self.constraint_value:
            parts.append(f"Expected: {self.constraint_value}")
        if self.violated_rule:
            parts.append(f"Rule: {self.violated_rule}")
        return parts


class SchemaReferenceError(SchemaValidationError):
    """Schema $ref could not be resolved."""

    __slots__ = ("reference_path", "reference_target")

    def __init__(
        self,
        message: str,
        reference_path: str | None = None,
        reference_target: str | None = None,
        schema_name: str | None = None,
        schema_version: str | None = None,
    ):
        """Initialize SchemaReferenceError.

        Args:
            message (str): Error message.
            reference_path (str | None): Path of the unresolved reference.
            reference_target (str | None): Target of the reference.
            schema_name (str | None): Name of the schema.
            schema_version (str | None): Version of the schema.
        """
        super().__init__(message, schema_name, schema_version)
        self.reference_path = reference_path
        self.reference_target = reference_target

    def get_context_parts(self) -> list[str]:
        """Return a list of context parts describing the reference error.

        Includes reference path and target if available.
        """
        parts = super().get_context_parts()
        if self.reference_path:
            parts.append(f"Reference: {self.reference_path}")
        if self.reference_target:
            parts.append(f"Target: {self.reference_target}")
        return parts


class SchemaCircularReferenceError(SchemaValidationError):
    """Schema contains circular references."""

    __slots__ = ("reference_chain",)

    def __init__(
        self,
        message: str,
        reference_chain: list[str] | None = None,
        schema_name: str | None = None,
        schema_version: str | None = None,
    ):
        """Initialize SchemaCircularReferenceError.

        Args:
            message (str): Error message.
            reference_chain (list[str] | None): List representing the chain of circular references.
            schema_name (str | None): Name of the schema.
            schema_version (str | None): Version of the schema.
        """
        super().__init__(message, schema_name, schema_version)
        self.reference_chain = reference_chain or []

    def get_context_parts(self) -> list[str]:
        """Return a list of context parts describing the circular reference error.

        Includes the reference chain if available.
        """
        parts = super().get_context_parts()
        if self.reference_chain:
            parts.append(f"Chain: {' → '.join(self.reference_chain)}")
        return parts


__all__ = [
    "SchemaCircularReferenceError",
    "SchemaConstraintError",
    "SchemaDataValidationError",
    "SchemaError",
    "SchemaFieldValidationError",
    "SchemaFormatError",
    "SchemaLoadingError",
    "SchemaNotFoundError",
    "SchemaParsingError",
    "SchemaReferenceError",
    "SchemaValidationError",
    "SchemaVersionError",
]
