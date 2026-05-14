# Creator Intelligence Architecture

## Summary

Creator Intelligence extends DHQ with a control-plane backend, distributed workers, typed queues, multimodal analysis, vector search, and explainable memory. It keeps scraping, inference, embeddings, memory, and frontend concerns separate so the system can evolve safely.

## Machine Roles

- Home Server: control plane, MongoDB, Redis, Qdrant, backend APIs, scheduler, dashboard, durable state.
- ThinkPad E16 Gen 2: scraper/control worker, Playwright browser automation, TikTok/Instagram sessions, light preprocessing.
- ASUS TUF Gaming: AI inference worker, Gemma 4 E4B GGUF, OCR, embeddings, frame/video semantic parsing.

The Home Server does not run heavy multimodal inference by default. It routes jobs by capabilities and stores structured outputs.

## Core Flow

1. A user starts a typed task from the Vue dashboard or AI chat intent layer.
2. FastAPI validates permissions, normalizes inputs, and enqueues a `JobEnvelope` into Redis Streams.
3. A worker with matching capabilities claims the job.
4. The worker emits progress events and returns a typed `JobResult`.
5. Backend validates the result schema, stores Mongo records, writes embeddings to Qdrant when appropriate, and updates memory only through memory-candidate validation.
6. Frontend renders status, confidence, evidence, warnings, and source references.

## Subsystems

- Worker registry: registration tokens, capability reports, heartbeat expiry, audit logs.
- Queue manager: Redis Streams, priority lanes, retries, cancellation, dead letters.
- Scraper: supervised Playwright tasks, platform extractors, artifact storage, browser cognition packets.
- Analysis: Gemma perception packets, OCR timeline, hook/pacing/shot/emotion/fatigue signals.
- Embeddings/vector: Qdrant collections, namespace payloads, similarity search.
- Memory: creator/trend/competitor/strategist/predictor memories with confidence, decay, and provenance.
- Strategist: optional external API routing for high-level synthesis, never raw memory writes.
- Frontend: Creator Intelligence route with operational and research views.

## Non-Goals

- No black-box mega-agent.
- No uncontrolled autonomous browser.
- No automatic captcha solving.
- No shell-command execution from dashboard tasks.
- No raw LLM output written directly into memory.
