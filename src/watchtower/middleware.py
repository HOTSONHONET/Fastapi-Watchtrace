from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .pipeline import process_request_artifacts
from .profiler import RequestProfiler


class WatchTowerMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        output_dir: str = ".watchtower",
    ) -> None:
        super().__init__(app)
        self.output_dir = output_dir
        print("WatchTower is alive")

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path.startswith("/__watchtower"):
            return await call_next(request)
        
        request_id = uuid.uuid4().hex
        start = time.perf_counter()

        profiler = RequestProfiler(output_dir=self.output_dir)
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
                    "duration_ms": duration_ms,
                }
            )

            code_index = request.app.state.watchtower_code_index

            process_request_artifacts(
                request_dir=str(Path(self.output_dir) / request_id),
                code_index=code_index,
            )