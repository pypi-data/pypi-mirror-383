import asyncio
import json
import socket
import os
import time
from enum import Enum
from typing import Any, Optional, Dict
from .adapter import Adapter
from .status import JobStatus
from .job_context import JobContext


class PublisherChannel:
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

    async def start(self):
        if self.devel:
            self.running = True
            return

        if not await self.adapter.open():
            self.logger.error("PublisherChannel: Failed to open adapter")
            return

        self.running = True
        self._task = asyncio.create_task(self._run_loop())
        self.logger.info("PublisherChannel: Started")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.adapter.close()
        self.logger.info("PublisherChannel: Stopped")

    async def _run_loop(self):
        while self.running:
            try:
                item = await self.queue.get()
                await self.adapter.publish(item["exchange"], item["routing_key"], item["body"])
            except Exception as e:
                self.logger.error("PublisherChannel: Publish failed - %s", e)
            await asyncio.sleep(0.001)

    async def publish_heartbeat(self, worker_name: str):
        data = {
            'metric-type': 4,
            'metric-status': 0,
            'metric-name': self.alias,
            'namespace': self.namespace,
            'process': worker_name,
            'psn': 0,
            'hostname': self.hostname,
            'timestamp': time.time()
        }
        rk = f'sys.{self.namespace}.heartbeat.agent'
        await self._enqueue(Adapter.EXCHANGE_METRIC, rk, json.dumps(data))

    async def publish_job(self, ctx: JobContext):
        if not ctx.msglist:
            ctx.msgbox = {"type": "ascii", "size": 0, "data": ""}
            await self._nextjob(ctx, self._build_data(ctx))
            return

        for msg in ctx.msglist.copy():
            ctx.msgbox = {"type": "ascii", "size": len(msg), "data": msg}
            await self._nextjob(ctx, self._build_data(ctx))

    def _build_data(self, ctx: JobContext) -> Dict[str, Any]:
        return {
            'regkey': ctx.regkey,
            'topic': ctx.topic,
            'action-id': ctx.action_id,
            'action-ns': ctx.action_ns,
            'action-app': ctx.action_app,
            'action-params': ctx.action_params,
            'job-id': ctx.job_id,
            'job-hostname': ctx.job_hostname,
            'job-seq': ctx.job_seq,
            'timestamp': ctx.timestamp,
            'filenames': ctx.filenames,
            'msgbox': ctx.msgbox,
        }

    async def _nextjob(self, ctx: JobContext, data: Dict[str, Any]):
        key = f'job.des.msm.early.{ctx.topic}' if ctx.timestamp == 0 else f'job.des.msm.now.{ctx.topic}'
        await self._enqueue(Adapter.EXCHANGE_ACTION, key, json.dumps(data))

    async def publish_notify(self, ctx: JobContext, text: str = '', status: Enum = JobStatus.RUNNING, elapsed: int = 0):
        job_status_value = status.value if isinstance(status, Enum) else int(status)
        data = {
            'job-id': ctx.job_id,
            'job-status': job_status_value,
            'job-elapsed': elapsed,
            'reg-subject': ctx.regkey.split('@')[0],
            'reg-version': ctx.regkey.split('@')[1],
            'reg-topic': ctx.topic,
            'action-id': ctx.action_id,
            'action-app': ctx.action_app,
            'action-ns': ctx.action_ns,
            'hostname': self.hostname,
            'timestamp': int(time.time()),
            'filesize': 0,
            'filenames': ctx.filenames,
            'err-code': 0,
            'err-mesg': text
        }

        for f in ctx.filenames:
            try:
                data['filesize'] += os.stat(f).st_size
            except Exception as e:
                self.logger.debug("PublisherChannel: Failed to stat file %s - %s", f, e)

        await self._enqueue(Adapter.EXCHANGE_LOGS, f'log.{ctx.action_ns}', json.dumps(data))

    async def _enqueue(self, exchange: str, routing_key: str, body: str):
        await self.queue.put({
            "exchange": exchange,
            "routing_key": routing_key,
            "body": body
        })