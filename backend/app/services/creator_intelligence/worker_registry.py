import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.core.config import settings
from app.core.database import redis_client
from app.models.creator_intelligence import CIWorkerRecord
from app.services.creator_intelligence.queue_manager import queue_manager
from app.services.creator_intelligence.schemas import WorkerHeartbeat, WorkerRegistration, model_to_dict


TOKEN_PREFIX = "ci:worker-token:"


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class WorkerRegistry:
    def __init__(self, redis=redis_client):
        self.redis = redis

    async def create_registration_token(self, scope: str = "worker", expires_seconds: int = 86400) -> Dict[str, str]:
        token = secrets.token_urlsafe(32)
        digest = token_digest(token)
        await self.redis.hset(
            f"{TOKEN_PREFIX}{digest}",
            mapping={
                "scope": scope,
                "created_at": datetime.utcnow().isoformat(),
                "expires_seconds": str(expires_seconds),
            },
        )
        await self.redis.expire(f"{TOKEN_PREFIX}{digest}", expires_seconds)
        return {"token": token, "scope": scope, "expires_seconds": expires_seconds}

    async def verify_registration_token(self, token: str) -> bool:
        if settings.CI_WORKER_REGISTRATION_TOKEN and secrets.compare_digest(token, settings.CI_WORKER_REGISTRATION_TOKEN):
            return True

        digest = token_digest(token)
        return bool(await self.redis.exists(f"{TOKEN_PREFIX}{digest}"))

    async def register(self, registration: WorkerRegistration) -> CIWorkerRecord:
        allowed = await self.verify_registration_token(registration.auth_token)
        if not allowed:
            raise PermissionError("invalid worker registration token")

        digest = token_digest(registration.auth_token)
        capabilities = registration.capabilities.as_match_dict()
        worker = CIWorkerRecord.objects(worker_id=registration.worker_id).first()
        if not worker:
            worker = CIWorkerRecord(worker_id=registration.worker_id)

        worker.worker_name = registration.worker_name
        worker.machine_role = registration.machine_role.value
        worker.host_fingerprint = registration.host_fingerprint
        worker.capabilities = capabilities
        worker.version = registration.version
        worker.token_digest = digest
        worker.status = "online"
        worker.last_heartbeat = datetime.utcnow()
        worker.save()
        await queue_manager.emit_event("worker_registered", None, {"worker_id": worker.worker_id, "machine_role": worker.machine_role})
        return worker

    async def heartbeat(self, heartbeat: WorkerHeartbeat) -> Optional[CIWorkerRecord]:
        worker = CIWorkerRecord.objects(worker_id=heartbeat.worker_id).first()
        if not worker:
            return None

        worker.status = "online"
        worker.last_heartbeat = heartbeat.created_at
        worker.load = heartbeat.load
        worker.current_jobs = heartbeat.current_jobs
        worker.model_runtime = model_to_dict(heartbeat.model_runtime) if heartbeat.model_runtime else {}
        worker.save()
        return worker

    def list_workers(self) -> List[Dict]:
        self.refresh_stale_statuses()
        return [worker.to_dict() for worker in CIWorkerRecord.objects().order_by("-updated_at")]

    def refresh_stale_statuses(self):
        now = datetime.utcnow()
        stale_before = now - timedelta(seconds=settings.CI_WORKER_HEARTBEAT_STALE_SECONDS)
        offline_before = now - timedelta(seconds=settings.CI_WORKER_HEARTBEAT_OFFLINE_SECONDS)

        for worker in CIWorkerRecord.objects(status__in=["online", "registered"]):
            if not worker.last_heartbeat:
                continue
            if worker.last_heartbeat < offline_before:
                worker.status = "offline"
                worker.save()
            elif worker.last_heartbeat < stale_before:
                worker.status = "stale"
                worker.save()


worker_registry = WorkerRegistry()
