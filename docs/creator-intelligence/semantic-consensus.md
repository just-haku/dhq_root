# Semantic Consensus

## Purpose

When Gemma and cloud models disagree, the system stores disagreement explicitly instead of polluting memory with whichever phrasing arrived last.

## Flow

1. Interpretive packets provide ontology labels and confidence derivations.
2. Consensus compares labels, evidence overlap, model fingerprints, and provenance.
3. Agreement strengthens confidence.
4. Disagreement creates `InterpretationDisagreement`.
5. High-impact disagreements are quarantined or sent for human feedback.

## Conflict Resolution

The resolver prefers:

- observable evidence over interpretation;
- human-confirmed feedback over single model claims;
- ontology labels over freeform text;
- recent trend signals only when temporal policy says they should dominate.
