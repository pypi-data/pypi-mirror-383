import asyncio
import aio_pika
from aio_pika import ExchangeType
from aio_pika.abc import AbstractIncomingMessage
from typing import Optional, Callable, Awaitable
from .config import Config


class Adapter:
    EXCHANGE_ACTION = "action"
    EXCHANGE_CONTROL = "control"
    EXCHANGE_METRIC = "metric"
    EXCHANGE_LOGS = "logs"

    def __init__(self, logger):
        self.logger = logger
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.abc.AbstractChannel] = None

    async def open(self) -> bool:
        try:
            amqp_url = await self._build_amqp_url()
            self.connection = await aio_pika.connect_robust(amqp_url)
            self.channel = await self.connection.channel()
            self.logger.info("Adapter: Connected to AMQP")
            return True
        except Exception as e:
            self.logger.error(f"Adapter: Connection failed: {e}")
            return False

    async def _build_amqp_url(self) -> str:
        config = Config('athena-env.yaml')
        hosts = config.get_value('broker/hosts')
        port = config.get_value('broker/amqp-port')
        username = config.get_value('broker/username')
        password = config.get_value('broker/password')

        if not hosts:
            raise RuntimeError("AMQP hosts not found in configuration")

        host = hosts[0]
        return f"amqp://{username}:{password}@{host}:{port}/"

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
            queue = await self.channel.declare_queue(queue_name, durable=True)
            await queue.consume(callback)
            self.logger.info(f"Adapter: Started consuming on {queue_name}")
        except Exception as e:
            self.logger.error(f"Adapter: Consume failed - {e}")

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

    async def get_queue_name(self, namespace: str) -> str:
        subsystem, module = namespace.split('.')[:2]
        config = Config('athena-mq.yaml')
        entries = config.get_value(subsystem)
        for entry in entries:
            if module == entry.split(':')[1]:
                return 'ovq.' + subsystem + '-' + entry.split(':')[0]
        raise RuntimeError(f"Queue name not found for namespace {namespace}")