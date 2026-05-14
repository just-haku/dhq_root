from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


SCHEMA_VERSION = "1.0"


class MachineRole(str, Enum):
    CONTROL_PLANE = "control_plane"
    SCRAPER_CONTROL = "scraper_control"
    AI_INFERENCE = "ai_inference"
    GENERIC = "generic"


class JobType(str, Enum):
    SCRAPE_PROFILE = "scrape_profile"
    SCRAPE_CONTENT_BATCH = "scrape_content_batch"
    SAMPLE_FRAMES = "sample_frames"
    OCR_TIMELINE = "ocr_timeline"
    ANALYZE_VIDEO = "analyze_video"
    EMBED_CONTENT = "embed_content"
    UPDATE_MEMORY = "update_memory"
    COMPARE_COMPETITOR = "compare_competitor"
    DRAFT_CRITIQUE = "draft_critique"
    TREND_SCAN = "trend_scan"
    STRATEGIC_SYNTHESIS = "strategic_synthesis"
    MODEL_SCAN = "model_scan"
    MODEL_HEALTH_CHECK = "model_health_check"


class JobPriority(str, Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DEAD = "dead"


class ResultStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class SourceReference(BaseModel):
    ref_type: str = Field(..., min_length=1)
    ref_id: str = Field(..., min_length=1)
    url: Optional[str] = None
    label: Optional[str] = None
    timestamp_ms: Optional[int] = None


class EvidenceItem(BaseModel):
    kind: str = Field(..., min_length=1)
    text: Optional[str] = None
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    source_refs: List[SourceReference] = Field(default_factory=list)


class WorkerCapability(BaseModel):
    gpu: bool = False
    multimodal: bool = False
    ocr: bool = False
    embeddings: bool = False
    playwright: bool = False
    browser_cognition: bool = False
    gguf_runtime: bool = False
    vram_gb: Optional[float] = Field(default=None, ge=0)
    embedding_speed: Optional[str] = None
    supported_platforms: List[str] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)

    def as_match_dict(self) -> Dict[str, Any]:
        return {
            "gpu": self.gpu,
            "multimodal": self.multimodal,
            "ocr": self.ocr,
            "embeddings": self.embeddings,
            "playwright": self.playwright,
            "browser_cognition": self.browser_cognition,
            "gguf_runtime": self.gguf_runtime,
            "vram_gb": self.vram_gb,
            "embedding_speed": self.embedding_speed,
            "supported_platforms": self.supported_platforms,
            **self.extra,
        }


class WorkerRegistration(BaseModel):
    message_type: str = "register"
    schema_version: str = SCHEMA_VERSION
    worker_id: str = Field(..., min_length=3, max_length=128)
    worker_name: str = Field(..., min_length=1, max_length=128)
    machine_role: MachineRole = MachineRole.GENERIC
    host_fingerprint: str = Field(..., min_length=6, max_length=256)
    capabilities: WorkerCapability = Field(default_factory=WorkerCapability)
    version: str = "0.1.0"
    auth_token: str = Field(..., min_length=8)


class ModelRuntimeStatus(BaseModel):
    runtime: str = "unknown"
    healthy: bool = False
    active_model: Optional[str] = None
    endpoint: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    error: Optional[str] = None


class WorkerHeartbeat(BaseModel):
    model_config = {"protected_namespaces": ()}

    message_type: str = "heartbeat"
    schema_version: str = SCHEMA_VERSION
    worker_id: str
    load: Dict[str, Any] = Field(default_factory=dict)
    current_jobs: List[str] = Field(default_factory=list)
    model_runtime: Optional[ModelRuntimeStatus] = None
    errors: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkerHealth(BaseModel):
    worker_id: str
    status: str
    last_heartbeat: Optional[datetime] = None
    stale_after_seconds: int = 45
    offline_after_seconds: int = 90


class CapabilityRequirements(BaseModel):
    gpu: Optional[bool] = None
    multimodal: Optional[bool] = None
    ocr: Optional[bool] = None
    embeddings: Optional[bool] = None
    playwright: Optional[bool] = None
    browser_cognition: Optional[bool] = None
    gguf_runtime: Optional[bool] = None
    min_vram_gb: Optional[float] = Field(default=None, ge=0)
    platform: Optional[str] = None


