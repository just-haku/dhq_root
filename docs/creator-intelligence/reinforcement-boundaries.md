# Human Feedback Reinforcement Boundaries

## Purpose

Human feedback is high-value signal, but it is not raw authority to overwrite the system. It updates weights, corrections, ontology candidates, and strategy rankings through typed events.

## Accepted Feedback

- Recommendation quality confirmation.
- Interpretation rejection.
- Emotional resonance labels.
- Actual performance mismatch.
- Manual semantic override.

## Boundaries

- Feedback creates `HumanFeedbackEvent` records.
- Manual overrides remain source-referenced and scoped.
- Feedback can influence memory weighting and ontology candidates.
- Feedback cannot directly write persistent creator memory without the memory gateway.
- Feedback cannot grant agents new capabilities.
