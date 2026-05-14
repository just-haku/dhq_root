from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


class QdrantVectorStore:
    def __init__(self, base_url: Optional[str] = None, collection: Optional[str] = None):
        self.base_url = (base_url or settings.CI_QDRANT_URL).rstrip("/")
        self.collection = collection or settings.CI_QDRANT_COLLECTION

    async def health(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/")
            return {"healthy": response.status_code < 500, "status_code": response.status_code}
        except Exception as exc:
            return {"healthy": False, "error": str(exc)}

    async def ensure_collection(self, vector_size: int, distance: str = "Cosine") -> Dict[str, Any]:
        payload = {"vectors": {"size": vector_size, "distance": distance}}
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.put(f"{self.base_url}/collections/{self.collection}", json=payload)
        return {"status_code": response.status_code, "body": _safe_json(response)}

    async def upsert_vector(self, point_id: str, vector: List[float], namespace: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        point_payload = {"namespace": namespace, **(payload or {})}
        body = {"points": [{"id": point_id, "vector": vector, "payload": point_payload}]}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(f"{self.base_url}/collections/{self.collection}/points", json=body)
        return {"status_code": response.status_code, "body": _safe_json(response)}

    async def search(self, vector: List[float], namespace: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        body: Dict[str, Any] = {"vector": vector, "limit": limit, "with_payload": True}
        if namespace:
            body["filter"] = {"must": [{"key": "namespace", "match": {"value": namespace}}]}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}/collections/{self.collection}/points/search", json=body)
        return {"status_code": response.status_code, "body": _safe_json(response)}


def namespace_for(kind: str, name: str) -> str:
    cleaned = (name or "unknown").strip().replace(" ", "_").lower()
    return f"{kind}:{cleaned}"


def _safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except Exception:
        return response.text


vector_store = QdrantVectorStore()
