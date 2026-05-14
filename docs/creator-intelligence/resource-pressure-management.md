# Resource Pressure Management

## Purpose

Workers, especially the GTX 1650 Ti inference node, must expose pressure so the scheduler can avoid overheating, VRAM exhaustion, and runaway inference queues.

## Snapshot

Workers report `WorkerPressureSnapshot` in heartbeat load:

- CPU pressure
- GPU pressure
- VRAM used/total
- thermal state
- queue congestion
- inference load

## Policies

- Thermal protection pauses non-urgent inference when state is `hot`.
- Resource-aware scheduling avoids assigning multimodal jobs to overloaded workers.
- Inference backpressure keeps low-priority competitor batches from blocking urgent draft critique.
