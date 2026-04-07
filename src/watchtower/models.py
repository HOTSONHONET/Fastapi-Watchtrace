from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class FunctionInfo:
    name: str
    qualified_name: str
    lineno: int
    end_lineno: int | None
    parent_class: str | None = None
    decorators: list[str] = field(default_factory=list)
    route_path: str | None = None
    route_methods: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ClassInfo:
    name: str
    qualified_name: str
    lineno: int
    end_lineno: int | None
    methods: list[FunctionInfo] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["methods"] = [m.to_dict() for m in self.methods]
        return data


@dataclass
class ModuleInfo:
    file_path: str
    module_name: str
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "module_name": self.module_name,
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
        }


@dataclass
class CodeIndex:
    root_dir: str
    modules: list[ModuleInfo] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_dir": self.root_dir,
            "modules": [m.to_dict() for m in self.modules],
        }