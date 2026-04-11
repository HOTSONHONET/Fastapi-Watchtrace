from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

EVENT_NAME_RE = re.compile(r"^(?P<func>.+?) \((?P<file>.*?):(?P<line>\d+)\)$")


def load_memory_artifact(memory_file: str) -> dict[str, Any]:
    return json.loads(Path(memory_file).read_text(encoding="utf-8"))


def load_trace(trace_file: str) -> list[dict[str, Any]]:
    data = json.loads(Path(trace_file).read_text(encoding="utf-8"))
    return data.get("traceEvents", [])


def parse_event_name(name: str) -> dict[str, Any] | None:
    match = EVENT_NAME_RE.match(name)
    if not match:
        return None

    return {
        "func_name": match.group("func"),
        "file_path": str(Path(match.group("file")).resolve()),
        "line_no": int(match.group("line")),
    }


def normalize_trace_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for idx, event in enumerate(events):
        if event.get("ph") != "X":
            continue

        parsed = parse_event_name(event.get("name", ""))
        if not parsed:
            continue

        event_args = event.get("args", {}) or {}
        func_args = event_args.get("func_args")

        normalized.append(
            {
                "event_id": f"{parsed['func_name']}::{event.get('ts', 0.0)}::{idx}",
                "func_name": parsed["func_name"],
                "file_path": parsed["file_path"],
                "line_no": parsed["line_no"],
                "duration_us": event.get("dur", 0.0),
                "ts": event.get("ts", 0.0),
                "pid": event.get("pid"),
                "tid": event.get("tid"),
                "raw_name": event.get("name", ""),
                "func_args": func_args,
                "raw_args": event_args,
            }
        )

    return normalized