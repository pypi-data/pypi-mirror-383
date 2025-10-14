"""Subscriber task for polling messages."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import anyio
from anyio import create_task_group, get_cancelled_exc_class
from anyio.abc import TaskGroup
from google.api_core.exceptions import (
    Aborted,
    Cancelled,
    DeadlineExceeded,
    GatewayTimeout,
    InternalServerError,
    InvalidArgument,
    NotFound,
    PermissionDenied,
    ResourceExhausted,
    ServiceUnavailable,
    Unauthenticated,
    Unauthorized,
    Unknown,
    from_grpc_error,
)
from google.pubsub_v1 import ReceivedMessage
from grpc import RpcError

from fastpubsub.clients.pubsub import PubSubClient
from fastpubsub.datastructures import Message
from fastpubsub.exceptions import Drop, Retry
from fastpubsub.logger import logger
from fastpubsub.observability import get_apm_provider
from fastpubsub.pubsub.subscriber import Subscriber

RETRYABLE_GCP_EXCEPTIONS = (
    Aborted,
    DeadlineExceeded,
    GatewayTimeout,
    InternalServerError,
    ResourceExhausted,
    ServiceUnavailable,
    Unknown,
)

FATAL_GCP_EXCEPTIONS = (
    Cancelled,
    InvalidArgument,
    NotFound,
    PermissionDenied,
    Unauthenticated,
    Unauthorized,
)


class PubSubPollTask:
    """A task for polling messages from a Pub/Sub subscription."""

    def __init__(self, subscriber: Subscriber) -> None:
        """Initializes the PubSubPollTask.

        Args:
            subscriber: The subscriber to poll messages for.
        """
        self.ready = False
        self.running = False
        self.subscriber = subscriber

        self.apm = get_apm_provider()
        self.client = PubSubClient(self.subscriber.project_id)

    async def start(self) -> None:
        """Starts the message polling loop."""
        logger.info(f"The {self.subscriber.name} handler is waiting for messages.")

        self.running = True
        async with create_task_group() as task_group:
            while self.running:
                try:
                    await self._consume_messages(task_group)
                except get_cancelled_exc_class():
                    logger.info(f"The {self.subscriber.name} handler is turning off...")
                    self.shutdown()
                    task_group.cancel_scope.cancel()
                    raise
                except Exception as e:
                    self._on_exception(e)

    async def _consume_messages(self, task_group: TaskGroup) -> None:
        received_messages = await self.client.pull(
            self.subscriber.subscription_name, self.subscriber.control_flow_policy.max_messages
        )

        self.ready = True
        messages_to_consume = []
        for received_message in received_messages:
            message = await self._deserialize_message(received_message)
            messages_to_consume.append(message)

        for message in messages_to_consume:
            task_group.start_soon(self._consume, message)

        await anyio.sleep(0.5)

    async def _deserialize_message(self, received_message: ReceivedMessage) -> Message:
        wrapped_message = received_message.message

        delivery_attempt = 0
        if received_message.delivery_attempt is not None:
            delivery_attempt = received_message.delivery_attempt

        ack_id = received_message.ack_id
        size = len(wrapped_message.data)
        attributes = dict(wrapped_message.attributes)

        return Message(
            id=wrapped_message.message_id,
            data=wrapped_message.data,
            size=size,
            ack_id=ack_id,
            attributes=attributes,
            delivery_attempt=delivery_attempt,
        )

    async def _consume(self, message: Message) -> Any:
        with self._contextualize(message=message):
            try:
                callstack = await self.subscriber._build_callstack()
                response = await callstack.on_message(message)
                await self.client.ack([message.ack_id], self.subscriber.subscription_name)
                logger.info("Message successfully processed.")
                return response
            except Drop:
                await self.client.ack([message.ack_id], self.subscriber.subscription_name)
                logger.info("Message will be dropped.")
                return
            except Retry:
                await self.client.nack([message.ack_id], self.subscriber.subscription_name)
                logger.warning("Message processing will be retried later.")
                return
            except Exception:
                await self.client.nack([message.ack_id], self.subscriber.subscription_name)
                logger.exception("Unhandled exception on message", stacklevel=5)
                return

    @contextmanager
    def _contextualize(self, message: Message) -> Generator[None]:
        with self.apm.start_trace(name=self.subscriber.name, context=message.attributes):
            context = {
                "name": self.subscriber.name,
                "span_id": self.apm.get_span_id(),
                "trace_id": self.apm.get_trace_id(),
                "message_id": message.id,
                "topic_name": self.subscriber.topic_name,
            }
            with logger.contextualize(**context):
                yield

    def _on_exception(self, e: Exception) -> None:
        self.ready = False
        if self._should_terminate(e):
            self.running = False
            logger.exception(
                f"A non-recoverable exception happened on message handler {self.subscriber.name}."
            )
            return

        if not self._should_recover(e):
            logger.warning(
                "An recoverable error ocurred, we will try to recover from it.",
                exc_info=True,
            )
            return

        logger.warning(
            "A unhandled error ocurred, trying to recover with no guarantees.",
            exc_info=True,
        )

    def _should_recover(self, exception: Exception) -> bool:
        wrapped_exception = exception
        if isinstance(exception, RpcError):
            wrapped_exception = from_grpc_error(exception)  # type: ignore[no-untyped-call]

        if isinstance(wrapped_exception, RETRYABLE_GCP_EXCEPTIONS):
            return True

        return False

    def _should_terminate(self, exception: Exception) -> bool:
        wrapped_exception = exception
        if isinstance(exception, RpcError):
            wrapped_exception = from_grpc_error(exception)  # type: ignore[no-untyped-call]

        if isinstance(wrapped_exception, FATAL_GCP_EXCEPTIONS):
            return True

        return False

    def task_ready(self) -> bool:
        """Checks if the task is ready.

        Returns:
            True if the task is ready, False otherwise.
        """
        return self.ready

    def task_alive(self) -> bool:
        """Checks if the task is alive.

        Returns:
            True if the task is alive, False otherwise.
        """
        return self.running

    def shutdown(self) -> None:
        """Shuts down the task."""
        self.running = False
