import json
from pathlib import Path

from watchtower.trace_parser import load_trace

watchtower_dir = Path(".watchtower")
request_dirs = [p for p in watchtower_dir.iterdir() if p.is_dir()]
request_dirs.sort()

latest = request_dirs[-1]
events = load_trace(str(latest / "trace.json"))

print(f"Latest request dir: {latest}")
print(f"Total events: {len(events)}")
print(json.dumps(events[:10], indent=2)[:4000])