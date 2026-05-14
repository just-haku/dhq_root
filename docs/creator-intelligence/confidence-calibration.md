# Confidence Calibration

## Purpose

Confidence must be reproducible and explainable. Scores are not generic vibes; they are derived from explicit sources.

## Confidence Sources

- `heuristic`: deterministic rule or metric threshold.
- `model_derived`: single model output with model fingerprint.
- `ensemble_derived`: agreement across multiple models or passes.
- `human_confirmed`: user confirmation or correction.
- `experimentally_reinforced`: linked performance or experiment outcome.

## Aggregation

`ConfidenceAggregation` stores the component sources, weights, resulting score, and policy id. Human-confirmed and experimentally reinforced sources can increase durability, but cannot bypass provenance requirements.

## Use

- Memory gateway stores confidence derivation next to records.
- Strategy lineage exposes confidence evidence.
- Frontend shows confidence source badges and score derivation.
