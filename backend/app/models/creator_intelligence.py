from datetime import datetime

from mongoengine import (
    BooleanField,
    DateTimeField,
    DictField,
    Document,
    FloatField,
    IntField,
    ListField,
    LongField,
    ReferenceField,
    StringField,
)

from app.models.user import User


class CICreatorProfile(Document):
    platform = StringField(required=True, choices=("tiktok", "instagram", "youtube_shorts", "other"))
    handle = StringField(required=True)
    display_name = StringField()
    profile_url = StringField()
    creator_type = StringField(default="external", choices=("internal", "competitor", "external"))
    tracked = BooleanField(default=True)
    tags = ListField(StringField())
    notes = StringField()
    metadata = DictField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "ci_creators",
        "indexes": [
            {"fields": ["platform", "handle"], "unique": True},
            "creator_type",
            "tracked",
            "tags",
        ],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": str(self.id),
            "platform": self.platform,
            "handle": self.handle,
            "display_name": self.display_name,
            "profile_url": self.profile_url,
            "creator_type": self.creator_type,
            "tracked": self.tracked,
            "tags": self.tags or [],
            "notes": self.notes,
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CIContentItem(Document):
    creator = ReferenceField(CICreatorProfile)
    platform = StringField(required=True, choices=("tiktok", "instagram", "youtube_shorts", "other"))
    platform_content_id = StringField()
    content_url = StringField(required=True)
    caption_sanitized = StringField()
    hashtags = ListField(StringField())
    metrics = DictField()
    sound_metadata = DictField()
    upload_date = DateTimeField()
    artifact_refs = ListField(DictField())
    scrape_run_id = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "ci_content_items",
        "indexes": [
            "creator",
            "platform",
            "platform_content_id",
            "scrape_run_id",
            "created_at",
        ],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": str(self.id),
            "creator_id": str(self.creator.id) if self.creator else None,
            "platform": self.platform,
            "platform_content_id": self.platform_content_id,
            "content_url": self.content_url,
            "caption_sanitized": self.caption_sanitized,
            "hashtags": self.hashtags or [],
            "metrics": self.metrics or {},
            "sound_metadata": self.sound_metadata or {},
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "artifact_refs": self.artifact_refs or [],
            "scrape_run_id": self.scrape_run_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CIScrapeRun(Document):
    platform = StringField(required=True)
    target = StringField(required=True)
    requested_by = ReferenceField(User)
    status = StringField(default="queued", choices=("queued", "running", "paused", "completed", "failed", "cancelled"))
    job_id = StringField()
    items_found = IntField(default=0)
    warnings = ListField(StringField())
    browser_cognition = DictField()
    created_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()

    meta = {"collection": "ci_scrape_runs", "indexes": ["platform", "target", "status", "job_id", "created_at"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "platform": self.platform,
            "target": self.target,
            "requested_by": self.requested_by.username if self.requested_by else None,
            "status": self.status,
            "job_id": self.job_id,
            "items_found": self.items_found,
            "warnings": self.warnings or [],
            "browser_cognition": self.browser_cognition or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class CIAnalysisPacket(Document):
    job_id = StringField(required=True)
    content = ReferenceField(CIContentItem)
    packet_type = StringField(required=True)
    schema_version = StringField(default="1.0")
    output = DictField(required=True)
    confidence = FloatField(default=0.0)
    evidence = ListField(DictField())
    warnings = ListField(StringField())
    source_refs = ListField(DictField())
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "ci_analysis_packets",
        "indexes": ["job_id", "content", "packet_type", "confidence", "created_at"],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": str(self.id),
            "job_id": self.job_id,
            "content_id": str(self.content.id) if self.content else None,
            "packet_type": self.packet_type,
            "schema_version": self.schema_version,
            "output": self.output or {},
            "confidence": self.confidence,
            "evidence": self.evidence or [],
            "warnings": self.warnings or [],
            "source_refs": self.source_refs or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CIMemoryRecord(Document):
    memory_type = StringField(
        required=True,
        choices=("creator", "trend", "competitor", "strategist", "predictor"),
    )
    namespace = StringField(required=True)
    subject_id = StringField()
    statement = StringField(required=True)
    confidence = FloatField(default=0.0)
    source_refs = ListField(DictField())
    evidence = ListField(DictField())
    decay_rate = FloatField(default=0.01)
    validation_status = StringField(default="pending", choices=("pending", "accepted", "rejected", "quarantined"))
    created_at = DateTimeField(default=datetime.utcnow)
    last_seen_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()

    meta = {
        "collection": "ci_memory_records",
        "indexes": [
            "memory_type",
            "namespace",
            "subject_id",
            "validation_status",
            "confidence",
            "created_at",
        ],
    }

    def to_dict(self):
        return {
            "id": str(self.id),
            "memory_type": self.memory_type,
            "namespace": self.namespace,
            "subject_id": self.subject_id,
            "statement": self.statement,
            "confidence": self.confidence,
            "source_refs": self.source_refs or [],
            "evidence": self.evidence or [],
            "decay_rate": self.decay_rate,
            "validation_status": self.validation_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class CIWorkerRecord(Document):
    worker_id = StringField(required=True, unique=True)
    worker_name = StringField(required=True)
    machine_role = StringField(required=True, choices=("control_plane", "scraper_control", "ai_inference", "generic"))
    host_fingerprint = StringField(required=True)
    capabilities = DictField()
    status = StringField(default="registered", choices=("registered", "online", "stale", "offline", "disabled"))
    version = StringField()
    token_digest = StringField()
    last_heartbeat = DateTimeField()
    load = DictField()
    current_jobs = ListField(StringField())
    model_runtime = DictField()
    registered_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "ci_workers", "indexes": ["worker_id", "machine_role", "status", "last_heartbeat"]}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": str(self.id),
            "worker_id": self.worker_id,
            "worker_name": self.worker_name,
            "machine_role": self.machine_role,
            "host_fingerprint": self.host_fingerprint,
            "capabilities": self.capabilities or {},
            "status": self.status,
            "version": self.version,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "load": self.load or {},
            "current_jobs": self.current_jobs or [],
            "model_runtime": self.model_runtime or {},
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CIJobRecord(Document):
    job_id = StringField(required=True, unique=True)
    stream_id = StringField()
    job_type = StringField(required=True)
    priority = StringField(default="normal", choices=("high", "normal", "low"))
    status = StringField(
        default="queued",
        choices=("queued", "running", "paused", "completed", "failed", "cancelled", "dead"),
    )
    requested_by = ReferenceField(User)
    assigned_worker_id = StringField()
    payload = DictField()
    capability_requirements = DictField()
    trace_id = StringField()
    attempt = IntField(default=0)
    max_attempts = IntField(default=3)
    timeout_seconds = IntField(default=900)
    error = StringField()
    progress = ListField(DictField())
    result = DictField()
    created_at = DateTimeField(default=datetime.utcnow)
    scheduled_at = DateTimeField(default=datetime.utcnow)
    started_at = DateTimeField()
    completed_at = DateTimeField()

    meta = {
        "collection": "ci_jobs",
        "indexes": [
            "job_id",
            "stream_id",
            "job_type",
            "priority",
            "status",
            "assigned_worker_id",
            "created_at",
            "scheduled_at",
        ],
    }

    def to_dict(self):
        return {
            "id": str(self.id),
            "job_id": self.job_id,
            "stream_id": self.stream_id,
            "job_type": self.job_type,
            "priority": self.priority,
            "status": self.status,
            "requested_by": self.requested_by.username if self.requested_by else None,
            "assigned_worker_id": self.assigned_worker_id,
            "payload": self.payload or {},
            "capability_requirements": self.capability_requirements or {},
            "trace_id": self.trace_id,
            "attempt": self.attempt,
            "max_attempts": self.max_attempts,
            "timeout_seconds": self.timeout_seconds,
            "error": self.error,
            "progress": self.progress or [],
            "result": self.result or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class CIModelRegistryEntry(Document):
    worker_id = StringField(required=True)
    model_name = StringField(required=True)
    model_type = StringField(default="gguf")
    path = StringField(required=True)
    sha256 = StringField()
    md5 = StringField()
    size_bytes = LongField()
    validation_status = StringField(default="detected", choices=("detected", "validated", "mismatch", "missing", "error"))
    runtime_status = DictField()
    detected_at = DateTimeField(default=datetime.utcnow)
    verified_at = DateTimeField()

    meta = {"collection": "ci_model_registry", "indexes": ["worker_id", "model_name", "model_type", "validation_status"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "worker_id": self.worker_id,
            "model_name": self.model_name,
            "model_type": self.model_type,
            "path": self.path,
            "sha256": self.sha256,
            "md5": self.md5,
            "size_bytes": self.size_bytes,
            "validation_status": self.validation_status,
            "runtime_status": self.runtime_status or {},
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
        }


class CIAgentOutput(Document):
    agent_type = StringField(
        required=True,
        choices=("analyst", "strategist", "critic", "predictor", "trend_observer", "browser_cognition"),
    )
    job_id = StringField(required=True)
    model_route = DictField()
    input_refs = ListField(DictField())
    output = DictField(required=True)
    confidence = FloatField(default=0.0)
    evidence = ListField(DictField())
    warnings = ListField(StringField())
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "ci_agent_outputs", "indexes": ["agent_type", "job_id", "confidence", "created_at"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "agent_type": self.agent_type,
            "job_id": self.job_id,
            "model_route": self.model_route or {},
            "input_refs": self.input_refs or [],
            "output": self.output or {},
            "confidence": self.confidence,
            "evidence": self.evidence or [],
            "warnings": self.warnings or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CIHumanFeedbackEvent(Document):
    event_id = StringField(required=True, unique=True)
    feedback_type = StringField(required=True)
    target_ref = DictField(required=True)
    rating = FloatField()
    correction = DictField()
    manual_override = DictField()
    reinforcement = DictField()
    comment = StringField()
    created_by = ReferenceField(User)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "ci_human_feedback", "indexes": ["event_id", "feedback_type", "created_by", "created_at"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "event_id": self.event_id,
            "feedback_type": self.feedback_type,
            "target_ref": self.target_ref or {},
            "rating": self.rating,
            "correction": self.correction or {},
            "manual_override": self.manual_override or {},
            "reinforcement": self.reinforcement or {},
            "comment": self.comment,
            "created_by": self.created_by.username if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CIStrategyLineageRecord(Document):
    lineage_id = StringField(required=True, unique=True)
    recommendation_id = StringField(required=True)
    evidence = ListField(DictField())
    experiments = ListField(DictField())
    semantic_packets = ListField(DictField())
    trends = ListField(DictField())
    memories = ListField(DictField())
    routing_decisions = ListField(DictField())
    observation_graph = DictField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "ci_strategy_lineage", "indexes": ["lineage_id", "recommendation_id", "created_at"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "lineage_id": self.lineage_id,
            "recommendation_id": self.recommendation_id,
            "evidence": self.evidence or [],
            "experiments": self.experiments or [],
            "semantic_packets": self.semantic_packets or [],
            "trends": self.trends or [],
            "memories": self.memories or [],
            "routing_decisions": self.routing_decisions or [],
            "observation_graph": self.observation_graph or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CIWorkerPressureRecord(Document):
    worker_id = StringField(required=True)
    cpu_pressure = FloatField(default=0.0)
    gpu_pressure = FloatField(default=0.0)
    vram_used_gb = FloatField()
    vram_total_gb = FloatField()
    thermal_state = StringField(default="nominal")
    queue_congestion = FloatField(default=0.0)
    inference_load = FloatField(default=0.0)
    scheduling = DictField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "ci_worker_pressure", "indexes": ["worker_id", "thermal_state", "created_at"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "worker_id": self.worker_id,
            "cpu_pressure": self.cpu_pressure,
            "gpu_pressure": self.gpu_pressure,
            "vram_used_gb": self.vram_used_gb,
            "vram_total_gb": self.vram_total_gb,
            "thermal_state": self.thermal_state,
            "queue_congestion": self.queue_congestion,
            "inference_load": self.inference_load,
            "scheduling": self.scheduling or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CIModelInferenceRecord(Document):
    inference_id = StringField(required=True, unique=True)
    job_id = StringField()
    model_fingerprint = DictField()
    runtime_fingerprint = DictField()
    embedding_fingerprint = DictField()
    confidence = DictField()
    diagnostics = DictField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "ci_model_inferences", "indexes": ["inference_id", "job_id", "created_at"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "inference_id": self.inference_id,
            "job_id": self.job_id,
            "model_fingerprint": self.model_fingerprint or {},
            "runtime_fingerprint": self.runtime_fingerprint or {},
            "embedding_fingerprint": self.embedding_fingerprint or {},
            "confidence": self.confidence or {},
            "diagnostics": self.diagnostics or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CISemanticConsensusRecord(Document):
    consensus_id = StringField(required=True, unique=True)
    subject_ref = DictField(required=True)
    agreed_labels = ListField(DictField())
    disagreements = ListField(DictField())
    agreement_score = FloatField(default=0.0)
    resolution = StringField(default="pending")
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "ci_semantic_consensus", "indexes": ["consensus_id", "agreement_score", "resolution", "created_at"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "consensus_id": self.consensus_id,
            "subject_ref": self.subject_ref or {},
            "agreed_labels": self.agreed_labels or [],
            "disagreements": self.disagreements or [],
            "agreement_score": self.agreement_score,
            "resolution": self.resolution,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CICreatorCognitiveStateRecord(Document):
    creator_id = StringField(required=True)
    creator_mode = StringField(required=True)
    novelty = FloatField(default=0.0)
    resonance = DictField()
    fatigue = DictField()
    audience_alignment = DictField()
    identity_stability = DictField()
    source_refs = ListField(DictField())
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "ci_creator_cognitive_states", "indexes": ["creator_id", "creator_mode", "created_at"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "creator_id": self.creator_id,
            "creator_mode": self.creator_mode,
            "novelty": self.novelty,
            "resonance": self.resonance or {},
            "fatigue": self.fatigue or {},
            "audience_alignment": self.audience_alignment or {},
            "identity_stability": self.identity_stability or {},
            "source_refs": self.source_refs or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CIProvenanceGraphRecord(Document):
    graph_id = StringField(required=True, unique=True)
    subject_ref = DictField(required=True)
    observations = ListField(DictField())
    inferences = ListField(DictField())
    links = ListField(DictField())
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "ci_provenance_graphs", "indexes": ["graph_id", "created_at"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "graph_id": self.graph_id,
            "subject_ref": self.subject_ref or {},
            "observations": self.observations or [],
            "inferences": self.inferences or [],
            "links": self.links or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CISandboxWorkspaceRecord(Document):
    workspace_id = StringField(required=True, unique=True)
    owner = ReferenceField(User)
    creator_id = StringField()
    persistent = BooleanField(default=False)
    context = DictField()
    outputs = ListField(DictField())
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "ci_sandbox_workspaces", "indexes": ["workspace_id", "owner", "creator_id", "created_at"]}

    def to_dict(self):
        return {
            "id": str(self.id),
            "workspace_id": self.workspace_id,
            "owner": self.owner.username if self.owner else None,
            "creator_id": self.creator_id,
            "persistent": self.persistent,
            "context": self.context or {},
            "outputs": self.outputs or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
