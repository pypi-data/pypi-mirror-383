# pyright: strict

from dataclasses import FrozenInstanceError

import pytest

from ci.transparency.cwe.types.base.counts import (
    LoadingCounts,
    ProcessingCounts,
    ValidationCounts,
)

# --- LoadingCounts -------------------------------------------------------------------

def test_loading_counts_defaults() -> None:
    c = LoadingCounts()
    assert c.loaded_count == 0
    assert c.failed_count == 0
    assert c.total_attempted == 0
    assert c.success_rate == 1.0  # no attempts => 100% by definition
    assert c.is_successful is True


def test_loading_counts_nonzero() -> None:
    c = LoadingCounts(loaded_count=8, failed_count=2)
    assert c.total_attempted == 10
    assert c.success_rate == 0.8
    assert c.is_successful is False


def test_loading_counts_is_frozen() -> None:
    c = LoadingCounts()
    with pytest.raises(FrozenInstanceError):
        setattr(c, "loaded_count", 5)

# --- ProcessingCounts -----------------------------------------------------------------

def test_processing_counts_defaults() -> None:
    c = ProcessingCounts()
    assert c.processed_count == 0
    assert c.skipped_count == 0
    assert c.total_encountered == 0


def test_processing_counts_nonzero() -> None:
    c = ProcessingCounts(processed_count=4, skipped_count=1)
    assert c.total_encountered == 5


def test_processing_counts_is_frozen() -> None:
    c = ProcessingCounts()
    with pytest.raises(FrozenInstanceError):
        setattr(c, "processed_count", 10)

# --- ValidationCounts -----------------------------------------------------------------

def test_validation_counts_defaults() -> None:
    c = ValidationCounts()
    assert c.passed_count == 0
    assert c.failed_count == 0
    assert c.total_validated == 0
    assert c.pass_rate == 1.0  # no validations => 100% by definition
    assert c.is_successful is True


def test_validation_counts_nonzero() -> None:
    c = ValidationCounts(passed_count=7, failed_count=3)
    assert c.total_validated == 10
    assert c.pass_rate == 0.7
    assert c.is_successful is False


def test_validation_counts_is_frozen() -> None:
    c = ValidationCounts()
    with pytest.raises(FrozenInstanceError):
        setattr(c, "passed_count", 5)
