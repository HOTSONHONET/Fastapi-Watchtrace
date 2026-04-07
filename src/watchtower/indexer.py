from __future__ import annotations

import ast
import json
from pathlib import Path

from .models import ClassInfo, CodeIndex, FunctionInfo, ModuleInfo


FASTAPI_HTTP_METHODS = {
    "get": "GET",
    "post": "POST",
    "put": "PUT",
    "delete": "DELETE",
    "patch": "PATCH",
    "options": "OPTIONS",
    "head": "HEAD",
}


class ModuleVisitor(ast.NodeVisitor):
    def __init__(self, module_name: str) -> None:
        self.module_name = module_name
        self.module_functions: list[FunctionInfo] = []
        self.classes: list[ClassInfo] = []
        self._class_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_name = node.name
        qualified_class_name = f"{self.module_name}.{class_name}"

        class_info = ClassInfo(
            name=class_name,
            qualified_name=qualified_class_name,
            lineno=node.lineno,
            end_lineno=getattr(node, "end_lineno", None),
        )

        self._class_stack.append(class_name)

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._build_function_info(item, parent_class=class_name)
                class_info.methods.append(method_info)

        self.classes.append(class_info)

        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._class_stack:
            return
        self.module_functions.append(self._build_function_info(node, parent_class=None))

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self._class_stack:
            return
        self.module_functions.append(self._build_function_info(node, parent_class=None))

    def _build_function_info(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        parent_class: str | None,
    ) -> FunctionInfo:
        if parent_class:
            qualified_name = f"{self.module_name}.{parent_class}.{node.name}"
        else:
            qualified_name = f"{self.module_name}.{node.name}"

        decorators = [self._decorator_to_str(d) for d in node.decorator_list]
        route_path, route_methods = self._extract_fastapi_route(node.decorator_list)

        return FunctionInfo(
            name=node.name,
            qualified_name=qualified_name,
            lineno=node.lineno,
            end_lineno=getattr(node, "end_lineno", None),
            parent_class=parent_class,
            decorators=decorators,
            route_path=route_path,
            route_methods=route_methods,
        )

    def _extract_fastapi_route(
        self, decorators: list[ast.expr]
    ) -> tuple[str | None, list[str]]:
        for decorator in decorators:
            if not isinstance(decorator, ast.Call):
                continue

            func = decorator.func
            if not isinstance(func, ast.Attribute):
                continue

            method_name = func.attr.lower()
            if method_name not in FASTAPI_HTTP_METHODS:
                continue

            route_path = None
            if decorator.args:
                first_arg = decorator.args[0]
                if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                    route_path = first_arg.value

            return route_path, [FASTAPI_HTTP_METHODS[method_name]]

        return None, []

    def _decorator_to_str(self, decorator: ast.AST) -> str:
        try:
            return ast.unparse(decorator)
        except Exception:
            return "<decorator>"
        

def should_skip_path(path: Path) -> bool:
    skip_parts = {
        ".git",
        ".venv",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        "dist",
        "build",
        "node_modules",
    }
    return any(part in skip_parts for part in path.parts)


def path_to_module(root_dir: Path, file_path: Path) -> str:
    relative = file_path.relative_to(root_dir)
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def parse_python_file(root_dir: Path, file_path: Path) -> ModuleInfo | None:
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except Exception as exc:
        print(f"Skipping {file_path}: {exc}")
        return None

    module_name = path_to_module(root_dir, file_path)
    visitor = ModuleVisitor(module_name=module_name)
    visitor.visit(tree)

    return ModuleInfo(
        file_path=str(file_path.resolve()),
        module_name=module_name,
        functions=visitor.module_functions,
        classes=visitor.classes,
    )


def build_code_index(root_dir: str) -> CodeIndex:
    root_path = Path(root_dir).resolve()
    modules: list[ModuleInfo] = []

    for file_path in root_path.rglob("*.py"):
        if should_skip_path(file_path):
            continue

        module_info = parse_python_file(root_path, file_path)
        if module_info is not None:
            modules.append(module_info)

    modules.sort(key=lambda m: m.module_name)
    return CodeIndex(root_dir=str(root_path), modules=modules)


def save_code_index(code_index: CodeIndex, output_file: str) -> None:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(code_index.to_dict(), indent=2),
        encoding="utf-8",
    )


def build_and_save_code_index(root_dir: str, output_file: str) -> CodeIndex:
    code_index = build_code_index(root_dir)
    save_code_index(code_index, output_file)
    return code_index


def build_file_function_map(code_index: CodeIndex) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {}

    for module in code_index.modules:
        entries: list[dict] = []

        for fn in module.functions:
            entries.append(
                {
                    "name": fn.name,
                    "qualified_name": fn.qualified_name,
                    "lineno": fn.lineno,
                    "end_lineno": fn.end_lineno,
                    "parent_class": fn.parent_class,
                }
            )

        for cls in module.classes:
            for method in cls.methods:
                entries.append(
                    {
                        "name": method.name,
                        "qualified_name": method.qualified_name,
                        "lineno": method.lineno,
                        "end_lineno": method.end_lineno,
                        "parent_class": method.parent_class,
                    }
                )

        result[module.file_path] = entries

    return result

def load_code_index(index_file: str) -> dict:
    path = Path(index_file)
    return json.loads(path.read_text(encoding="utf-8"))