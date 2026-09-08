"""Persistent task history for AutoShutdown."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from threading import Lock

APP_DIR = Path.home() / ".autoshutdown"
HISTORY_FILE = APP_DIR / "history.json"
MAX_HISTORY = 500


class HistoryStore:
    def __init__(self, path: Path = HISTORY_FILE) -> None:
        self.path = path
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load_unlocked(self) -> list[dict]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    def list(self, limit: int = 200) -> list[dict]:
        with self._lock:
            return list(reversed(self._load_unlocked()[-max(1, limit):]))

    def add(self, action: str, status: str, detail: str = "", task_id: str | None = None) -> None:
        entry = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "task_id": task_id or "",
            "action": action,
            "status": status,
            "detail": detail,
        }
        with self._lock:
            items = self._load_unlocked()
            items.append(entry)
            items = items[-MAX_HISTORY:]
            self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def clear(self) -> None:
        with self._lock:
            self.path.write_text("[]\n", encoding="utf-8")
