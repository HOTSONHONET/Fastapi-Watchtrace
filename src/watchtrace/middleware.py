from __future__ import annotations

import time
import uuid
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .pipeline import process_request_artifacts
from .profiler import RequestProfiler


class WatchTraceMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        source_root: str,
        output_dir: str,
        exclude_paths: list[str] | None = None,
        trace_inputs: bool = True,
        include_self: bool = False,
        input_max_depth: int = 2,
        input_max_string_length: int = 200,
        input_max_collection_items: int = 10,
    ) -> None:
        super().__init__(app)
        self.source_root = source_root
        self.output_dir = output_dir
        self.exclude_paths = exclude_paths or []
        self.trace_inputs = trace_inputs
        self.include_self = include_self
        self.input_max_depth = input_max_depth
        self.input_max_string_length = input_max_string_length
        self.input_max_collection_items = input_max_collection_items
        self.exclude_suffixes = (
            ".js",
            ".css",
            ".map",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            ".woff",
            ".woff2",
            ".ttf",
        )
        print("WatchTrace is alive")

    def _should_skip(self, path: str) -> bool:
        if any(path.startswith(prefix) for prefix in self.exclude_paths):
            return True

        if path.endswith(self.exclude_suffixes):
            return True

        return False

    async def dispatch(self, request: Request, call_next) -> Response:
        if self._should_skip(request.url.path):
            return await call_next(request)

        request_id = uuid.uuid4().hex
        start = time.perf_counter()

        request_body = None
        if self.trace_inputs:
            try:
                raw = await request.body()
                if raw:
                    request_body = raw.decode("utf-8", errors="replace")[:5000]

                async def receive():
                    return {
                        "type": "http.request",
                        "body": raw,
                        "more_body": False,
                    }

                request._receive = receive
            except Exception:
                request_body = "<unavailable>"

        profiler = RequestProfiler(
            output_dir=self.output_dir,
            trace_inputs=self.trace_inputs,
            include_self=self.include_self,
            input_max_depth=self.input_max_depth,
            input_max_string_length=self.input_max_string_length,
            input_max_collection_items=self.input_max_collection_items,
            source_root=self.source_root,
        )

        profiler.start(request_id=request_id)

        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            profiler.stop(
                meta={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                    "duration_ms": duration_ms,
                    "created_at": time.time(),
                    "request_body": request_body,
                }
            )

            code_index = request.app.state.watchtrace_code_index

            process_request_artifacts(
                request_dir=str(Path(self.output_dir) / request_id),
                code_index=code_index,
            )