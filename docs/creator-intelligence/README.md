# DHQ Creator Intelligence

Creator Intelligence is a distributed, typed subsystem for short-form creator research. It is designed as DHQ infrastructure, not as a monolithic autonomous agent.

## Document Map

- [Architecture](architecture.md): control plane, workers, storage, and model responsibilities.
- [Service Boundaries](service-boundaries.md): backend modules and ownership rules.
- [Queue Design](queue-design.md): Redis Streams queue contract, retries, priorities, and cancellation.
- [Worker Protocol](worker-protocol.md): registration, heartbeat, jobs, progress, and result envelopes.
- [Memory Design](memory-design.md): memory records, decay, provenance, and poisoning controls.
- [API Contracts](api-contracts.md): backend REST and WebSocket interfaces.
- [Frontend Navigation](frontend-navigation.md): Vue route and dashboard modules.
- [Security Audit](security-audit.md): current DHQ risks and remediation plan.
- [Execution Phases](execution-phases.md): phased implementation and acceptance gates.
- [Ontology Design](ontology-design.md): canonical labels for stable interpretation.
- [Confidence Calibration](confidence-calibration.md): reproducible confidence derivation.
- [Semantic Consensus](semantic-consensus.md): model disagreement handling.
- [Resource Pressure](resource-pressure-management.md): inference node protection.
- [Cancellation Flows](cancellation-flows.md): interruption and priority preemption.
- [Provenance Graphs](provenance-graphs.md): traceable conclusion ancestry.
- [Cognitive State](cognitive-state-lifecycle.md): creator evolution snapshots.
- [Reinforcement Boundaries](reinforcement-boundaries.md): human feedback without memory bypass.
- [Anti-Recursion Strategy](anti-recursion-strategy.md): synthesis depth and loop guards.

## Design Commitments

- Typed job envelopes and typed outputs only.
- Redis Streams for distributed queue state.
- Qdrant for vector search and embedding namespaces.
- Gemma local inference as perception, not strategy authority.
- Human-supervised browser cognition for scraping.
- Sanitized boundaries between scraped text, prompts, memory, and strategy.
- Logs, confidence scores, evidence, and source references on every major output.
