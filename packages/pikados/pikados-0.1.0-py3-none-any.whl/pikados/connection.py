"""
Async Pika API.
"""

__all__ = ["AsyncConnection", "connect"]

import asyncio
from typing import Optional, Callable

import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.connection import Parameters

import pikados
from pikados.channel import AsyncChannel
from pikados.futures import FutureSet

# Default product string so RabbitMQ can tell what's going on.
_PRODUCT = "pika-{}/pikados-{}".format(
    getattr(pika, "__version__", "?"), pikados.__version__
)


class AsyncConnection:
    """
    AsyncConnection with async/await API.
    """

    def __init__(self, connection: AsyncioConnection, futures: FutureSet):
        """
        Initialize a new AsyncConnection.
        The 'on_close' should have been attached already.
        :param connection: AsyncioConnection.
        :param futures: Futures (inherited by AsyncChannel)
        """
        self.base = connection
        self.futures = futures
        self.closed = asyncio.Event()
        self.base.add_on_close_callback(self._closed)

    def _closed(self, con, ex):
        self.futures.set_exception(ex)
        self.closed.set()

    @property
    def params(self) -> Parameters:
        """
        Connection parameters.
        :return: Connection parameters.
        """
        return self.base.params

    @property
    def is_open(self) -> bool:
        return self.base.is_open

    @classmethod
    def wrap(cls, con: AsyncioConnection, futures: Optional[FutureSet] = None):
        """
        Wrap an AsyncioConnection to facilitate a cleaner API.
        :param con: Connection in the 'open' state.
        :param futures: Event Loop to use for asyncio/Future systems.
        :return: Wrapped connection as AsyncConnection.
        """
        assert con.is_open
        if futures is None:
            futures = FutureSet(None, con.ioloop or asyncio.get_running_loop())
            con.add_on_close_callback(lambda _, ex: futures.set_exception(ex))
        return cls(con, futures)

    async def channel(self, channel_number: int | None = None) -> AsyncChannel:
        """
        Create a channel.
        :param channel_number: Channel number (optional).
        :return: AsyncChannel (wrapping a regular channel).
        """
        f = self.futures.create()
        ch = self.base.channel(channel_number, on_open_callback=f.set_result)
        await f
        return AsyncChannel.wrap(ch, self.futures.create_child())

    async def aclose(self, reply_code: int = 200, reply_text: str = "Normal shutdown"):
        self.close(reply_code, reply_text)
        await self.closed.wait()

    def add_on_close_callback(
        self, callback: Callable[["AsyncConnection", BaseException], None]
    ):
        """
        Add a callback for connection closure due to errors or regular shutdown.
        :param callback: Close Callback.
        """
        # Replace 'AsyncioConnection' with 'AsyncConnection' (self).
        cb = lambda con, ex: callback(self, ex)
        self.base.add_on_close_callback(cb)

    def close(self, reply_code: int = 200, reply_text: str = "Normal shutdown"):
        """
        Clean disconnect the connection.
        :param int reply_code: The code number for the close
        :param str reply_text: The text reason for the close

        :raises pika.exceptions.ConnectionWrongStateError: if connection is
            closed or closing.
        """
        if self.is_open:
            self.base.close(reply_code, reply_text)


async def connect(
    parameters: Parameters,
    connection_name: Optional[str] = None,
) -> AsyncConnection:
    """
    Connect Async.
    :param parameters: Parameters.
    :param connection_name: Connection name shared with RabbitMQ.
    :return: AsyncConnection.
    """
    props = parameters.client_properties or {}
    props.setdefault("product", _PRODUCT)
    if connection_name:
        props["connection_name"] = connection_name

    futures = FutureSet()
    f = futures.create()
    con = AsyncioConnection(
        parameters,
        on_open_callback=f.set_result,
        on_open_error_callback=lambda _, ex: f.set_exception(ex),
        on_close_callback=lambda _, ex: futures.set_exception(ex),
    )
    await f
    return AsyncConnection(con, futures)
