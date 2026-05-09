from __future__ import annotations

import json
from pathlib import Path

from watchtrace.indexer import load_code_index
from watchtrace.trace_parser import load_trace, normalize_trace_events, load_memory_artifact
from watchtrace.filtering import (
    attach_index_metadata,
    filter_user_events,
    get_indexed_files,
)
from watchtrace.tree_builder import build_request_tree
from watchtrace.graph_builder import tree_to_graph
from watchtrace.artifacts import save_json

watchtrace_dir = Path(".watchtrace")
request_dirs = sorted([p for p in watchtrace_dir.iterdir() if p.is_dir()])
latest = request_dirs[-1]

code_index = load_code_index(".watchtrace/code_index.json")
indexed_files = get_indexed_files(code_index)

events = load_trace(str(latest / "trace.json"))
memory = load_memory_artifact(str(latest / "memory.json"))

normalized = normalize_trace_events(events)
user_events = filter_user_events(normalized, indexed_files)
enriched = attach_index_metadata(user_events, code_index)

tree = build_request_tree(enriched, memory["meta"])
graph = tree_to_graph(tree)

save_json(tree, str(latest / "request_tree.json"))
save_json(graph, str(latest / "request_graph.json"))

print(f"Saved request_tree.json and request_graph.json in {latest}")
print(json.dumps(graph, indent=2))