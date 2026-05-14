from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect

from app.api.auth import get_current_user, get_op_user
from app.models.creator_intelligence import (
    CIContentItem,
    CICreatorProfile,
    CIJobRecord,
    CIMemoryRecord,
    CIModelRegistryEntry,
)
from app.models.user import User
from app.services.creator_intelligence.memory_service import create_memory_from_candidate
from app.services.creator_intelligence.model_manager import scan_gguf_models, upsert_model_registry
from app.services.creator_intelligence.queue_manager import queue_manager
from app.services.creator_intelligence.schemas import (
    JobCreateRequest,
    JobEnvelope,
    JobProgressEvent,
    JobResult,
    MemoryCandidate,
    ModelScanRequest,
    WorkerHeartbeat,
    WorkerRegistration,
    model_to_dict,
)
from app.services.creator_intelligence.vector_store import vector_store
from app.services.creator_intelligence.worker_registry import worker_registry

router = APIRouter()


@router.get("/overview")
async def overview(current_user: User = Depends(get_current_user)):
    stats = await queue_manager.queue_stats()
    qdrant_health = await vector_store.health()
    return {
        "creators": CICreatorProfile.objects().count(),
        "content_items": CIContentItem.objects().count(),
        "memory_records": CIMemoryRecord.objects().count(),
        "workers": {
            "online": len([w for w in worker_registry.list_workers() if w["status"] == "online"]),
            "total": len(worker_registry.list_workers()),
        },
        "queues": stats,
        "qdrant": qdrant_health,
    }


@router.get("/workers")
async def list_workers(current_user: User = Depends(get_current_user)):
    return {"workers": worker_registry.list_workers()}


@router.post("/workers/register-token")
async def create_worker_token(current_user: User = Depends(get_op_user)):
    return await worker_registry.create_registration_token()


@router.get("/queues")
async def queues(current_user: User = Depends(get_current_user)):
    return await queue_manager.queue_stats()


@router.post("/jobs")
async def create_job(request: JobCreateRequest, current_user: User = Depends(get_current_user)):
    requirements = request.capability_requirements
    payload = dict(request.payload or {})
    if request.target_worker_id:
        payload["target_worker_id"] = request.target_worker_id

    envelope = JobEnvelope(
        job_type=request.job_type,
        priority=request.priority,
        requested_by=current_user.username,
        capability_requirements=requirements,
        payload=payload,
        max_attempts=request.max_attempts,
        timeout_seconds=request.timeout_seconds,
    )
    record = await queue_manager.enqueue(envelope, requested_by=current_user)
    return {"job": record.to_dict()}


@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    query = {}
    if status:
        query["status"] = status
    if job_type:
        query["job_type"] = job_type
    jobs = CIJobRecord.objects(**query).order_by("-created_at").limit(limit)
    return {"jobs": [job.to_dict() for job in jobs]}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, current_user: User = Depends(get_current_user)):
    job = CIJobRecord.objects(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job": job.to_dict()}


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, current_user: User = Depends(get_current_user)):
    cancelled = await queue_manager.cancel(job_id, reason=f"cancelled_by:{current_user.username}")
    if not cancelled:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "cancel_requested", "job_id": job_id}


@router.get("/models")
async def list_models(current_user: User = Depends(get_current_user)):
    return {"models": [entry.to_dict() for entry in CIModelRegistryEntry.objects().order_by("-detected_at")]}


@router.post("/models/scan")
async def scan_models(request: ModelScanRequest, current_user: User = Depends(get_current_user)):
    if request.worker_id:
        job_request = JobCreateRequest(
            job_type="model_scan",
            priority="high",
            payload={"roots": request.roots, "validate_hashes": request.validate_hashes},
            target_worker_id=request.worker_id,
        )
        return await create_job(job_request, current_user)

    result = scan_gguf_models(roots=request.roots or None, validate_hashes=request.validate_hashes)
    saved = upsert_model_registry("control-plane", result["models"])
    return {"scan": result, "saved": saved}


@router.get("/creators")
async def list_creators(current_user: User = Depends(get_current_user)):
    creators = CICreatorProfile.objects().order_by("-updated_at").limit(200)
    return {"creators": [creator.to_dict() for creator in creators]}


@router.get("/creators/{creator_id}/content")
async def creator_content(creator_id: str, current_user: User = Depends(get_current_user)):
    content = CIContentItem.objects(creator=creator_id).order_by("-created_at").limit(200)
    return {"content": [item.to_dict() for item in content]}


@router.get("/memory")
async def list_memory(
    namespace: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=300),
    current_user: User = Depends(get_current_user),
):
    query = {}
    if namespace:
        query["namespace"] = namespace
    if memory_type:
        query["memory_type"] = memory_type
    records = CIMemoryRecord.objects(**query).order_by("-last_seen_at").limit(limit)
    return {"memory": [record.to_dict() for record in records]}


@router.post("/memory/candidates")
async def memory_candidate(candidate: MemoryCandidate, current_user: User = Depends(get_current_user)):
    return {"memory": create_memory_from_candidate(candidate)}


@router.get("/vectors/health")
async def vector_health(current_user: User = Depends(get_current_user)):
    return await vector_store.health()


@router.websocket("/workers/ws")
async def worker_socket(websocket: WebSocket):
    await websocket.accept()
    worker_id = None
    capabilities = {}
    try:
        while True:
            message = await websocket.receive_json()
            message_type = message.get("message_type") or message.get("type")

            if message_type == "register":
                payload = message.get("payload", message)
                registration = WorkerRegistration(**payload)
                worker = await worker_registry.register(registration)
                worker_id = worker.worker_id
                capabilities = worker.capabilities or {}
                await websocket.send_json({"message_type": "registered", "worker": worker.to_dict()})

            elif message_type == "heartbeat":
                heartbeat = WorkerHeartbeat(**message.get("payload", message))
                worker = await worker_registry.heartbeat(heartbeat)
                if worker:
                    capabilities = worker.capabilities or capabilities
                await websocket.send_json({"message_type": "heartbeat_ack", "created_at": datetime.utcnow().isoformat()})

            elif message_type == "claim_request":
                if not worker_id:
                    await websocket.send_json({"message_type": "error", "error": "worker must register first"})
                    continue
                job = await queue_manager.claim_next_job(worker_id, capabilities)
                if job:
                    await websocket.send_json({"message_type": "job_available", "job": model_to_dict(job)})
                else:
                    await websocket.send_json({"message_type": "no_job"})

            elif message_type == "progress":
                event = JobProgressEvent(**message.get("payload", message))
                await queue_manager.record_progress(event)
                await websocket.send_json({"message_type": "progress_ack", "job_id": event.job_id})

            elif message_type == "result":
                result = JobResult(**message.get("payload", message))
                await queue_manager.complete(result)
                if result.output.get("model_scan"):
                    scan = result.output["model_scan"]
                    upsert_model_registry(result.worker_id, scan.get("models", []))
                await websocket.send_json({"message_type": "result_ack", "job_id": result.job_id})

            else:
                await websocket.send_json({"message_type": "error", "error": f"unknown message_type: {message_type}"})

    except WebSocketDisconnect:
        return
    except PermissionError as exc:
        await websocket.send_json({"message_type": "error", "error": str(exc)})
        await websocket.close(code=4403)
    except Exception as exc:
        await websocket.send_json({"message_type": "error", "error": str(exc)})
        await websocket.close(code=1011)
