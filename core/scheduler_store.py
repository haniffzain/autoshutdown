"""Persistent daily and weekly scheduler definitions."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from threading import Lock

APP_DIR = Path.home() / ".autoshutdown"
SCHEDULE_FILE = APP_DIR / "schedules.json"


class ScheduleStore:
    def __init__(self, path: Path = SCHEDULE_FILE) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _load_unlocked(self) -> list[dict]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    def list(self) -> list[dict]:
        with self._lock:
            return self._load_unlocked()

    def save(self, items: list[dict]) -> None:
        with self._lock:
            self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def add(self, *, name: str, action: str, time_text: str, recurrence: str,
            weekdays: list[int] | None = None, target: str = "", duration: str = "") -> dict:
        datetime.strptime(time_text, "%H:%M")
        item = {
            "id": uuid.uuid4().hex[:8],
            "name": name.strip() or action.title(),
            "action": action,
            "time": time_text,
            "recurrence": recurrence,
            "weekdays": weekdays or [],
            "target": target.strip(),
            "duration": duration.strip(),
            "enabled": True,
            "last_run": "",
        }
        items = self.list()
        items.append(item)
        self.save(items)
        return item

    def delete(self, schedule_id: str) -> bool:
        items = self.list()
        new_items = [item for item in items if item.get("id") != schedule_id]
        if len(new_items) == len(items):
            return False
        self.save(new_items)
        return True

    def toggle(self, schedule_id: str) -> bool:
        items = self.list()
        changed = False
        for item in items:
            if item.get("id") == schedule_id:
                item["enabled"] = not bool(item.get("enabled", True))
                changed = True
        if changed:
            self.save(items)
        return changed

    def due(self, now: datetime | None = None) -> list[dict]:
        now = now or datetime.now()
        minute_key = now.strftime("%Y-%m-%d %H:%M")
        hhmm = now.strftime("%H:%M")
        weekday = now.weekday()
        items = self.list()
        due_items: list[dict] = []
        changed = False

        for item in items:
            if not item.get("enabled", True) or item.get("time") != hhmm:
                continue
            recurrence = item.get("recurrence", "daily")
            if recurrence == "weekly" and weekday not in item.get("weekdays", []):
                continue
            if item.get("last_run") == minute_key:
                continue
            item["last_run"] = minute_key
            due_items.append(dict(item))
            changed = True

        if changed:
            self.save(items)
        return due_items
