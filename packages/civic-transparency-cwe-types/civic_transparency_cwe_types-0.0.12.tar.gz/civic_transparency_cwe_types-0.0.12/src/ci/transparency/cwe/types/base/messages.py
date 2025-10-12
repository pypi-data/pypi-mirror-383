# src/ci/transparency/cwe/types/base/messages.py
"""Define message collection classes for error, warning, and informational messages.

It provides:
- MessageCollection: a dataclass for collecting and counting error, warning, and info messages.
"""

from dataclasses import dataclass, field


def _empty_str_list() -> list[str]:
    """Return an empty list of strings (for Pyright)."""
    return []


@dataclass(frozen=True)
class MessageCollection:
    """Collects error, warning, and info messages.

    Attributes
    ----------
    errors : list[str]
        list of error messages.
    warnings : list[str]
        list of warning messages.
    infos : list[str]
        list of informational messages.
    """

    errors: list[str] = field(default_factory=_empty_str_list)
    warnings: list[str] = field(default_factory=_empty_str_list)
    infos: list[str] = field(default_factory=_empty_str_list)

    @property
    def error_count(self) -> int:
        """Return the number of error messages."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Return the number of warning messages."""
        return len(self.warnings)

    @property
    def info_count(self) -> int:
        """Return the number of informational messages."""
        return len(self.infos)

    @property
    def total_messages(self) -> int:
        """Return the total number of messages (errors, warnings, infos)."""
        return self.error_count + self.warning_count + self.info_count

    @property
    def has_errors(self) -> bool:
        """Return True if there are any error messages, otherwise False."""
        return bool(self.errors)

    @property
    def has_warnings(self) -> bool:
        """Return True if there are any warning messages, otherwise False."""
        return bool(self.warnings)


__all__ = ["MessageCollection"]
