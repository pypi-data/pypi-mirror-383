import asyncio
from typing import Any, Callable, Awaitable, Optional
from aio_pika.abc import AbstractIncomingMessage
from .adapter import Adapter


class ConsumerChannel:
    def __init__(self, logger: Any, namespace: str, callback: Callable[[AbstractIncomingMessage], Awaitable[None]]):
        self.logger = logger
        self.namespace = namespace
        self.callback = callback
        self.adapter = Adapter(logger)
        self._task: Optional[asyncio.Task] = None
        self.running = False
        self.queue_config: Optional[dict] = None

    async def start(self):
        if not await self.adapter.open():
            self.logger.error("ConsumerChannel: Failed to open adapter")
            return

        # Get queue configuration from adapter
        self.queue_config = self.adapter.get_queue_config()

        self.running = True

        # Set up queue specific configuration
        await self._setup_queue()

        self._task = asyncio.create_task(
            self.adapter.start_consume(self.namespace, self._enhanced_callback)
        )
        self.logger.info(f"ConsumerChannel: Started consuming on {self.queue_config['queue_type']} queue {self.namespace}")

    async def _setup_queue(self):
        """
        Setup queue with proper configuration based on queue type
        """
        try:
            # Set QoS based on queue type
            await self.adapter.channel.set_qos(
                prefetch_count=self.queue_config['prefetch_count']
            )

            queue_type = self.queue_config['queue_type']
            self.logger.info(f"ConsumerChannel: Queue setup completed for {queue_type} queue")

        except Exception as e:
            self.logger.error(f"ConsumerChannel: Failed to setup queue - {e}")
            raise

    async def _enhanced_callback(self, message: AbstractIncomingMessage):
        """
        Enhanced callback with queue type specific handling
        """
        try:
            queue_type = self.queue_config['queue_type']

            # Handle delivery count for quorum queues
            if queue_type == 'quorum':
                delivery_count = getattr(message, 'delivery_count', 0)
                if delivery_count > self.queue_config.get('delivery_limit', 5):
                    self.logger.warning(
                        f"ConsumerChannel: Message exceeded delivery limit ({delivery_count}), rejecting"
                    )
                    await self.adapter.reject(message, requeue=False)
                    return

                # Log delivery attempt for monitoring
                if delivery_count > 1:
                    self.logger.info(f"ConsumerChannel: Processing message (attempt {delivery_count})")

            # Call original callback
            await self.callback(message)

        except Exception as e:
            self.logger.error(f"ConsumerChannel: Enhanced callback failed - {e}")
            # Let the original callback handle the error
            raise

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

    async def reject(self, message: AbstractIncomingMessage, requeue: bool = False):
        """
        Reject message - sends to dead letter exchange in quorum queues
        """
        await self.adapter.reject(message, requeue=requeue)

    async def get_queue_status(self) -> dict:
        """
        Get current queue status and metrics
        """
        try:
            queue_name = await self.adapter.get_queue_name(self.namespace)
            return {
                "name": queue_name,
                "type": self.queue_config['queue_type'] if self.queue_config else "unknown",
                "status": "active" if self.running else "stopped"
            }
        except Exception as e:
            self.logger.warning(f"ConsumerChannel: Failed to get queue status - {e}")
            return {}

    def _load_quorum_config(self) -> dict:
        """
        Deprecated: Configuration is now loaded from adapter
        """
        return {}