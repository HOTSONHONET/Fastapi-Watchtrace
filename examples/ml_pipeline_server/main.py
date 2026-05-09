from fastapi import FastAPI

from .api.routes import router
from .core.config import settings
from .core.logging_util import configure_logging
from watchtrace import setup_watchtrace

configure_logging()

app = FastAPI(
    title="ML Pipeline Server Example",
    version="1.0.0",
    description="A layered FastAPI example for demonstrating WatchTrace tracing on realistic ML pipelines.",
)

setup_watchtrace(
    app,
    source_root="examples/ml_pipeline_server",
    code_index_path=".watchtrace-ml_pipeline_server/code_index.json",
    output_dir=".watchtrace-ml_pipeline_server",
    enable_ui=True,
    ui_dist_dir="frontend/watchtrace-ui/dist",
)

app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
async def healthcheck():
    return {
        "status": "ok",
        "service": "ml-pipeline-server",
        "api_prefix": settings.api_prefix,
    }
