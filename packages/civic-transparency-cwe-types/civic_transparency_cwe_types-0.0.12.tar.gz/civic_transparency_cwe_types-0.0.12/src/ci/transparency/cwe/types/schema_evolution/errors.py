"""Schema evolution (freeze/compatibility) error types using enhanced base classes.

These mirror our domain patterns (like CWE/Standards) and use the flatter base errors.
We compose all evolution-specific details into the base fields (validation_rule,
field_path, file_path) and a single validation_context string, so formatting stays
consistent and stable across domains.
"""

from pathlib import Path
from typing import Any

from ci.transparency.cwe.types.base.errors import ValidationError


class SchemaFreezeError(ValidationError):
    """Base schema evolution error comparing old vs new versions."""

    def __init__(
        self,
        message: str,
        *,
        old_version: str | None = None,
        new_version: str | None = None,
        freeze_rule: str | None = None,
        field_path: str | None = None,
        file_path: Path | str | None = None,
        extra_context: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize schema evolution error with version/rule context.

        Args:
            message: Human-readable error message
            old_version: Old schema version identifier
            new_version: New schema version identifier
            freeze_rule: Name of the freeze/compatibility rule
            field_path: Path of the affected field (if any)
            file_path: A relevant file path (old/new/newly-generated)
            extra_context: Additional context parts to append
            **kwargs: Forwarded to base ValidationError
        """
        parts: list[str] = []
        if old_version and new_version:
            parts.append(f"Versions: {old_version} → {new_version}")
        elif old_version:
            parts.append(f"Old: {old_version}")
        elif new_version:
            parts.append(f"New: {new_version}")

        if extra_context:
            parts.extend(extra_context)

        validation_context = " | ".join(parts) if parts else None

        super().__init__(
            message,
            validation_rule=freeze_rule,
            field_path=field_path,
            file_path=file_path,
            validation_context=validation_context,
            **kwargs,
        )


class SchemaFreezeViolationError(SchemaFreezeError):
    """Schema freeze rule violation detected (may or may not be breaking)."""

    def __init__(
        self,
        message: str,
        *,
        violation_type: str | None = None,
        affected_fields: list[str] | None = None,
        old_version: str | None = None,
        new_version: str | None = None,
        freeze_rule: str | None = None,
        field_path: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize SchemaFreezeViolationError with violation details.

        Args:
            message: Human-readable error message
            violation_type: Type of freeze violation detected
            affected_fields: List of affected fields
            old_version: Old schema version identifier
            new_version: New schema version identifier
            freeze_rule: Name of the freeze/compatibility rule
            field_path: Path of the affected field (if any)
            file_path: A relevant file path (old/new/newly-generated)
            **kwargs: Forwarded to base SchemaFreezeError
        """
        parts: list[str] = []
        if violation_type:
            parts.append(f"Violation: {violation_type}")
        if affected_fields:
            parts.append(f"Affected: {', '.join(affected_fields)}")

        super().__init__(
            message,
            old_version=old_version,
            new_version=new_version,
            freeze_rule=freeze_rule or "freeze_violation",
            field_path=field_path,
            file_path=file_path,
            extra_context=parts,
            **kwargs,
        )


class SchemaCompatibilityError(SchemaFreezeError):
    """Backward-compatibility check failed."""

    def __init__(
        self,
        message: str,
        *,
        compatibility_issue: str | None = None,
        backward_compatible: bool = False,
        old_version: str | None = None,
        new_version: str | None = None,
        freeze_rule: str | None = None,
        field_path: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize SchemaCompatibilityError with compatibility issue details.

        Args:
            message: Human-readable error message
            compatibility_issue: Description of the compatibility issue
            backward_compatible: Whether the change is backward compatible
            old_version: Old schema version identifier
            new_version: New schema version identifier
            freeze_rule: Name of the freeze/compatibility rule
            field_path: Path of the affected field (if any)
            file_path: A relevant file path (old/new/newly-generated)
            **kwargs: Forwarded to base SchemaFreezeError
        """
        parts: list[str] = []
        if compatibility_issue:
            parts.append(f"Issue: {compatibility_issue}")
        parts.append(f"Backward: {'Yes' if backward_compatible else 'No'}")

        super().__init__(
            message,
            old_version=old_version,
            new_version=new_version,
            freeze_rule=freeze_rule or "compatibility",
            field_path=field_path,
            file_path=file_path,
            extra_context=parts,
            **kwargs,
        )


class SchemaBreakingChangeError(SchemaFreezeError):
    """Breaking change detected between schema versions."""

    def __init__(
        self,
        message: str,
        *,
        change_type: str | None = None,
        change_description: str | None = None,
        impact_level: str | None = None,
        old_version: str | None = None,
        new_version: str | None = None,
        freeze_rule: str | None = None,
        field_path: str | None = None,
        file_path: Path | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize SchemaBreakingChangeError with details about the breaking change.

        Args:
            message: Human-readable error message
            change_type: Type of breaking change detected
            change_description: Description of the breaking change
            impact_level: Level of impact caused by the change
            old_version: Old schema version identifier
            new_version: New schema version identifier
            freeze_rule: Name of the freeze/compatibility rule
            field_path: Path of the affected field (if any)
            file_path: A relevant file path (old/new/newly-generated)
            **kwargs: Forwarded to base SchemaFreezeError
        """
        parts: list[str] = []
        if change_type:
            parts.append(f"Change: {change_type}")
        if impact_level:
            parts.append(f"Impact: {impact_level}")
        if change_description:
            parts.append(f"Description: {change_description}")

        super().__init__(
            message,
            old_version=old_version,
            new_version=new_version,
            freeze_rule=freeze_rule or "breaking_change",
            field_path=field_path,
            file_path=file_path,
            extra_context=parts,
            **kwargs,
        )


__all__ = [
    "SchemaBreakingChangeError",
    "SchemaCompatibilityError",
    "SchemaFreezeError",
    "SchemaFreezeViolationError",
]
