import typing
from collections.abc import Awaitable, Callable
from typing import Any, Protocol, TypeVar

from whenever import SystemDateTime

if typing.TYPE_CHECKING:
    from .events import Event

E_contra = TypeVar("E_contra", bound="Event[Any]", contravariant=True)


class Predicate(Protocol[E_contra]):
    """Protocol for defining predicates that evaluate events."""

    def __call__(self, event: E_contra) -> bool | Awaitable[bool]: ...


class Handler(Protocol[E_contra]):
    """Protocol for defining event handlers."""

    def __call__(self, event: E_contra) -> Awaitable[None] | None: ...


class AsyncHandler(Protocol[E_contra]):
    """Protocol for defining asynchronous event handlers."""

    def __call__(self, event: E_contra) -> Awaitable[None]: ...


class TriggerProtocol(Protocol):
    def next_run_time(self) -> SystemDateTime:
        """Return the next run time of the trigger."""
        ...


JobCallable = Callable[..., Awaitable[None]] | Callable[..., Any]
