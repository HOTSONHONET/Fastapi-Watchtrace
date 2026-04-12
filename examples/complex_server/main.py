from fastapi import FastAPI
from .api.routes import router
from watchtower import setup_watchtower

app = FastAPI(title="Complex Profiling Demo")

setup_watchtower(
    app,
    source_root="examples/complex_server",
    code_index_path=".watchtower-complex_server/code_index.json",
    output_dir=".watchtower-complex_server",
    enable_ui=True,
    ui_dist_dir="frontend/watchtower-ui/dist",
)
app.include_router(router)