from __future__ import annotations

from typing import Any


def _short_label(name: str) -> str:
    if "." in name:
        return name.split(".")[-1]
    return name


def tree_to_graph(tree: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    def visit(node: dict[str, Any], parent_id: str | None = None, depth: int = 0) -> None:
        node_id = node["name"]

        node_type = "request" if depth == 0 else "function"

        nodes.append(
            {
                "id": node_id,
                "label": _short_label(node["name"]),
                "full_name": node["name"],
                "type": node_type,
                "duration": node.get("dur", node.get("duration_ms")),
                "file_path": node.get("file_path"),
                "line_no": node.get("line_no"),
                "route_path": node.get("route_path"),
                "route_methods": node.get("route_methods", []),
                "expandable": len(node.get("children", [])) > 0,
            }
        )

        if parent_id is not None:
            edges.append(
                {
                    "id": f"{parent_id}->{node_id}",
                    "source": parent_id,
                    "target": node_id,
                }
            )

        for child in node.get("children", []):
            visit(child, node_id, depth + 1)

    visit(tree)
    return {"nodes": nodes, "edges": edges}