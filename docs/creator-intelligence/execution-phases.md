# Execution Phases

## Phase 0: Documentation and Contracts

- Architecture docs.
- Service boundaries.
- Queue design.
- Worker protocol.
- Memory design.
- API contracts.
- Frontend navigation plan.
- Security audit.

Acceptance: implementer can build without choosing core architecture.

## Phase 1: Core Infrastructure

- MongoEngine models.
- Pydantic schemas.
- Redis Streams queue manager.
- Worker registration and heartbeat.
- WebSocket worker endpoint.
- Qdrant adapter.
- Model registry.
- Worker dashboard and queue monitor.

Acceptance: a fake worker can register, heartbeat, receive a typed job, emit progress, and return a typed result.

## Phase 2: Scraper Foundation

- Supervised Playwright job handlers.
- TikTok/Instagram scrape schemas.
- Browser cognition packet.
- Captcha/suspicious-state pause flow.
- Scrape artifact storage and observability.

Acceptance: scraper worker can perform a supervised metadata scrape and pause safely on uncertain states.

## Phase 3: Gemma Multimodal Analysis

- GGUF discovery and hash validation.
- Runtime health verification.
- Frame sampling.
- OCR timeline.
- Hook, pacing, shot boundary, emotion, novelty, and fatigue packets.

Acceptance: inference worker can process a sampled video artifact and return validated analysis packets.

## Phase 4: Embeddings, Memory, Strategy

- Embedding generation.
- Qdrant writes and search.
- Memory validation and decay.
- Creator identity tracking.
- Trend clustering and competitor comparison.
- Cost-aware strategist routing.

Acceptance: system can compare content semantically and create validated memory records.

## Phase 5: Polish and Explainability

- Full frontend dashboard modules.
- Confidence and evidence UI.
- Model manager UX.
- Report exports.
- Observability and operational tuning.

Acceptance: creator workflows are usable from the dashboard with visible worker/queue/model state.
