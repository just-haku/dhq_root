# Worker Protocol

## Registration

Workers connect to `/api/creator-intelligence/workers/ws` and send `WorkerRegistration`.

Required fields:

- `worker_id`
- `worker_name`
- `machine_role`
- `host_fingerprint`
- `capabilities`
- `version`
- `auth_token`

The backend validates the token, stores capability metadata, and returns typed acceptance or rejection.

## Heartbeat

Workers send `WorkerHeartbeat` every 15 seconds. Heartbeats include load, current job IDs, model runtime state, disk hints, and error summaries.

Workers are stale after 45 seconds without heartbeat and offline after 90 seconds.

## Capabilities

Capabilities are explicit booleans or numeric traits:

- `gpu`
- `multimodal`
- `ocr`
- `embeddings`
- `playwright`
- `browser_cognition`
- `gguf_runtime`
- `vram_gb`
- `embedding_speed`
- `supported_platforms`

## Job Execution

The dashboard never sends shell commands. It creates typed jobs only. Workers execute allowlisted handlers keyed by `job_type`.

## Result Validation

Every `JobResult` includes:

- `job_id`
- `status`
- `output`
- `confidence`
- `evidence`
- `warnings`
- `artifacts`
- `started_at`
- `completed_at`

Backend rejects results that fail schema validation or attempt to write memory directly.
