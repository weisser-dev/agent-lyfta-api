#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

MAP_PATH = Path(__file__).resolve().parents[1] / "references" / "exercise_name_map.json"


def load_exercise_name_map() -> dict[str, str]:
    if not MAP_PATH.exists():
        return {}
    try:
        return json.loads(MAP_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def normalize_exercise_name(name: str, mapping: dict[str, str] | None = None) -> str:
    m = mapping or load_exercise_name_map()
    clean = (name or "").strip()
    return m.get(clean, clean)
