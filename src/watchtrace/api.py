from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException


def create_watchtrace_router(output_dir: str = ".watchtrace") -> APIRouter:
    router = APIRouter()
    watchtrace_dir = Path(output_dir)

    @router.get("/requests")
    async def list_requests():
        if not watchtrace_dir.exists():
            return {"requests": []}

        results = []

        for request_dir in sorted(
            [p for p in watchtrace_dir.iterdir() if p.is_dir()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        ):
            memory_file = request_dir / "memory.json"

            entry = {
                "request_id": request_dir.name,
                "created_at": request_dir.stat().st_mtime,
                "method": None,
                "path": None,
                "duration_ms": None,
            }

            if memory_file.exists():
                data = json.loads(memory_file.read_text(encoding="utf-8"))
                meta = data.get("meta", {})
                entry["method"] = meta.get("method")
                entry["path"] = meta.get("path")
                entry["duration_ms"] = meta.get("duration_ms")

            results.append(entry)

        return {"requests": results}

    @router.get("/requests/latest/graph")
    async def latest_graph():
        if not watchtrace_dir.exists():
            raise HTTPException(status_code=404, detail="No WatchTrace artifacts found")

        request_dirs = sorted(
            [p for p in watchtrace_dir.iterdir() if p.is_dir()],
            reverse=True,
        )

        for request_dir in request_dirs:
            graph_file = request_dir / "request_graph.json"
            if graph_file.exists():
                return json.loads(graph_file.read_text(encoding="utf-8"))

        raise HTTPException(status_code=404, detail="No completed request_graph.json found")

    @router.get("/requests/{request_id}/graph")
    async def request_graph(request_id: str):
        graph_file = watchtrace_dir / request_id / "request_graph.json"

        if not graph_file.exists():
            raise HTTPException(status_code=404, detail="request_graph.json not found")

        return json.loads(graph_file.read_text(encoding="utf-8"))

    return router