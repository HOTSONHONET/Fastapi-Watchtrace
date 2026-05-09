from __future__ import annotations

import json
from pathlib import Path

from watchtrace.trace_parser import (
    load_memory_artifact,
    load_trace,
    normalize_trace_events,
    parse_event_name,
)


def test_loaders_and_parse_event_name(tmp_path: Path) -> None:
    trace_file = tmp_path / "trace.json"
    trace_file.write_text(json.dumps({"traceEvents": [{"name": "x"}]}), encoding="utf-8")
    memory_file = tmp_path / "memory.json"
    memory_file.write_text(json.dumps({"meta": {"request_id": "abc"}}), encoding="utf-8")

    parsed = parse_event_name(f"handler ({tmp_path / 'app.py'}:42)")

    assert load_trace(str(trace_file)) == [{"name": "x"}]
    assert load_memory_artifact(str(memory_file)) == {"meta": {"request_id": "abc"}}
    assert parsed == {
        "func_name": "handler",
        "file_path": str((tmp_path / "app.py").resolve()),
        "line_no": 42,
    }
    assert parse_event_name("not a viztracer function event") is None


def test_normalize_trace_events_keeps_complete_duration_events(tmp_path: Path) -> None:
    file_path = tmp_path / "app.py"
    events = [
        {"ph": "B", "name": "ignored"},
        {
            "ph": "X",
            "name": f"handler ({file_path}:9)",
            "dur": 12.5,
            "ts": 100,
            "pid": 1,
            "tid": 2,
        },
        {"ph": "X", "name": "malformed"},
    ]

    normalized = normalize_trace_events(events)

    assert len(normalized) == 1
    assert normalized[0]["func_name"] == "handler"
    assert normalized[0]["duration_us"] == 12.5
    assert normalized[0]["event_id"] == "handler::100::1"
    assert normalized[0]["inputs"] is None
