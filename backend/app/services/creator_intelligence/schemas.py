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
    REPLAY_ANALYSIS = "replay_analysis"
    UPDATE_COGNITIVE_STATE = "update_cognitive_state"


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


class ConfidenceSource(str, Enum):
    HEURISTIC = "heuristic"
    MODEL_DERIVED = "model_derived"
    ENSEMBLE_DERIVED = "ensemble_derived"
    HUMAN_CONFIRMED = "human_confirmed"
    EXPERIMENTALLY_REINFORCED = "experimentally_reinforced"


class FeedbackEventType(str, Enum):
    CONFIRM_RECOMMENDATION = "confirm_recommendation"
    REJECT_INTERPRETATION = "reject_interpretation"
    LABEL_RESONANCE = "label_resonance"
    PERFORMANCE_MISMATCH = "performance_mismatch"
    MANUAL_OVERRIDE = "manual_override"


class AgentType(str, Enum):
    ANALYST = "analyst"
    STRATEGIST = "strategist"
    CRITIC = "critic"
    PREDICTOR = "predictor"
    TREND_OBSERVER = "trend_observer"
    BROWSER_COGNITION = "browser_cognition"


class OntologyDomain(str, Enum):
    EMOTIONS = "emotions"
    HOOK_TAXONOMY = "hook_taxonomy"
    VISUAL_STYLES = "visual_styles"
    PACING_LABELS = "pacing_labels"
    CREATOR_ARCHETYPES = "creator_archetypes"
    AUDIENCE_STATES = "audience_states"
    CONTENT_GOALS = "content_goals"


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


class OntologyLabel(BaseModel):
    id: str
    name: str
    description: str = ""
    domain: Optional[str] = None
    version: str = SCHEMA_VERSION


class OntologyRegistry(BaseModel):
    version: str
    domain: str
    labels: List[OntologyLabel] = Field(default_factory=list)


class OntologyLabelRef(BaseModel):
    label_id: str
    domain: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_refs: List[SourceReference] = Field(default_factory=list)


class ConfidenceEvidence(BaseModel):
    source: ConfidenceSource
    score: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    rationale: Optional[str] = None
    source_refs: List[SourceReference] = Field(default_factory=list)


class ConfidenceCalibrationPolicy(BaseModel):
    policy_id: str = "default"
    source_weights: Dict[ConfidenceSource, float] = Field(
        default_factory=lambda: {
            ConfidenceSource.HEURISTIC: 0.8,
            ConfidenceSource.MODEL_DERIVED: 1.0,
            ConfidenceSource.ENSEMBLE_DERIVED: 1.2,
            ConfidenceSource.HUMAN_CONFIRMED: 1.6,
            ConfidenceSource.EXPERIMENTALLY_REINFORCED: 1.5,
        }
    )
    minimum_sources_for_high_confidence: int = Field(default=2, ge=1)
    high_confidence_threshold: float = Field(default=0.75, ge=0.0, le=1.0)


class ConfidenceAggregation(BaseModel):
    policy_id: str = "default"
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: List[ConfidenceEvidence] = Field(default_factory=list)
    derivation: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FeedbackCorrection(BaseModel):
    target_ref: SourceReference
    original_label: Optional[str] = None
    corrected_label: Optional[str] = None
    comment: Optional[str] = None


class ManualSemanticOverride(BaseModel):
    target_ref: SourceReference
    ontology_labels: List[OntologyLabelRef] = Field(default_factory=list)
    replacement_summary: Optional[str] = None
    reason: str


