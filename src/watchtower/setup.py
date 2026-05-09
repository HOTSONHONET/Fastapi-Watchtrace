from __future__ import annotations

from pathlib import Path
from importlib.resources import files, as_file

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
    """
    Configure WatchTower for a FastAPI application.

    WatchTower adds request-level middleware, builds or loads a project code index,
    exposes internal WatchTower API endpoints, and optionally mounts the bundled
    WatchTower UI.

    In normal package usage, users do not need to provide ``ui_dist_dir``.
    When ``enable_ui=True`` and ``ui_dist_dir`` is not provided, WatchTower uses
    the packaged UI assets from ``watchtower/ui_dist``.

    ``ui_dist_dir`` is only intended for development or advanced use cases where
    the caller wants to override the bundled frontend with a custom/local UI build.

    Args:
        app: FastAPI application instance to instrument.
        source_root: Root directory of the user application source code to index
            and trace.
        code_index_path: Path where the generated code index JSON is stored or
            loaded from.
        output_dir: Directory where WatchTower request artifacts are written.
        auto_build_index: If True, automatically build the code index when it
            does not exist.
        enable_ui: If True, mount the WatchTower UI at ``ui_mount_path``.
        api_prefix: URL prefix for WatchTower's internal API routes.
        ui_mount_path: URL path where the WatchTower UI is mounted.
        ui_dist_dir: Optional path to a custom frontend build directory. If not
            provided, the packaged WatchTower UI is used.
        exclude_paths: Request path prefixes excluded from tracing.
        trace_inputs: If True, capture request and function inputs.
        include_self: Whether to include ``self`` when serializing method inputs.
        input_max_depth: Maximum depth for serialized input objects.
        input_max_string_length: Maximum string length when serializing inputs.
        input_max_collection_items: Maximum number of items captured from lists,
            tuples, sets, and dictionaries.

    Raises:
        FileNotFoundError: If the code index is missing and auto-build is disabled,
            or if the configured UI directory cannot be found.
    """
    resolved_source_root = str(Path(source_root).resolve())
    code_index_file = Path(code_index_path)

    if code_index_file.exists():
        code_index = load_code_index(str(code_index_file))
    else:
        if not auto_build_index:
            raise FileNotFoundError(
                f"WatchTower code index not found at {code_index_file}"
            )

        code_index = build_and_save_code_index(
            root_dir=resolved_source_root,
            output_file=str(code_index_file),
        ).to_dict()

    app.state.watchtower_code_index = code_index
    app.state.watchtower_output_dir = output_dir

    app.add_middleware(
        WatchTowerMiddleware,
        source_root=resolved_source_root,
        output_dir=output_dir,
        exclude_paths=exclude_paths
        or [ui_mount_path, "/docs", "/redoc", "/openapi.json"],
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
        if ui_dist_dir:
            dist_dir = Path(ui_dist_dir)
            if not dist_dir.exists():
                print("Warning: Configured WatchTower UI directory not found. Using packaged UI.")

            app.mount(
                ui_mount_path,
                StaticFiles(directory=str(dist_dir), html=True),
                name="watchtower-ui",
            )
            return

        packaged_ui = files("watchtower").joinpath("ui_dist")

        with as_file(packaged_ui) as dist_path:
            if not dist_path.exists():
                raise FileNotFoundError(
                    "Packaged WatchTower UI not found. "
                    "Make sure src/watchtower/ui_dist is included in package data."
                )

            app.mount(
                ui_mount_path,
                StaticFiles(directory=str(dist_path), html=True),
                name="watchtower-ui",
            )