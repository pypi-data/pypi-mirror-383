import asyncio
import aio_pika
from aio_pika import ExchangeType
from aio_pika.abc import AbstractIncomingMessage
from typing import Optional, Callable, Awaitable
from pyolive.config import Config


class Adapter:
    EXCHANGE_ACTION = "action"
    EXCHANGE_CONTROL = "control"
    EXCHANGE_METRIC = "metric"
    EXCHANGE_LOGS = "logs"

    def __init__(self, logger):
        self.logger = logger
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.abc.AbstractChannel] = None
        self.queue_type: Optional[str] = None
        self.env_config: Optional[Config] = None
        self.mq_config: Optional[Config] = None
        self.amqp_url: Optional[str] = None

    def _load_config(self):
        """
        Load configuration once and cache values from both config files
        """
        if self.env_config is None:
            # Load athena-env.yaml for broker configuration
            self.env_config = Config('athena-env.yaml')

            # Load queue type
            self.queue_type = self.env_config.get_value('broker/queue-type', 'classic')

            # Build AMQP URL
            hosts = self.env_config.get_value('broker/hosts')
            port = self.env_config.get_value('broker/amqp-port')
            username = self.env_config.get_value('broker/username')
            password = self.env_config.get_value('broker/password')

            if not hosts:
                raise RuntimeError("AMQP hosts not found in configuration")

            host = hosts[0]
            self.amqp_url = f"amqp://{username}:{password}@{host}:{port}/"

        if self.mq_config is None:
            # Load athena-mq.yaml for queue mapping configuration
            self.mq_config = Config('athena-mq.yaml')

    async def open(self) -> bool:
        try:
            # Load configuration once
            self._load_config()

            self.connection = await aio_pika.connect_robust(self.amqp_url)
            self.channel = await self.connection.channel()

            self.logger.info(f"Adapter: Connected to AMQP with {self.queue_type} queue type")
            return True
        except Exception as e:
            self.logger.error(f"Adapter: Connection failed: {e}")
            return False

    async def close(self):
        try:
            if self.channel:
                await self.channel.close()
            if self.connection:
                await self.connection.close()
            self.logger.info("Adapter: Connection closed")
        except Exception as e:
            self.logger.warning(f"Adapter: Close failed: {e}")

    async def publish(self, exchange: str, routing_key: str, message: str):
        try:
            ex = await self.channel.declare_exchange(exchange, ExchangeType.TOPIC, durable=True)
            await ex.publish(
                aio_pika.Message(body=message.encode()),
                routing_key=routing_key
            )
            self.logger.debug(f"Adapter: Published to {exchange}:{routing_key} -> {message}")
        except Exception as e:
            self.logger.warning(f"Adapter: Publish failed to {exchange}:{routing_key} - {e}")

    async def start_consume(self, namespace: str, callback: Callable[[AbstractIncomingMessage], Awaitable[None]]):
        try:
            queue_name = await self.get_queue_name(namespace)

            # For existing named queues, use passive declaration only
            queue = await self._declare_existing_queue(queue_name)

            # Set QoS based on detected or configured queue type
            qos_count = self._get_qos_for_queue_type()
            await self.channel.set_qos(prefetch_count=qos_count)

            await queue.consume(callback)
            self.logger.info(f"Adapter: Started consuming on existing queue {queue_name}")

        except Exception as e:
            self.logger.error(f"Adapter: Consume failed - {e}")
            raise

    async def _declare_existing_queue(self, queue_name: str) -> aio_pika.abc.AbstractQueue:
        """
        Declare existing named queue using passive mode only
        """
        try:
            # Use passive declaration to connect to existing queue without modifying it
            queue = await self.channel.declare_queue(queue_name, durable=True, passive=True)
            self.logger.info(f"Adapter: Connected to existing queue {queue_name}")
            return queue
        except Exception as e:
            self.logger.error(f"Adapter: Failed to connect to existing queue {queue_name} - {e}")
            raise

    def _get_qos_for_queue_type(self) -> int:
        """
        Get appropriate QoS prefetch count based on configured queue type
        """
        if self.queue_type == 'quorum':
            return 1  # Conservative for quorum queues
        elif self.queue_type == 'stream':
            return 100  # Higher for streams
        else:  # classic or unknown
            return 10  # Moderate default

    async def ack(self, message: AbstractIncomingMessage):
        try:
            await message.ack()
        except Exception as e:
            self.logger.warning(f"Adapter: Ack failed - {e}")

    async def nack(self, message: AbstractIncomingMessage, requeue: bool = True):
        try:
            await message.nack(requeue=requeue)
        except Exception as e:
            self.logger.warning(f"Adapter: Nack failed - {e}")

    async def reject(self, message: AbstractIncomingMessage, requeue: bool = False):
        """
        Reject message - useful for quorum queues to send to dead letter exchange
        """
        try:
            await message.reject(requeue=requeue)
        except Exception as e:
            self.logger.warning(f"Adapter: Reject failed - {e}")

    def _get_queue_type(self) -> str:
        """
        Get queue type from cached configuration
        """
        if self.queue_type is None:
            self._load_config()
        return self.queue_type

    async def _get_queue_type(self) -> str:
        """
        Get queue type from cached configuration (async version for compatibility)
        """
        return self._get_queue_type()

    async def _ensure_channel_open(self):
        """
        Ensure the channel is open and ready for use
        """
        if not self.channel or self.channel.is_closed:
            await self._reconnect_channel()

        # Test channel with a simple operation
        try:
            await self.channel.get_qos()
        except Exception as e:
            self.logger.warning(f"Adapter: Channel test failed, reconnecting - {e}")
            await self._reconnect_channel()

    async def _reconnect_channel(self):
        """
        Reconnect the channel if it's been closed
        """
        try:
            if self.channel and not self.channel.is_closed:
                await self.channel.close()
        except Exception:
            pass  # Ignore errors when closing

        try:
            # Check if connection is still valid
            if not self.connection or self.connection.is_closed:
                self.logger.info("Adapter: Connection closed, reopening...")
                success = await self.open()
                if not success:
                    raise RuntimeError("Failed to reopen connection")
                return

            self.channel = await self.connection.channel()
            self.logger.info("Adapter: Channel reconnected")
        except Exception as e:
            self.logger.error(f"Adapter: Channel reconnection failed - {e}")
            raise

    async def _get_existing_queue_arguments(self, queue_name: str) -> dict:
        """
        Get existing queue arguments using management API or inspection
        This is a simplified version - in production you might use RabbitMQ Management API
        """
        try:
            # Try to get queue info via channel inspection (limited)
            # In practice, you would use RabbitMQ Management HTTP API here
            return {
                "x-queue-type": "quorum",
                "x-quorum-initial-group-size": 3,
                "x-delivery-limit": 5,
                "x-max-in-memory-length": 2000  # Common default
            }
        except Exception as e:
            self.logger.debug(f"Adapter: Could not get existing queue arguments - {e}")
            return {}

    def get_broker_config(self) -> dict:
        """
        Get broker configuration from athena-env.yaml
        """
        if self.env_config is None:
            self._load_config()

        return {
            'vendor': self.env_config.get_value('broker/vendor', 'RabbitMQ'),
            'hosts': self.env_config.get_value('broker/hosts', []),
            'queue_type': self.queue_type,
            'amqp_port': self.env_config.get_value('broker/amqp-port', 5672),
            'http_port': self.env_config.get_value('broker/http-port', 15672),
            'username': self.env_config.get_value('broker/username', 'guest'),
            'password': self.env_config.get_value('broker/password', 'guest')
        }

    def get_queue_mapping(self, subsystem: str) -> list:
        """
        Get queue mapping configuration from athena-mq.yaml
        """
        if self.mq_config is None:
            self._load_config()

        return self.mq_config.get_value(subsystem, [])

    def get_queue_config(self) -> dict:
        """
        Get queue configuration based on queue type
        Note: For existing named queues, these are suggested settings based on queue_type configuration
        """
        if self.queue_type == 'quorum':
            return {
                'queue_type': 'quorum',
                'delivery_limit': 5,
                'prefetch_count': 1,
                'quorum_size': 3,
                'confirm_delivery': True,
                'delivery_mode': 2,
                'priority': 0,
                'retry_attempts': 3,
                'retry_delay': 1.0
            }
        elif self.queue_type == 'stream':
            return {
                'queue_type': 'stream',
                'prefetch_count': 100,
                'consumer_offset': 'next',
                'confirm_delivery': False,
                'delivery_mode': 2,
                'priority': 0,
                'retry_attempts': 1,
                'retry_delay': 0.5
            }
        else:  # classic or unknown - safe defaults for existing queues
            return {
                'queue_type': 'classic',
                'prefetch_count': 10,
                'confirm_delivery': False,
                'delivery_mode': 2,
                'priority': 0,
                'retry_attempts': 2,
                'retry_delay': 1.0
            }

    async def get_queue_name(self, namespace: str) -> str:
        subsystem, module = namespace.split('.')[:2]

        # Use cached config or load if not available
        if self.mq_config is None:
            self._load_config()

        entries = self.mq_config.get_value(subsystem)
        for entry in entries:
            if module == entry.split(':')[1]:
                return 'ovq.' + subsystem + '-' + entry.split(':')[0]
        raise RuntimeError(f"Queue name not found for namespace {namespace}")

    # Legacy methods - kept for compatibility but not used for existing named queues
    async def _declare_queue_with_fallback(self, queue_name: str) -> aio_pika.abc.AbstractQueue:
        """
        Legacy method - use _declare_existing_queue for named queues instead
        """
        return await self._declare_existing_queue(queue_name)

    async def _declare_compatible_quorum_queue(self, queue_name: str) -> aio_pika.abc.AbstractQueue:
        """
        Legacy method - only used if creating new queues (not for existing named queues)
        """
        # Try different argument combinations to match existing queue
        argument_combinations = [
            # Most comprehensive - match typical production settings
            {
                "x-queue-type": "quorum",
                "x-quorum-initial-group-size": 3,
                "x-delivery-limit": 5,
                "x-max-in-memory-length": 2000,
                "x-max-length": 1000000,
                "x-overflow": "reject-publish"
            },
            # Common basic quorum settings
            {
                "x-queue-type": "quorum",
                "x-max-in-memory-length": 2000,
                "x-delivery-limit": 5
            },
            # Minimal quorum settings
            {
                "x-queue-type": "quorum",
                "x-max-in-memory-length": 2000
            },
            # Just queue type
            {
                "x-queue-type": "quorum"
            }
        ]

        last_error = None
        for i, args in enumerate(argument_combinations):
            try:
                self.logger.debug(f"Adapter: Trying quorum queue declaration attempt {i+1}")
                return await self.channel.declare_queue(
                    queue_name,
                    durable=True,
                    arguments=args
                )
            except Exception as e:
                last_error = e
                self.logger.debug(f"Adapter: Attempt {i+1} failed - {e}")
                continue

        # If all attempts failed, raise the last error
        if last_error:
            raise last_error
        else:
            raise RuntimeError("All queue declaration attempts failed")

    async def _declare_classic_queue(self, queue_name: str) -> aio_pika.abc.AbstractQueue:
        """
        Legacy method - only used if creating new queues (not for existing named queues)
        """
        return await self.channel.declare_queue(
            queue_name,
            durable=True
        )

    async def _declare_stream_queue(self, queue_name: str) -> aio_pika.abc.AbstractQueue:
        """
        Legacy method - only used if creating new queues (not for existing named queues)
        """
        arguments = {
            "x-queue-type": "stream",
            "x-max-length-bytes": 20000000000,  # 20GB default
            "x-stream-max-segment-size-bytes": 500000000  # 500MB default
        }

        return await self.channel.declare_queue(
            queue_name,
            durable=True,
            arguments=arguments
        )