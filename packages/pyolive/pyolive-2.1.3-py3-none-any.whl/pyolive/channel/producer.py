import asyncio
import json
import socket
import os
import time
import base64
import aio_pika
from enum import Enum
from typing import Any, Optional, Dict
from pyolive.status import JobStatus
from pyolive.job_context import JobContext
from .adapter import Adapter


class ProducerChannel:
    def __init__(self, logger: Any, namespace: str, alias: str, devel: bool = False):
        self.logger = logger
        self.namespace = namespace
        self.alias = alias
        self.hostname = socket.gethostname()
        self.adapter = Adapter(logger)
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.devel = devel
        self.queue_config: Optional[dict] = None

    async def start(self):
        if self.devel:
            self.running = True
            return

        if not await self.adapter.open():
            self.logger.error("ProducerChannel: Failed to open adapter")
            return

        # Get queue configuration from adapter
        self.queue_config = self.adapter.get_queue_config()

        # Enable publisher confirms for quorum queues only
        if self.queue_config['confirm_delivery'] and self.queue_config['queue_type'] == 'quorum':
            try:
                # Try different methods depending on aio-pika version
                if hasattr(self.adapter.channel, 'confirm_delivery'):
                    await self.adapter.channel.confirm_delivery()
                elif hasattr(self.adapter.channel, 'set_publisher_confirms'):
                    await self.adapter.channel.set_publisher_confirms(True)
                elif hasattr(self.adapter.channel, 'confirm_select'):
                    await self.adapter.channel.confirm_select()
                else:
                    # Fallback: try to access publisher_confirms property
                    self.adapter.channel.publisher_confirms = True

                self.logger.info("ProducerChannel: Publisher confirms enabled")
            except Exception as e:
                self.logger.warning(f"ProducerChannel: Failed to enable publisher confirms - {e}")
                # Continue without publisher confirms

        self.running = True
        self._task = asyncio.create_task(self._run_loop())
        self.logger.info(f"ProducerChannel: Started with {self.queue_config['queue_type']} queue support")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.adapter.close()
        self.logger.info("ProducerChannel: Stopped")

    async def _run_loop(self):
        while self.running:
            try:
                item = await self.queue.get()
                await self._publish_with_retry(
                    item["exchange"],
                    item["routing_key"],
                    item["body"],
                    item.get("priority", self.queue_config['priority'])
                )
            except Exception as e:
                self.logger.error("ProducerChannel: Publish failed - %s", e)
            await asyncio.sleep(0.001)

    async def _publish_with_retry(self, exchange: str, routing_key: str, message: str, priority: int = 0):
        """
        Publish message with retry logic based on queue type
        """
        retry_count = 0
        max_retries = self.queue_config['retry_attempts']

        while retry_count <= max_retries:
            try:
                await self._publish_enhanced(exchange, routing_key, message, priority)
                return  # Success

            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    self.logger.error(
                        f"ProducerChannel: Failed to publish after {max_retries} attempts - {e}"
                    )
                    raise

                self.logger.warning(
                    f"ProducerChannel: Publish attempt {retry_count} failed, retrying - {e}"
                )
                await asyncio.sleep(self.queue_config['retry_delay'] * retry_count)

    async def _publish_enhanced(self, exchange: str, routing_key: str, message: str, priority: int = 0):
        """
        Enhanced publish method with queue type specific features
        """
        try:
            ex = await self.adapter.channel.declare_exchange(exchange, "topic", durable=True)

            # Create message with queue type optimized properties
            message_props = {
                'body': message.encode(),
                'delivery_mode': self.queue_config['delivery_mode'],
                'timestamp': time.time()
            }

            # Add priority only for classic and quorum queues (not streams)
            if self.queue_config['queue_type'] != 'stream':
                message_props['priority'] = priority

            # Add message ID for quorum queues
            if self.queue_config['queue_type'] == 'quorum':
                message_props['message_id'] = f"{self.hostname}-{int(time.time() * 1000000)}"

            aio_message = aio_pika.Message(**message_props)

            # Publish with confirmation if enabled for quorum queues
            if self.queue_config['confirm_delivery'] and self.queue_config['queue_type'] == 'quorum':
                confirmation = await ex.publish(aio_message, routing_key=routing_key)
                if hasattr(confirmation, 'delivery_tag'):
                    self.logger.debug(
                        f"ProducerChannel: Confirmed delivery to {exchange}:{routing_key} "
                        f"(tag: {confirmation.delivery_tag})"
                    )
            else:
                await ex.publish(aio_message, routing_key=routing_key)

            self.logger.debug(f"ProducerChannel: Published to {exchange}:{routing_key}")

        except Exception as e:
            self.logger.warning(f"ProducerChannel: Enhanced publish failed to {exchange}:{routing_key} - {e}")
            raise

    async def publish_heartbeat(self, agent_name: str):
        data = {
            'metric_type': 4,
            'metric_status': 0,
            'metric_name': self.alias,
            'namespace': self.namespace,
            'process': agent_name,
            'psn': 0,
            'hostname': self.hostname,
            'timestamp': time.time()
        }
        rk = f'sys.{self.namespace}.heartbeat.agent'
        await self._enqueue(Adapter.EXCHANGE_METRIC, rk, json.dumps(data), priority=1)  # Higher priority

    async def publish_job(self, ctx: JobContext, priority: int = 0):
        if not ctx.msglist:
            ctx.msgbox = {"type": "ascii", "size": 0, "data": ""}
            await self._nextjob(ctx, self._build_data(ctx), priority)
            return

        for msg in ctx.msglist.copy():
            if isinstance(msg, bytes):
                # Binary message -> base64 encoding
                encoded = base64.b64encode(msg).decode('ascii')
                ctx.msgbox = {
                    "type": "binary",
                    "size": len(msg),
                    "data": encoded
                }
            elif isinstance(msg, str):
                msg_bytes = msg.encode('utf-8')
                ctx.msgbox = {
                    "type": "ascii",
                    "size": len(msg_bytes),
                    "data": msg
                }
            else:
                # Fallback: force convert to string
                msg_str = str(msg)
                msg_bytes = msg_str.encode('utf-8')
                ctx.msgbox = {
                    "type": "ascii",
                    "size": len(msg_bytes),
                    "data": msg_str
                }

            await self._nextjob(ctx, self._build_data(ctx), priority)

    def _build_data(self, ctx: JobContext) -> Dict[str, Any]:
        return {
            'regkey': ctx.regkey,
            'topic': ctx.topic,
            'action_id': ctx.action_id,
            'action_ns': ctx.action_ns,
            'action_app': ctx.action_app,
            'action_params': ctx.action_params,
            'job_id': ctx.job_id,
            'job_hostname': ctx.job_hostname,
            'job_seq': ctx.job_seq,
            'timestamp': ctx.timestamp,
            'filenames': ctx.filenames,
            'msgbox': ctx.msgbox,
        }

    async def _nextjob(self, ctx: JobContext, data: Dict[str, Any], priority: int = 0):
        key = f'job.des.msm.early.{ctx.topic}' if ctx.timestamp == 0 else f'job.des.msm.now.{ctx.topic}'
        await self._enqueue(Adapter.EXCHANGE_ACTION, key, json.dumps(data), priority)

    async def publish_notify(self, ctx: JobContext, text: str = '', status: Enum = JobStatus.RUNNING, elapsed: int = 0):
        job_status_value = status.value if isinstance(status, Enum) else int(status)
        data = {
            'job_id': ctx.job_id,
            'job_status': job_status_value,
            'job_elapsed': elapsed,
            'reg_subject': ctx.regkey.split('@')[0],
            'reg_version': ctx.regkey.split('@')[1],
            'reg_topic': ctx.topic,
            'action_id': ctx.action_id,
            'action_app': ctx.action_app,
            'action_ns': ctx.action_ns,
            'hostname': self.hostname,
            'timestamp': int(time.time()),
            'filesize': 0,
            'filenames': ctx.filenames,
            'err_code': 0,
            'err_mesg': text
        }

        for f in ctx.filenames:
            try:
                data['filesize'] += os.stat(f).st_size
            except Exception as e:
                self.logger.debug("ProducerChannel: Failed to stat file %s - %s", f, e)

        # Logs have lower priority than jobs
        await self._enqueue(Adapter.EXCHANGE_LOGS, f'log.{ctx.action_ns}', json.dumps(data), priority=0)

    async def _enqueue(self, exchange: str, routing_key: str, body: str, priority: int = 0):
        await self.queue.put({
            "exchange": exchange,
            "routing_key": routing_key,
            "body": body,
            "priority": priority
        })

    async def get_queue_size(self) -> int:
        """
        Get current internal queue size
        """
        return self.queue.qsize()

    async def flush_queue(self, timeout: float = 30.0):
        """
        Wait for internal queue to be processed
        """
        start_time = time.time()
        while not self.queue.empty() and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.1)

        if not self.queue.empty():
            self.logger.warning(f"ProducerChannel: Queue flush timeout, {self.queue.qsize()} messages remaining")

    def _load_quorum_config(self) -> dict:
        """
        Deprecated: Configuration is now loaded from adapter
        """
        return {}