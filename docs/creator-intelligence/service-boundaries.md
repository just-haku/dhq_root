# Service Boundaries

## Backend Package Boundary

Creator Intelligence lives under `backend/app/services/creator_intelligence/` and uses a dedicated API router. Existing DHQ modules may call the service layer through typed functions, but they should not import worker internals.

## Modules

- `schemas.py`: Pydantic contracts shared by APIs, queue manager, worker daemon, and tests.
- `queue_manager.py`: Redis Streams job lifecycle.
- `worker_registry.py`: worker registration, heartbeat, capability matching.
- `model_manager.py`: GGUF scan result validation, model registry records, runtime health shape.
- `vector_store.py`: Qdrant adapter and namespace helpers.
- `memory_service.py`: memory candidate validation, decay, and retrieval.
- `security.py`: sanitization, URL/path guards, prompt-boundary helpers.
- `api_helpers.py`: response conversion and shared API validation.

## Data Ownership

- MongoDB owns durable records: creators, content items, jobs, workers, analysis packets, memories, models, agents.
- Redis owns volatile and replayable processing state: streams, consumer groups, cancellation flags, heartbeat cache, worker event logs.
- Qdrant owns embedding vectors and payload-filtered similarity search.
- Local workers own local browser sessions, local model runtimes, and temporary artifacts until uploaded or reported.

## Interface Rule

Every cross-boundary call uses a schema. Raw dictionaries are accepted only at API/queue edges and must be validated immediately.

## Security Boundary

Scraped captions, comments, OCR text, filenames, URLs, and model outputs are untrusted. They can be stored as observations, but cannot become prompt instructions, memory records, shell arguments, or browser actions without validation.
