# API Contracts

## REST API

Base prefix: `/api/creator-intelligence`

- `GET /overview`: dashboard counts, queue health, recent activity.
- `GET /workers`: registered worker list.
- `POST /workers/register-token`: OP-only scoped token creation.
- `GET /queues`: queue lengths, dead-letter counts, stale jobs.
- `POST /jobs`: enqueue a typed job.
- `GET /jobs`: list jobs by status, type, priority, and creator.
- `GET /jobs/{job_id}`: job detail and progress events.
- `POST /jobs/{job_id}/cancel`: set cancellation flag.
- `GET /models`: model registry and runtime status.
- `POST /models/scan`: enqueue local model scan on a selected worker.
- `GET /creators`: known creator profiles.
- `GET /creators/{creator_id}/content`: content inventory.
- `GET /memory`: memory search by type, namespace, subject, confidence.
- `GET /vectors/search`: embedding search by namespace and query vector reference.

## Worker WebSocket

Endpoint: `/api/creator-intelligence/workers/ws`

Message types:

- `register`
- `heartbeat`
- `claim_request`
- `progress`
- `result`
- `error`
- `cancel_ack`

## API Guarantees

- All write endpoints require DHQ auth.
- Worker management requires OP role.
- User-facing task creation requires regular authenticated user role or better.
- No endpoint accepts arbitrary shell commands.
- Job payloads are validated against job-type allowlists.
