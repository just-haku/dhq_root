# Redis Streams Queue Design

## Streams

- `ci:jobs:high`: urgent jobs such as draft critique and user-requested analysis.
- `ci:jobs:normal`: standard scraping, analysis, embedding, and memory jobs.
- `ci:jobs:low`: competitor scraping, broad trend scans, background enrichment.
- `ci:events`: progress, result, cancellation, retry, and audit events.
- `ci:dead`: jobs that exhausted retries or failed validation.

## Job Envelope

All jobs use `JobEnvelope`:

- `job_id`
- `job_type`
- `priority`
- `requested_by`
- `capability_requirements`
- `payload`
- `trace_id`
- `created_at`
- `scheduled_at`
- `max_attempts`
- `attempt`
- `timeout_seconds`
- `schema_version`

## Lifecycle

1. API validates and enqueues.
2. Worker claims from a consumer group only if capabilities match.
3. Worker sends `JobProgressEvent` records.
4. Worker completes with `JobResult`.
5. Backend validates result, stores durable state, acknowledges the stream item.
6. Failed jobs are retried with backoff until `max_attempts`, then moved to `ci:dead`.

## Cancellation

Cancellation is represented by a Redis key: `ci:cancel:{job_id}`. Workers must check the key before starting and during long-running operations.

## Offline Continuation

Streams retain pending entries. If a worker disappears, the control plane reclaims stale pending jobs after heartbeat expiry plus job timeout grace.

## Priorities

- High: draft critique, explicit user chat analysis, local model health checks.
- Normal: content analysis, embeddings, memory update.
- Low: competitor scrape, trend scan, broad enrichment.
