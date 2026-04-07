from __future__ import annotations

from typing import Any


def build_request_tree(events: list[dict[str, Any]], request_meta: dict[str, Any]) -> dict[str, Any]:
    sorted_events = sorted(events, key=lambda e: e["ts"])

    nodes = []
    for event in sorted_events:
        node = {
            "name": event["qualified_name"],
            "func_name": event["func_name"],
            "file_path": event["file_path"],
            "line_no": event["line_no"],
            "ts": event["ts"],
            "dur": event["duration_us"],
            "end_ts": event["ts"] + event["duration_us"],
            "route_path": event.get("route_path"),
            "route_methods": event.get("route_methods", []),
            "children": [],
        }
        nodes.append(node)

    root = {
        "name": f'{request_meta["method"]} {request_meta["path"]}',
        "request_id": request_meta["request_id"],
        "duration_ms": request_meta["duration_ms"],
        "children": [],
    }

    stack: list[dict[str, Any]] = []

    for node in nodes:
        while stack and node["ts"] >= stack[-1]["end_ts"]:
            stack.pop()

        if stack:
            stack[-1]["children"].append(node)
        else:
            root["children"].append(node)

        stack.append(node)

    return root