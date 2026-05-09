from __future__ import annotations

from watchtrace.expansion import get_child_events_within_range


def test_get_child_events_within_range_keeps_events_inside_parent_window() -> None:
    parent = {"ts": 10, "end_ts": 50, "raw_name": "parent"}
    inside = {"ts": 20, "duration_us": 5, "raw_name": "inside"}
    starts_before = {"ts": 5, "duration_us": 5, "raw_name": "before"}
    ends_after = {"ts": 45, "duration_us": 10, "raw_name": "after"}
    same_raw_name = {"ts": 20, "duration_us": 5, "raw_name": "parent"}

    assert get_child_events_within_range(
        [inside, starts_before, ends_after, same_raw_name],
        parent,
    ) == [inside]
