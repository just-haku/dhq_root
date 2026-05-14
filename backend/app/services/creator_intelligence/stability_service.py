import math
from typing import Dict, Iterable, List, Set

from app.services.creator_intelligence.schemas import (
    AgentCapabilityBoundary,
    AgentType,
    ConfidenceAggregation,
    ConfidenceCalibrationPolicy,
    ConfidenceEvidence,
    HumanFeedbackEvent,
    InterpretationDisagreement,
    MultiModelAgreementScore,
    OntologyLabelRef,
    PermissionScopedExecution,
    ReasoningDepthPolicy,
    ResourceAwareScheduling,
    RestrictedToolContext,
    SemanticConsensus,
    SourceReference,
    SynthesisBoundary,
    TemporalWeightPolicy,
    ThermalProtectionPolicy,
    WorkerPressureSnapshot,
    model_to_dict,
)
from app.services.creator_intelligence.ontology_service import validate_label_ids


DEFAULT_BOUNDARIES = {
    AgentType.STRATEGIST: AgentCapabilityBoundary(
        agent_type=AgentType.STRATEGIST,
        can_scrape=False,
        can_execute_browser_actions=False,
        can_write_memory_directly=False,
        can_modify_routing=False,
        can_alter_embeddings=False,
    ),
    AgentType.BROWSER_COGNITION: AgentCapabilityBoundary(
        agent_type=AgentType.BROWSER_COGNITION,
        can_scrape=False,
        can_execute_browser_actions=False,
        can_write_memory_directly=False,
        can_modify_routing=False,
        can_alter_embeddings=False,
    ),
}


def aggregate_confidence(
    evidence: List[ConfidenceEvidence],
    policy: ConfidenceCalibrationPolicy = None,
) -> ConfidenceAggregation:
    policy = policy or ConfidenceCalibrationPolicy()
    if not evidence:
        return ConfidenceAggregation(policy_id=policy.policy_id, score=0.0, derivation="no confidence evidence")

    weighted_total = 0.0
    total_weight = 0.0
    for item in evidence:
        policy_weight = policy.source_weights.get(item.source, policy.source_weights.get(item.source.value, 1.0))
        weight = item.weight * policy_weight
        weighted_total += item.score * weight
        total_weight += weight

    score = max(0.0, min(1.0, weighted_total / total_weight if total_weight else 0.0))
    if score >= policy.high_confidence_threshold and len(evidence) < policy.minimum_sources_for_high_confidence:
        score = policy.high_confidence_threshold - 0.01
    return ConfidenceAggregation(
        policy_id=policy.policy_id,
        score=round(score, 4),
        evidence=evidence,
        derivation=f"weighted_average:{len(evidence)} sources",
    )


def temporal_weight(kind: str, age_days: float, policy: TemporalWeightPolicy = None) -> float:
    policy = policy or TemporalWeightPolicy()
    half_life = {
        "trend": policy.trend_half_life_days,
        "creator_identity": policy.identity_half_life_days,
        "audience": policy.audience_half_life_days,
    }.get(kind, policy.audience_half_life_days)
    return max(0.0, min(1.0, math.pow(0.5, max(age_days, 0.0) / half_life)))


def evaluate_worker_pressure(
    snapshot: WorkerPressureSnapshot,
    policy: ThermalProtectionPolicy = None,
) -> ResourceAwareScheduling:
    policy = policy or ThermalProtectionPolicy()
    vram_ratio = 0.0
    if snapshot.vram_used_gb is not None and snapshot.vram_total_gb:
        vram_ratio = snapshot.vram_used_gb / snapshot.vram_total_gb

    if snapshot.thermal_state in policy.hot_states:
        return ResourceAwareScheduling(eligible=False, reason=f"thermal_state:{snapshot.thermal_state}", recommended_priority_ceiling="low")
    if snapshot.gpu_pressure >= policy.max_gpu_pressure:
        return ResourceAwareScheduling(eligible=False, reason="gpu_pressure_high", recommended_priority_ceiling="low")
    if vram_ratio >= policy.max_vram_ratio:
        return ResourceAwareScheduling(eligible=False, reason="vram_pressure_high", recommended_priority_ceiling="low")
    if snapshot.inference_load > 0.8 or snapshot.queue_congestion > 0.8:
        return ResourceAwareScheduling(eligible=True, reason="congested", recommended_priority_ceiling="normal")
    return ResourceAwareScheduling(eligible=True, reason="nominal", recommended_priority_ceiling="high")


