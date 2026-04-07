from __future__ import annotations

from typing import Any


def get_indexed_files(code_index: dict[str, Any]) -> set[str]:
    return {module["file_path"] for module in code_index.get("modules", [])}


def filter_user_events(
    normalized_events: list[dict[str, Any]],
    indexed_files: set[str],
) -> list[dict[str, Any]]:
    return [
        event
        for event in normalized_events
        if event["file_path"] in indexed_files
    ]


def find_matching_function(
    file_path: str,
    line_no: int,
    code_index: dict[str, Any],
) -> dict[str, Any] | None:
    for module in code_index.get("modules", []):
        if module["file_path"] != file_path:
            continue

        for fn in module.get("functions", []):
            end_lineno = fn.get("end_lineno") or fn["lineno"]
            if fn["lineno"] <= line_no <= end_lineno:
                return fn

        for cls in module.get("classes", []):
            for method in cls.get("methods", []):
                end_lineno = method.get("end_lineno") or method["lineno"]
                if method["lineno"] <= line_no <= end_lineno:
                    return method

    return None


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
                "qualified_name": match["qualified_name"],
                "route_path": match.get("route_path"),
                "route_methods": match.get("route_methods", []),
                "parent_class": match.get("parent_class"),
            }
        )

    return enriched