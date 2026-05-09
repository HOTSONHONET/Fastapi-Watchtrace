from __future__ import annotations

import inspect

from watchtrace.frame_utils import extract_inputs_from_frame


def capture_frame(alpha, request, *items, beta="b", **kwargs):
    return extract_inputs_from_frame(inspect.currentframe())


class Example:
    def method(self, value):
        return extract_inputs_from_frame(inspect.currentframe(), include_self=True)


def test_extract_inputs_from_frame_skips_framework_args_and_serializes_varargs() -> None:
    result = capture_frame(1, object(), 2, 3, beta="changed", extra="yes")

    assert result["class_name"] is None
    assert result["inputs"]["args"] == [
        {"name": "alpha", "value": 1},
        {"name": "beta", "value": "changed"},
        {"name": "*items", "value": [2, 3]},
    ]
    assert result["inputs"]["kwargs"] == {"extra": "yes"}


def test_extract_inputs_from_frame_can_include_self_and_class_name() -> None:
    result = Example().method("x")

    assert result["class_name"] == "Example"
    assert result["inputs"]["args"][0]["name"] == "self"
    assert result["inputs"]["args"][1] == {"name": "value", "value": "x"}
