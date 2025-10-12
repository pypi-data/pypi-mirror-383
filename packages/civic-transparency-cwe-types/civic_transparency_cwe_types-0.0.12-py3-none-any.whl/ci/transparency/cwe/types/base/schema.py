"""Defines schema metadata and statistics tracking for civic transparency.

This module provides:
- FileTypeStatsDict: type alias for file type statistics.
- SchemaCollection: dataclass for schema metadata and file type statistics.
"""

from dataclasses import dataclass, field, replace
from typing import cast

type FileTypeStatsDict = dict[str, int]


@dataclass(frozen=True)
class SchemaCollection:
    """Tracks schema metadata and statistics.

    Could be reused for any domain that works with schemas.
    """

    schema_name: str | None = None
    schema_version: str | None = None
    file_type_stats: FileTypeStatsDict = cast("FileTypeStatsDict", field(default_factory=dict))

    @property
    def has_schema_metadata(self) -> bool:
        """True if schema name and version are available."""
        return bool(self.schema_name and self.schema_version)

    @property
    def file_type_count(self) -> int:
        """Number of different file types processed."""
        return len(self.file_type_stats)

    def add_file_type(self, file_type: str) -> "SchemaCollection":
        """Add or increment a file type count."""
        new_stats = {**self.file_type_stats}
        new_stats[file_type] = new_stats.get(file_type, 0) + 1
        return replace(self, file_type_stats=new_stats)

    def with_metadata(
        self, schema_name: str | None, schema_version: str | None
    ) -> "SchemaCollection":
        """Return new collection with updated schema metadata."""
        return replace(self, schema_name=schema_name, schema_version=schema_version)


__all__ = [
    "FileTypeStatsDict",
    "SchemaCollection",
]
