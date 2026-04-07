from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_json(data: dict[str, Any], output_file: str) -> None:
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")