"""Advanced GUI controller for AutoShutdown tasks, schedules, history and startup."""

from __future__ import annotations

import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

import autoshutdown
from core.history_store import HistoryStore
from core.scheduler_store import ScheduleStore
from core.task_manager import TaskManager
from core import startup

WEEKDAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


class AdvancedController:
    def __init__(self, app) -> None:
        self.app = app
        self.history = HistoryStore()
        self.schedules = ScheduleStore()
        self.tasks = TaskManager(self.history, self._task_changed)
        self.task_tree = None
        self.schedule_tree = None
        self.history_tree = None
        self.startup_var = tk.BooleanVar(value=startup.is_enabled())
        self._last_scheduler_check = 0.0

    def build_tabs(self, notebook: ttk.Notebook) -> None:
        self._build_tasks_tab(notebook)
        self._build_schedule_tab(notebook)
        self._build_history_tab(notebook)
        self._build_settings_tab(notebook)
        self.refresh_all()
        self.app.after(500, self._tick)

    def _build_tasks_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=6)
        notebook.add(tab, text="Tasks")
        ttk.Label(tab, text="Active & Recent Tasks", style="Section.TLabel").pack(anchor="w", pady=(0, 4))
        columns = ("id", "action", "state", "remaining", "detail")
        self.task_tree = ttk.Treeview(tab, columns=columns, show="headings", height=6)
        widths = (72, 105, 82, 82, 220)
        for col, width in zip(columns, widths):
            self.task_tree.heading(col, text=col.title())
            self.task_tree.column(col, width=width, anchor="w")
        self.task_tree.pack(fill="x")
        row = ttk.Frame(tab)
        row.pack(fill="x", pady=(5, 0))
        ttk.Button(row, text="Cancel Selected", command=self.cancel_selected).pack(side="left")
        ttk.Button(row, text="Cancel All", command=self.cancel_all).pack(side="left", padx=(4, 0))
        ttk.Button(row, text="Refresh", command=self.refresh_tasks).pack(side="left", padx=(4, 0))

    def _build_schedule_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=6)
        notebook.add(tab, text="Schedule")
        top = ttk.Frame(tab)
        top.pack(fill="x")

        self.schedule_name = tk.StringVar(value="Daily shutdown")
        self.schedule_action = tk.StringVar(value="shutdown")
        self.schedule_time = tk.StringVar(value="23:00")
        self.schedule_recurrence = tk.StringVar(value="daily")
        self.schedule_days = tk.StringVar(value="Mon,Tue,Wed,Thu,Fri")
        self.schedule_target = tk.StringVar()
        self.schedule_duration = tk.StringVar(value="1h")

        fields = (
            ("Name", self.schedule_name, "entry"),
            ("Action", self.schedule_action, "action"),
            ("Time", self.schedule_time, "entry"),
            ("Repeat", self.schedule_recurrence, "repeat"),
            ("Days", self.schedule_days, "entry"),
            ("Target", self.schedule_target, "entry"),
            ("Duration", self.schedule_duration, "entry"),
        )
        for index, (label, variable, kind) in enumerate(fields):
            frame = ttk.Frame(top)
            frame.grid(row=index // 4, column=index % 4, sticky="ew", padx=(0, 5), pady=2)
            ttk.Label(frame, text=label).pack(anchor="w")
            if kind == "action":
                widget = ttk.Combobox(frame, textvariable=variable, values=("shutdown", "restart", "logout", "close", "restrict"), state="readonly", width=14)
            elif kind == "repeat":
                widget = ttk.Combobox(frame, textvariable=variable, values=("daily", "weekly"), state="readonly", width=14)
            else:
                widget = ttk.Entry(frame, textvariable=variable, width=16)
            widget.pack(fill="x")

        ttk.Label(tab, text="Weekly days use Mon,Tue,Wed...  Target is used by Close/Restrict.", font=("TkDefaultFont", 8)).pack(anchor="w", pady=(3, 3))
        buttons = ttk.Frame(tab)
        buttons.pack(fill="x", pady=(0, 4))
        ttk.Button(buttons, text="Add Schedule", command=self.add_schedule).pack(side="left")
        ttk.Button(buttons, text="Enable / Disable", command=self.toggle_schedule).pack(side="left", padx=(4, 0))
        ttk.Button(buttons, text="Delete", command=self.delete_schedule).pack(side="left", padx=(4, 0))

        columns = ("id", "enabled", "name", "action", "time", "repeat", "days")
        self.schedule_tree = ttk.Treeview(tab, columns=columns, show="headings", height=5)
        widths = (70, 60, 150, 85, 65, 70, 160)
        for col, width in zip(columns, widths):
            self.schedule_tree.heading(col, text=col.title())
            self.schedule_tree.column(col, width=width, anchor="w")
        self.schedule_tree.pack(fill="x")

    def _build_history_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=6)
        notebook.add(tab, text="History")
        columns = ("time", "id", "action", "status", "detail")
        self.history_tree = ttk.Treeview(tab, columns=columns, show="headings", height=8)
        widths = (145, 70, 90, 85, 255)
        for col, width in zip(columns, widths):
            self.history_tree.heading(col, text=col.title())
            self.history_tree.column(col, width=width, anchor="w")
        self.history_tree.pack(fill="x")
        row = ttk.Frame(tab)
        row.pack(fill="x", pady=(5, 0))
        ttk.Button(row, text="Refresh", command=self.refresh_history).pack(side="left")
        ttk.Button(row, text="Clear History", command=self.clear_history).pack(side="left", padx=(4, 0))

    def _build_settings_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=8)
        notebook.add(tab, text="Settings")
        ttk.Label(tab, text="Desktop Integration", style="Section.TLabel").pack(anchor="w")
        ttk.Checkbutton(tab, text="Start AutoShutdown when I sign in", variable=self.startup_var, command=self.toggle_startup).pack(anchor="w", pady=(6, 2))
        ttk.Label(tab, text="Startup integration is user-level: GNOME autostart on Linux and HKCU Run on Windows.", wraplength=540, justify="left", font=("TkDefaultFont", 8)).pack(anchor="w")
        ttk.Separator(tab).pack(fill="x", pady=8)
        ttk.Label(tab, text="Persistent data", style="Section.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Schedules and history are stored in ~/.autoshutdown and remain available after restarting the app.", wraplength=540, justify="left", font=("TkDefaultFont", 8)).pack(anchor="w", pady=(4, 0))

    def schedule_power(self, action: str, delay: int) -> str:
        label = action.title()

        def runner(_cancel_event):
            code = autoshutdown.run_command(autoshutdown.command_for(action, 0), False)
            if code != 0:
                raise RuntimeError(f"{action} command returned {code}")
            return f"{label} command executed"

        task_id = self.tasks.add(label, action, delay, runner)
        self._notify_scheduled(task_id, label, delay)
        return task_id

    def schedule_close(self, process: str, delay: int) -> str:
        label = f"Close {process}"

        def runner(_cancel_event):
            count = self.app._terminate_processes(process)
            return f"Closed {count} matching process(es)"

        task_id = self.tasks.add(label, "close", delay, runner)
        self._notify_scheduled(task_id, label, delay)
        return task_id

    def schedule_restrict(self, process: str, start: int, duration: int) -> str:
        label = f"Restrict {process}"

        def runner(cancel_event):
            deadline = time.monotonic() + duration
            total = 0
            while time.monotonic() < deadline and not cancel_event.is_set():
                total += self.app._terminate_processes(process)
                cancel_event.wait(1.0)
            return f"Restriction finished; {total} process termination(s)"

        task_id = self.tasks.add(label, "restrict", start, runner)
        self._notify_scheduled(task_id, f"{label} for {duration}s", start)
        return task_id

    def _notify_scheduled(self, task_id: str, label: str, delay: int) -> None:
        self.app._set_status(f"Task {task_id} scheduled: {label}.")
        self.app.desktop.notify("AutoShutdown", f"{label} scheduled in {self.app.clock_text(delay) if hasattr(self.app, 'clock_text') else delay}.")
        self.refresh_tasks()

    def cancel_selected(self) -> None:
        if not self.app._require_unlock() or not self.task_tree:
            return
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showinfo("Tasks", "Select a task first.")
            return
        task_id = self.task_tree.item(selected[0], "values")[0]
        if self.tasks.cancel(task_id):
            self.app._set_status(f"Task {task_id} cancelled.")
        self.refresh_all()

    def cancel_all(self) -> None:
        if not self.app._require_unlock():
            return
        count = self.tasks.cancel_all()
        try:
            autoshutdown.run_command(autoshutdown.command_for("cancel"), False)
        except Exception:
            pass
        self.app._set_status(f"Cancelled {count} active task(s).")
        self.refresh_all()

    def _parse_weekdays(self, raw: str) -> list[int]:
        if not raw.strip():
            return []
        lookup = {name.lower(): index for index, name in enumerate(WEEKDAY_NAMES)}
        days = []
        for token in raw.replace(" ", "").split(","):
            key = token[:3].lower()
            if key not in lookup:
                raise ValueError(f"Unknown weekday: {token}")
            days.append(lookup[key])
        return sorted(set(days))

    def add_schedule(self) -> None:
        if not self.app._require_unlock():
            return
        try:
            weekdays = self._parse_weekdays(self.schedule_days.get()) if self.schedule_recurrence.get() == "weekly" else []
            action = self.schedule_action.get()
            target = self.schedule_target.get().strip()
            if action in {"close", "restrict"} and not target:
                raise ValueError("Target is required for Close/Restrict schedules.")
            if action == "restrict":
                autoshutdown.parse_duration(self.schedule_duration.get())
            self.schedules.add(
                name=self.schedule_name.get(),
                action=action,
                time_text=self.schedule_time.get(),
                recurrence=self.schedule_recurrence.get(),
                weekdays=weekdays,
                target=target,
                duration=self.schedule_duration.get(),
            )
        except Exception as exc:
            messagebox.showerror("Invalid Schedule", str(exc))
            return
        self.app._set_status("Schedule saved.")
        self.refresh_schedules()

    def _selected_schedule_id(self) -> str | None:
        if not self.schedule_tree:
            return None
        selected = self.schedule_tree.selection()
        if not selected:
            return None
        return str(self.schedule_tree.item(selected[0], "values")[0])

    def toggle_schedule(self) -> None:
        if not self.app._require_unlock():
            return
        schedule_id = self._selected_schedule_id()
        if not schedule_id:
            messagebox.showinfo("Schedule", "Select a schedule first.")
            return
        self.schedules.toggle(schedule_id)
        self.refresh_schedules()

    def delete_schedule(self) -> None:
        if not self.app._require_unlock():
            return
        schedule_id = self._selected_schedule_id()
        if not schedule_id:
            messagebox.showinfo("Schedule", "Select a schedule first.")
            return
        self.schedules.delete(schedule_id)
        self.refresh_schedules()

    def toggle_startup(self) -> None:
        if not self.app._require_unlock():
            self.startup_var.set(startup.is_enabled())
            return
        try:
            if self.startup_var.get():
                startup.enable()
                self.app._set_status("Startup enabled.")
            else:
                startup.disable()
                self.app._set_status("Startup disabled.")
        except Exception as exc:
            self.startup_var.set(startup.is_enabled())
            messagebox.showerror("Startup", str(exc))

    def clear_history(self) -> None:
        if not self.app._require_unlock():
            return
        if messagebox.askyesno("Clear History?", "Remove all saved task history?"):
            self.history.clear()
            self.refresh_history()

    def refresh_tasks(self) -> None:
        if not self.task_tree:
            return
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        for task in self.tasks.all()[:100]:
            remaining = self.app.clock_text(task.remaining) if hasattr(self.app, "clock_text") else str(task.remaining)
            self.task_tree.insert("", "end", values=(task.id, task.action, task.state, remaining, task.detail or task.label))

    def refresh_schedules(self) -> None:
        if not self.schedule_tree:
            return
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        for schedule in self.schedules.list():
            days = ",".join(WEEKDAY_NAMES[index] for index in schedule.get("weekdays", []) if 0 <= index < 7)
            self.schedule_tree.insert("", "end", values=(
                schedule.get("id", ""),
                "Yes" if schedule.get("enabled", True) else "No",
                schedule.get("name", ""),
                schedule.get("action", ""),
                schedule.get("time", ""),
                schedule.get("recurrence", ""),
                days,
            ))

    def refresh_history(self) -> None:
        if not self.history_tree:
            return
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for entry in self.history.list(200):
            self.history_tree.insert("", "end", values=(
                entry.get("time", "").replace("T", " "),
                entry.get("task_id", ""),
                entry.get("action", ""),
                entry.get("status", ""),
                entry.get("detail", ""),
            ))

    def refresh_all(self) -> None:
        self.refresh_tasks()
        self.refresh_schedules()
        self.refresh_history()
        self.startup_var.set(startup.is_enabled())
        self._update_header()

    def _task_changed(self) -> None:
        try:
            self.app.after(0, self.refresh_all)
        except Exception:
            pass

    def _update_header(self) -> None:
        active = self.tasks.active()
        if not active:
            self.app.state_var.set("READY")
            self.app.countdown_var.set("00:00:00")
            self.app.task_var.set("No active task")
            self.app.desktop.set_title("Ready")
            return
        next_task = min(active, key=lambda task: task.due_at)
        remaining = self.app.clock_text(next_task.remaining) if hasattr(self.app, "clock_text") else str(next_task.remaining)
        self.app.state_var.set(f"ACTIVE {len(active)}")
        self.app.countdown_var.set(remaining)
        self.app.task_var.set(next_task.label)
        self.app.desktop.set_title(f"{len(active)} task(s) - {remaining}")

    def _run_due_schedule(self, item: dict) -> None:
        action = item.get("action", "shutdown")
        target = item.get("target", "")
        try:
            if action in {"shutdown", "restart", "logout"}:
                self.schedule_power(action, 0)
            elif action == "close":
                self.schedule_close(target, 0)
            elif action == "restrict":
                duration = autoshutdown.parse_duration(item.get("duration") or "1h")
                self.schedule_restrict(target, 0, duration)
            self.history.add(action, "schedule-triggered", item.get("name", "Scheduled task"), item.get("id"))
        except Exception as exc:
            self.history.add(action, "schedule-failed", str(exc), item.get("id"))

    def _tick(self) -> None:
        self._update_header()
        self.refresh_tasks()
        now = time.monotonic()
        if now - self._last_scheduler_check >= 15:
            self._last_scheduler_check = now
            for item in self.schedules.due(datetime.now()):
                self._run_due_schedule(item)
            self.refresh_schedules()
            self.refresh_history()
        self.app.after(500, self._tick)
