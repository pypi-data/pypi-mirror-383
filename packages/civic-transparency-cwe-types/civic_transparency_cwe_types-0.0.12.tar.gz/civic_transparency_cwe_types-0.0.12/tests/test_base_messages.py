# pyright: strict

from dataclasses import FrozenInstanceError

import pytest

from ci.transparency.cwe.types.base.messages import MessageCollection


# --- MessageCollection ---------------------------------------------------------------

def test_message_collection_defaults() -> None:
    coll = MessageCollection()
    assert coll.errors == []
    assert coll.warnings == []
    assert coll.infos == []
    assert coll.error_count == 0
    assert coll.warning_count == 0
    assert coll.info_count == 0
    assert coll.total_messages == 0
    assert coll.has_errors is False
    assert coll.has_warnings is False


def test_message_collection_counts_and_flags() -> None:
    coll = MessageCollection(
        errors=["err1", "err2"],
        warnings=["warn1"],
        infos=["info1", "info2", "info3"],
    )
    assert coll.error_count == 2
    assert coll.warning_count == 1
    assert coll.info_count == 3
    assert coll.total_messages == 6
    assert coll.has_errors is True
    assert coll.has_warnings is True


def test_message_collection_is_frozen() -> None:
    coll = MessageCollection()
    with pytest.raises(FrozenInstanceError):
        setattr(coll, "errors", ["oops"])
