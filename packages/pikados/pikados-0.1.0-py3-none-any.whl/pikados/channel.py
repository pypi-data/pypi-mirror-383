"""
Async Pika API.
"""

__all__ = ["AsyncChannel"]

import asyncio
import inspect
import logging
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

from pika.channel import Channel
from pika.exceptions import UnroutableError
from pika.exchange_type import ExchangeType
from pika.frame import Method
from pika.spec import Basic, BasicProperties

from pikados.futures import FutureSet, autoconfirm

logger = logging.getLogger(__name__)


class AsyncChannel:
    """
    Pika Channel with async API.
    """

    base: Channel
    """The underlying channel."""
    futures: FutureSet
    """Futures for this channel, often a child of the Connection FutureSet."""
    consumers: Dict[str, Callable]
    """Consumer registration."""
    response_window: float
    """Time window for the server to supply an error."""
    closed: asyncio.Event
    """Awaitable event for synchronous shutdowns.."""

    _exception: Optional[BaseException]
    """Most recent exception."""
    _lock: asyncio.Lock
    """Basic lock to prevent conflict in 'mandatory' publishing."""
    _mandatory: Dict[tuple, asyncio.Future]
    """Callbacks for messages published with the mandatory flag."""

    def __init__(self, channel: Channel, futures: FutureSet):
        """
        Initialize a new AsyncChannel.
        :param channel: Underlying channel.
        :param futures: Futures.
        """
        self.base = channel
        self.futures = futures
        self._exception = None
        self.base.add_on_close_callback(self._closed)
        self.base.add_on_return_callback(self._on_return)
        self.closed = asyncio.Event()

        self.consumers = {}
        self.response_window = 0.02
        self._lock = asyncio.Lock()
        self._mandatory = {}

    async def aclose(self, reply_code: int = 0, reply_text: str = "Normal shutdown"):
        self.close(reply_code, reply_text)
        await self.closed.wait()

    def close(self, reply_code: int = 0, reply_text: str = "Normal shutdown"):
        """
        Shutdown the channel, cancelling all associated listeners.
        :param int reply_code: The reason code to send to broker
        :param str reply_text: The reason text to send to broker
        """
        if self.is_open:
            self.base.close(reply_code, reply_text)
        self.consumers.clear()
        self.futures.close()
        self.closed.set()

    def _on_return(
        self,
        channel: "Channel",
        basic: Basic.Return,
        properties: BasicProperties,
        data: bytes,
    ):
        """
        Handles a Return message.
        :param channel: Channel of origin.
        :param basic: Basic Return.
        :param properties: Message properties.
        :param data: Data.
        """
        assert channel is self.base
        key = basic.exchange, basic.routing_key
        if future := self._mandatory.get(key):
            if future.done():
                return
            if basic.reply_code == 312:
                ex = UnroutableError([basic])
                future.set_exception(ex)

    @property
    def channel_number(self) -> int:
        return self.base.channel_number

    @property
    def consumer_tags(self) -> Sequence[str]:
        return self.base.consumer_tags

    @classmethod
    def wrap(cls, channel: Channel, futures: FutureSet):
        """
        Wrap a channel for Async support.
        :param channel: Channel to wrap.
        :param futures: Futures
        :return: AsyncChannel.
        """
        return cls(channel, futures)

    def _closed(self, instance: Channel, ex: BaseException):
        assert instance == self.base
        self.closed.set()
        self._exception = ex
        self.futures.set_exception(ex)

    def dispatch(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        """
        Dispatch a raw Pika message.
        :param channel: Original Pika Channel.
        :param method: Delivery information (queue, exchange, consumer/delivery tag).
        :param properties: Message and Body Metadata.
        :param body: Message Body.
        """
        assert self.base == channel
        consumer = self.consumers.get(method.consumer_tag)
        result = consumer(self, method, properties, body)
        if inspect.iscoroutine(result):
            logger.warning(
                "Consumer %r returned unexpected coroutine.", method.consumer_tag
            )

    async def topic_consume(
        self,
        exchange: str,
        routing_key: str,
        on_message_callback,
        queue: str = "",
        exclusive: bool = True,
        auto_delete: bool = True,
        auto_ack: bool = True,
        consumer_tag: Optional[str] = "",
        arguments: Optional[dict] = None,
    ) -> Tuple[str, str]:
        """
        Consume messages from a topic, with a pattern for routing keys.
        This method is a shorthand method for creating a temporary queue
        and binding it to a 'topic' exchange.
        This uses a temporary queue.

        Patterns:

        - `my_routes.*` is valid for `my_routes.abc`,
        - `*.abc` is valid for `my_routes.abc`.
        - `my_*` is NOT valid for `my_routes.abc`
        - `#` is valid for all routes.

        Using `#` as the pattern will receive all messages from that exchange,
        just like a fanout.
        :param exchange: Exchange of the topics.
        :param routing_key: Pattern for topics. Routing keys are split by '.'.
        :param on_message_callback: Callback for these topics
        :param queue: The queue to use for receiving (empty string auto-generates).
        :param exclusive: Run the underlying queue in exclusive mode.
        :param auto_delete: Auto_delete the queue upon disconnect.
        :param auto_ack: Automatically ACK received messages.
        :param consumer_tag:
        :param arguments:
        :return: Name of the temporary queue.
        """
        # Let it auto-generate a queue name.
        frame = await self.queue_declare(
            queue, exclusive=exclusive, auto_delete=auto_delete
        )
        queue = frame.method.queue
        await self.queue_bind(queue, exchange, routing_key)
        consumer_tag = await self.basic_consume(
            queue,
            on_message_callback,
            auto_ack=auto_ack,
            exclusive=exclusive,
            consumer_tag=consumer_tag,
            arguments=arguments,
        )
        return consumer_tag, queue

    # region basic

    async def basic_consume(
        self,
        queue: str,
        on_message_callback: Callable,
        auto_ack: bool = False,
        exclusive: bool = False,
        consumer_tag: Optional[str] = None,
        arguments: Optional[dict] = None,
    ):
        """
        Consume from a queue via the `on_message_callback`.
        :param queue: Queue to consume.
        :param callable on_message_callback: The function to call when
            consuming with the signature
            on_message_callback(channel, method, properties, body), where
            - channel: pika.channel.Channel
            - method: pika.spec.Basic.Deliver
            - properties: pika.spec.BasicProperties
            - body: bytes
        :param auto_ack: Immediately ack message upon reception.
        :param exclusive: Don't allow other consumers on the queue.
        :param consumer_tag: Specify a custom consumer tag.
        :param arguments: Custom key/value pair arguments for the consumer.
        :raises TypeError: Callback is async (not allowed).
        :raises pika.exceptions.ChannelClosedByBroker: Queue not found.
        """
        future = self.futures.create()
        if inspect.iscoroutinefunction(on_message_callback):
            raise TypeError(
                "AsyncChannel does not orchestrate AsyncIO Tasking,"
                " provide synchronous callbacks and use loop.create_task for async"
                "handling."
            )
        tag = self.base.basic_consume(
            queue,
            auto_ack=auto_ack,
            exclusive=exclusive,
            consumer_tag=consumer_tag,
            arguments=arguments,
            callback=future.set_result,
            on_message_callback=self.dispatch,
        )
        self.consumers[tag] = on_message_callback
        await future
        return tag

    async def basic_qos(
        self,
        prefetch_size: int = 0,
        prefetch_count: int = 0,
        global_qos: bool = False,
    ):
        """
        Apply quality of service by setting.
        :param prefetch_size: Set a receive-window size.
        :param prefetch_count:
        :param global_qos: Apply to all consumers on the channel.
        """
        f = self.futures.create()
        self.base.basic_qos(
            prefetch_size=prefetch_size,
            prefetch_count=prefetch_count,
            global_qos=global_qos,
            callback=f.set_result,
        )
        await f

    def ack(self, delivery_tag: int = 0, multiple: bool = False) -> None:
        """
        Performs a blanket 'ack' with no asyncio features or confirmations.
        :param delivery_tag: The server-assigned delivery tag.
        :param multiple: ACK the delivery tag is treated as "up to and including".
        """
        self.base.basic_ack(delivery_tag, multiple)

    async def basic_ack(self, delivery_tag: int = 0, multiple: bool = False):
        """
        Confirm 1 or more delivery tags.
        A delivery_tag of `0` and multiple of `True` will ACK all
        outstanding messages.
        :param delivery_tag: The server-assigned delivery tag.
        :param multiple: ACK the delivery tag is treated as "up to and including".
        """
        f = self.futures.create()
        self.base.basic_ack(delivery_tag, multiple)
        await autoconfirm(f, self.response_window)

    async def basic_publish(
        self,
        exchange: str,
        routing_key: str,
        body: Union[bytes, str],
        properties: Optional[BasicProperties] = None,
        mandatory: bool = False,
    ):
        """
        Publish to the given exchange and routing key.
        :param exchange: The exchange to publish to (default = '')
        :param routing_key: Routing key or queue name to send to.
        :param body: Message Body.
        :param properties: Message Properties.
        :param mandatory: Confirm the target queue or exchange accept the message.
        """
        if not mandatory:
            self.base.basic_publish(
                exchange, routing_key, body, properties=properties, mandatory=mandatory
            )
            return

        key = exchange, routing_key
        if isinstance(body, str):
            body = body.encode("utf-8")

        f = self.futures.create()
        async with self._lock:
            # Mandatory 'returns' in a callback.
            # The _lock tries to prevent duplicate callbacks
            self._mandatory[key] = f
            self.base.basic_publish(
                exchange, routing_key, body, properties=properties, mandatory=mandatory
            )
            await autoconfirm(f, self.response_window)

    async def basic_cancel(self, consumer_tag: str = ""):
        """
        Cancel a consumer.
        :param consumer_tag: Consumer to cancel.
        """
        f = self.futures.create()
        self.base.basic_cancel(consumer_tag, callback=f.set_result)
        await f
        self.consumers.pop(consumer_tag, None)

    async def basic_nack(
        self, delivery_tag: int = 0, multiple: bool = False, requeue: bool = True
    ):
        """
        Reject one or more incoming messages
        To reject all outstanding messages, use a delivery tag of 0.
        :param integer delivery_tag: int/long The server-assigned delivery tag
        :param bool multiple: When True, reject "up to and including" that delivery tag.
        :param bool requeue: Attempt to requeue the messages.
        """
        f = self.futures.create()
        self.base.basic_nack(delivery_tag, multiple=multiple, requeue=requeue)
        await autoconfirm(f, self.response_window)

    async def basic_reject(self, delivery_tag: int = 0, requeue: bool = True):
        """
        Reject an incoming message, cancelling or requeue-ing the message.
        :param integer delivery_tag: int/long The server-assigned delivery tag
        :param bool requeue: Attempt to requeue the messages.
        """
        f = self.futures.create()
        self.base.basic_reject(delivery_tag=delivery_tag, requeue=requeue)
        await autoconfirm(f, self.response_window)

    # endregion

    # region exchange

    # exchange_bind
    async def exchange_declare(
        self,
        exchange: str,
        exchange_type: ExchangeType = ExchangeType.direct,
        passive: bool = False,
        durable: bool = False,
        auto_delete: bool = False,
        internal: bool = False,
        arguments: Optional[dict] = None,
    ):
        """
        Declare an exchange.
        :param exchange: Exchange name.
        :param exchange_type: Exchange type.
        :param passive: Do not create, merely verify the config.
        :param durable: Survive reboots of the broker
        :param auto_delete: Remove when no more queues are bound to it
        :param internal: Can only be published to by other exchanges
        :param arguments: Custom key/value pair arguments for the exchange
        :return:
        """
        f = self.futures.create()
        self.base.exchange_declare(
            exchange=exchange,
            exchange_type=exchange_type,
            passive=passive,
            durable=durable,
            auto_delete=auto_delete,
            internal=internal,
            arguments=arguments,
            # ---
            callback=f.set_result,
        )
        return await f

    async def exchange_delete(self, exchange: str, if_unused: bool = False) -> Method:
        """
        Delete an exchange.
        :param exchange: Exchange to delete.
        :param if_unused: Only delete if the exchange has no bindings.
        :return: Method(DeleteOk)
        :raises pika.exceptions.ChannelClosedByBroker: Error 406, Precondition failed, "vhost in use".
        """
        f = self.futures.create()
        self.base.exchange_delete(exchange, if_unused, f.set_result)
        return await f

    async def exchange_unbind(
        self,
        destination: str,
        source: Optional[str] = None,
        routing_key: str = "",
        arguments: Optional[dict] = None,
    ) -> Method:
        """
        Unbind an exchange from another exchange.
        :param destination: The destination exchange to unbind
        :param source: The source exchange to unbind from
        :param routing_key: The routing key to unbind
        :param dict arguments: Custom key/value pair arguments for the binding
        :return: Method(UnbindOk)
        :raises ValueError:
        """
        t = self.futures.create()
        self.base.exchange_unbind(
            destination, source, routing_key, arguments, t.set_result
        )
        return await t

    # endregion

    # region queue
    async def queue_bind(
        self,
        queue: str,
        exchange: str,
        routing_key: Optional[str] = None,
        arguments: Optional[dict] = None,
    ):
        """
        Create an exchange/route binding for a queue.
        :param queue: Queue to bind.
        :param exchange: Exchange to bind to.
        :param routing_key: New routing key to bind to.
        :param arguments: Additional arguments.
        """
        f = self.futures.create()
        self.base.queue_bind(
            queue,
            exchange,
            routing_key=routing_key,
            arguments=arguments,
            callback=f.set_result,
        )
        await f

    async def queue_declare(
        self,
        queue: str,
        passive: bool = False,
        durable: bool = False,
        exclusive: bool = False,
        auto_delete: bool = False,
        arguments: Optional[dict] = None,
    ) -> Method:
        """
        Create a queue with a specific name and configuration.
        Raises exceptions on permission errors and configuration errors.
        Use 'Passive' to check, but not create if missing.
        :param queue: Queue Name.
        :param passive: Do not create, merely verify the config.
        :param durable: Survive reboots of the broker
        :param exclusive: Only allow access by the current connection
        :param auto_delete: Delete after consumer cancels or disconnects
        :param arguments: Custom key/value arguments for the queue
        :returns: Method(Frame)
        """
        result = self.futures.create()
        self.base.queue_declare(
            queue,
            passive=passive,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            arguments=arguments,
            callback=result.set_result,
        )
        return await result

    async def queue_delete(
        self,
        queue: str,
        if_unused: bool = False,
        if_empty: bool = False,
    ) -> Method:
        """
        Delete a specific queue.
        :param queue: Queue name.
        :param if_unused: Only delete if no consumers are attached.
        :param if_empty: Only delete if the queue is empty.
        :return: Method(DeleteOk)
        """
        result = self.futures.create()
        self.base.queue_delete(queue, if_unused, if_empty, result.set_result)
        return await result

    async def queue_purge(self, queue: str) -> Method:
        """
        Purge all messages from a queue.
        :param queue: Queue name.
        :return: Method(PurgeOk).
        """
        result = self.futures.create()
        self.base.queue_purge(queue, result.set_result)
        return await result

    async def queue_unbind(
        self,
        queue: str,
        exchange: str,
        routing_key: str,
        arguments: Optional[dict] = None,
    ) -> Method:
        """
        Unbind a specific queue binding, can only unbind 1 entry at a time.
        :param queue: Queue to unbind.
        :param exchange: Bound Exchange.
        :param routing_key: Bound Queue.
        :param arguments: Additional arguments.
        :return: Method(UnbindOk).
        """
        result = self.futures.create()
        self.base.queue_unbind(
            queue, exchange, routing_key, arguments, callback=result.set_result
        )
        return await result

    # endregion

    # region Transactions

    async def tx_select(self) -> Method:
        """
        Start transaction.
        :return: Method(SelectOk)
        """
        f = self.futures.create()
        self.base.tx_select(callback=f.set_result)
        return await f

    async def tx_commit(self) -> Method:
        """
        Commit the transaction
        :return: Method(CommitOk)
        """
        f = self.futures.create()
        self.base.tx_commit(callback=f.set_result)
        return await f

    async def tx_rollback(self) -> Method:
        """
        Rollback the transaction, allowing it to be reused.
        :return: Method(RollbackOk)
        """
        f = self.futures.create()
        self.base.tx_rollback(callback=f.set_result)
        return await f

    # endregion

    # region properties pass-through

    @property
    def is_closed(self) -> bool:
        """Returns True if the channel is closed."""
        return self.base.is_closed

    @property
    def is_closing(self) -> bool:
        """Returns True if client-initiated closing of the channel is in
        progress."""
        return self.base.is_closing

    @property
    def is_open(self) -> bool:
        """Returns True if the channel is open."""
        return self.base.is_open

    @property
    def is_opening(self) -> bool:
        """Returns True if the channel is opening."""
        return self.base.is_opening

    # endregion

    def __del__(self):
        if self.is_open:
            logger.warning(
                "Garbage collected AsyncChannel %s in the 'open' state.",
                self.channel_number,
            )
