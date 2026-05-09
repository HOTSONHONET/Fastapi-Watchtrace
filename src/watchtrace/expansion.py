from __future__ import annotations

from typing import Any


def get_child_events_within_range(
    all_events: list[dict[str, Any]],
    parent_event: dict[str, Any],
) -> list[dict[str, Any]]:
    parent_start = parent_event["ts"]
    parent_end = parent_event["end_ts"]

    children = []
    for event in all_events:
        if event["ts"] < parent_start:
            continue
        if (event["ts"] + event["duration_us"]) > parent_end:
            continue
        if event["raw_name"] == parent_event.get("raw_name"):
            continue
        children.append(event)

    return children