from __future__ import annotations

import json
from pathlib import Path

from watchtower.indexer import (
    build_and_save_code_index,
    build_code_index,
    build_file_function_map,
    load_code_index,
    parse_python_file,
    path_to_module,
    should_skip_path,
)


def test_build_code_index_extracts_functions_classes_and_routes(tmp_path: Path) -> None:
    app_file = tmp_path / "app.py"
    app_file.write_text(
        "\n".join(
            [
                "from fastapi import FastAPI",
                "app = FastAPI()",
                "",
                "@app.get('/items')",
                "async def list_items():",
                "    return []",
                "",
                "class Service:",
                "    def run(self):",
                "        return 1",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "ignored.py").write_text("def ignored(): pass", encoding="utf-8")

    code_index = build_code_index(str(tmp_path))
    module = code_index.modules[0]

    assert module.module_name == "app"
    assert module.functions[0].qualified_name == "app.list_items"
    assert module.functions[0].route_path == "/items"
    assert module.functions[0].route_methods == ["GET"]
    assert module.classes[0].methods[0].qualified_name == "app.Service.run"
    assert should_skip_path(tmp_path / ".venv" / "ignored.py") is True


def test_parse_save_load_and_file_function_map(tmp_path: Path) -> None:
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()
    init_file = package_dir / "__init__.py"
    init_file.write_text("def boot():\n    return True\n", encoding="utf-8")

    assert path_to_module(tmp_path, init_file) == "pkg"
    module = parse_python_file(tmp_path, init_file)
    assert module is not None
    assert module.functions[0].name == "boot"

    output_file = tmp_path / "index" / "code.json"
    code_index = build_and_save_code_index(str(tmp_path), str(output_file))

    assert json.loads(output_file.read_text(encoding="utf-8")) == load_code_index(str(output_file))
    function_map = build_file_function_map(code_index)
    assert function_map[module.file_path][0]["name"] == "boot"


def test_parse_python_file_returns_none_for_invalid_python(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("def nope(:\n", encoding="utf-8")

    assert parse_python_file(tmp_path, bad_file) is None
