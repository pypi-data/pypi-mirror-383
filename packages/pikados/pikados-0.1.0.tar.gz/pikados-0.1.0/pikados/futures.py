"""
Provides a 'Future' system with hierarchy.
"""

__all__ = ["FutureSet", "autoconfirm"]

import asyncio
from typing import Any, Callable, List, Optional, Self, Set, Union


class FutureSet:
    """
    Set of 'Future' objects and underlying 'FutureSet' nodes.
    """

    parent: Optional[Self]
    """Parent FutureSet (if any)."""
    futures: Set[asyncio.Future | Self]
    """Pending futures."""
    loop: asyncio.AbstractEventLoop
    """Event loop to creates Future instances on."""
    callbacks: List[Callable[[Self], Any]]
    """Callbacks for the 'close'/'done' event."""

    def __init__(
        self, parent: Optional[Self] = None, loop: asyncio.AbstractEventLoop = None
    ):
        """
        Initialize a new FutureSet.
        :param parent: Parent FutureSet.
        :param loop: Event Loop.
        """
        self.parent = parent
        self.futures = set()
        self.loop = loop or asyncio.get_running_loop()
        self.callbacks = []

    def create(self) -> asyncio.Future:
        """
        Create a new 'Future', tracked by this FutureSet.
        :return: Future.
        """
        future = self.loop.create_future()
        self.futures.add(future)
        future.add_done_callback(self.futures.discard)
        return future

    def remove(self, future: Union[asyncio.Future, Self]):
        """
        Remove an entry from the registered promises.
        :param future: Future to remove.
        """
        self.futures.discard(future)

    def set_exception(self, ex: BaseException):
        """
        Propagates an exception to all registered Future and FutureSet instances.
        :param ex: Exception to set.
        """
        for entry in self.futures:
            entry.set_exception(ex)
        self.futures.clear()

    def create_child(self) -> Self:
        """
        Create a 'child' FutureSet, allowing 'set_exception' to trickle downwards.
        :return: Child FutureSet.
        """
        child = FutureSet(parent=self, loop=self.loop)
        self.futures.add(child)
        child.add_done_callback(self.futures.discard)
        return child

    def add_done_callback(self, callback: Callable[[Self], Any]):
        """
        Add a callback for the 'close' event, marking this as 'done'.
        :param callback: Callback to invoke `(caller: FutureSet) -> Any`.
        """
        self.callbacks.append(callback)  # noqa

    def close(self):
        """
        Close the futureSet
        :raises RuntimeError: Pending futures are still present.
        """
        if self.futures:
            raise RuntimeError(
                "Cannot close FutureSet, pending futures might never resolve."
            )
        q, self.callbacks = self.callbacks, []
        for entry in q:
            entry(self)
        if self.parent:
            self.parent.remove(self)

    def __hash__(self) -> int:
        return hash(id(self))


def _confirm(future: asyncio.Future, value: Any):
    """
    Confirm a future if it is not done yet.
    :param future: Future to confirm.
    :param value: Confirmation Value.
    """
    if not future.done():
        future.set_result(value)


def autoconfirm(future: asyncio.Future, delay: float, value=None) -> asyncio.Future:
    """
    Set the result of a future after a delay has passed, and no result was set.
    :param future: Future to auto-confirm.
    :param delay: Delay before confirming.
    :param value: Value to use for `set_result`.
    :return: Original Future.
    """
    future.get_loop().call_later(delay, _confirm, future, value)
    return future
