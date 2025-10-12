# tests/test_base_message_mixin.py
# pyright: strict

from dataclasses import dataclass
from typing import Protocol, cast

from ci.transparency.cwe.types.base.messages import MessageCollection
from ci.transparency.cwe.types.base.result_helpers import HasMessages, with_message_methods


# Protocol so the checker knows the decorator-added methods exist and return DummyResult
class _MsgMethods(Protocol):
    def add_error(self, msg: str) -> "DummyResult": ...
    def add_warning(self, msg: str) -> "DummyResult": ...
    def add_info(self, msg: str) -> "DummyResult": ...


@with_message_methods
@dataclass(frozen=True, slots=True)
class DummyResult(HasMessages):
    """Minimal result type just to exercise the mixin."""
    messages: MessageCollection


def _empty_mc() -> MessageCollection:
    """Construct a valid, empty MessageCollection with proper list types."""
    return MessageCollection(errors=[], warnings=[], infos=[])


def test_decorator_adds_methods_and_preserves_type() -> None:
    r0 = DummyResult(messages=_empty_mc())

    # Runtime presence checks
    assert hasattr(r0, "add_error")
    assert hasattr(r0, "add_warning")
    assert hasattr(r0, "add_info")

    # Static typing + return type
    r1: DummyResult = cast(_MsgMethods, r0).add_error("E1")
    assert isinstance(r1, DummyResult)
    assert r1 is not r0  # immutability


def test_error_warning_info_append_correct_buckets() -> None:
    r0 = DummyResult(messages=_empty_mc())
    r1: DummyResult = cast(_MsgMethods, r0).add_error("E1")
    r2: DummyResult = cast(_MsgMethods, r1).add_warning("W1")
    r3: DummyResult = cast(_MsgMethods, r2).add_info("I1")

    # Buckets
    assert r3.messages.errors == ["E1"]
    assert r3.messages.warnings == ["W1"]
    assert r3.messages.infos == ["I1"]

    # Originals untouched
    assert len(r0.messages.errors) == len(r0.messages.warnings) == len(r0.messages.infos) == 0


def test_multiple_adds_accumulate_in_order() -> None:
    r0 = DummyResult(messages=_empty_mc())
    r1: DummyResult = cast(_MsgMethods, r0).add_error("E1")
    r2: DummyResult = cast(_MsgMethods, r1).add_error("E2")
    r3: DummyResult = cast(_MsgMethods, r2).add_error("E3")

    assert r3.messages.errors[-3:] == ["E1", "E2", "E3"]
    assert len(r3.messages.warnings) == 0
    assert len(r3.messages.infos) == 0


def test_messages_object_is_replaced_not_mutated() -> None:
    r0 = DummyResult(messages=_empty_mc())
    m0: MessageCollection = r0.messages
    r1: DummyResult = cast(_MsgMethods, r0).add_info("I1")
    m1: MessageCollection = r1.messages

    assert m1 is not m0  # dataclasses.replace produced a new MessageCollection
