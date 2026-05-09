from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import HTTPException

from watchtrace.api import create_watchtrace_router


def get_route_endpoint(router, path: str):
    for route in router.routes:
        if route.path == path:
            return route.endpoint
    raise AssertionError(f"Route not found: {path}")


@pytest.mark.anyio
async def test_watchtrace_router_lists_requests_and_reads_graphs(tmp_path: Path) -> None:
    first = tmp_path / "first"
    latest = tmp_path / "latest"
    first.mkdir()
    latest.mkdir()
    (first / "memory.json").write_text(
        json.dumps({"meta": {"method": "GET", "path": "/a", "duration_ms": 1}}),
        encoding="utf-8",
    )
    (latest / "request_graph.json").write_text(json.dumps({"nodes": ["latest"]}), encoding="utf-8")
    router = create_watchtrace_router(str(tmp_path))

    list_requests = get_route_endpoint(router, "/requests")
    latest_graph = get_route_endpoint(router, "/requests/latest/graph")
    request_graph = get_route_endpoint(router, "/requests/{request_id}/graph")

    listed = await list_requests()

    assert len(listed["requests"]) == 2
    assert any(item["request_id"] == "first" and item["method"] == "GET" for item in listed["requests"])
    assert await latest_graph() == {"nodes": ["latest"]}
    assert await request_graph("latest") == {"nodes": ["latest"]}


@pytest.mark.anyio
async def test_watchtrace_router_raises_for_missing_artifacts(tmp_path: Path) -> None:
    router = create_watchtrace_router(str(tmp_path / "missing"))
    latest_graph = get_route_endpoint(router, "/requests/latest/graph")
    request_graph = get_route_endpoint(router, "/requests/{request_id}/graph")

    with pytest.raises(HTTPException) as latest_error:
        await latest_graph()
    with pytest.raises(HTTPException) as request_error:
        await request_graph("nope")

    assert latest_error.value.status_code == 404
    assert request_error.value.status_code == 404
