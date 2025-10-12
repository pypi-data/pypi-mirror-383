"""Enhanced base error types for transparency operations.

Provides comprehensive base exception classes that capture common patterns across
all transparency domains (CWE, schema validation, standards processing).

Design principles:
    - Flexible: supports optional context fields without requiring all errors to use them
    - Contextual: captures progress, operations, resources, files, validation, and abort context
    - Consistent: maintains uniform formatting with " | " separator
    - Slotted: minimal memory overhead with __slots__
    - Hierarchical: specific base classes for common operation types

Core error hierarchy:
    - BaseTransparencyError: Root exception with flexible context support
    - OperationError: Operations with progress tracking (batch, phase processing)
    - ResourceError: Resource-constrained operations (timeouts, limits)
    - ValidationError: Validation operations with rule/schema context
    - FileError: File-based operations with path context

All errors use consistent formatting: "message | Context1: value | Context2: value"
Context is only included when relevant fields are populated.
"""

from pathlib import Path
from typing import Any


class BaseTransparencyError(Exception):
    """Enhanced base exception for all transparency operations.

    Provides flexible context tracking for common error patterns without
    requiring all errors to specify every possible context field.
    """

    __slots__ = (
        "message",
        # Progress tracking
        "processed_count",
        "total_count",
        "batch_size",
        # Operation identification
        "operation",
        "phase_name",
        "stage",
        # Resource constraints
        "timeout_seconds",
        "elapsed_seconds",
        "resource_type",
        "limit_reached",
        "resource_usage",
        # File/item context
        "file_path",
        "item_id",
        # Validation context
        "validation_context",
        "validation_rule",
        "schema_name",
        "field_path",
        # Error flow control
        "abort_reason",
        "error_code",
    )

    def __init__(
        self,
        message: str,
        *,
        # Progress tracking
        processed_count: int | None = None,
        total_count: int | None = None,
        batch_size: int | None = None,
        # Operation identification
        operation: str | None = None,
        phase_name: str | None = None,
        stage: str | None = None,
        # Resource constraints
        timeout_seconds: float | None = None,
        elapsed_seconds: float | None = None,
        resource_type: str | None = None,
        limit_reached: str | None = None,
        resource_usage: str | None = None,
        # File/item context
        file_path: Path | str | None = None,
        item_id: str | None = None,
        # Validation context
        validation_context: str | None = None,
        validation_rule: str | None = None,
        schema_name: str | None = None,
        field_path: str | None = None,
        # Error flow control
        abort_reason: str | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize transparency error with optional context.

        Args:
            message: The error message describing what went wrong
            processed_count: Number of items processed before error
            total_count: Total number of items expected
            batch_size: Size of processing batch
            operation: Name of the operation being performed
            phase_name: Name of the processing phase
            stage: Processing stage (setup, processing, cleanup, etc.)
            timeout_seconds: Timeout limit that was exceeded
            elapsed_seconds: Actual time elapsed before timeout
            resource_type: Type of resource (memory, disk, threads, etc.)
            limit_reached: Description of limit that was reached
            resource_usage: Description of current resource usage
            file_path: Path to relevant file
            item_id: Identifier of specific item being processed
            validation_context: Context about what was being validated
            validation_rule: Name of validation rule that failed
            schema_name: Name of schema being validated against
            field_path: Path to field that failed (e.g., "data.items[0].id")
            abort_reason: Reason why operation was aborted
            error_code: Machine-readable error code
        """
        super().__init__(message)
        self.message: str = message

        # Progress tracking
        self.processed_count: int | None = processed_count
        self.total_count: int | None = total_count
        self.batch_size: int | None = batch_size

        # Operation identification
        self.operation: str | None = operation
        self.phase_name: str | None = phase_name
        self.stage: str | None = stage

        # Resource constraints
        self.timeout_seconds: float | None = timeout_seconds
        self.elapsed_seconds: float | None = elapsed_seconds
        self.resource_type: str | None = resource_type
        self.limit_reached: str | None = limit_reached
        self.resource_usage: str | None = resource_usage

        # File/item context
        self.file_path: Path | None = Path(file_path) if file_path else None
        self.item_id: str | None = item_id

        # Validation context
        self.validation_context: str | None = validation_context
        self.validation_rule: str | None = validation_rule
        self.schema_name: str | None = schema_name
        self.field_path: str | None = field_path

        # Error flow control
        self.abort_reason: str | None = abort_reason
        self.error_code: str | None = error_code

    def _add_operation_context(self, parts: list[str]) -> None:
        """Add operation identification context."""
        if self.phase_name:
            parts.append(f"Phase: {self.phase_name}")
        elif self.operation:
            parts.append(f"Operation: {self.operation}")

        if self.stage:
            parts.append(f"Stage: {self.stage}")

    def _add_progress_context(self, parts: list[str]) -> None:
        """Add progress tracking context."""
        if self.processed_count is not None and self.total_count is not None:
            parts.append(f"Progress: {self.processed_count}/{self.total_count}")
        elif self.processed_count is not None:
            parts.append(f"Processed: {self.processed_count}")

        if self.batch_size is not None:
            parts.append(f"Batch Size: {self.batch_size}")

    def _add_resource_context(self, parts: list[str]) -> None:
        """Add resource constraint context."""
        if self.resource_type:
            parts.append(f"Resource: {self.resource_type}")
        if self.timeout_seconds:
            parts.append(f"Timeout: {self.timeout_seconds}s")
        if self.elapsed_seconds:
            parts.append(f"Elapsed: {self.elapsed_seconds:.1f}s")
        if self.limit_reached:
            parts.append(f"Limit: {self.limit_reached}")
        if self.resource_usage:
            parts.append(f"Usage: {self.resource_usage}")

    def _add_file_item_context(self, parts: list[str]) -> None:
        """Add file and item context."""
        if self.file_path:
            parts.append(f"File: {self.file_path}")
        if self.item_id:
            parts.append(f"Item: {self.item_id}")

    def _add_validation_context(self, parts: list[str]) -> None:
        """Add validation context."""
        if self.schema_name:
            parts.append(f"Schema: {self.schema_name}")
        if self.validation_rule:
            parts.append(f"Rule: {self.validation_rule}")
        if self.field_path:
            parts.append(f"Field: {self.field_path}")
        if self.validation_context:
            parts.append(f"Context: {self.validation_context}")

    def _add_error_flow_context(self, parts: list[str]) -> None:
        """Add error flow control context."""
        if self.abort_reason:
            parts.append(f"Reason: {self.abort_reason}")
        if self.error_code:
            parts.append(f"Code: {self.error_code}")

    def get_context_parts(self) -> list[str]:
        """Get contextual information parts for error formatting.

        Returns context in order of importance:
        1. Operation identification (phase, operation, stage)
        2. Progress information (processed/total counts)
        3. Resource information (timeouts, limits)
        4. File/item context
        5. Validation context
        6. Error flow context (abort reason, error code)

        Returns:
            List of context strings (e.g., ["Phase: validation", "Progress: 150/500"])
        """
        parts: list[str] = []

        # Add context in order of importance
        self._add_operation_context(parts)
        self._add_progress_context(parts)
        self._add_resource_context(parts)
        self._add_file_item_context(parts)
        self._add_validation_context(parts)
        self._add_error_flow_context(parts)

        return parts

    def __str__(self) -> str:
        """Format error with message and context information.

        Returns:
            Formatted error string with message and context joined by " | "
        """
        parts: list[str] = [self.message]
        parts.extend(self.get_context_parts())
        return " | ".join(parts)


# ============================================================================
# Specialized base classes for common operation types
# ============================================================================


class OperationError(BaseTransparencyError):
    """Base exception for operations with progress tracking.

    Convenient base for batch processing, phase validation, and other
    operations that process multiple items with progress tracking.
    """

    def __init__(
        self,
        message: str,
        *,
        operation: str | None = None,
        phase_name: str | None = None,
        stage: str | None = None,
        processed_count: int | None = None,
        total_count: int | None = None,
        batch_size: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize operation error with operation context."""
        super().__init__(
            message,
            operation=operation,
            phase_name=phase_name,
            stage=stage,
            processed_count=processed_count,
            total_count=total_count,
            batch_size=batch_size,
            **kwargs,
        )


class ResourceError(BaseTransparencyError):
    """Base exception for resource-constrained operations.

    Convenient base for timeout, memory, disk space, and other
    resource-related errors.
    """

    def __init__(
        self,
        message: str,
        *,
        resource_type: str | None = None,
        timeout_seconds: float | None = None,
        elapsed_seconds: float | None = None,
        limit_reached: str | None = None,
        resource_usage: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize resource error with resource context."""
        super().__init__(
            message,
            resource_type=resource_type,
            timeout_seconds=timeout_seconds,
            elapsed_seconds=elapsed_seconds,
            limit_reached=limit_reached,
            resource_usage=resource_usage,
            **kwargs,
        )


class ValidationError(BaseTransparencyError):
    """Base exception for validation operations.

    Convenient base for schema validation, rule checking, and other
    validation-related errors.
    """

    def __init__(
        self,
        message: str,
        *,
        validation_context: str | None = None,
        validation_rule: str | None = None,
        schema_name: str | None = None,
        field_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize validation error with validation context."""
        super().__init__(
            message,
            validation_context=validation_context,
            validation_rule=validation_rule,
            schema_name=schema_name,
            field_path=field_path,
            **kwargs,
        )


class FileError(BaseTransparencyError):
    """Base exception for file-based operations.

    Convenient base for file loading, parsing, and other
    file-related errors.
    """

    def __init__(
        self,
        message: str,
        *,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize file error with file context."""
        super().__init__(message, file_path=file_path, **kwargs)


# ============================================================================
# Common error types using the enhanced base
# ============================================================================


class LoadingError(FileError):
    """File could not be loaded."""


class ParsingError(FileError):
    """File could not be parsed."""

    def __init__(
        self,
        message: str,
        *,
        file_path: Path | str | None = None,
        parser_type: str | None = None,
        line_number: int | None = None,
        parse_details: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize parsing error with parser context."""
        # Build comprehensive parser validation context
        context_parts: list[str] = []
        if parser_type:
            context_parts.append(f"Parser: {parser_type}")
        if line_number is not None:
            context_parts.append(f"Line: {line_number}")
        if parse_details:
            context_parts.append(f"Details: {parse_details}")

        validation_context = " | ".join(context_parts) if context_parts else None

        super().__init__(
            message,
            file_path=file_path,
            validation_context=validation_context,
            **kwargs,
        )


class ConfigurationError(BaseTransparencyError):
    """Configuration is invalid or incomplete."""

    def __init__(
        self,
        message: str,
        *,
        config_key: str | None = None,
        config_file: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize configuration error with config context."""
        super().__init__(
            message,
            item_id=config_key,  # Use item_id for config key
            file_path=config_file,
            **kwargs,
        )


class TransparencyTimeoutError(ResourceError):
    """Operation timed out."""

    def __init__(
        self,
        message: str,
        *,
        timeout_seconds: float | None = None,
        elapsed_seconds: float | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize timeout error with timing context."""
        super().__init__(
            message,
            timeout_seconds=timeout_seconds,
            elapsed_seconds=elapsed_seconds,
            operation=operation,
            **kwargs,
        )


class AbortedError(BaseTransparencyError):
    """Operation was aborted before completion."""

    def __init__(
        self,
        message: str,
        *,
        abort_reason: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize aborted error with abort context."""
        super().__init__(message, abort_reason=abort_reason, **kwargs)


class NetworkError(BaseTransparencyError):
    """Network operation failed."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
        status_code: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize network error with network context."""
        super().__init__(
            message,
            item_id=url,  # Use item_id for URL
            error_code=str(status_code) if status_code else None,
            **kwargs,
        )


__all__ = [
    # Base error types
    "BaseTransparencyError",
    "OperationError",
    "ResourceError",
    "ValidationError",
    "FileError",
    # Common error types
    "LoadingError",
    "ParsingError",
    "ConfigurationError",
    "TransparencyTimeoutError",
    "AbortedError",
    "NetworkError",
]
