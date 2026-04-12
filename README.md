# WatchTower


WatchTower is a project-aware FastAPI runtime observability tool that maps requests to user-defined classes and functions, helping developers understand request flow and inspect profiling data without framework noise.

### Requirements
- Use `async def` endpoints for best tracing accuracy
- Sync endpoints (`def`) may lead to incomplete or unstable traces


### Example usage

```python


from fastapi import FastAPI

from .api.routes import router
from .core.config import settings
from .core.logging_util import configure_logging
from watchtower import setup_watchtower

configure_logging()

app = FastAPI(
    title="ML Pipeline Server Example",
    version="1.0.0",
    description="A layered FastAPI example for demonstrating WatchTower tracing on realistic ML pipelines.",
)

setup_watchtower(
    app,
    source_root="examples/ml_pipeline_server",
    code_index_path=".watchtower-ml_pipeline_server/code_index.json",
    output_dir=".watchtower-ml_pipeline_server",
    enable_ui=True,
    ui_dist_dir="frontend/watchtower-ui/dist",
)

app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
async def healthcheck():
    return {
        "status": "ok",
        "service": "ml-pipeline-server",
        "api_prefix": settings.api_prefix,
    }


```


### Example of Request Flow animation of a complex server

![Request Flow Animation](https://github.com/HOTSONHONET/WatchTower/blob/master/assets/request-animation-flow.gif?raw=true)
