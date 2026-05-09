from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import FastAPI

from watchtower.setup import setup_watchtower


def test_setup_watchtower_loads_existing_index_and_registers_routes(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()
    index_file = tmp_path / "code_index.json"
    index_file.write_text(json.dumps({"root_dir": str(source_root), "modules": []}), encoding="utf-8")
    app = FastAPI()

    setup_watchtower(
        app,
        source_root=str(source_root),
        code_index_path=str(index_file),
        output_dir=str(tmp_path / "out"),
        enable_ui=False,
    )

    assert app.state.watchtower_code_index == {"root_dir": str(source_root), "modules": []}
    assert app.state.watchtower_output_dir == str(tmp_path / "out")
    assert any(route.path == "/__watchtower/api/requests" for route in app.routes)


def test_setup_watchtower_raises_when_index_missing_and_auto_build_disabled(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        setup_watchtower(
            FastAPI(),
            source_root=str(tmp_path),
            code_index_path=str(tmp_path / "missing.json"),
            auto_build_index=False,
        )


def test_setup_watchtower_builds_index_when_missing(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()
    (source_root / "app.py").write_text("def handler():\n    return 1\n", encoding="utf-8")
    index_file = tmp_path / "index.json"
    app = FastAPI()

    setup_watchtower(
        app,
        source_root=str(source_root),
        code_index_path=str(index_file),
        output_dir=str(tmp_path / "out"),
        enable_ui=False,
    )

    assert index_file.exists()
    assert app.state.watchtower_code_index["modules"][0]["functions"][0]["name"] == "handler"
