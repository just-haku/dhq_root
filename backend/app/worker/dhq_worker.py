import argparse
import asyncio
import hashlib
import json
import os
import platform
import socket
from datetime import datetime
from typing import Any, Dict

import websockets

from app.services.creator_intelligence.model_manager import scan_gguf_models
from app.services.creator_intelligence.schemas import (
    JobResult,
    ResultStatus,
    WorkerCapability,
    WorkerHeartbeat,
    WorkerRegistration,
    model_to_dict,
)


DEFAULT_VERSION = "0.1.0"


def stable_host_fingerprint() -> str:
    raw = f"{platform.node()}:{platform.platform()}:{socket.gethostname()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def make_capabilities(args) -> WorkerCapability:
    platforms = []
    if args.tiktok:
        platforms.append("tiktok")
    if args.instagram:
        platforms.append("instagram")

    return WorkerCapability(
        gpu=args.gpu,
        multimodal=args.multimodal,
        ocr=args.ocr,
        embeddings=args.embeddings,
        playwright=args.playwright,
        browser_cognition=args.browser_cognition,
        gguf_runtime=args.gguf_runtime,
        vram_gb=args.vram_gb,
        embedding_speed=args.embedding_speed,
        supported_platforms=platforms,
    )


async def send_json(ws, message: Dict[str, Any]):
    await ws.send(json.dumps(message, default=str))


async def heartbeat_loop(ws, worker_id: str):
    while True:
        heartbeat = WorkerHeartbeat(
            worker_id=worker_id,
            load={
                "pid": os.getpid(),
                "hostname": socket.gethostname(),
            },
            current_jobs=[],
        )
        await send_json(ws, {"message_type": "heartbeat", "payload": model_to_dict(heartbeat)})
        await asyncio.sleep(15)


async def execute_job(job: Dict[str, Any], args) -> JobResult:
    job_id = job["job_id"]
    job_type = job["job_type"]
    started_at = datetime.utcnow()

    if job_type == "model_scan":
        payload = job.get("payload") or {}
        roots = payload.get("roots") or args.model_roots
        validate_hashes = bool(payload.get("validate_hashes", args.validate_hashes))
        scan = scan_gguf_models(roots=roots, validate_hashes=validate_hashes)
        return JobResult(
            job_id=job_id,
            worker_id=args.worker_id,
            status=ResultStatus.COMPLETED,
            output={"model_scan": scan},
            confidence=1.0,
            warnings=scan.get("warnings", []),
            started_at=started_at,
        )

    if job_type == "model_health_check":
        payload = job.get("payload") or {}
        model_path = payload.get("model_path")
        exists = bool(model_path and os.path.exists(model_path))
        return JobResult(
            job_id=job_id,
            worker_id=args.worker_id,
            status=ResultStatus.COMPLETED if exists else ResultStatus.FAILED,
            output={"healthy": exists, "model_path": model_path},
            confidence=1.0 if exists else 0.0,
            warnings=[] if exists else ["model_path_missing"],
            error=None if exists else "model_path_missing",
            started_at=started_at,
        )

    supervised_placeholders = {
        "scrape_profile",
        "scrape_content_batch",
        "sample_frames",
        "ocr_timeline",
        "analyze_video",
        "embed_content",
        "update_memory",
        "compare_competitor",
        "draft_critique",
        "trend_scan",
        "strategic_synthesis",
    }
    if job_type in supervised_placeholders:
        return JobResult(
            job_id=job_id,
            worker_id=args.worker_id,
            status=ResultStatus.PAUSED,
            output={
                "requires_phase": "future_handler",
                "job_type": job_type,
                "safe_to_continue": False,
            },
            confidence=0.0,
            warnings=["typed_handler_not_enabled_yet"],
            error="typed handler scaffold exists but execution is intentionally paused",
            started_at=started_at,
        )

    return JobResult(
        job_id=job_id,
        worker_id=args.worker_id,
        status=ResultStatus.FAILED,
        output={},
        confidence=0.0,
        warnings=["unknown_job_type"],
        error=f"unknown job_type: {job_type}",
        started_at=started_at,
    )


async def worker_loop(args):
    capabilities = make_capabilities(args)
    async with websockets.connect(args.server) as ws:
        registration = WorkerRegistration(
            worker_id=args.worker_id,
            worker_name=args.name,
            machine_role=args.role,
            host_fingerprint=stable_host_fingerprint(),
            capabilities=capabilities,
            version=DEFAULT_VERSION,
            auth_token=args.token,
        )
        await send_json(ws, {"message_type": "register", "payload": model_to_dict(registration)})

        heartbeat_task = None
        try:
            while True:
                raw = await ws.recv()
                message = json.loads(raw)
                message_type = message.get("message_type")

                if message_type == "registered":
                    heartbeat_task = asyncio.create_task(heartbeat_loop(ws, args.worker_id))
                    await send_json(ws, {"message_type": "claim_request"})

                elif message_type == "heartbeat_ack":
                    continue

                elif message_type == "no_job":
                    await asyncio.sleep(args.poll_interval)
                    await send_json(ws, {"message_type": "claim_request"})

                elif message_type == "job_available":
                    job = message["job"]
                    await send_json(
                        ws,
                        {
                            "message_type": "progress",
                            "payload": {
                                "job_id": job["job_id"],
                                "worker_id": args.worker_id,
                                "progress": 0.05,
                                "message": "typed job accepted",
                            },
                        },
                    )
                    result = await execute_job(job, args)
                    await send_json(ws, {"message_type": "result", "payload": model_to_dict(result)})
                    await send_json(ws, {"message_type": "claim_request"})

                elif message_type == "error":
                    raise RuntimeError(message.get("error", "worker socket error"))
        finally:
            if heartbeat_task:
                heartbeat_task.cancel()


def parse_args():
    parser = argparse.ArgumentParser(description="DHQ Creator Intelligence worker daemon")
    parser.add_argument("--server", default="ws://localhost:8000/api/creator-intelligence/workers/ws")
    parser.add_argument("--token", default=os.environ.get("DHQ_WORKER_TOKEN", ""))
    parser.add_argument("--worker-id", default=os.environ.get("DHQ_WORKER_ID", socket.gethostname()))
    parser.add_argument("--name", default=os.environ.get("DHQ_WORKER_NAME", socket.gethostname()))
    parser.add_argument("--role", default=os.environ.get("DHQ_WORKER_ROLE", "generic"))
    parser.add_argument("--model-root", action="append", dest="model_roots", default=[])
    parser.add_argument("--validate-hashes", action="store_true")
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--gpu", action="store_true")
    parser.add_argument("--multimodal", action="store_true")
    parser.add_argument("--ocr", action="store_true")
    parser.add_argument("--embeddings", action="store_true")
    parser.add_argument("--playwright", action="store_true")
    parser.add_argument("--browser-cognition", action="store_true")
    parser.add_argument("--gguf-runtime", action="store_true")
    parser.add_argument("--vram-gb", type=float)
    parser.add_argument("--embedding-speed", default=None)
    parser.add_argument("--tiktok", action="store_true")
    parser.add_argument("--instagram", action="store_true")
    args = parser.parse_args()
    if not args.token:
        raise SystemExit("DHQ worker token is required via --token or DHQ_WORKER_TOKEN")
    return args


def main():
    args = parse_args()
    asyncio.run(worker_loop(args))


if __name__ == "__main__":
    main()
