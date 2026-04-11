from __future__ import annotations

import json
import tracemalloc
from pathlib import Path
from typing import Any

from viztracer import VizTracer

from .serializer import safe_serialize


def _safe_repr_for_viztracer(obj: Any) -> str:
    """
    Convert objects to a safe, bounded string for VizTracer's log_func_args.
    VizTracer will call this for function arguments when log_func_args=True.
    """
    try:
        serialized = safe_serialize(
            obj,
            max_depth=2,
            max_string_length=200,
            max_collection_items=10,
        )
        return json.dumps(serialized, ensure_ascii=False)
    except Exception:
        try:
            return repr(obj)[:200]
        except Exception:
            return f"<unreprable {type(obj).__name__}>"

class RequestProfiler:
    def __init__(
        self,
        output_dir: str,
        trace_inputs: bool = True,
        include_self: bool = False,  # kept for compatibility; not used here yet
        input_max_depth: int = 2,
        input_max_string_length: int = 200,
        input_max_collection_items: int = 10,
    ):
        self.output_dir = Path(output_dir)
        self.trace_inputs = trace_inputs
        self.include_self = include_self
        self.input_max_depth = input_max_depth
        self.input_max_string_length = input_max_string_length
        self.input_max_collection_items = input_max_collection_items

        self.request_dir: Path | None = None
        self.tracer: VizTracer | None = None

    def start(self, request_id: str) -> None:
        self.request_dir = self.output_dir / request_id
        self.request_dir.mkdir(parents=True, exist_ok=True)

        tracemalloc.start()

        self.tracer = VizTracer(
            output_file=str(self.request_dir / "trace.json"),
            tracer_entries=500000,
            log_func_args=self.trace_inputs,
            log_func_repr=_safe_repr_for_viztracer if self.trace_inputs else None,
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