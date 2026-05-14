# Anti-Recursion Strategy

## Purpose

Prevent analysis-of-analysis loops, recursive synthesis, and hidden autonomy.

## Controls

- `ReasoningDepthPolicy` defines max depth and synthesis hop limits.
- `RecursiveAnalysisGuard` detects repeated source ids and packet ids.
- `SynthesisBoundary` blocks raw outputs from being recursively reinterpreted without new evidence.
- Strategy agents can summarize prior conclusions but cannot recursively generate new memory from their own summaries.

## Defaults

- Max reasoning depth: 3.
- Max synthesis hops: 4.
- Analysis-of-analysis requires explicit replay job and source refs.
