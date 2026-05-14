import math
from datetime import datetime
from typing import Dict, List, Tuple

from app.models.creator_intelligence import CIMemoryRecord
from app.services.creator_intelligence.schemas import MemoryCandidate, model_to_dict
from app.services.creator_intelligence.security import sanitize_untrusted_text


ALLOWED_MEMORY_TYPES = {"creator", "trend", "competitor", "strategist", "predictor"}


def validate_memory_candidate(candidate: MemoryCandidate) -> Tuple[bool, List[str]]:
    warnings: List[str] = []
    if candidate.memory_type not in ALLOWED_MEMORY_TYPES:
        warnings.append("invalid_memory_type")
    if candidate.confidence < 0.35:
        warnings.append("confidence_too_low")
    if not candidate.source_refs:
        warnings.append("missing_source_refs")
    if len(candidate.statement.strip()) < 8:
        warnings.append("statement_too_short")
    return not warnings, warnings


def create_memory_from_candidate(candidate: MemoryCandidate) -> Dict:
    accepted, warnings = validate_memory_candidate(candidate)
    statement, sanitize_warnings = sanitize_untrusted_text(candidate.statement, max_length=4000)
    warnings.extend(sanitize_warnings)

    record = CIMemoryRecord(
        memory_type=candidate.memory_type,
        namespace=candidate.namespace,
        subject_id=candidate.subject_id,
        statement=statement,
        confidence=candidate.confidence,
        source_refs=[model_to_dict(ref) for ref in candidate.source_refs],
        evidence=[model_to_dict(item) for item in candidate.evidence],
        decay_rate=candidate.decay_rate,
        validation_status="accepted" if accepted else "quarantined",
        created_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow(),
    )
    record.save()
    data = record.to_dict()
    data["validation_warnings"] = warnings
    return data


def decayed_confidence(record: CIMemoryRecord, as_of: datetime = None) -> float:
    as_of = as_of or datetime.utcnow()
    age_days = max((as_of - record.last_seen_at).total_seconds() / 86400, 0)
    return max(0.0, min(1.0, record.confidence * math.exp(-record.decay_rate * age_days)))
