#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from env_loader import load_dotenv


class LyftaApiError(RuntimeError):
    pass


class LyftaClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: int | None = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("API_KEY", "")
        self.base_url = (base_url or os.getenv("LYFTA_BASE_URL", "https://my.lyfta.app")).rstrip("/")
        self.timeout = timeout or int(os.getenv("LYFTA_TIMEOUT", "20"))
        if not self.api_key:
            raise ValueError("Missing API_KEY")

    def _request(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        query = ""
        if params:
            query = "?" + urllib.parse.urlencode(params)
        url = f"{self.base_url}{path}{query}"
        req = urllib.request.Request(
            url=url,
            method="GET",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ssl.create_default_context()) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise LyftaApiError(f"HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise LyftaApiError(f"Network error: {exc.reason}") from exc

    def workouts(self, page: int = 1, limit: int = 20) -> dict[str, Any]:
        return self._request("/api/v1/workouts", {"page": page, "limit": limit})

    def workouts_summary(self, page: int = 1, limit: int = 100) -> dict[str, Any]:
        return self._request("/api/v1/workouts/summary", {"page": page, "limit": limit})

    def exercises(self, page: int = 1, limit: int = 100) -> dict[str, Any]:
        return self._request("/api/v1/exercises", {"page": page, "limit": limit})

    def exercise_progress(self, exercise_id: int | str, duration_days: int = 365) -> dict[str, Any]:
        return self._request("/api/v1/exercises/progress", {"exercise_id": exercise_id, "duration": duration_days})

    def paginate(self, fetch_fn, limit: int = 100, max_pages: int = 50) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        page = 1
        while page <= max_pages:
            data = fetch_fn(page=page, limit=limit)
            key = "workouts" if "workouts" in data else "exercises"
            items = data.get(key) or []
            if not isinstance(items, list) or not items:
                break
            rows.extend([x for x in items if isinstance(x, dict)])
            total_pages = int(data.get("total_pages") or page)
            if page >= total_pages:
                break
            page += 1
        return rows
