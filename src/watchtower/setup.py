from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI

from .indexer import build_and_save_code_index, load_code_index
from .middleware import WatchTowerMiddleware
from .api import create_watchtower_router
from fastapi.staticfiles import StaticFiles

def setup_watchtower(
    app: FastAPI,
    source_root: str,
    output_dir: str = ".watchtower",
    code_index_path: str = ".watchtower/code_index.json",
    auto_build_index: bool = True,
    enable_ui: bool = False,
    ui_mount_path: str = "/__watchtower",
    ui_dist_dir: str | None = None,
) -> None:
    
    code_index_file = Path(code_index_path)

    if code_index_file.exists():
        code_index = load_code_index(str(code_index_file))
    else:
        if not auto_build_index:
            raise FileNotFoundError(
                f"WatchTower code index not found at {code_index_file}"
            )
        
        code_index = build_and_save_code_index(
            root_dir = source_root,
            output_file = str(code_index_file),
        ).to_dict()

    app.state.watchtower_code_index = code_index
    app.state.watchtower_output_dir = output_dir


    app.add_middleware(
        WatchTowerMiddleware, 
        output_dir=output_dir
    )

    app.include_router(
        create_watchtower_router(output_dir=output_dir),
        prefix=f"{ui_mount_path}/api",
        tags=["watchtower"],
    )

    if enable_ui:
        dist_dir = Path(ui_dist_dir)
        if dist_dir.exists():
            app.mount(
                ui_mount_path,
                StaticFiles(directory=str(dist_dir), html=True),
                name="watchtower-ui",
            )