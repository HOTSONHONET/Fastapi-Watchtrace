from __future__ import annotations

import json
import tracemalloc
from pathlib import Path
from typing import Any

from viztracer import VizTracer


class RequestProfiler:
    def __init__(self, output_dir: str = ".watchtower") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.request_dir: Path | None = None
        self.tracer: VizTracer | None = None

    def start(self, request_id: str) -> None:
        self.request_dir = self.output_dir / request_id
        self.request_dir.mkdir(parents=True, exist_ok=True)

        tracemalloc.start()

        self.tracer = VizTracer(
            output_file=str(self.request_dir / "trace.json"),
            tracer_entries=500000,
        )
        self.tracer.start()

    def stop(self, meta: dict[str, Any] | None = None) -> None:
        if self.tracer is not None:
            self.tracer.stop()
            self.tracer.save()

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        if self.request_dir is not None:
            with open(self.request_dir / "memory.json", "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "meta": meta or {},
                        "current_bytes": current,
                        "peak_bytes": peak,
                    },
                    f,
                    indent=2,
                )