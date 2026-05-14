# Ontology Design

## Purpose

Creator Intelligence uses canonical ontology labels for interpretive reasoning so memory, embeddings, clustering, and recommendations do not drift into incompatible freeform language over time.

## Registries

Canonical registries live in `backend/app/services/creator_intelligence/ontology/`:

- `emotions.yaml`
- `hook_taxonomy.yaml`
- `visual_styles.yaml`
- `pacing_labels.yaml`
- `creator_archetypes.yaml`
- `audience_states.yaml`
- `content_goals.yaml`

## Rules

- Interpretive packets reference ontology ids such as `emotion:quiet_ambition` or `hook:open_loop_question`.
- Observable packets remain raw measurements and do not require ontology labels.
- Unknown labels are stored as candidates, not accepted memory.
- Human feedback can propose ontology refinements, but does not mutate registries automatically.
- Embedding payloads include ontology version and label ids for reindexing.

## Versioning

Each registry has `version`, `domain`, and `labels`. Label ids are stable. Names and descriptions may change, but ids must not be repurposed.
