import json
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, Optional

from mongoengine import Q

from app.core.database import redis_client
from app.models.creator_intelligence import CIJobRecord
from app.models.user import User
from app.services.creator_intelligence.schemas import (
    JobEnvelope,
    JobPriority,
    JobProgressEvent,
    JobResult,
    JobStatus,
    model_to_dict,
)


STREAMS = {
    JobPriority.HIGH.value: "ci:jobs:high",
    JobPriority.NORMAL.value: "ci:jobs:normal",
    JobPriority.LOW.value: "ci:jobs:low",
}
EVENT_STREAM = "ci:events"
DEAD_STREAM = "ci:dead"
CANCEL_KEY_PREFIX = "ci:cancel:"


class CreatorIntelligenceQueue:
    def __init__(self, redis=redis_client):
        self.redis = redis

    async def enqueue(self, envelope: JobEnvelope, requested_by: Optional[User] = None) -> CIJobRecord:
        stream_name = STREAMS[envelope.priority.value]
        payload = json.dumps(model_to_dict(envelope), default=str)
        stream_id = await self.redis.xadd(stream_name, {"job": payload, "job_id": envelope.job_id})

        record = CIJobRecord(
            job_id=envelope.job_id,
            stream_id=stream_id.decode() if isinstance(stream_id, bytes) else str(stream_id),
            job_type=envelope.job_type.value,
            priority=envelope.priority.value,
            status=JobStatus.QUEUED.value,
            requested_by=requested_by,
            payload=envelope.payload,
            capability_requirements=model_to_dict(envelope.capability_requirements),
            trace_id=envelope.trace_id,
            attempt=envelope.attempt,
            max_attempts=envelope.max_attempts,
            timeout_seconds=envelope.timeout_seconds,
            created_at=envelope.created_at,
            scheduled_at=envelope.scheduled_at,
        )
        record.save()
        await self.emit_event("job_enqueued", envelope.job_id, {"priority": envelope.priority.value, "job_type": envelope.job_type.value})
        return record

    async def emit_event(self, event_type: str, job_id: Optional[str], payload: Dict[str, Any]) -> str:
        event = {
            "event_type": event_type,
            "job_id": job_id or "",
            "payload": json.dumps(payload, default=str),
            "created_at": datetime.utcnow().isoformat(),
        }
        event_id = await self.redis.xadd(EVENT_STREAM, event)
        return event_id.decode() if isinstance(event_id, bytes) else str(event_id)

    async def queue_stats(self) -> Dict[str, Any]:
        stream_lengths = {}
        for priority, stream_name in STREAMS.items():
            try:
                stream_lengths[priority] = await self.redis.xlen(stream_name)
            except Exception:
                stream_lengths[priority] = 0

        return {
            "streams": stream_lengths,
            "jobs": {
                "queued": CIJobRecord.objects(status=JobStatus.QUEUED.value).count(),
                "running": CIJobRecord.objects(status=JobStatus.RUNNING.value).count(),
                "completed": CIJobRecord.objects(status=JobStatus.COMPLETED.value).count(),
                "failed": CIJobRecord.objects(status=JobStatus.FAILED.value).count(),
                "cancelled": CIJobRecord.objects(status=JobStatus.CANCELLED.value).count(),
                "dead": CIJobRecord.objects(status=JobStatus.DEAD.value).count(),
            },
            "events": await self.redis.xlen(EVENT_STREAM),
            "dead_stream": await self.redis.xlen(DEAD_STREAM),
        }

    async def cancel(self, job_id: str, reason: str = "user_requested") -> bool:
        record = CIJobRecord.objects(job_id=job_id).first()
        if not record:
            return False

        await self.redis.set(f"{CANCEL_KEY_PREFIX}{job_id}", reason, ex=86400)
        if record.status == JobStatus.QUEUED.value:
            record.status = JobStatus.CANCELLED.value
            record.error = reason
            record.completed_at = datetime.utcnow()
            record.save()
        await self.emit_event("job_cancel_requested", job_id, {"reason": reason})
        return True

    async def is_cancelled(self, job_id: str) -> bool:
        return bool(await self.redis.get(f"{CANCEL_KEY_PREFIX}{job_id}"))

    async def claim_next_job(self, worker_id: str, capabilities: Dict[str, Any], priorities: Iterable[str] = ("high", "normal", "low")) -> Optional[JobEnvelope]:
        now = datetime.utcnow()
        for priority in priorities:
            query = Q(status=JobStatus.QUEUED.value) & Q(priority=priority) & Q(scheduled_at__lte=now)
            for record in CIJobRecord.objects(query).order_by("created_at").limit(25):
                target_worker_id = (record.payload or {}).get("target_worker_id")
                if target_worker_id and target_worker_id != worker_id:
                    continue
                if not self._capabilities_match(record.capability_requirements or {}, capabilities):
                    continue
                if await self.is_cancelled(record.job_id):
                    record.status = JobStatus.CANCELLED.value
                    record.completed_at = datetime.utcnow()
                    record.save()
                    continue

                record.status = JobStatus.RUNNING.value
                record.assigned_worker_id = worker_id
                record.attempt += 1
                record.started_at = datetime.utcnow()
                record.save()
                await self.emit_event("job_claimed", record.job_id, {"worker_id": worker_id})
                return self._record_to_envelope(record)
        return None

    async def record_progress(self, event: JobProgressEvent):
        record = CIJobRecord.objects(job_id=event.job_id).first()
        if not record:
            return
        progress = record.progress or []
        progress.append(model_to_dict(event))
        record.progress = progress[-200:]
        record.save()
        await self.emit_event("job_progress", event.job_id, model_to_dict(event))

    async def complete(self, result: JobResult):
        record = CIJobRecord.objects(job_id=result.job_id).first()
        if not record:
            return

        record.result = model_to_dict(result)
        record.completed_at = result.completed_at
        record.error = result.error
        if result.status.value == JobStatus.COMPLETED.value:
            record.status = JobStatus.COMPLETED.value
        elif result.status.value == JobStatus.CANCELLED.value:
            record.status = JobStatus.CANCELLED.value
        elif result.status.value == JobStatus.PAUSED.value:
            record.status = JobStatus.PAUSED.value
        else:
            if record.attempt >= record.max_attempts:
                record.status = JobStatus.DEAD.value
                await self.redis.xadd(DEAD_STREAM, {"job_id": record.job_id, "result": json.dumps(model_to_dict(result), default=str)})
            else:
                record.status = JobStatus.QUEUED.value
                record.assigned_worker_id = None
                record.scheduled_at = datetime.utcnow() + timedelta(seconds=min(60 * record.attempt, 300))
                await self.emit_event("job_requeued", result.job_id, {"attempt": record.attempt, "max_attempts": record.max_attempts})
        record.save()
        await self.emit_event("job_completed", result.job_id, model_to_dict(result))

    def _record_to_envelope(self, record: CIJobRecord) -> JobEnvelope:
        return JobEnvelope(
            job_id=record.job_id,
            job_type=record.job_type,
            priority=record.priority,
            requested_by=record.requested_by.username if record.requested_by else None,
            capability_requirements=record.capability_requirements or {},
            payload=record.payload or {},
            trace_id=record.trace_id,
            created_at=record.created_at,
            scheduled_at=record.scheduled_at,
            max_attempts=record.max_attempts,
            attempt=record.attempt,
            timeout_seconds=record.timeout_seconds,
        )

    def _capabilities_match(self, requirements: Dict[str, Any], capabilities: Dict[str, Any]) -> bool:
        if not requirements:
            return True

        boolean_keys = ["gpu", "multimodal", "ocr", "embeddings", "playwright", "browser_cognition", "gguf_runtime"]
        for key in boolean_keys:
            required = requirements.get(key)
            if required is True and capabilities.get(key) is not True:
                return False

        min_vram = requirements.get("min_vram_gb")
        if min_vram is not None and float(capabilities.get("vram_gb") or 0) < float(min_vram):
            return False

        platform = requirements.get("platform")
        if platform:
            supported = capabilities.get("supported_platforms") or []
            if platform not in supported:
                return False

        return True


queue_manager = CreatorIntelligenceQueue()
