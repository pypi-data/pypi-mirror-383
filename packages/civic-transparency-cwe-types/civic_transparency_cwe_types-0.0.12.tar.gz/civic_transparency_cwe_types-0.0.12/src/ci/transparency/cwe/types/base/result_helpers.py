"""Helpers for adding message methods to result classes.

This module provides a decorator to add error, warning, and info message methods to result classes.
"""

from dataclasses import replace
from typing import Protocol, TypeVar, runtime_checkable

from ci.transparency.cwe.types.base.messages import MessageCollection


# Protocol for result types that have a messages field
@runtime_checkable
class HasMessages(Protocol):
    """Protocol for result types that have a messages field."""

    messages: MessageCollection


T = TypeVar("T", bound=HasMessages)


def _add_message_to_result[T: HasMessages](result: T, level: str, message: str) -> T:
    """Add a message to any result with MessageCollection.

    Internal helper that modifies the messages collection immutably.
    """
    messages = result.messages

    if level == "error":
        new_errors = messages.errors + [message]
        new_messages = replace(messages, errors=new_errors)
    elif level == "warning":
        new_warnings = messages.warnings + [message]
        new_messages = replace(messages, warnings=new_warnings)
    else:  # info
        new_infos = messages.infos + [message]
        new_messages = replace(messages, infos=new_infos)

    return replace(result, messages=new_messages)  # type: ignore[return-value]


def with_message_methods[T: HasMessages](cls: type[T]) -> type[T]:
    """Add message methods to result classes.

    Decorator that adds add_error(), add_warning(), and add_info() methods
    to any result class with a MessageCollection field.
    """

    def add_error(self: T, msg: str) -> T:
        return _add_message_to_result(self, "error", msg)

    def add_warning(self: T, msg: str) -> T:
        return _add_message_to_result(self, "warning", msg)

    def add_info(self: T, msg: str) -> T:
        return _add_message_to_result(self, "info", msg)

    # Add methods to class
    cls.add_error = add_error  # type: ignore[attr-defined]
    cls.add_warning = add_warning  # type: ignore[attr-defined]
    cls.add_info = add_info  # type: ignore[attr-defined]

    return cls


__all__ = [
    "HasMessages",
    "with_message_methods",
]
