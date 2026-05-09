from __future__ import annotations

from watchtrace.serializer import safe_serialize


class SampleObject:
    def __init__(self) -> None:
        self.name = "visible"
        self._private = "hidden"


def test_safe_serialize_truncates_strings_and_collections() -> None:
    assert safe_serialize("abcdef", max_string_length=3) == "abc...<truncated>"

    result = safe_serialize({"a": 1, "b": 2, "c": 3}, max_collection_items=2)

    assert result == {"a": 1, "b": 2, "__truncated__": "1 more item(s)"}


def test_safe_serialize_handles_bytes_objects_and_depth() -> None:
    assert safe_serialize(b"\x00\xff") == {
        "type": "bytes",
        "length": 2,
        "preview_hex": "00ff",
    }

    result = safe_serialize({"outer": {"inner": 1}}, max_depth=0)

    assert result == {
        "outer": {
            "type": "dict",
            "value": "<max-depth-reached>",
        }
    }


def test_safe_serialize_public_object_attributes_only() -> None:
    result = safe_serialize(SampleObject())

    assert result == {"type": "SampleObject", "attrs": {"name": "visible"}}