class ReinforcementWeight(BaseModel):
    target_namespace: str
    weight_delta: float = Field(default=0.0, ge=-1.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    expires_at: Optional[datetime] = None


class HumanFeedbackEvent(BaseModel):
    schema_version: str = SCHEMA_VERSION
    event_id: str = Field(default_factory=lambda: uuid4().hex)
    feedback_type: FeedbackEventType
    target_ref: SourceReference
    rating: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    correction: Optional[FeedbackCorrection] = None
    manual_override: Optional[ManualSemanticOverride] = None
    reinforcement: Optional[ReinforcementWeight] = None
    comment: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


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


class ModelFingerprint(BaseModel):
    model_config = {"protected_namespaces": ()}

    model_name: str
    model_family: Optional[str] = None
    quantization: Optional[str] = None
    context_size: Optional[int] = Field(default=None, ge=1)
    seed: Optional[int] = None
    temperature: Optional[float] = Field(default=None, ge=0.0)


class RuntimeFingerprint(BaseModel):
    runtime: str
    backend: str
    runtime_version: Optional[str] = None
    device: Optional[str] = None
    worker_id: Optional[str] = None


class EmbeddingFingerprint(BaseModel):
    embedding_model: str
    embedding_version: str
    tokenizer_version: Optional[str] = None
    vector_size: Optional[int] = Field(default=None, ge=1)
    distance: str = "Cosine"


class ModelInferenceRecord(BaseModel):
    model_config = {"protected_namespaces": ()}

    schema_version: str = SCHEMA_VERSION
    inference_id: str = Field(default_factory=lambda: uuid4().hex)
    job_id: Optional[str] = None
    model_fingerprint: Optional[ModelFingerprint] = None
    runtime_fingerprint: Optional[RuntimeFingerprint] = None
    embedding_fingerprint: Optional[EmbeddingFingerprint] = None
    confidence: Optional[ConfidenceAggregation] = None
    diagnostics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


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


class WorkerPressureSnapshot(BaseModel):
    worker_id: str
    cpu_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    gpu_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    vram_used_gb: Optional[float] = Field(default=None, ge=0.0)
    vram_total_gb: Optional[float] = Field(default=None, ge=0.0)
    thermal_state: str = "nominal"
    queue_congestion: float = Field(default=0.0, ge=0.0, le=1.0)
    inference_load: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ThermalProtectionPolicy(BaseModel):
    policy_id: str = "default"
    hot_states: List[str] = Field(default_factory=lambda: ["hot", "critical"])
    pause_low_priority_when_hot: bool = True
    max_gpu_pressure: float = Field(default=0.9, ge=0.0, le=1.0)
    max_vram_ratio: float = Field(default=0.92, ge=0.0, le=1.0)


class ResourceAwareScheduling(BaseModel):
    eligible: bool
    reason: str
    recommended_priority_ceiling: JobPriority = JobPriority.NORMAL


class InferenceBackpressure(BaseModel):
    should_throttle: bool
    reason: str
    retry_after_seconds: int = Field(default=0, ge=0)


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


class CancellationToken(BaseModel):
    job_id: str
    token_id: str = Field(default_factory=lambda: uuid4().hex)
    reason: str = "user_requested"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class PriorityEscalationPolicy(BaseModel):
    urgent_job_types: List[JobType] = Field(default_factory=lambda: [JobType.DRAFT_CRITIQUE])
    suspend_low_priority_for_urgent: bool = True
    max_low_priority_runtime_before_checkpoint_seconds: int = 120


class ResumeCheckpoint(BaseModel):
    job_id: str
    checkpoint_id: str = Field(default_factory=lambda: uuid4().hex)
    stage: str
    artifact_refs: List[SourceReference] = Field(default_factory=list)
    state: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InterruptibleJob(BaseModel):
    job_id: str
    interruptible: bool = True
    safe_checkpoint_stages: List[str] = Field(default_factory=list)
    latest_checkpoint: Optional[ResumeCheckpoint] = None


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


class RecommendationEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: uuid4().hex)
    evidence_type: str
    source_refs: List[SourceReference] = Field(default_factory=list)
    confidence: Optional[ConfidenceAggregation] = None
    summary: Optional[str] = None


class ReasoningReference(BaseModel):
    ref_type: str
    ref_id: str
    role: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class SupportingObservationGraph(BaseModel):
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)


class StrategyLineage(BaseModel):
    lineage_id: str = Field(default_factory=lambda: uuid4().hex)
    recommendation_id: str
    evidence: List[RecommendationEvidence] = Field(default_factory=list)
    experiments: List[ReasoningReference] = Field(default_factory=list)
    semantic_packets: List[ReasoningReference] = Field(default_factory=list)
    trends: List[ReasoningReference] = Field(default_factory=list)
    memories: List[ReasoningReference] = Field(default_factory=list)
    routing_decisions: List[ReasoningReference] = Field(default_factory=list)
    observation_graph: SupportingObservationGraph = Field(default_factory=SupportingObservationGraph)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TemporalWeightPolicy(BaseModel):
    policy_id: str = "default"
    trend_half_life_days: float = Field(default=7.0, gt=0)
    identity_half_life_days: float = Field(default=120.0, gt=0)
    audience_half_life_days: float = Field(default=30.0, gt=0)


class TrendDecayCurve(BaseModel):
    age_days: float = Field(default=0.0, ge=0.0)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class IdentityPersistenceCurve(BaseModel):
    age_days: float = Field(default=0.0, ge=0.0)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class AudienceShiftWeight(BaseModel):
    age_days: float = Field(default=0.0, ge=0.0)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


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


class SemanticConsensus(BaseModel):
    consensus_id: str = Field(default_factory=lambda: uuid4().hex)
    subject_ref: SourceReference
    agreed_labels: List[OntologyLabelRef] = Field(default_factory=list)
    disagreements: List[Dict[str, Any]] = Field(default_factory=list)
    agreement_score: float = Field(default=0.0, ge=0.0, le=1.0)
    resolution: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InterpretationDisagreement(BaseModel):
    disagreement_id: str = Field(default_factory=lambda: uuid4().hex)
    subject_ref: SourceReference
    interpretations: List[Dict[str, Any]] = Field(default_factory=list)
    conflict_labels: List[str] = Field(default_factory=list)
    severity: str = "medium"
    requires_human_review: bool = False


