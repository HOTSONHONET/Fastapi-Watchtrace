from __future__ import annotations

from typing import Any
from pathlib import Path

import plotly.graph_objects as go

def tree_to_sunburst_rows(
    node: dict[str, Any],
    parent_name: str | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    name = node["name"]

    if "dur" in node:
        value = node["dur"]
    else:
        # root node uses request duration in ms; convert to microseconds for consistency
        value = node.get("duration_ms", 0) * 1000

    rows.append(
        {
            "id": name if parent_name is None else f"{parent_name}>{name}",
            "label": name,
            "parent": "" if parent_name is None else parent_name,
            "value": value,
        }
    )

    current_parent = name if parent_name is None else f"{parent_name}>{name}"

    for child in node.get("children", []):
        child_rows = tree_to_sunburst_rows(child, current_parent)
        rows.extend(child_rows)

    return rows

def render_sunburst_html(tree: dict[str, Any], output_file: str) -> None:
    rows = tree_to_sunburst_rows(tree)

    ids = [row["id"] for row in rows]
    labels = [row["label"] for row in rows]
    parents = [row["parent"] for row in rows]
    values = [row["value"] for row in rows]

    fig = go.Figure(
        go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
        )
    )

    fig.update_layout(
        margin=dict(t=30, l=10, r=10, b=10),
        title="WatchTower Request Flow",
    )

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path), include_plotlyjs="cdn")