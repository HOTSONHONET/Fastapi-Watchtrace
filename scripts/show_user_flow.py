from __future__ import annotations

import json
from pathlib import Path

from watchtower.indexer import load_code_index
from watchtower.trace_parser import load_trace, normalize_trace_events, load_memory_artifact
from watchtower.filtering import (
    attach_index_metadata,
    filter_user_events,
    get_indexed_files,
)
from watchtower.tree_builder import build_request_tree

watchtower_dir = Path(".watchtower")
request_dirs = sorted([p for p in watchtower_dir.iterdir() if p.is_dir()])
latest = request_dirs[-1]

code_index = load_code_index(".watchtower/code_index.json")
indexed_files = get_indexed_files(code_index)

events = load_trace(str(latest / "trace.json"))
memory = load_memory_artifact(str(latest / "memory.json"))

normalized = normalize_trace_events(events)
user_events = filter_user_events(normalized, indexed_files)
enriched = attach_index_metadata(user_events, code_index)

tree = build_request_tree(enriched, memory["meta"])

print(f"Latest request dir: {latest}")
print(json.dumps(tree, indent=2))