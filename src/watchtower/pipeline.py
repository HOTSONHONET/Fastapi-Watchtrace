from __future__ import annotations

import json
from pathlib import Path

from .artifacts import save_json
from .filtering import attach_index_metadata, filter_user_events, get_indexed_files
from .graph_builder import tree_to_graph
from .trace_parser import load_memory_artifact, load_trace, normalize_trace_events
from .tree_builder import build_request_tree


def load_call_inputs(path: Path) -> list[dict]:
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_path(path: str | None) -> str | None:
    if not path:
        return None
    return str(Path(path)).replace("\\", "/")


def attach_call_inputs(events: list[dict], call_inputs: list[dict]) -> list[dict]:
    """
    Attach captured frame locals to normalized/enriched trace events.

    Matching priority:
    1. file_path
    2. function name
    3. line number
    4. consume matches in order so repeated calls map sensibly
    """
    if not call_inputs:
        for event in events:
            event["inputs"] = None
        return events

    # build grouped lookup
    grouped: dict[tuple[str | None, str | None, int | None], list[dict]] = {}
    for item in call_inputs:
        key = (
            normalize_path(item.get("file_path")),
            item.get("func_name"),
            item.get("line_no"),
        )
        grouped.setdefault(key, []).append(item)

    # attach inputs
    for event in events:
        event["inputs"] = None

        key = (
            normalize_path(event.get("file_path")),
            event.get("function") or event.get("func_name") or event.get("name"),
            event.get("line_no"),
        )

        matches = grouped.get(key, [])
        if matches:
            matched = matches.pop(0)
            event["inputs"] = matched.get("inputs")

    return events


def process_request_artifacts(request_dir: str, code_index: dict) -> None:
    request_path = Path(request_dir)

    trace_file = request_path / "trace.json"
    memory_file = request_path / "memory.json"
    call_inputs_file = request_path / "call_inputs.json"

    events = load_trace(str(trace_file))
    memory = load_memory_artifact(str(memory_file))
    call_inputs = load_call_inputs(call_inputs_file)

    indexed_files = get_indexed_files(code_index)

    normalized = normalize_trace_events(events)
    user_events = filter_user_events(normalized, indexed_files)
    enriched = attach_index_metadata(user_events, code_index)
    enriched = attach_call_inputs(enriched, call_inputs)

    tree = build_request_tree(enriched, memory["meta"])
    graph = tree_to_graph(tree)

    save_json(normalized, str(request_path / "normalized_events.json"))
    save_json(enriched, str(request_path / "enriched_events.json"))
    save_json(tree, str(request_path / "request_tree.json"))
    save_json(graph, str(request_path / "request_graph.json"))