class MultiModelAgreementScore(BaseModel):
    model_config = {"protected_namespaces": ()}

    subject_ref: SourceReference
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    model_count: int = Field(default=0, ge=0)
    label_overlap: float = Field(default=0.0, ge=0.0, le=1.0)


class AgentCapabilityBoundary(BaseModel):
    agent_type: AgentType
    can_scrape: bool = False
    can_execute_browser_actions: bool = False
    can_write_memory_directly: bool = False
    can_modify_routing: bool = False
    can_alter_embeddings: bool = False
    allowed_job_types: List[JobType] = Field(default_factory=list)


class PermissionScopedExecution(BaseModel):
    agent_type: AgentType
    requested_action: str
    allowed: bool
    reason: str


class RestrictedToolContext(BaseModel):
    agent_type: AgentType
    allowed_tools: List[str] = Field(default_factory=list)
    denied_tools: List[str] = Field(default_factory=list)
    max_reasoning_depth: int = 3


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


class ResonanceEstimate(BaseModel):
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: Optional[ConfidenceAggregation] = None
    ontology_labels: List[OntologyLabelRef] = Field(default_factory=list)


class FatigueEstimate(BaseModel):
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: Optional[ConfidenceAggregation] = None
    drivers: List[str] = Field(default_factory=list)


class AudienceAlignment(BaseModel):
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    audience_states: List[OntologyLabelRef] = Field(default_factory=list)
    confidence: Optional[ConfidenceAggregation] = None


class IdentityStability(BaseModel):
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    drift_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: Optional[ConfidenceAggregation] = None


class CreatorCognitiveState(BaseModel):
    schema_version: str = SCHEMA_VERSION
    creator_id: str
    creator_mode: str
    novelty: float = Field(default=0.0, ge=0.0, le=1.0)
    resonance: ResonanceEstimate = Field(default_factory=ResonanceEstimate)
    fatigue: FatigueEstimate = Field(default_factory=FatigueEstimate)
    audience_alignment: AudienceAlignment = Field(default_factory=AudienceAlignment)
    identity_stability: IdentityStability = Field(default_factory=IdentityStability)
    source_refs: List[SourceReference] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MemoryCandidate(BaseModel):
    memory_type: str
    namespace: str
    subject_id: Optional[str] = None
    statement: str = Field(..., min_length=1, max_length=4000)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_refs: List[SourceReference] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    decay_rate: float = Field(default=0.01, ge=0.0, le=1.0)
    confidence_aggregation: Optional[ConfidenceAggregation] = None


class ReasoningDepthPolicy(BaseModel):
    policy_id: str = "default"
    max_reasoning_depth: int = Field(default=3, ge=1, le=10)
    max_synthesis_hops: int = Field(default=4, ge=1, le=20)
    max_analysis_of_analysis_hops: int = Field(default=1, ge=0, le=5)


class RecursiveAnalysisGuard(BaseModel):
    policy: ReasoningDepthPolicy = Field(default_factory=ReasoningDepthPolicy)
    visited_refs: List[str] = Field(default_factory=list)
    current_depth: int = 0


class SynthesisBoundary(BaseModel):
    allowed: bool
    reason: str
    depth: int
    hop_count: int


class SandboxWorkspace(BaseModel):
    workspace_id: str = Field(default_factory=lambda: uuid4().hex)
    owner: Optional[str] = None
    creator_id: Optional[str] = None
    persistent: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HypotheticalStrategy(BaseModel):
    strategy_id: str = Field(default_factory=lambda: uuid4().hex)
    workspace_id: str
    title: str
    assumptions: List[str] = Field(default_factory=list)
    expected_effects: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[ConfidenceAggregation] = None


class SimulationContext(BaseModel):
    workspace_id: str
    source_refs: List[SourceReference] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    ontology_labels: List[OntologyLabelRef] = Field(default_factory=list)


class NonPersistentReasoning(BaseModel):
    workspace_id: str
    output: Dict[str, Any] = Field(default_factory=dict)
    may_write_memory: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ObservationNode(BaseModel):
    node_id: str
    node_type: str = "observation"
    source_ref: SourceReference
    summary: Optional[str] = None


class InferenceNode(BaseModel):
    model_config = {"protected_namespaces": ()}

    node_id: str
    node_type: str = "inference"
    model_fingerprint: Optional[ModelFingerprint] = None
    runtime_fingerprint: Optional[RuntimeFingerprint] = None
    summary: str
    confidence: Optional[ConfidenceAggregation] = None


class EvidenceLink(BaseModel):
    from_node: str
    to_node: str
    link_type: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class AnalysisProvenanceGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: uuid4().hex)
    subject_ref: SourceReference
    observations: List[ObservationNode] = Field(default_factory=list)
    inferences: List[InferenceNode] = Field(default_factory=list)
    links: List[EvidenceLink] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return model.dict()
