from __future__ import annotations

import inspect

from .serializer import safe_serialize

DEFAULT_SKIPPED_ARG_NAMES = {"request", "response", "app", "db"}


def extract_inputs_from_frame(
    frame,
    *,
    include_self: bool = False,
    max_depth: int = 2,
    max_string_length: int = 200,
    max_collection_items: int = 10,
) -> dict:
    arg_info = inspect.getargvalues(frame)

    args_out = []
    kwargs_out = {}

    skipped = set(DEFAULT_SKIPPED_ARG_NAMES)
    if not include_self:
        skipped.update({"self", "cls"})

    for name in arg_info.args:
        if name in skipped:
            continue

        value = arg_info.locals.get(name)
        args_out.append(
            {
                "name": name,
                "value": safe_serialize(
                    value,
                    max_depth=max_depth,
                    max_string_length=max_string_length,
                    max_collection_items=max_collection_items,
                ),
            }
        )

    if arg_info.varargs:
        varargs_value = arg_info.locals.get(arg_info.varargs, ())
        args_out.append(
            {
                "name": f"*{arg_info.varargs}",
                "value": safe_serialize(
                    varargs_value,
                    max_depth=max_depth,
                    max_string_length=max_string_length,
                    max_collection_items=max_collection_items,
                ),
            }
        )

    if arg_info.keywords:
        kw_value = arg_info.locals.get(arg_info.keywords, {})
        if isinstance(kw_value, dict):
            kwargs_out = {
                str(k): safe_serialize(
                    v,
                    max_depth=max_depth,
                    max_string_length=max_string_length,
                    max_collection_items=max_collection_items,
                )
                for k, v in kw_value.items()
            }
        else:
            kwargs_out = {
                f"**{arg_info.keywords}": safe_serialize(
                    kw_value,
                    max_depth=max_depth,
                    max_string_length=max_string_length,
                    max_collection_items=max_collection_items,
                )
            }

    class_name = None
    if "self" in frame.f_locals:
        class_name = type(frame.f_locals["self"]).__name__
    elif "cls" in frame.f_locals and hasattr(frame.f_locals["cls"], "__name__"):
        class_name = frame.f_locals["cls"].__name__

    return {
        "class_name": class_name,
        "inputs": {
            "args": args_out,
            "kwargs": kwargs_out,
        },
    }