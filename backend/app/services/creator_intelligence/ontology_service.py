import os
from functools import lru_cache
from typing import Dict, List, Tuple

from app.services.creator_intelligence.schemas import OntologyLabel, OntologyRegistry, model_to_dict


ONTOLOGY_DIR = os.path.join(os.path.dirname(__file__), "ontology")


def _parse_registry_file(path: str) -> OntologyRegistry:
    version = "1.0"
    domain = os.path.splitext(os.path.basename(path))[0]
    labels: List[Dict[str, str]] = []
    current = None

    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("version:"):
                version = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("domain:"):
                domain = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("- id:"):
                if current:
                    labels.append(current)
                current = {"id": stripped.split(":", 1)[1].strip()}
            elif current is not None and ":" in stripped:
                key, value = stripped.split(":", 1)
                current[key.strip()] = value.strip()

    if current:
        labels.append(current)

    return OntologyRegistry(
        version=version,
        domain=domain,
        labels=[
            OntologyLabel(
                id=item.get("id", ""),
                name=item.get("name", item.get("id", "")),
                description=item.get("description", ""),
                domain=domain,
                version=version,
            )
            for item in labels
            if item.get("id")
        ],
    )


@lru_cache(maxsize=1)
def load_registries() -> Dict[str, OntologyRegistry]:
    registries: Dict[str, OntologyRegistry] = {}
    if not os.path.isdir(ONTOLOGY_DIR):
        return registries

    for filename in sorted(os.listdir(ONTOLOGY_DIR)):
        if not filename.endswith((".yaml", ".yml")):
            continue
        registry = _parse_registry_file(os.path.join(ONTOLOGY_DIR, filename))
        registries[registry.domain] = registry
    return registries


def list_registries() -> Dict[str, Dict]:
    return {
        domain: {
            "version": registry.version,
            "domain": registry.domain,
            "label_count": len(registry.labels),
            "labels": [model_to_dict(label) for label in registry.labels],
        }
        for domain, registry in load_registries().items()
    }


def label_index() -> Dict[str, OntologyLabel]:
    index: Dict[str, OntologyLabel] = {}
    for registry in load_registries().values():
        for label in registry.labels:
            index[label.id] = label
    return index


def validate_label_ids(label_ids: List[str]) -> Tuple[bool, List[str]]:
    index = label_index()
    missing = [label_id for label_id in label_ids if label_id not in index]
    return len(missing) == 0, missing
