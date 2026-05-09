from __future__ import annotations

import json
import sys
import tracemalloc
from pathlib import Path
from typing import Any
from collections import defaultdict

from viztracer import VizTracer

from .serializer import safe_serialize


class RequestProfiler:
    def __init__(
        self,
        output_dir: str,
        trace_inputs: bool = True,
        include_self: bool = False,
        input_max_depth: int = 2,
        input_max_string_length: int = 200,
        input_max_collection_items: int = 10,
        source_root: str | None = None,
    ):
        self.output_dir = Path(output_dir)
        self.trace_inputs = trace_inputs
        self.include_self = include_self
        self.input_max_depth = input_max_depth
        self.input_max_string_length = input_max_string_length
        self.input_max_collection_items = input_max_collection_items
        self.source_root = str(Path(source_root).resolve()) if source_root else None

        self.request_dir: Path | None = None
        self.tracer: VizTracer | None = None
        self.call_inputs: list[dict[str, Any]] = []
        self._previous_profiler = None

    def _should_capture_frame(self, frame) -> bool:
        filename = frame.f_code.co_filename
        if not filename:
            return False

        filename = str(Path(filename).resolve())

        if self.source_root and not filename.startswith(self.source_root):
            return False

        return True

    def _profile_func(self, frame, event, arg):
        if event != "call":
            return self._profile_func

        if not self.trace_inputs:
            return self._profile_func

        if not self._should_capture_frame(frame):
            return self._profile_func

        code = frame.f_code
        filename = str(Path(code.co_filename).resolve())

        try:
            serialized_inputs = safe_serialize(
                frame.f_locals,
                max_depth=self.input_max_depth,
                max_string_length=self.input_max_string_length,
                max_collection_items=self.input_max_collection_items,
            )
        except Exception:
            serialized_inputs = {"error": "failed_to_serialize_inputs"}

        self.call_inputs.append(
            {
                "func_name": code.co_name,
                "file_path": filename,
                "line_no": code.co_firstlineno,
                "inputs": serialized_inputs,
            }
        )

        return self._profile_func

    def start(self, request_id: str) -> None:
        self.request_dir = self.output_dir / request_id
        self.request_dir.mkdir(parents=True, exist_ok=True)

        tracemalloc.start()

        self.tracer = VizTracer(
            output_file=str(self.request_dir / "trace.json"),
            tracer_entries=500000,
            log_func_args=False,
            log_func_repr=None,
        )
        self.tracer.start()

        self._previous_profiler = sys.getprofile()
        sys.setprofile(self._profile_func)

    def stop(self, meta: dict[str, Any] | None = None) -> None:
        sys.setprofile(self._previous_profiler)

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

            with open(self.request_dir / "call_inputs.json", "w", encoding="utf-8") as f:
                json.dump(self.call_inputs, f, indent=2)