# src/ci/transparency/cwe/types/base/counts.py
"""Core counting components for transparency CWE types.

This module provides dataclasses for tracking counts of loaded, validated, and processed items:
- LoadingCounts: Tracks successfully loaded and failed items.
- ValidationCounts: Tracks passed and failed validations.
- ProcessingCounts: Tracks processed and skipped items.
"""

# Core counting components

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadingCounts:
    """Tracks the number of successfully loaded and failed items.

    Attributes
    ----------
    loaded_count : int
        Number of items successfully loaded.
    failed_count : int
        Number of items that failed to load.
    """

    loaded_count: int = 0
    failed_count: int = 0

    @property
    def total_attempted(self) -> int:
        """Return the total number of attempted loads (successful + failed)."""
        return self.loaded_count + self.failed_count

    @property
    def success_rate(self) -> float:
        """Return the rate of successful loads as a float between 0 and 1."""
        total = self.total_attempted
        return self.loaded_count / total if total else 1.0

    @property
    def is_successful(self) -> bool:
        """Return True if there are no failed validations, otherwise False."""
        return self.failed_count == 0


@dataclass(frozen=True)
class ProcessingCounts:
    """Tracks the number of processed and skipped items.

    Attributes
    ----------
    processed_count : int
        Number of items that have been processed.
    skipped_count : int
        Number of items that have been skipped.
    """

    processed_count: int = 0
    skipped_count: int = 0

    @property
    def total_encountered(self) -> int:
        """Return the total number of encountered items (processed + skipped)."""
        return self.processed_count + self.skipped_count


@dataclass(frozen=True)
class ValidationCounts:
    """Tracks the number of passed and failed validations.

    Attributes
    ----------
    passed_count : int
        Number of items that passed validation.
    failed_count : int
        Number of items that failed validation.
    """

    passed_count: int = 0
    failed_count: int = 0

    @property
    def total_validated(self) -> int:
        """Return the total number of validated items (passed + failed)."""
        return self.passed_count + self.failed_count

    @property
    def pass_rate(self) -> float:
        """Return the rate of passed validations as a float between 0 and 1."""
        total = self.total_validated
        return self.passed_count / total if total else 1.0

    @property
    def is_successful(self) -> bool:
        """Return True if there are no failed validations, otherwise False."""
        return self.failed_count == 0


__all__ = [
    "LoadingCounts",
    "ProcessingCounts",
    "ValidationCounts",
]
