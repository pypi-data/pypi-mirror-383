import asyncio
from typing import Any, Callable, Awaitable
from aio_pika.abc import AbstractIncomingMessage
from .adapter import Adapter


class ConsumerChannel:
    def __init__(self, logger: Any, namespace: str, callback: Callable[[AbstractIncomingMessage], Awaitable[None]]):
        self.logger = logger
        self.namespace = namespace
        self.callback = callback
        self.adapter = Adapter(logger)
        self._task: asyncio.Task | None = None
        self.running = False

    async def start(self):
        if not await self.adapter.open():
            self.logger.error("ConsumerChannel: Failed to open adapter")
            return

        self.running = True
        self._task = asyncio.create_task(
            self.adapter.start_consume(self.namespace, self.callback)
        )
        self.logger.info(f"ConsumerChannel: Started consuming on {self.namespace}")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.adapter.close()
        self.logger.info("ConsumerChannel: Stopped")

    async def ack(self, message: AbstractIncomingMessage):
        await self.adapter.ack(message)

    async def nack(self, message: AbstractIncomingMessage, requeue: bool = True):
        await self.adapter.nack(message, requeue=requeue)