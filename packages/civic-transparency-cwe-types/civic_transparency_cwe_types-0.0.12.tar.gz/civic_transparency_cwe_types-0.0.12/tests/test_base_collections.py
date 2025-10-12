from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from ci.transparency.cwe.types.base.collections import (
    CategoryCollection,
    DuplicateCollection,
    FileCollection,
    FrameworkCollection,
    ReferenceCollection,
)

# --- CategoryCollection --------------------------------------------------------------

def test_category_collection_empty() -> None:
    coll = CategoryCollection()
    assert coll.category_stats == {}
    assert coll.category_count == 0
    assert coll.most_common_category is None


def test_category_collection_most_common() -> None:
    coll = CategoryCollection(category_stats={"A": 2, "B": 5, "C": 3})
    assert coll.category_count == 3
    assert coll.most_common_category == "B"


def test_category_collection_is_frozen() -> None:
    coll = CategoryCollection()
    with pytest.raises(FrozenInstanceError):
        setattr(coll, "category_stats", {"X": 1})


# --- DuplicateCollection -------------------------------------------------------------

def test_duplicate_collection_empty() -> None:
    coll = DuplicateCollection()
    assert coll.duplicate_ids == {}
    assert coll.duplicate_count == 0
    assert coll.has_duplicates is False


def test_duplicate_collection_basic_counts(tmp_path: Path) -> None:
    p1 = tmp_path / "x.json"
    p2 = tmp_path / "y.json"
    coll = DuplicateCollection(
        duplicate_ids={
            "CWE-001": [p1, p2],
            "CWE-002": [p2],
        }
    )
    assert coll.duplicate_count == 2  # keys, not total files
    assert coll.has_duplicates is True


def test_duplicate_collection_is_frozen() -> None:
    coll = DuplicateCollection()
    with pytest.raises(FrozenInstanceError):
        setattr(coll, "duplicate_ids", {})


# --- FileCollection ------------------------------------------------------------------

def test_file_collection_empty() -> None:
    coll = FileCollection()
    assert coll.processed_file_count == 0
    assert coll.failed_file_count == 0
    assert coll.skipped_file_count == 0
    assert coll.total_files == 0


def test_file_collection_counts(tmp_path: Path) -> None:
    processed = [tmp_path / "a.json", tmp_path / "b.json"]
    failed = [tmp_path / "bad.json"]
    skipped: list[Path] = []

    coll = FileCollection(
        processed_files=processed,
        failed_files=failed,
        skipped_files=skipped,
    )

    assert coll.processed_file_count == 2
    assert coll.failed_file_count == 1
    assert coll.skipped_file_count == 0
    assert coll.total_files == 3


def test_file_collection_is_frozen() -> None:
    coll = FileCollection()
    with pytest.raises(FrozenInstanceError):
        setattr(coll, "processed_files", [])


# --- FrameworkCollection -------------------------------------------------------------

def test_framework_collection_empty() -> None:
    coll = FrameworkCollection()
    assert coll.framework_stats == {}
    assert coll.framework_count == 0
    assert coll.most_common_framework is None


def test_framework_collection_add_is_functional_not_mutating() -> None:
    coll1 = FrameworkCollection()
    coll2 = coll1.add_framework("nist")
    coll3 = coll2.add_framework("nist").add_framework("owasp")

    # Original unchanged
    assert coll1.framework_stats == {}
    assert coll1.framework_count == 0

    # After first add
    assert coll2.framework_stats == {"nist": 1}
    assert coll2.framework_count == 1
    assert coll2.most_common_framework == "nist"

    # After subsequent adds
    assert coll3.framework_stats == {"nist": 2, "owasp": 1}
    assert coll3.framework_count == 2
    assert coll3.most_common_framework == "nist"


def test_framework_collection_is_frozen() -> None:
    coll = FrameworkCollection()
    with pytest.raises(FrozenInstanceError):
        setattr(coll, "framework_stats", {})


# --- ReferenceCollection -------------------------------------------------------------

def test_reference_collection_empty() -> None:
    coll = ReferenceCollection()
    assert coll.reference_map == {}
    assert coll.invalid_references == []
    assert coll.orphaned_items == []
    assert coll.total_references_count == 0
    assert coll.invalid_reference_count == 0
    assert coll.orphaned_item_count == 0
    assert coll.has_invalid_references is False
    assert coll.has_orphaned_items is False


def test_reference_collection_add_reference_is_idempotent() -> None:
    coll1 = ReferenceCollection()
    coll2 = coll1.add_reference("A", "B")
    coll3 = coll2.add_reference("A", "B")  # duplicate edge should be ignored
    coll4 = coll3.add_reference("A", "C")

    assert coll1.reference_map == {}
    assert coll2.reference_map == {"A": ["B"]}
    assert coll3.reference_map == {"A": ["B"]}  # unchanged on duplicate
    assert coll4.reference_map == {"A": ["B", "C"]}
    assert coll4.total_references_count == 2


def test_reference_collection_invalid_and_orphaned_helpers() -> None:
    coll = ReferenceCollection()
    coll = coll.add_invalid_reference("A -> Z (missing)")
    coll = coll.add_orphaned_item("Q42")

    assert coll.invalid_references == ["A -> Z (missing)"]
    assert coll.orphaned_items == ["Q42"]
    assert coll.invalid_reference_count == 1
    assert coll.orphaned_item_count == 1
    assert coll.has_invalid_references is True
    assert coll.has_orphaned_items is True


def test_reference_collection_is_frozen() -> None:
    coll = ReferenceCollection()
    with pytest.raises(FrozenInstanceError):
        setattr(coll, "reference_map", {})
