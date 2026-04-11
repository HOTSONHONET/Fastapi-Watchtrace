# WatchTower


WatchTower is a project-aware FastAPI runtime observability tool that maps requests to user-defined classes and functions, helping developers understand request flow and inspect profiling data without framework noise.

### Requirements
- Use `async def` endpoints for best tracing accuracy
- Sync endpoints (`def`) may lead to incomplete or unstable traces


### Example usage

```python


from fastapi import FastAPI
from .api.routes import router
from watchtower import setup_watchtower

app = FastAPI(title="Complex Profiling Demo")

setup_watchtower(
    app,
    source_root="examples",
    output_dir=".watchtower-complex_server",
    enable_ui=True,
    ui_dist_dir="frontend/watchtower-ui/dist",
)
app.include_router(router)

```

