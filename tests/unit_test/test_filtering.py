from __future__ import annotations

from pathlib import Path

from watchtrace.filtering import (
    attach_index_metadata,
    filter_user_events,
    find_matching_function,
    get_indexed_files,
)


def test_filter_user_events_and_attach_metadata_choose_narrowest_match(tmp_path: Path) -> None:
    file_path = tmp_path / "app.py"
    code_index = {
        "modules": [
            {
                "file_path": str(file_path),
                "functions": [
                    {
                        "name": "outer",
                        "qualified_name": "app.outer",
                        "lineno": 1,
                        "end_lineno": 50,
                    }
                ],
                "classes": [
                    {
                        "name": "Service",
                        "methods": [
                            {
                                "name": "inner",
                                "qualified_name": "app.Service.inner",
                                "lineno": 10,
                                "end_lineno": 12,
                                "parent_class": "Service",
                                "route_path": None,
                                "route_methods": [],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    events = [
        {
            "file_path": str(file_path),
            "line_no": 11,
            "ts": 20,
            "duration_us": 5,
            "func_name": "inner",
        },
        {"file_path": str(tmp_path / "other.py"), "line_no": 1, "ts": 1, "duration_us": 1},
    ]

    indexed_files = get_indexed_files(code_index)
    user_events = filter_user_events(events, indexed_files)
    enriched = attach_index_metadata(user_events, code_index)

    assert indexed_files == {str(file_path.resolve())}
    assert len(user_events) == 1
    assert find_matching_function(str(file_path), 11, code_index)["qualified_name"] == "app.Service.inner"
    assert enriched[0]["qualified_name"] == "app.Service.inner"
    assert enriched[0]["call_index"] == 1
    assert enriched[0]["file_path"] == str(file_path.resolve())


def test_find_matching_function_returns_none_for_missing_file(tmp_path: Path) -> None:
    assert find_matching_function(str(tmp_path / "missing.py"), 1, {"modules": []}) is None
