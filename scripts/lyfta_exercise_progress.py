#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from lyfta_api import LyftaClient
from exercise_name_map import load_exercise_name_map, normalize_exercise_name


def run(args: argparse.Namespace) -> int:
    client = LyftaClient()

    if args.exercise_id:
        progress = client.exercise_progress(exercise_id=args.exercise_id, duration_days=args.duration)
        print(json.dumps(progress, indent=2, ensure_ascii=False))
        return 0

    exercises = client.paginate(client.exercises, limit=args.limit, max_pages=args.max_pages)
    mapping = load_exercise_name_map()
    normalized = []
    for e in exercises:
        row = dict(e)
        original = str(row.get("name") or "").strip()
        row["name_original"] = original
        row["name_de"] = normalize_exercise_name(original, mapping)
        row["name"] = row["name_de"]
        normalized.append(row)

    out = {
        "count": len(normalized),
        "exercises": normalized[: args.show],
        "note": "Pass --exercise-id <id> to fetch progress for one exercise.",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Lyfta exercises and progress")
    p.add_argument("--exercise-id", type=int)
    p.add_argument("--duration", type=int, default=365)
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--max-pages", type=int, default=20)
    p.add_argument("--show", type=int, default=20)
    raise SystemExit(run(p.parse_args()))
