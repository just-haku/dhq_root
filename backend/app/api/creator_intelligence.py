from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.api.auth import get_current_user, get_op_user
from app.models.creator_intelligence import (
    CIContentItem,
    CICreatorProfile,
    CICreatorCognitiveStateRecord,
    CIHumanFeedbackEvent,
    CIJobRecord,
    CIMemoryRecord,
    CIModelInferenceRecord,
    CIModelRegistryEntry,
    CIProvenanceGraphRecord,
    CISandboxWorkspaceRecord,
    CISemanticConsensusRecord,
    CIStrategyLineageRecord,
    CIWorkerPressureRecord,
)
from app.models.user import User
from app.services.creator_intelligence.memory_service import create_memory_from_candidate
from app.services.creator_intelligence.model_manager import scan_gguf_models, upsert_model_registry
from app.services.creator_intelligence.ontology_service import list_registries, load_registries, validate_label_ids
from app.services.creator_intelligence.queue_manager import queue_manager
from app.services.creator_intelligence.schemas import (
    AgentType,
    AnalysisProvenanceGraph,
    ConfidenceCalibrationPolicy,
    ConfidenceEvidence,
    CreatorCognitiveState,
    HumanFeedbackEvent,
    JobCreateRequest,
    JobEnvelope,
    JobProgressEvent,
    JobResult,
    MemoryCandidate,
    ModelInferenceRecord,
    ModelScanRequest,
    NonPersistentReasoning,
    ReasoningDepthPolicy,
    SandboxWorkspace,
    SourceReference,
    StrategyLineage,
    WorkerHeartbeat,
    WorkerPressureSnapshot,
    WorkerRegistration,
    model_to_dict,
)
from app.services.creator_intelligence.stability_service import (
    aggregate_confidence,
    check_agent_permission,
    check_synthesis_boundary,
    evaluate_worker_pressure,
    feedback_reinforcement_hint,
    resolve_semantic_consensus,
    restricted_context,
    temporal_weight,
)
from app.services.creator_intelligence.vector_store import vector_store
from app.services.creator_intelligence.worker_registry import worker_registry

router = APIRouter()


class OntologyValidateRequest(BaseModel):
    label_ids: List[str] = Field(default_factory=list)


class ConfidenceAggregateRequest(BaseModel):
    evidence: List[ConfidenceEvidence] = Field(default_factory=list)
    policy: Optional[ConfidenceCalibrationPolicy] = None


class ConsensusResolveRequest(BaseModel):
    subject_ref: SourceReference
    interpretations: List[Dict[str, Any]] = Field(default_factory=list)


class SynthesisGuardRequest(BaseModel):
    visited_refs: List[str] = Field(default_factory=list)
    new_ref: str
    depth: int = Field(default=0, ge=0)
    hop_count: int = Field(default=0, ge=0)
    policy: Optional[ReasoningDepthPolicy] = None


class AgentPermissionRequest(BaseModel):
    agent_type: AgentType
    requested_action: str


def persist_worker_pressure(snapshot: WorkerPressureSnapshot):
    scheduling = evaluate_worker_pressure(snapshot)
    record = CIWorkerPressureRecord(
        worker_id=snapshot.worker_id,
        cpu_pressure=snapshot.cpu_pressure,
        gpu_pressure=snapshot.gpu_pressure,
        vram_used_gb=snapshot.vram_used_gb,
        vram_total_gb=snapshot.vram_total_gb,
        thermal_state=snapshot.thermal_state,
        queue_congestion=snapshot.queue_congestion,
        inference_load=snapshot.inference_load,
        scheduling=model_to_dict(scheduling),
        created_at=snapshot.created_at,
    )
    record.save()
    return record, scheduling


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


@router.get("/ontology")
async def ontology_registries(current_user: User = Depends(get_current_user)):
    return {"registries": list_registries()}


@router.post("/ontology/validate")
async def ontology_validate(request: OntologyValidateRequest, current_user: User = Depends(get_current_user)):
    valid, missing = validate_label_ids(request.label_ids)
    return {"valid": valid, "missing": missing}


@router.get("/ontology/{domain}")
async def ontology_registry(domain: str, current_user: User = Depends(get_current_user)):
    registry = load_registries().get(domain)
    if not registry:
        raise HTTPException(status_code=404, detail="Ontology registry not found")
    return {"registry": model_to_dict(registry)}


@router.post("/confidence/aggregate")
async def confidence_aggregate(request: ConfidenceAggregateRequest, current_user: User = Depends(get_current_user)):
    aggregation = aggregate_confidence(request.evidence, request.policy)
    return {"confidence": model_to_dict(aggregation)}


