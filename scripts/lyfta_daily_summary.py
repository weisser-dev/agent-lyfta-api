#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from typing import Any

from lyfta_api import LyftaClient
from exercise_name_map import load_exercise_name_map, normalize_exercise_name


def _parse_date(value: str) -> dt.date | None:
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            return dt.datetime.strptime(value[: len(fmt)], fmt).date()
        except Exception:
            continue
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except Exception:
        return None


def run(args: argparse.Namespace) -> int:
    client = LyftaClient()
    workouts = client.paginate(client.workouts, limit=min(args.limit, 100), max_pages=args.max_pages)
    name_map = load_exercise_name_map()

    today = dt.date.today()
    target = today if not args.date else dt.date.fromisoformat(args.date)

    todays: list[dict[str, Any]] = []
    for w in workouts:
        d = _parse_date(str(w.get("workout_perform_date") or ""))
        if d == target:
            todays.append(w)

    # Normalize exercise names to simple German labels when mapping exists.
    for w in todays:
        exs = w.get("exercises")
        if not isinstance(exs, list):
            continue
        normalized: list[dict[str, Any]] = []
        for e in exs:
            if not isinstance(e, dict):
                continue
            original = str(e.get("excercise_name") or e.get("exercise_name") or "").strip()
            de = normalize_exercise_name(original, name_map)
            row = dict(e)
            row["exercise_name_original"] = original
            row["exercise_name_de"] = de
            # keep legacy typo field but normalized for easier downstream usage
            row["excercise_name"] = de
            normalized.append(row)
        w["exercises"] = normalized

    total_volume = 0.0
    total_secs = 0
    for w in todays:
        try:
            total_volume += float(w.get("total_volume") or 0)
        except Exception:
            pass
        dur = str(w.get("workout_duration") or "")
        if dur.count(":") == 2:
            h, m, s = dur.split(":")
            try:
                total_secs += int(h) * 3600 + int(m) * 60 + int(s)
            except Exception:
                pass

    out = {
        "date": target.isoformat(),
        "workoutCount": len(todays),
        "totalVolume": round(total_volume, 1),
        "totalDurationMinutes": round(total_secs / 60, 1),
        "workouts": todays,
    }

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"Date: {out['date']}")
        print(f"Workouts: {out['workoutCount']}")
        print(f"Volume: {out['totalVolume']}")
        print(f"Duration: {out['totalDurationMinutes']} min")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Daily Lyfta workout summary")
    p.add_argument("--date", help="YYYY-MM-DD (default: today)")
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--max-pages", type=int, default=20)
    p.add_argument("--json", action="store_true")
    raise SystemExit(run(p.parse_args()))
