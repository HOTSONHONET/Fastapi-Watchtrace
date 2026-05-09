from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from watchtower.profiler import RequestProfiler


def make_frame(file_path: Path, func_name: str = "handler", lineno: int = 7):
    code = SimpleNamespace(
        co_filename=str(file_path),
        co_name=func_name,
        co_firstlineno=lineno,
    )
    return SimpleNamespace(f_code=code, f_locals={"value": 1})


def test_profiler_filters_frames_to_source_root_and_captures_call_inputs(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()
    in_source = source_root / "app.py"
    outside_source = tmp_path / "external.py"
    in_source.write_text("", encoding="utf-8")
    outside_source.write_text("", encoding="utf-8")
    profiler = RequestProfiler(output_dir=str(tmp_path), source_root=str(source_root))

    assert profiler._should_capture_frame(make_frame(in_source)) is True
    assert profiler._should_capture_frame(make_frame(outside_source)) is False

    profiler._profile_func(make_frame(in_source), "call", None)
    profiler._profile_func(make_frame(in_source, func_name="ignored"), "return", None)

    assert profiler.call_inputs == [
        {
            "func_name": "handler",
            "file_path": str(in_source.resolve()),
            "line_no": 7,
            "inputs": {"value": 1},
        }
    ]


def test_profiler_does_not_capture_when_trace_inputs_disabled(tmp_path: Path) -> None:
    source_file = tmp_path / "app.py"
    source_file.write_text("", encoding="utf-8")
    profiler = RequestProfiler(output_dir=str(tmp_path), trace_inputs=False)

    profiler._profile_func(make_frame(source_file), "call", None)

    assert profiler.call_inputs == []