@router.post("/feedback")
async def create_feedback(event: HumanFeedbackEvent, current_user: User = Depends(get_current_user)):
    event.created_by = current_user.username
    record = CIHumanFeedbackEvent(
        event_id=event.event_id,
        feedback_type=event.feedback_type.value,
        target_ref=model_to_dict(event.target_ref),
        rating=event.rating,
        correction=model_to_dict(event.correction) if event.correction else {},
        manual_override=model_to_dict(event.manual_override) if event.manual_override else {},
        reinforcement=model_to_dict(event.reinforcement) if event.reinforcement else {},
        comment=event.comment,
        created_by=current_user,
        created_at=event.created_at,
    )
    record.save()
    return {"feedback": record.to_dict(), "reinforcement_hint": feedback_reinforcement_hint(event)}


@router.get("/feedback")
async def list_feedback(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    records = CIHumanFeedbackEvent.objects().order_by("-created_at").limit(limit)
    return {"feedback": [record.to_dict() for record in records]}


@router.post("/consensus/resolve")
async def create_consensus(request: ConsensusResolveRequest, current_user: User = Depends(get_current_user)):
    consensus = resolve_semantic_consensus(request.subject_ref, request.interpretations)
    record = CISemanticConsensusRecord(
        consensus_id=consensus.consensus_id,
        subject_ref=model_to_dict(consensus.subject_ref),
        agreed_labels=[model_to_dict(label) for label in consensus.agreed_labels],
        disagreements=consensus.disagreements,
        agreement_score=consensus.agreement_score,
        resolution=consensus.resolution,
        created_at=consensus.created_at,
    )
    record.save()
    return {"consensus": model_to_dict(consensus), "record": record.to_dict()}


@router.get("/consensus")
async def list_consensus(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    records = CISemanticConsensusRecord.objects().order_by("-created_at").limit(limit)
    return {"consensus": [record.to_dict() for record in records]}


@router.post("/lineage")
async def create_lineage(lineage: StrategyLineage, current_user: User = Depends(get_current_user)):
    record = CIStrategyLineageRecord(
        lineage_id=lineage.lineage_id,
        recommendation_id=lineage.recommendation_id,
        evidence=[model_to_dict(item) for item in lineage.evidence],
        experiments=[model_to_dict(item) for item in lineage.experiments],
        semantic_packets=[model_to_dict(item) for item in lineage.semantic_packets],
        trends=[model_to_dict(item) for item in lineage.trends],
        memories=[model_to_dict(item) for item in lineage.memories],
        routing_decisions=[model_to_dict(item) for item in lineage.routing_decisions],
        observation_graph=model_to_dict(lineage.observation_graph),
        created_at=lineage.created_at,
    )
    record.save()
    return {"lineage": record.to_dict()}


@router.get("/lineage/{recommendation_id}")
async def get_lineage(recommendation_id: str, current_user: User = Depends(get_current_user)):
    records = CIStrategyLineageRecord.objects(recommendation_id=recommendation_id).order_by("-created_at")
    return {"lineage": [record.to_dict() for record in records]}


@router.post("/pressure")
async def record_worker_pressure(snapshot: WorkerPressureSnapshot, current_user: User = Depends(get_current_user)):
    record, scheduling = persist_worker_pressure(snapshot)
    return {"pressure": record.to_dict(), "scheduling": model_to_dict(scheduling)}


@router.get("/pressure")
async def list_worker_pressure(
    worker_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    query = {"worker_id": worker_id} if worker_id else {}
    records = CIWorkerPressureRecord.objects(**query).order_by("-created_at").limit(limit)
    return {"pressure": [record.to_dict() for record in records]}


@router.post("/cognitive-state")
async def create_cognitive_state(state: CreatorCognitiveState, current_user: User = Depends(get_current_user)):
    record = CICreatorCognitiveStateRecord(
        creator_id=state.creator_id,
        creator_mode=state.creator_mode,
        novelty=state.novelty,
        resonance=model_to_dict(state.resonance),
        fatigue=model_to_dict(state.fatigue),
        audience_alignment=model_to_dict(state.audience_alignment),
        identity_stability=model_to_dict(state.identity_stability),
        source_refs=[model_to_dict(ref) for ref in state.source_refs],
        created_at=state.created_at,
    )
    record.save()
    return {"cognitive_state": record.to_dict()}


@router.get("/cognitive-state/{creator_id}")
async def get_cognitive_state(
    creator_id: str,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    records = CICreatorCognitiveStateRecord.objects(creator_id=creator_id).order_by("-created_at").limit(limit)
    return {"cognitive_states": [record.to_dict() for record in records]}


@router.post("/inference-records")
async def create_inference_record(record_request: ModelInferenceRecord, current_user: User = Depends(get_current_user)):
    record = CIModelInferenceRecord(
        inference_id=record_request.inference_id,
        job_id=record_request.job_id,
        model_fingerprint=model_to_dict(record_request.model_fingerprint) if record_request.model_fingerprint else {},
        runtime_fingerprint=model_to_dict(record_request.runtime_fingerprint) if record_request.runtime_fingerprint else {},
        embedding_fingerprint=model_to_dict(record_request.embedding_fingerprint) if record_request.embedding_fingerprint else {},
        confidence=model_to_dict(record_request.confidence) if record_request.confidence else {},
        diagnostics=record_request.diagnostics,
        created_at=record_request.created_at,
    )
    record.save()
    return {"inference_record": record.to_dict()}


@router.post("/provenance")
async def create_provenance_graph(graph: AnalysisProvenanceGraph, current_user: User = Depends(get_current_user)):
    record = CIProvenanceGraphRecord(
        graph_id=graph.graph_id,
        subject_ref=model_to_dict(graph.subject_ref),
        observations=[model_to_dict(node) for node in graph.observations],
        inferences=[model_to_dict(node) for node in graph.inferences],
        links=[model_to_dict(link) for link in graph.links],
        created_at=graph.created_at,
    )
    record.save()
    return {"provenance": record.to_dict()}


@router.get("/provenance/{graph_id}")
async def get_provenance_graph(graph_id: str, current_user: User = Depends(get_current_user)):
    record = CIProvenanceGraphRecord.objects(graph_id=graph_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Provenance graph not found")
    return {"provenance": record.to_dict()}


@router.post("/sandbox")
async def create_sandbox_workspace(workspace: SandboxWorkspace, current_user: User = Depends(get_current_user)):
    record = CISandboxWorkspaceRecord(
        workspace_id=workspace.workspace_id,
        owner=current_user,
        creator_id=workspace.creator_id,
        persistent=False,
        context={"created_by": current_user.username},
        outputs=[],
        created_at=workspace.created_at,
    )
    record.save()
    return {"sandbox": record.to_dict()}


@router.post("/sandbox/reasoning")
async def sandbox_reasoning(reasoning: NonPersistentReasoning, current_user: User = Depends(get_current_user)):
    reasoning.may_write_memory = False
    return {"reasoning": model_to_dict(reasoning), "persistent": False}


@router.post("/guard/synthesis")
async def synthesis_guard(request: SynthesisGuardRequest, current_user: User = Depends(get_current_user)):
    boundary = check_synthesis_boundary(
        request.visited_refs,
        request.new_ref,
        request.depth,
        request.hop_count,
        request.policy,
    )
    return {"boundary": model_to_dict(boundary)}


@router.post("/agents/permission-check")
async def agent_permission_check(request: AgentPermissionRequest, current_user: User = Depends(get_current_user)):
    permission = check_agent_permission(request.agent_type, request.requested_action)
    return {"permission": model_to_dict(permission)}


@router.get("/agents/{agent_type}/restricted-context")
async def agent_restricted_context(agent_type: AgentType, current_user: User = Depends(get_current_user)):
    context = restricted_context(agent_type)
    return {"context": model_to_dict(context)}


@router.get("/policies/defaults")
async def policy_defaults(current_user: User = Depends(get_current_user)):
    return {
        "confidence": model_to_dict(ConfidenceCalibrationPolicy()),
        "reasoning_depth": model_to_dict(ReasoningDepthPolicy()),
        "temporal_weights": {
            "trend_14_days": temporal_weight("trend", 14),
            "creator_identity_14_days": temporal_weight("creator_identity", 14),
            "audience_14_days": temporal_weight("audience", 14),
        },
    }


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

            elif message_type == "pressure":
                if not worker_id:
                    await websocket.send_json({"message_type": "error", "error": "worker must register first"})
                    continue
                snapshot = WorkerPressureSnapshot(**message.get("payload", message))
                if snapshot.worker_id != worker_id:
                    await websocket.send_json({"message_type": "error", "error": "pressure worker_id mismatch"})
                    continue
                record, scheduling = persist_worker_pressure(snapshot)
                await websocket.send_json(
                    {
                        "message_type": "pressure_ack",
                        "pressure": record.to_dict(),
                        "scheduling": model_to_dict(scheduling),
                    }
                )

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
