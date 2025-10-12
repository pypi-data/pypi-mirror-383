# tests/test_cwe_result_message_mixin.py
# pyright: strict

from typing import Protocol, cast

from ci.transparency.cwe.types.cwe.results import CweLoadingResult
from ci.transparency.cwe.types.base.messages import MessageCollection


class _MsgMethods(Protocol):
    """Structural typing shim so Pyright knows about the decorator-added methods."""

    def add_error(self, msg: str) -> "CweLoadingResult": ...
    def add_warning(self, msg: str) -> "CweLoadingResult": ...
    def add_info(self, msg: str) -> "CweLoadingResult": ...


def test_methods_exist_and_return_type_preserved() -> None:
    r0 = CweLoadingResult()
    # Runtime presence checks (works whether or not type checker knows about them)
    assert hasattr(r0, "add_error")
    assert hasattr(r0, "add_warning")
    assert hasattr(r0, "add_info")

    # Tell Pyright those methods exist and return CweLoadingResult
    r1: CweLoadingResult = cast(_MsgMethods, r0).add_error("boom")
    assert isinstance(r1, CweLoadingResult)
    assert r1 is not r0  # immutability


def test_add_error_appends_without_mutating_original() -> None:
    r0 = CweLoadingResult()
    # Ensure messages is properly typed for the checker
    m0: MessageCollection = r0.messages
    assert len(m0.errors) == 0

    r1: CweLoadingResult = cast(_MsgMethods, r0).add_error("E1")

    # Original unchanged
    m0_after: MessageCollection = r0.messages
    assert len(m0_after.errors) == 0

    # New instance has the message
    m1: MessageCollection = r1.messages
    assert "E1" in list(m1.errors)


def test_warning_and_info_land_in_right_buckets() -> None:
    r0 = CweLoadingResult()
    r1: CweLoadingResult = cast(_MsgMethods, r0).add_warning("W1")
    r2: CweLoadingResult = cast(_MsgMethods, r1).add_info("I1")

    m2: MessageCollection = r2.messages
    assert "W1" in list(m2.warnings)
    assert "I1" in list(m2.infos)
    assert len(m2.errors) == 0


def test_chaining_accumulates_and_preserves_type() -> None:
    r0 = CweLoadingResult()
    r1: CweLoadingResult = cast(_MsgMethods, r0).add_error("E1")
    r2: CweLoadingResult = cast(_MsgMethods, r1).add_warning("W1")
    r3: CweLoadingResult = cast(_MsgMethods, r2).add_info("I1")

    assert isinstance(r3, CweLoadingResult)

    m3: MessageCollection = r3.messages
    assert "E1" in list(m3.errors)
    assert "W1" in list(m3.warnings)
    assert "I1" in list(m3.infos)

    # Originals untouched
    m0: MessageCollection = r0.messages
    assert len(m0.errors) == len(m0.warnings) == len(m0.infos) == 0


def test_multiple_adds_accumulate_in_order() -> None:
    r0 = CweLoadingResult()
    r1: CweLoadingResult = cast(_MsgMethods, r0).add_error("E1")
    r2: CweLoadingResult = cast(_MsgMethods, r1).add_error("E2")

    m2: MessageCollection = r2.messages
    # Expect insertion order
    assert list(m2.errors)[-2:] == ["E1", "E2"]
    assert len(m2.warnings) == 0
    assert len(m2.infos) == 0


def test_messages_object_is_replaced() -> None:
    r0 = CweLoadingResult()
    m0: MessageCollection = r0.messages
    r1: CweLoadingResult = cast(_MsgMethods, r0).add_info("I1")
    m1: MessageCollection = r1.messages
    assert m1 is not m0
