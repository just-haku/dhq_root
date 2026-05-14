import hashlib
import os
from typing import Dict, Iterable, List, Optional

from app.core.config import settings
from app.models.creator_intelligence import CIModelRegistryEntry
from app.services.creator_intelligence.security import normalize_allowed_path, split_model_roots


def default_model_roots() -> List[str]:
    return split_model_roots(settings.CI_MODEL_SCAN_ROOTS)


def compute_file_hashes(path: str) -> Dict[str, str]:
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            sha256.update(chunk)
            md5.update(chunk)
    return {"sha256": sha256.hexdigest(), "md5": md5.hexdigest()}


def scan_gguf_models(roots: Optional[Iterable[str]] = None, validate_hashes: bool = False) -> Dict:
    allowed_roots = list(roots or default_model_roots())
    models: List[Dict] = []
    warnings: List[str] = []

    for root in allowed_roots:
        try:
            safe_root = normalize_allowed_path(root, allowed_roots)
        except ValueError as exc:
            warnings.append(f"{root}: {exc}")
            continue

        if not os.path.exists(safe_root):
            warnings.append(f"{safe_root}: missing")
            continue

        for current_root, _, files in os.walk(safe_root):
            for filename in files:
                if not filename.lower().endswith(".gguf"):
                    continue
                path = os.path.join(current_root, filename)
                item = {
                    "model_name": filename,
                    "model_type": "gguf",
                    "path": path,
                    "size_bytes": os.path.getsize(path),
                    "validation_status": "detected",
                }
                if validate_hashes:
                    try:
                        item.update(compute_file_hashes(path))
                        item["validation_status"] = "validated"
                    except Exception as exc:
                        item["validation_status"] = "error"
                        item["error"] = str(exc)
                models.append(item)

    return {"root_paths": allowed_roots, "models": models, "warnings": warnings}


def upsert_model_registry(worker_id: str, models: List[Dict]) -> List[Dict]:
    saved = []
    for model in models:
        entry = CIModelRegistryEntry.objects(worker_id=worker_id, path=model["path"]).first()
        if not entry:
            entry = CIModelRegistryEntry(worker_id=worker_id, path=model["path"], model_name=model["model_name"])
        entry.model_name = model.get("model_name") or os.path.basename(model["path"])
        entry.model_type = model.get("model_type", "gguf")
        entry.sha256 = model.get("sha256")
        entry.md5 = model.get("md5")
        entry.size_bytes = model.get("size_bytes")
        entry.validation_status = model.get("validation_status", "detected")
        entry.save()
        saved.append(entry.to_dict())
    return saved
