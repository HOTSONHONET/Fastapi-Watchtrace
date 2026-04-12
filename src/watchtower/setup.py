from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .indexer import build_and_save_code_index, load_code_index
from .middleware import WatchTowerMiddleware
from .api import create_watchtower_router


def setup_watchtower(
    app: FastAPI,
    source_root: str,
    code_index_path: str,
    output_dir: str = ".watchtower",
    auto_build_index: bool = True,
    enable_ui: bool = False,
    api_prefix: str = "/__watchtower/api",
    ui_mount_path: str = "/__watchtower",
    ui_dist_dir: str | None = None,
    exclude_paths: list[str] | None = None,
    trace_inputs: bool = True,
    include_self: bool = False,
    input_max_depth: int = 2,
    input_max_string_length: int = 200,
    input_max_collection_items: int = 10,
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
            root_dir=source_root,
            output_file=str(code_index_file),
        ).to_dict()

    app.state.watchtower_code_index = code_index
    app.state.watchtower_output_dir = output_dir

    app.add_middleware(
        WatchTowerMiddleware,
        source_root=source_root,
        output_dir=output_dir,
        exclude_paths=exclude_paths or [ui_mount_path, "/docs", "/redoc", "/openapi.json"],
        trace_inputs=trace_inputs,
        include_self=include_self,
        input_max_depth=input_max_depth,
        input_max_string_length=input_max_string_length,
        input_max_collection_items=input_max_collection_items,
    )

    app.include_router(
        create_watchtower_router(output_dir=output_dir),
        prefix=api_prefix,
        tags=["watchtower"],
    )

    if enable_ui:
        if not ui_dist_dir:
            raise ValueError("ui_dist_dir must be provided when enable_ui=True")

        dist_dir = Path(ui_dist_dir)
        if not dist_dir.exists():
            raise FileNotFoundError(f"UI dist directory not found: {dist_dir}")

        app.mount(
            ui_mount_path,
            StaticFiles(directory=str(dist_dir), html=True),
            name="watchtower-ui",
        )