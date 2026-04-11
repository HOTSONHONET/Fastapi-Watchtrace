from __future__ import annotations

from typing import Any


def build_request_tree(events: list[dict[str, Any]], request_meta: dict[str, Any]) -> dict[str, Any]:
    sorted_events = sorted(events, key=lambda e: (e["ts"], e.get("duration_us", 0)))

    nodes = []
    for event in sorted_events:
        call_index = event.get("call_index")
        qualified_name = event["qualified_name"]
        node_id = f"{qualified_name}::{call_index}"

        node = {
            "id": node_id,
            "name": qualified_name,
            "func_name": event["func_name"],
            "qualified_name": qualified_name,
            "call_index": call_index,
            "event_id": event.get("event_id"),
            "file_path": event["file_path"],
            "line_no": event["line_no"],
            "ts": event["ts"],
            "dur": event["duration_us"],
            "end_ts": event["ts"] + event["duration_us"],
            "route_path": event.get("route_path"),
            "route_methods": event.get("route_methods", []),
            "parent_class": event.get("parent_class"),
            "inputs": event.get("func_args"),
            "raw_args": event.get("raw_args"),
            "children": [],
        }
        nodes.append(node)

    root = {
        "id": request_meta["request_id"],
        "name": f'{request_meta["method"]} {request_meta["path"]}',
        "request_id": request_meta["request_id"],
        "duration_ms": request_meta["duration_ms"],
        "created_at": request_meta.get("created_at"),
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