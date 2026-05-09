from __future__ import annotations

import json
from pathlib import Path

from watchtower.artifacts import save_json
from watchtower.pipeline import attach_call_inputs, load_call_inputs, normalize_path, process_request_artifacts


def test_attach_call_inputs_consumes_repeated_matches_in_order(tmp_path: Path) -> None:
    file_path = str(tmp_path / "app.py")
    events = [
        {"file_path": file_path, "func_name": "handler", "line_no": 3},
        {"file_path": file_path, "func_name": "handler", "line_no": 3},
    ]
    call_inputs = [
        {"file_path": file_path, "func_name": "handler", "line_no": 3, "inputs": {"n": 1}},
        {"file_path": file_path, "func_name": "handler", "line_no": 3, "inputs": {"n": 2}},
    ]

    result = attach_call_inputs(events, call_inputs)

    assert normalize_path(r"a\b\c.py") == "a/b/c.py"
    assert result[0]["inputs"] == {"n": 1}
    assert result[1]["inputs"] == {"n": 2}


def test_process_request_artifacts_writes_normalized_enriched_tree_and_graph(tmp_path: Path) -> None:
    source_file = tmp_path / "app.py"
    source_file.write_text("def handler(x):\n    return x\n", encoding="utf-8")
    request_dir = tmp_path / "req-1"
    request_dir.mkdir()
    trace_name = f"handler ({source_file}:1)"
    (request_dir / "trace.json").write_text(
        json.dumps({"traceEvents": [{"ph": "X", "name": trace_name, "ts": 1, "dur": 2}]}),
        encoding="utf-8",
    )
    (request_dir / "memory.json").write_text(
        json.dumps(
            {
                "meta": {
                    "request_id": "req-1",
                    "method": "GET",
                    "path": "/x",
                    "duration_ms": 3,
                }
            }
        ),
        encoding="utf-8",
    )
    (request_dir / "call_inputs.json").write_text(
        json.dumps(
            [
                {
                    "file_path": str(source_file),
                    "func_name": "handler",
                    "line_no": 1,
                    "inputs": {"x": 1},
                }
            ]
        ),
        encoding="utf-8",
    )
    code_index = {
        "modules": [
            {
                "file_path": str(source_file),
                "functions": [
                    {
                        "name": "handler",
                        "qualified_name": "app.handler",
                        "lineno": 1,
                        "end_lineno": 2,
                    }
                ],
                "classes": [],
            }
        ]
    }

    process_request_artifacts(str(request_dir), code_index)

    assert load_call_inputs(request_dir / "missing.json") == []
    assert json.loads((request_dir / "enriched_events.json").read_text(encoding="utf-8"))[0]["inputs"] == {"x": 1}
    graph = json.loads((request_dir / "request_graph.json").read_text(encoding="utf-8"))
    assert graph["nodes"][1]["full_name"] == "app.handler"


def test_save_json_creates_parent_directories(tmp_path: Path) -> None:
    output_file = tmp_path / "nested" / "data.json"

    save_json({"ok": True}, str(output_file))

    assert json.loads(output_file.read_text(encoding="utf-8")) == {"ok": True}
