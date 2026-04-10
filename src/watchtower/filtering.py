from __future__ import annotations

from pathlib import Path
from typing import Any


def _normalize_path(path: str | None) -> str | None:
    if not path:
        return None
    try:
        return str(Path(path).resolve())
    except Exception:
        return str(Path(path))


def get_indexed_files(code_index: dict[str, Any]) -> set[str]:
    files: set[str] = set()

    for module in code_index.get("modules", []):
        normalized = _normalize_path(module.get("file_path"))
        if normalized:
            files.add(normalized)

    return files


def filter_user_events(
    normalized_events: list[dict[str, Any]],
    indexed_files: set[str],
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []

    for event in normalized_events:
        event_file = _normalize_path(event.get("file_path"))
        if event_file and event_file in indexed_files:
            filtered.append(
                {
                    **event,
                    "file_path": event_file,
                }
            )

    return filtered


def _build_module_lookup(code_index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}

    for module in code_index.get("modules", []):
        normalized = _normalize_path(module.get("file_path"))
        if normalized:
            lookup[normalized] = module

    return lookup


def find_matching_function(
    file_path: str,
    line_no: int,
    code_index: dict[str, Any],
) -> dict[str, Any] | None:
    normalized_file = _normalize_path(file_path)
    if not normalized_file:
        return None

    module_lookup = _build_module_lookup(code_index)
    module = module_lookup.get(normalized_file)
    if module is None:
        return None

    # Prefer the narrowest matching range.
    best_match: dict[str, Any] | None = None
    best_span: int | None = None

    for fn in module.get("functions", []):
        start = fn["lineno"]
        end = fn.get("end_lineno") or start
        if start <= line_no <= end:
            span = end - start
            if best_span is None or span < best_span:
                best_match = fn
                best_span = span

    for cls in module.get("classes", []):
        for method in cls.get("methods", []):
            start = method["lineno"]
            end = method.get("end_lineno") or start
            if start <= line_no <= end:
                span = end - start
                if best_span is None or span < best_span:
                    best_match = method
                    best_span = span

    return best_match


def attach_index_metadata(
    events: list[dict[str, Any]],
    code_index: dict[str, Any],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []

    for event in events:
        match = find_matching_function(
            file_path=event["file_path"],
            line_no=event["line_no"],
            code_index=code_index,
        )
        if match is None:
            continue

        enriched.append(
            {
                **event,
                "file_path": _normalize_path(event["file_path"]),
                "qualified_name": match["qualified_name"],
                "route_path": match.get("route_path"),
                "route_methods": match.get("route_methods", []),
                "parent_class": match.get("parent_class"),
            }
        )

    return enriched