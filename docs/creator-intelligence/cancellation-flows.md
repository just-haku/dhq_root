# Cancellation And Preemption Flows

## Purpose

Long inference, replay, and scrape jobs need cooperative cancellation and priority preemption without corrupting artifacts.

## Flow

```mermaid
sequenceDiagram
  participant UI
  participant API
  participant Redis
  participant Worker
  UI->>API: cancel or escalate job
  API->>Redis: write cancellation/preemption token
  Worker->>Redis: poll token at checkpoints
  Worker->>API: checkpoint or cancel_ack
  API->>Redis: requeue/resume if needed
```

## Rules

- Jobs check cancellation before work and at safe checkpoints.
- Replays can resume from artifact checkpoint.
- Urgent draft critique can preempt low-priority competitor batches.
- Preempted jobs retain `ResumeCheckpoint`.
