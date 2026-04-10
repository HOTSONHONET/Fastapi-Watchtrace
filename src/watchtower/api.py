from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException


def create_watchtower_router(output_dir: str = ".watchtower") -> APIRouter:
    router = APIRouter()
    watchtower_dir = Path(output_dir)

    @router.get("/requests")
    async def list_requests():
        if not watchtower_dir.exists():
            return {"requests": []}

        request_dirs = sorted(
            [p.name for p in watchtower_dir.iterdir() if p.is_dir()],
            reverse=True,
        )
        return {"requests": request_dirs}

    @router.get("/requests/latest/graph")
    async def latest_graph():
        if not watchtower_dir.exists():
            raise HTTPException(status_code=404, detail="No WatchTower artifacts found")

        request_dirs = sorted(
            [p for p in watchtower_dir.iterdir() if p.is_dir()],
            reverse=True,
        )

        for request_dir in request_dirs:
            graph_file = request_dir / "request_graph.json"
            if graph_file.exists():
                return json.loads(graph_file.read_text(encoding="utf-8"))

        raise HTTPException(status_code=404, detail="No completed request_graph.json found")

    @router.get("/requests/{request_id}/graph")
    async def request_graph(request_id: str):
        graph_file = watchtower_dir / request_id / "request_graph.json"

        if not graph_file.exists():
            raise HTTPException(status_code=404, detail="request_graph.json not found")

        return json.loads(graph_file.read_text(encoding="utf-8"))

    return router