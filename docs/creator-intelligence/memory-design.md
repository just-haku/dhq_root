# Memory Design

## Memory Types

- Creator memory
- Trend memory
- Competitor memory
- Strategist memory
- Predictor memory

## Record Shape

Memory records include:

- `memory_id`
- `memory_type`
- `namespace`
- `subject_id`
- `statement`
- `confidence`
- `source_refs`
- `evidence`
- `created_at`
- `last_seen_at`
- `decay_rate`
- `expires_at`
- `validation_status`

## Write Path

1. Analysis or strategy creates a `MemoryCandidate`.
2. Sanitizer marks untrusted source spans.
3. Memory validator checks provenance, confidence, deduplication, and poisoning risk.
4. Accepted records are stored in MongoDB.
5. Optional embeddings are written to Qdrant with matching namespace payloads.

## Poisoning Controls

- Scraped captions/comments/OCR never become instructions.
- Memory candidates must cite source references.
- Low-confidence or single-source claims stay pending.
- Strategic recommendations cannot silently rewrite facts.
- Decay reduces stale claims unless refreshed by new evidence.

## Retrieval

Memory retrieval returns facts with source references, confidence, age, and trust state. Prompt builders must render memory as quoted context, not as system instructions.
