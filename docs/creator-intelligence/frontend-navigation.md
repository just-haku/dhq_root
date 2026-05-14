# Frontend Navigation

## Route

Add `/creator-intelligence` to the authenticated DHQ dashboard.

## Dashboard Modules

- Creator Dashboard: creator summary, recent jobs, top signals.
- Video Explorer: content inventory, analysis packet viewer, source refs.
- Competitor Intelligence: tracked competitors, comparison jobs, deltas.
- Trend Radar: trend namespaces, movement, alerts.
- Draft Critic: high-priority draft critique submission and results.
- AI Chat with Gemma: typed analysis/chat actions routed through backend validation.
- Strategy Planner: strategy outputs with model route and evidence.
- Audience Psychology: emotion and audience-response estimates.
- Embedding Maps: namespace search and cluster previews.
- Hook Explorer: hook taxonomy, similarity, and performance notes.
- Memory Graph: memory records with confidence, decay, and sources.
- Worker Management: registered workers, capabilities, heartbeat, load.
- Queue Monitor: queue lengths, job status, retries, cancellations.
- Local Model Manager: GGUF scan jobs, hash validation, runtime health.

## UX Rules

- Use toggles and checkboxes for analysis modes.
- Show confidence, warnings, and evidence next to AI outputs.
- Show worker and queue state live where possible.
- Do not expose command execution controls.
- Browser actions require explicit typed tasks and permission checks.
