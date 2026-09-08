"""Concurrent in-process task manager for AutoShutdown."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from .history_store import HistoryStore

Runner = Callable[[threading.Event], str | None]
Callback = Callable[[], None]


@dataclass
class ManagedTask:
    id: str
    label: str
    action: str
    created_at: float
    due_at: float
    cancel_event: threading.Event = field(default_factory=threading.Event)
    state: str = "waiting"
    detail: str = ""
    thread: threading.Thread | None = None

    @property
    def remaining(self) -> int:
        return max(0, int(self.due_at - time.time() + 0.999))


class TaskManager:
    def __init__(self, history: HistoryStore | None = None, on_change: Callback | None = None) -> None:
        self.history = history or HistoryStore()
        self.on_change = on_change
        self._tasks: dict[str, ManagedTask] = {}
        self._lock = threading.RLock()

    def _changed(self) -> None:
        if self.on_change:
            try:
                self.on_change()
            except Exception:
                pass

    def add(self, label: str, action: str, delay_seconds: int, runner: Runner) -> str:
        task_id = uuid.uuid4().hex[:8]
        now = time.time()
        task = ManagedTask(task_id, label, action, now, now + max(0, delay_seconds))
        with self._lock:
            self._tasks[task_id] = task
        self.history.add(action, "scheduled", label, task_id)

        def worker() -> None:
            if task.cancel_event.wait(max(0, delay_seconds)):
                return
            with self._lock:
                if task.state == "cancelled":
                    return
                task.state = "running"
            self._changed()
            try:
                result = runner(task.cancel_event)
                with self._lock:
                    if task.cancel_event.is_set():
                        task.state = "cancelled"
                    else:
                        task.state = "completed"
                        task.detail = result or "Completed"
                self.history.add(action, task.state, task.detail, task_id)
            except Exception as exc:
                with self._lock:
                    task.state = "failed"
                    task.detail = str(exc)
                self.history.add(action, "failed", str(exc), task_id)
            self._changed()

        task.thread = threading.Thread(target=worker, name=f"autoshutdown-{task_id}", daemon=True)
        task.thread.start()
        self._changed()
        return task_id

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task.state not in {"waiting", "running"}:
                return False
            task.cancel_event.set()
            task.state = "cancelled"
            task.detail = "Cancelled by user"
        self.history.add(task.action, "cancelled", task.detail, task.id)
        self._changed()
        return True

    def cancel_all(self) -> int:
        ids = [task.id for task in self.active()]
        return sum(1 for task_id in ids if self.cancel(task_id))

    def active(self) -> list[ManagedTask]:
        with self._lock:
            return [task for task in self._tasks.values() if task.state in {"waiting", "running"}]

    def all(self) -> list[ManagedTask]:
        with self._lock:
            return sorted(self._tasks.values(), key=lambda task: task.created_at, reverse=True)

    def get(self, task_id: str) -> ManagedTask | None:
        with self._lock:
            return self._tasks.get(task_id)

    def summary(self) -> str:
        active = self.active()
        if not active:
            return "Ready"
        next_task = min(active, key=lambda task: task.due_at)
        when = datetime.fromtimestamp(next_task.due_at).strftime("%H:%M:%S")
        return f"{len(active)} task(s) - next {when}"