class JobEnvelope(BaseModel):
    schema_version: str = SCHEMA_VERSION
    job_id: str = Field(default_factory=lambda: uuid4().hex)
    job_type: JobType
    priority: JobPriority = JobPriority.NORMAL
    requested_by: Optional[str] = None
    capability_requirements: CapabilityRequirements = Field(default_factory=CapabilityRequirements)
    payload: Dict[str, Any] = Field(default_factory=dict)
    trace_id: str = Field(default_factory=lambda: uuid4().hex)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_at: datetime = Field(default_factory=datetime.utcnow)
    max_attempts: int = Field(default=3, ge=1, le=10)
    attempt: int = Field(default=0, ge=0)
    timeout_seconds: int = Field(default=900, ge=5, le=86400)


class JobCreateRequest(BaseModel):
    job_type: JobType
    priority: JobPriority = JobPriority.NORMAL
    payload: Dict[str, Any] = Field(default_factory=dict)
    capability_requirements: CapabilityRequirements = Field(default_factory=CapabilityRequirements)
    target_worker_id: Optional[str] = None
    max_attempts: int = Field(default=3, ge=1, le=10)
    timeout_seconds: int = Field(default=900, ge=5, le=86400)


class JobProgressEvent(BaseModel):
    schema_version: str = SCHEMA_VERSION
    job_id: str
    worker_id: str
    status: str = "running"
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    message: Optional[str] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class JobResult(BaseModel):
    schema_version: str = SCHEMA_VERSION
    job_id: str
    worker_id: str
    status: ResultStatus
    output: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


class ModelScanRequest(BaseModel):
    worker_id: Optional[str] = None
    roots: List[str] = Field(default_factory=list)
    validate_hashes: bool = False


class ModelScanResult(BaseModel):
    schema_version: str = SCHEMA_VERSION
    worker_id: str
    root_paths: List[str]
    models: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisToggleSet(BaseModel):
    ocr_timeline: bool = True
    emotional_analysis: bool = True
    visual_fatigue: bool = True
    competitor_comparison: bool = False
    audience_psychology: bool = True
    shot_boundary_detection: bool = True
    pacing_graph: bool = True
    embedding_search: bool = True
    trend_comparison: bool = False
    draft_critique: bool = False


class BrowserCognitionPacket(BaseModel):
    page_state: str
    uncertainty: float = Field(default=0.0, ge=0.0, le=1.0)
    captcha_detected: bool = False
    suspicious_state: bool = False
    safe_to_continue: bool = True
    recommendation: str = "continue"
    evidence: List[EvidenceItem] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    @validator("recommendation")
    def validate_recommendation(cls, value):
        allowed = {"continue", "pause_for_user", "retry_later", "stop"}
        if value not in allowed:
            raise ValueError(f"recommendation must be one of {sorted(allowed)}")
        return value


class VideoSemanticPacket(BaseModel):
    schema_version: str = SCHEMA_VERSION
    job_id: str
    content_id: Optional[str] = None
    summary: str
    first_three_seconds: Dict[str, Any] = Field(default_factory=dict)
    visual_elements: List[str] = Field(default_factory=list)
    audio_elements: List[str] = Field(default_factory=list)
    text_overlays: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    source_refs: List[SourceReference] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HookAnalysis(BaseModel):
    hook_text: Optional[str] = None
    hook_taxonomy: List[str] = Field(default_factory=list)
    strength_score: float = Field(default=0.0, ge=0.0, le=1.0)
    novelty_score: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)


class PacingAnalysis(BaseModel):
    cuts_per_minute: Optional[float] = None
    dead_zones: List[Dict[str, Any]] = Field(default_factory=list)
    pacing_score: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)


class ShotBoundarySummary(BaseModel):
    shot_count: int = 0
    boundaries_ms: List[int] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class EmotionTimeline(BaseModel):
    segments: List[Dict[str, Any]] = Field(default_factory=list)
    dominant_emotions: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class VisualFatigueReport(BaseModel):
    fatigue_score: float = Field(default=0.0, ge=0.0, le=1.0)
    repeated_elements: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class AudiencePsychologyEstimate(BaseModel):
    likely_reactions: List[Dict[str, Any]] = Field(default_factory=list)
    resonance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class CreatorIdentitySignal(BaseModel):
    identity_traits: List[str] = Field(default_factory=list)
    recurring_formats: List[str] = Field(default_factory=list)
    consistency_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class MemoryCandidate(BaseModel):
    memory_type: str
    namespace: str
    subject_id: Optional[str] = None
    statement: str = Field(..., min_length=1, max_length=4000)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_refs: List[SourceReference] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    decay_rate: float = Field(default=0.01, ge=0.0, le=1.0)


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return model.dict()
