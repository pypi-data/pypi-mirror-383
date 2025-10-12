# src/ci/transparency/cwe/types/base/collections.py
"""Collections for tracking files, categories, and duplicates in the civic transparency CWE types module.

This module provides dataclasses for:
- FileCollection: tracking processed, failed, and skipped files.
- CategoryCollection: tracking category statistics.
- DuplicateCollection: tracking duplicate IDs and their associated file paths.
"""

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import cast

type FrameworkStatsDict = dict[str, int]
type RelationshipMapDict = dict[str, list[str]]
type RelationshipDepthsDict = dict[str, int]
type RelationshipTypesDict = dict[str, int]


# Domain-specific collections
@dataclass(frozen=True)
class CategoryCollection:
    """Tracks statistics for categories.

    Attributes
    ----------
    category_stats : dict[str, int]
        Dictionary mapping category names to their counts.
    """

    category_stats: dict[str, int] = cast("dict[str, int]", field(default_factory=dict))

    @property
    def category_count(self) -> int:
        """Return the number of categories tracked in the collection."""
        return len(self.category_stats)

    @property
    def most_common_category(self) -> str | None:
        """Return the most common category based on the highest count.

        Returns
        -------
        str or None
            The category with the highest count, or None if there are no categories.
        """
        if not self.category_stats:
            return None
        return max(self.category_stats, key=lambda k: self.category_stats[k])


@dataclass(frozen=True)
class DuplicateCollection:
    """Tracks duplicate IDs and their associated file paths.

    Attributes
    ----------
    duplicate_ids : dict[str, list[Path]]
        Dictionary mapping duplicate IDs to lists of file paths where duplicates were found.
    """

    duplicate_ids: dict[str, list[Path]] = cast(
        "dict[str, list[Path]]", field(default_factory=dict)
    )

    @property
    def duplicate_count(self) -> int:
        """Return the number of duplicate IDs tracked in the collection.

        Returns
        -------
        int
            The number of duplicate IDs.
        """
        return len(self.duplicate_ids)

    @property
    def has_duplicates(self) -> bool:
        """Return True if there are any duplicate IDs, otherwise False."""
        return bool(self.duplicate_ids)


# File tracking
@dataclass(frozen=True)
class FileCollection:
    """Tracks processed, failed, and skipped files.

    Attributes
    ----------
    processed_files : list[Path]
        list of files that have been processed.
    failed_files : list[Path]
        list of files that failed to process.
    skipped_files : list[Path]
        list of files that were skipped.
    """

    processed_files: list[Path] = cast("list[Path]", field(default_factory=list))
    failed_files: list[Path] = cast("list[Path]", field(default_factory=list))
    skipped_files: list[Path] = cast("list[Path]", field(default_factory=list))

    @property
    def processed_file_count(self) -> int:
        """Return the number of processed files."""
        return len(self.processed_files)

    @property
    def failed_file_count(self) -> int:
        """Return the number of failed files."""
        return len(self.failed_files)

    @property
    def skipped_file_count(self) -> int:
        """Return the number of skipped files."""
        return len(self.skipped_files)

    @property
    def total_files(self) -> int:
        """Return the total number of files (processed, failed, skipped)."""
        return self.processed_file_count + self.failed_file_count + self.skipped_file_count


@dataclass(frozen=True)
class FrameworkCollection:
    """Tracks statistics for frameworks.

    Could be reused for any domain that categorizes by framework.
    """

    framework_stats: FrameworkStatsDict = cast("FrameworkStatsDict", field(default_factory=dict))

    @property
    def framework_count(self) -> int:
        """Return the number of frameworks tracked."""
        return len(self.framework_stats)

    @property
    def most_common_framework(self) -> str | None:
        """Return the most common framework based on highest count."""
        if not self.framework_stats:
            return None
        return max(self.framework_stats, key=lambda k: self.framework_stats[k])

    def add_framework(self, framework: str) -> "FrameworkCollection":
        """Add or increment a framework count."""
        new_stats = {**self.framework_stats}
        new_stats[framework] = new_stats.get(framework, 0) + 1
        return replace(self, framework_stats=new_stats)


@dataclass(frozen=True)
class ReferenceCollection:
    """Tracks references between items and their validity.

    Could be reused for any domain that has inter-item references.
    """

    reference_map: RelationshipMapDict = field(default_factory=lambda: {})
    invalid_references: list[str] = cast("list[str]", field(default_factory=list))
    orphaned_items: list[str] = cast("list[str]", field(default_factory=list))

    @property
    def total_references_count(self) -> int:
        """Total number of references tracked."""
        return sum(len(refs) for refs in self.reference_map.values())

    @property
    def invalid_reference_count(self) -> int:
        """Number of invalid references."""
        return len(self.invalid_references)

    @property
    def orphaned_item_count(self) -> int:
        """Number of items with no references."""
        return len(self.orphaned_items)

    @property
    def has_invalid_references(self) -> bool:
        """True if there are invalid references."""
        return bool(self.invalid_references)

    @property
    def has_orphaned_items(self) -> bool:
        """True if there are orphaned items."""
        return bool(self.orphaned_items)

    def add_reference(self, from_item: str, to_item: str) -> "ReferenceCollection":
        """Add a reference between items."""
        current_refs = self.reference_map.get(from_item, [])
        if to_item not in current_refs:
            new_refs = current_refs + [to_item]
            new_map = {**self.reference_map, from_item: new_refs}
            return replace(self, reference_map=new_map)
        return self

    def add_invalid_reference(self, reference_desc: str) -> "ReferenceCollection":
        """Add an invalid reference."""
        new_invalid = self.invalid_references + [reference_desc]
        return replace(self, invalid_references=new_invalid)

    def add_orphaned_item(self, item_id: str) -> "ReferenceCollection":
        """Add an orphaned item."""
        new_orphaned = self.orphaned_items + [item_id]
        return replace(self, orphaned_items=new_orphaned)


__all__ = [
    # types
    "FrameworkStatsDict",
    "RelationshipMapDict",
    "RelationshipDepthsDict",
    "RelationshipTypesDict",
    # Domain-specific collections
    "CategoryCollection",
    "DuplicateCollection",
    "FileCollection",
    "FrameworkCollection",
    "ReferenceCollection",
]
