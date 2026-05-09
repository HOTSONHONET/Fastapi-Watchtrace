from fastapi import FastAPI
from .api.routes import router
from watchtrace import setup_watchtrace

app = FastAPI(title="Complex Profiling Demo")

setup_watchtrace(
    app,
    source_root="examples/complex_server",
    code_index_path=".watchtrace-complex_server/code_index.json",
    output_dir=".watchtrace-complex_server",
    enable_ui=True,
    ui_dist_dir="frontend/watchtrace-ui/dist",
)
app.include_router(router)