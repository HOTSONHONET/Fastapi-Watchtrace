from __future__ import annotations

from collections.abc import Mapping, Sequence


def safe_serialize(
    value,
    *,
    max_depth: int = 2,
    max_string_length: int = 200,
    max_collection_items: int = 10,
):
    if max_depth < 0:
        return {
            "type": type(value).__name__,
            "value": "<max-depth-reached>",
        }

    if value is None or isinstance(value, (bool, int, float)):
        return value

    if isinstance(value, str):
        if len(value) > max_string_length:
            return value[:max_string_length] + "...<truncated>"
        return value

    if isinstance(value, bytes):
        preview = value[: min(len(value), 32)]
        return {
            "type": "bytes",
            "length": len(value),
            "preview_hex": preview.hex(),
        }

    if isinstance(value, Mapping):
        items = list(value.items())[:max_collection_items]
        result = {}
        for k, v in items:
            result[str(k)] = safe_serialize(
                v,
                max_depth=max_depth - 1,
                max_string_length=max_string_length,
                max_collection_items=max_collection_items,
            )

        if len(value) > max_collection_items:
            result["__truncated__"] = f"{len(value) - max_collection_items} more item(s)"
        return result

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        items = list(value[:max_collection_items])
        result = [
            safe_serialize(
                item,
                max_depth=max_depth - 1,
                max_string_length=max_string_length,
                max_collection_items=max_collection_items,
            )
            for item in items
        ]

        if len(value) > max_collection_items:
            result.append(f"...<{len(value) - max_collection_items} more item(s)>")
        return result

    if hasattr(value, "__dict__"):
        public_attrs = {
            k: v
            for k, v in vars(value).items()
            if not k.startswith("_")
        }
        return {
            "type": type(value).__name__,
            "attrs": safe_serialize(
                public_attrs,
                max_depth=max_depth - 1,
                max_string_length=max_string_length,
                max_collection_items=max_collection_items,
            ),
        }

    return {
        "type": type(value).__name__,
        "repr": repr(value)[:max_string_length],
    }