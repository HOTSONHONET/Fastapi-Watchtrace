from __future__ import annotations

from pathlib import Path

from .artifacts import save_json
from .filtering import attach_index_metadata, filter_user_events, get_indexed_files
from .graph_builder import tree_to_graph
from .trace_parser import load_memory_artifact, load_trace, normalize_trace_events
from .tree_builder import build_request_tree


def process_request_artifacts(request_dir: str, code_index: dict) -> None:
    request_path = Path(request_dir)

    trace_file = request_path / "trace.json"
    memory_file = request_path / "memory.json"

    events = load_trace(str(trace_file))
    memory = load_memory_artifact(str(memory_file))

    indexed_files = get_indexed_files(code_index)

    normalized = normalize_trace_events(events)
    user_events = filter_user_events(normalized, indexed_files)
    enriched = attach_index_metadata(user_events, code_index)

    tree = build_request_tree(enriched, memory["meta"])
    graph = tree_to_graph(tree)

    save_json(tree, str(request_path / "request_tree.json"))
    save_json(graph, str(request_path / "request_graph.json"))