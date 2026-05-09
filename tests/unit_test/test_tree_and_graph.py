from __future__ import annotations

from watchtrace.graph_builder import tree_to_graph
from watchtrace.tree_builder import build_request_tree


def test_build_request_tree_nests_events_by_timing_and_graph_flattens_tree() -> None:
    events = [
        {
            "qualified_name": "app.parent",
            "func_name": "parent",
            "call_index": 1,
            "event_id": "parent",
            "file_path": "/tmp/app.py",
            "line_no": 1,
            "ts": 10,
            "duration_us": 100,
            "route_path": "/items",
            "route_methods": ["GET"],
            "parent_class": None,
            "inputs": {"args": []},
            "raw_args": None,
        },
        {
            "qualified_name": "app.child",
            "func_name": "child",
            "call_index": 2,
            "event_id": "child",
            "file_path": "/tmp/app.py",
            "line_no": 5,
            "ts": 20,
            "duration_us": 10,
        },
        {
            "qualified_name": "app.sibling",
            "func_name": "sibling",
            "call_index": 3,
            "event_id": "sibling",
            "file_path": "/tmp/app.py",
            "line_no": 8,
            "ts": 120,
            "duration_us": 5,
        },
    ]
    meta = {
        "request_id": "req-1",
        "method": "GET",
        "path": "/items",
        "duration_ms": 12,
        "query_params": {"q": "x"},
        "request_body": None,
    }

    tree = build_request_tree(events, meta)
    graph = tree_to_graph(tree)

    assert tree["name"] == "GET /items"
    assert tree["children"][0]["children"][0]["qualified_name"] == "app.child"
    assert tree["children"][1]["qualified_name"] == "app.sibling"
    assert graph["nodes"][0]["type"] == "request"
    assert graph["nodes"][1]["label"] == "parent"
    assert graph["nodes"][1]["expandable"] is True
    assert graph["edges"][0] == {
        "id": "req-1->app.parent::1",
        "source": "req-1",
        "target": "app.parent::1",
    }