def resolve_semantic_consensus(subject_ref: SourceReference, interpretations: List[Dict]) -> SemanticConsensus:
    label_sets: List[Set[str]] = []
    for item in interpretations:
        label_sets.append(set(item.get("labels", [])))

    if not label_sets:
        return SemanticConsensus(subject_ref=subject_ref, agreement_score=0.0, resolution="no_interpretations")

    common = set.intersection(*label_sets) if label_sets else set()
    union = set.union(*label_sets) if label_sets else set()
    score = len(common) / len(union) if union else 0.0
    disagreements = []
    valid_labels, missing_labels = validate_label_ids(sorted(union))
    if not valid_labels:
        disagreements.append(
            model_to_dict(
                InterpretationDisagreement(
                    subject_ref=subject_ref,
                    interpretations=interpretations,
                    conflict_labels=missing_labels,
                    severity="high",
                    requires_human_review=True,
                )
            )
        )
    if score < 0.6:
        disagreements.append(
            model_to_dict(
                InterpretationDisagreement(
                    subject_ref=subject_ref,
                    interpretations=interpretations,
                    conflict_labels=sorted(union - common),
                    severity="high" if score < 0.35 else "medium",
                    requires_human_review=score < 0.6,
                )
            )
        )

    return SemanticConsensus(
        subject_ref=subject_ref,
        agreed_labels=[
            OntologyLabelRef(label_id=label_id, confidence=score)
            for label_id in sorted(common)
        ],
        disagreements=disagreements,
        agreement_score=round(score, 4),
        resolution="accepted" if score >= 0.6 and valid_labels else "needs_review",
    )


def agreement_score(subject_ref: SourceReference, interpretations: List[Dict]) -> MultiModelAgreementScore:
    consensus = resolve_semantic_consensus(subject_ref, interpretations)
    label_sets = [set(item.get("labels", [])) for item in interpretations]
    union = set.union(*label_sets) if label_sets else set()
    overlap = consensus.agreement_score if union else 0.0
    return MultiModelAgreementScore(subject_ref=subject_ref, score=overlap, model_count=len(interpretations), label_overlap=overlap)


def check_agent_permission(agent_type: AgentType, requested_action: str) -> PermissionScopedExecution:
    boundary = DEFAULT_BOUNDARIES.get(agent_type, AgentCapabilityBoundary(agent_type=agent_type))
    denied = {
        "scrape": not boundary.can_scrape,
        "browser_action": not boundary.can_execute_browser_actions,
        "write_memory": not boundary.can_write_memory_directly,
        "modify_routing": not boundary.can_modify_routing,
        "alter_embeddings": not boundary.can_alter_embeddings,
    }
    if denied.get(requested_action, False):
        return PermissionScopedExecution(agent_type=agent_type, requested_action=requested_action, allowed=False, reason="capability_boundary_denied")
    return PermissionScopedExecution(agent_type=agent_type, requested_action=requested_action, allowed=True, reason="allowed")


def restricted_context(agent_type: AgentType) -> RestrictedToolContext:
    if agent_type == AgentType.STRATEGIST:
        return RestrictedToolContext(agent_type=agent_type, allowed_tools=["semantic_search", "strategy_synthesis"], denied_tools=["browser", "memory_write", "shell"])
    if agent_type == AgentType.BROWSER_COGNITION:
        return RestrictedToolContext(agent_type=agent_type, allowed_tools=["state_classification"], denied_tools=["browser_execute", "routing", "embedding_write", "shell"])
    return RestrictedToolContext(agent_type=agent_type, allowed_tools=["read_context"], denied_tools=["shell"])


def check_synthesis_boundary(
    visited_refs: Iterable[str],
    new_ref: str,
    depth: int,
    hop_count: int,
    policy: ReasoningDepthPolicy = None,
) -> SynthesisBoundary:
    policy = policy or ReasoningDepthPolicy()
    if new_ref in set(visited_refs):
        return SynthesisBoundary(allowed=False, reason="recursive_ref_detected", depth=depth, hop_count=hop_count)
    if depth > policy.max_reasoning_depth:
        return SynthesisBoundary(allowed=False, reason="max_reasoning_depth_exceeded", depth=depth, hop_count=hop_count)
    if hop_count > policy.max_synthesis_hops:
        return SynthesisBoundary(allowed=False, reason="max_synthesis_hops_exceeded", depth=depth, hop_count=hop_count)
    return SynthesisBoundary(allowed=True, reason="within_boundary", depth=depth, hop_count=hop_count)


def feedback_reinforcement_hint(event: HumanFeedbackEvent) -> Dict:
    multiplier = 1.0
    if event.feedback_type.value in {"confirm_recommendation", "label_resonance"}:
        multiplier = 1.15
    elif event.feedback_type.value in {"reject_interpretation", "performance_mismatch"}:
        multiplier = 0.75
    if event.rating is not None:
        multiplier += event.rating * 0.1
    return {"target_ref": model_to_dict(event.target_ref), "confidence_multiplier": round(max(0.1, multiplier), 4)}
