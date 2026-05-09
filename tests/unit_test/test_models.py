from __future__ import annotations

from watchtrace.models import ClassInfo, CodeIndex, FunctionInfo, ModuleInfo


def test_model_to_dict_serializes_nested_objects() -> None:
    function = FunctionInfo(
        name="handler",
        qualified_name="app.handler",
        lineno=3,
        end_lineno=7,
        route_path="/items",
        route_methods=["GET"],
    )
    method = FunctionInfo(
        name="run",
        qualified_name="app.Service.run",
        lineno=10,
        end_lineno=12,
        parent_class="Service",
    )
    klass = ClassInfo(
        name="Service",
        qualified_name="app.Service",
        lineno=9,
        end_lineno=13,
        methods=[method],
    )
    module = ModuleInfo(
        file_path="/tmp/app.py",
        module_name="app",
        functions=[function],
        classes=[klass],
    )
    index = CodeIndex(root_dir="/tmp", modules=[module])

    data = index.to_dict()

    assert data["root_dir"] == "/tmp"
    assert data["modules"][0]["functions"][0]["route_path"] == "/items"
    assert data["modules"][0]["classes"][0]["methods"][0]["parent_class"] == "Service"
