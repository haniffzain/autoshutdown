#!/usr/bin/env python3
"""Compact AutoShutdown desktop UI."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import psutil

import autoshutdown
from desktop_integration import DesktopIntegration
from desktop_theme import palette as desktop_palette

APP_DIR = Path.home() / ".autoshutdown"
SECURITY_FILE = APP_DIR / "security.json"
PBKDF2_ITERATIONS = 250_000
TIME_PRESETS = (("5m", "5m"), ("15m", "15m"), ("30m", "30m"), ("1h", "1h"), ("2h", "2h"), ("3h", "3h"))

CAT_ART = """⠀⠀⠀⠀⢠⡶⠚⢷⣤⡀⠀⠀⠀⠀⠀⣲⡶⠛⠻⣆
⠀⠀⠀⢠⡿⠁⠀⠀⠙⣷⣄⠀⢀⣴⡟⠁⠀⠀⢷⢹⡆
⠀⠀⠀⣾⠃⠀⠠⠶⠚⠛⠛⠛⠛⠋⠀⠀⣀⡀⢸⠈⣿
⠀⠀⢸⣏⡔⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⠉⠉⣿⠀⢹
⠀⠀⢾⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠀⢸⡇
⠀⢠⣿⢠⣶⡆⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇
⢒⡾⠁⠘⠟⠁⠀⠀⠀⠀⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⢸⡇
⠉⣧⠀⠀⠀⠀⠃⠀⠀⠀⠈⠉⠠⣍⠀⠀⠀⠀⠀⠀⣸⡇
⠀⠸⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡟
⠀⠀⠀⠛⣷⡦⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⡴⠞⠋
⠀⠀⠀⢰⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠳⣤⡀
⠀⠀⠀⣸⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷
⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠈⢿
⠀⠀⠀⢸⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿
⠀⠀⠀⢸⡇⠘⡇⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⢸
⠀⠀⠀⢸⡇⠀⠙⠀⠀⠀⠀⠀⢠⠞⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⡇⠀⢸⡆⠀⠀⠀⠀⣟⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⣿⠀⠀⡇⠀⠀⠀⠀⣿⡀⠀⠀⠀⠀⠀⠀⠀⢀
⠀⠀⠀⠘⠿⠶⢶⢧⣦⣦⡴⢾⣥⣽⣤⣤⣤⣤⣤⣤⡴"""

ABOUT_TEXT = (
    "Hubuntu OS is the foundation behind AutoShutdown and a growing family of small, focused utilities.\n\n"
    "Built on Ubuntu/Linux, Hubuntu is designed as a practical desktop platform where lightweight tools can be created, tested and integrated into one consistent environment.\n\n"
    "AutoShutdown follows that idea: one small utility, one clear purpose, minimal overhead."
)

MIT_LICENSE_TEXT = """MIT License

Copyright (c) 2026 Mohd Haniff

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def _hash_password(password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations).hex()


def password_is_configured() -> bool:
    return SECURITY_FILE.exists()


def set_password(password: str) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    salt = secrets.token_bytes(16)
    SECURITY_FILE.write_text(json.dumps({
        "version": 1,
        "iterations": PBKDF2_ITERATIONS,
        "salt": salt.hex(),
        "password_hash": _hash_password(password, salt),
    }, indent=2), encoding="utf-8")
    try:
        os.chmod(SECURITY_FILE, 0o600)
    except OSError:
        pass


def verify_password(password: str) -> bool:
    try:
        data = json.loads(SECURITY_FILE.read_text(encoding="utf-8"))
        salt = bytes.fromhex(data["salt"])
        actual = _hash_password(password, salt, int(data.get("iterations", PBKDF2_ITERATIONS)))
        return secrets.compare_digest(actual, data["password_hash"])
    except Exception:
        return False


def clock_text(seconds: int) -> str:
    h, rem = divmod(max(0, int(seconds)), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


class AutoShutdownGUI(tk.Tk):
    POLL_SECONDS = 1.0

    def __init__(self) -> None:
        super().__init__()
        self.colors = desktop_palette()
        self.title("AutoShutdown")
        self.geometry("760x370")
        self.minsize(720, 350)
        self.configure(bg=self.colors["bg"])

        self._cancel_event = threading.Event()
        self._worker: threading.Thread | None = None
        self._unlocked = False
        self._task_active = False
        self._countdown_deadline: float | None = None
        self._countdown_label = "No active task"
        self._warning_sent = False
        self._cat_shift = 0
        self.desktop = DesktopIntegration(self)

        self._build_style()
        self._build_ui()
        self.desktop.start()
        self.after(120, self._ensure_password)
        self.after(450, self._animate_cat)
        self.after(200, self._update_countdown)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_style(self) -> None:
        c = self.colors
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=c["bg"])
        style.configure("TLabel", background=c["bg"], foreground=c["fg"])
        style.configure("Title.TLabel", background=c["bg"], foreground=c["fg"], font=("TkDefaultFont", 15, "bold"))
        style.configure("Section.TLabel", background=c["bg"], foreground=c["fg"], font=("TkDefaultFont", 10, "bold"))
        style.configure("Countdown.TLabel", background=c["bg"], foreground=c["fg"], font=("TkFixedFont", 20, "bold"))
        style.configure("State.TLabel", background=c["bg"], foreground=c["fg"], font=("TkDefaultFont", 9, "bold"))
        style.configure("TButton", background=c["surface_alt"], foreground=c["fg"], bordercolor=c["border"], lightcolor=c["surface_alt"], darkcolor=c["surface_alt"])
        style.map("TButton", background=[("active", c["select"]), ("pressed", c["select"])], foreground=[("active", c["select_fg"])])
        style.configure("Start.TButton", font=("TkDefaultFont", 9, "bold"), padding=(9, 3))
        style.configure("Stop.TButton", font=("TkDefaultFont", 9, "bold"), padding=(9, 3))
        style.configure("TEntry", fieldbackground=c["surface"], foreground=c["fg"], bordercolor=c["border"], insertcolor=c["fg"])
        style.configure("TCombobox", fieldbackground=c["surface"], background=c["surface"], foreground=c["fg"], bordercolor=c["border"], arrowcolor=c["fg"])
        style.map("TCombobox", fieldbackground=[("readonly", c["surface"])], foreground=[("readonly", c["fg"])])
        style.configure("TNotebook", background=c["bg"], bordercolor=c["border"])
        style.configure("TNotebook.Tab", background=c["surface_alt"], foreground=c["fg"], padding=(7, 2))
        style.map("TNotebook.Tab", background=[("selected", c["surface"]), ("active", c["select"])], foreground=[("selected", c["fg"]), ("active", c["select_fg"])])

        self.option_add("*TCombobox*Listbox.background", c["surface"])
        self.option_add("*TCombobox*Listbox.foreground", c["fg"])
        self.option_add("*TCombobox*Listbox.selectBackground", c["select"])
        self.option_add("*TCombobox*Listbox.selectForeground", c["select_fg"])

    def _build_ui(self) -> None:
        c = self.colors
        root = ttk.Frame(self, padding=6)
        root.pack(fill="both", expand=True)

        left = tk.Frame(root, width=180, bg=c["cat_bg"], highlightthickness=1, highlightbackground=c["border"])
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="AUTOSHUTDOWN", bg=c["cat_bg"], fg=c["cat_fg"], font=("TkFixedFont", 10, "bold")).pack(pady=(7, 1))
        self.cat_label = tk.Label(left, text=CAT_ART, justify="left", bg=c["cat_bg"], fg=c["cat_fg"], font=("DejaVu Sans Mono", 5))
        self.cat_label.pack(padx=2, pady=(0, 1))
        self.cat_message = tk.StringVar(value="guardian ready")
        tk.Label(left, textvariable=self.cat_message, bg=c["cat_bg"], fg=c["cat_muted"], font=("TkFixedFont", 8)).pack(pady=1)
        tk.Label(left, text="[ TIMER ] [ APP GUARD ]\n[ TRAY ] [ PASSWORD ]", bg=c["cat_bg"], fg=c["cat_muted"], font=("TkFixedFont", 7), justify="left").pack(side="bottom", pady=6)

        main = ttk.Frame(root, padding=(8, 0, 0, 0))
        main.pack(side="left", fill="both", expand=True)

        header = ttk.Frame(main)
        header.pack(fill="x")
        ttk.Label(header, text="AutoShutdown", style="Title.TLabel").pack(side="left")
        self.lock_button = ttk.Button(header, text="Unlock", width=7, command=self.unlock_app)
        self.lock_button.pack(side="right")
        ttk.Button(header, text="Password", width=8, command=self.change_password).pack(side="right", padx=(0, 3))
        ttk.Button(header, text="Tray", width=6, command=self.hide_to_tray).pack(side="right", padx=(0, 3))

        status_box = ttk.Frame(main)
        status_box.pack(fill="x", pady=(2, 3))
        self.state_var = tk.StringVar(value="READY")
        ttk.Label(status_box, textvariable=self.state_var, style="State.TLabel").pack(side="left")
        self.countdown_var = tk.StringVar(value="00:00:00")
        ttk.Label(status_box, textvariable=self.countdown_var, style="Countdown.TLabel").pack(side="left", padx=(9, 7))
        self.task_var = tk.StringVar(value="No active task")
        ttk.Label(status_box, textvariable=self.task_var, font=("TkDefaultFont", 8)).pack(side="left", fill="x", expand=True)

        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill="x")
        self._build_power_tab()
        self._build_close_tab()
        self._build_restrict_tab()
        self._build_about_tab()

        footer = ttk.Frame(main)
        footer.pack(fill="x", pady=(3, 0))
        self.status_var = tk.StringVar(value=f"Ready. Theme: {self.colors['mode']}.")
        ttk.Label(footer, textvariable=self.status_var, font=("TkDefaultFont", 8)).pack(side="left", fill="x", expand=True)
        ttk.Button(footer, text="STOP", width=7, style="Stop.TButton", command=self.cancel_active_task).pack(side="right")

    def _duration_row(self, parent: ttk.Frame, label: str, default: str) -> tk.StringVar:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=label, width=11).pack(side="left")
        value = tk.StringVar(value=default)
        ttk.Entry(row, textvariable=value, width=8).pack(side="left")
        for text, duration in TIME_PRESETS:
            ttk.Button(row, text=text, width=3, command=lambda d=duration, v=value: v.set(d)).pack(side="left", padx=(2, 0))
        return value

    def _build_power_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(tab, text="Power")
        ttk.Label(tab, text="Timed Shutdown / Logout", style="Section.TLabel").pack(anchor="w", pady=(0, 3))
        row = ttk.Frame(tab)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text="Action", width=11).pack(side="left")
        self.power_action = tk.StringVar(value="shutdown")
        ttk.Combobox(row, textvariable=self.power_action, values=("shutdown", "restart", "logout"), state="readonly", width=12).pack(side="left")
        self.power_delay = self._duration_row(tab, "Run after", "30m")
        ttk.Button(tab, text="START", width=8, style="Start.TButton", command=self.schedule_power).pack(anchor="w", pady=(4, 0))

    def _build_close_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(tab, text="Close App")
        ttk.Label(tab, text="Timed Close App", style="Section.TLabel").pack(anchor="w", pady=(0, 3))
        self.close_process = self._process_picker(tab)
        self.close_delay = self._duration_row(tab, "Close after", "15m")
        ttk.Button(tab, text="START", width=8, style="Start.TButton", command=self.schedule_close_app).pack(anchor="w", pady=(4, 0))

    def _build_restrict_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(tab, text="Restrict")
        ttk.Label(tab, text="Timed Restrict App", style="Section.TLabel").pack(anchor="w", pady=(0, 3))
        self.restrict_process = self._process_picker(tab)
        self.restrict_start = self._duration_row(tab, "Start after", "5m")
        self.restrict_duration = self._duration_row(tab, "Restrict for", "1h")
        ttk.Button(tab, text="START", width=8, style="Start.TButton", command=self.schedule_restrict_app).pack(anchor="w", pady=(4, 0))

    def _build_about_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=7)
        self.notebook.add(tab, text="About")
        ttk.Label(tab, text="Hubuntu OS", style="Section.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Label(tab, text=ABOUT_TEXT, wraplength=535, justify="left", font=("TkDefaultFont", 8)).pack(anchor="w")
        row = ttk.Frame(tab)
        row.pack(fill="x", pady=(6, 0))
        ttk.Label(row, text="License: MIT", font=("TkDefaultFont", 8, "bold")).pack(side="left")
        ttk.Button(row, text="View License", width=11, command=self._show_license).pack(side="right")

    def _show_license(self) -> None:
        c = self.colors
        dialog = tk.Toplevel(self)
        dialog.title("MIT License")
        dialog.transient(self)
        dialog.geometry("610x390")
        dialog.minsize(500, 300)
        dialog.configure(bg=c["bg"])

        frame = ttk.Frame(dialog, padding=8)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="MIT License", style="Section.TLabel").pack(anchor="w", pady=(0, 5))

        text_frame = ttk.Frame(frame)
        text_frame.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(text_frame, orient="vertical")
        text = tk.Text(
            text_frame,
            wrap="word",
            yscrollcommand=scroll.set,
            bg=c["surface"],
            fg=c["fg"],
            insertbackground=c["fg"],
            relief="flat",
            padx=8,
            pady=8,
            font=("TkFixedFont", 9),
        )
        scroll.configure(command=text.yview)
        scroll.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)
        text.insert("1.0", MIT_LICENSE_TEXT)
        text.configure(state="disabled")
        ttk.Button(frame, text="Close", width=8, command=dialog.destroy).pack(anchor="e", pady=(6, 0))

    def _process_picker(self, parent: ttk.Frame) -> tk.StringVar:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text="Application", width=11).pack(side="left")
        value = tk.StringVar()
        ttk.Entry(row, textvariable=value, width=20).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse", width=7, command=lambda: self._browse_process(value)).pack(side="left", padx=(4, 0))
        return value

    def _browse_process(self, variable: tk.StringVar) -> None:
        if not self._require_unlock():
            return
        path = filedialog.askopenfilename(title="Select application")
        if path:
            variable.set(os.path.basename(path))

    def _ask_password(self, title: str, prompt: str) -> str | None:
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.transient(self)
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg=self.colors["bg"])
        result: dict[str, str | None] = {"value": None}
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=prompt).pack(anchor="w")
        entry = ttk.Entry(frame, show="*", width=24)
        entry.pack(fill="x", pady=(5, 8))
        buttons = ttk.Frame(frame)
        buttons.pack(anchor="e")

        def submit() -> None:
            result["value"] = entry.get()
            dialog.destroy()

        def cancel() -> None:
            dialog.destroy()

        ttk.Button(buttons, text="Cancel", width=7, command=cancel).pack(side="right")
        ttk.Button(buttons, text="OK", width=7, command=submit).pack(side="right", padx=(0, 4))
        dialog.bind("<Return>", lambda _e: submit())
        dialog.bind("<Escape>", lambda _e: cancel())
        dialog.update_idletasks()
        width, height = 285, 120
        x = self.winfo_rootx() + max(0, (self.winfo_width() - width) // 2)
        y = self.winfo_rooty() + max(0, (self.winfo_height() - height) // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        entry.focus_set()
        self.wait_window(dialog)
        return result["value"]

    def _ensure_password(self) -> None:
        if password_is_configured():
            self._unlocked = False
            self._update_lock_ui()
            return
        messagebox.showinfo("Create Password", "Create an AutoShutdown administrator password.")
        while not password_is_configured():
            first = self._ask_password("New Password", "Enter password")
            if first is None:
                self.exit_application(force=True)
                return
            if len(first) < 6:
                messagebox.showerror("Too Short", "Use at least 6 characters.")
                continue
            second = self._ask_password("Confirm Password", "Enter password again")
            if first != second:
                messagebox.showerror("Mismatch", "Passwords do not match.")
                continue
            set_password(first)
            self._unlocked = True
            self._update_lock_ui()

    def unlock_app(self) -> None:
        if self._unlocked:
            self._unlocked = False
            self._update_lock_ui()
            return
        password = self._ask_password("Unlock AutoShutdown", "Password")
        if password is None:
            return
        if verify_password(password):
            self._unlocked = True
            self._update_lock_ui()
            self._set_status("Settings unlocked.")
        else:
            messagebox.showerror("Access Denied", "Incorrect password.")

    def _update_lock_ui(self) -> None:
        self.lock_button.configure(text="Lock" if self._unlocked else "Unlock")
        self.cat_message.set("settings unlocked" if self._unlocked else "guardian ready")

    def _require_unlock(self) -> bool:
        if self._unlocked:
            return True
        self.show_window()
        messagebox.showwarning("Locked", "Unlock AutoShutdown before making changes.")
        return False

    def change_password(self) -> None:
        current = self._ask_password("Change Password", "Current password")
        if current is None or not verify_password(current):
            if current is not None:
                messagebox.showerror("Access Denied", "Incorrect password.")
            return
        new = self._ask_password("Change Password", "New password")
        if not new or len(new) < 6:
            messagebox.showerror("Invalid Password", "Use at least 6 characters.")
            return
        confirm = self._ask_password("Change Password", "Confirm new password")
        if new != confirm:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return
        set_password(new)
        self._set_status("Password changed.")

    def _parse_duration(self, raw: str, label: str) -> int | None:
        try:
            return autoshutdown.parse_duration(raw)
        except Exception:
            messagebox.showerror("Invalid Time", f"Invalid value for {label}.")
            return None

    def _activate_task(self, label: str, seconds: int) -> None:
        self._task_active = True
        self._countdown_deadline = time.monotonic() + max(0, seconds)
        self._countdown_label = label
        self._warning_sent = False
        self.state_var.set("ACTIVE")
        self.task_var.set(label)
        self.cat_message.set("timer running")
        self.desktop.set_title(f"{label} - {clock_text(seconds)}")
        self.desktop.notify("AutoShutdown", f"{label} scheduled in {clock_text(seconds)}.")

    def _finish_task(self, message: str = "Ready.") -> None:
        was_active = self._task_active
        self._task_active = False
        self._countdown_deadline = None
        self._warning_sent = False
        self.state_var.set("READY")
        self.countdown_var.set("00:00:00")
        self.task_var.set("No active task")
        self._set_status(message)
        self.cat_message.set("settings unlocked" if self._unlocked else "guardian ready")
        self.desktop.set_title("Ready")
        if was_active and message != "Ready.":
            self.desktop.notify("AutoShutdown", message)

    def _update_countdown(self) -> None:
        if self._task_active and self._countdown_deadline is not None:
            remaining = max(0, int(self._countdown_deadline - time.monotonic() + 0.999))
            text = clock_text(remaining)
            self.countdown_var.set(text)
            self.desktop.set_title(f"{self._countdown_label} - {text}")
            if 0 < remaining <= 60 and not self._warning_sent:
                self._warning_sent = True
                self.desktop.notify("AutoShutdown warning", f"{self._countdown_label} in {text}.")
        self.after(200, self._update_countdown)

    def _animate_cat(self) -> None:
        self._cat_shift = (self._cat_shift + 1) % 4
        offsets = ("", " ", "  ", " ")
        prefix = offsets[self._cat_shift]
        self.cat_label.configure(text="\n".join(prefix + line for line in CAT_ART.splitlines()))
        self.after(450, self._animate_cat)

    def _start_worker(self, target, *args) -> bool:
        if self._worker and self._worker.is_alive():
            messagebox.showwarning("Task Active", "Stop the active task first.")
            return False
        self._cancel_event.clear()
        self._worker = threading.Thread(target=target, args=args, daemon=True)
        self._worker.start()
        return True

    def schedule_power(self) -> None:
        if not self._require_unlock():
            return
        delay = self._parse_duration(self.power_delay.get(), "Run after")
        if delay is None:
            return
        action = self.power_action.get()
        if self._start_worker(self._power_worker, action, delay):
            self._activate_task(action.title(), delay)

    def _power_worker(self, action: str, delay: int) -> None:
        if action in {"shutdown", "restart"}:
            code = autoshutdown.run_command(autoshutdown.command_for(action, delay), False)
            if code != 0:
                self.after(0, self._finish_task, f"Failed to schedule {action}.")
            return
        if self._cancel_event.wait(delay):
            return
        autoshutdown.run_command(autoshutdown.command_for("logout"), False)

    def schedule_close_app(self) -> None:
        if not self._require_unlock():
            return
        process = self.close_process.get().strip()
        if not process:
            messagebox.showerror("Application Required", "Select or enter an application.")
            return
        delay = self._parse_duration(self.close_delay.get(), "Close after")
        if delay is None:
            return
        if self._start_worker(self._close_worker, process, delay):
            self._activate_task(f"Close {process}", delay)

    def _close_worker(self, process: str, delay: int) -> None:
        if self._cancel_event.wait(delay):
            return
        count = self._terminate_processes(process)
        self.after(0, self._finish_task, f"Closed {count} matching process(es).")

    def schedule_restrict_app(self) -> None:
        if not self._require_unlock():
            return
        process = self.restrict_process.get().strip()
        if not process:
            messagebox.showerror("Application Required", "Select or enter an application.")
            return
        start = self._parse_duration(self.restrict_start.get(), "Start after")
        duration = self._parse_duration(self.restrict_duration.get(), "Restrict for")
        if start is None or duration is None or duration <= 0:
            return
        if not messagebox.askyesno("Start Restriction?", f"{process} will be closed whenever detected during the restriction period."):
            return
        if self._start_worker(self._restrict_worker, process, start, duration):
            self._activate_task(f"Restrict {process}", start + duration)

    def _restrict_worker(self, process: str, start: int, duration: int) -> None:
        if self._cancel_event.wait(start):
            return
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline and not self._cancel_event.is_set():
            self._terminate_processes(process)
            time.sleep(self.POLL_SECONDS)
        if not self._cancel_event.is_set():
            self.after(0, self._finish_task, "Restriction completed.")

    @staticmethod
    def _terminate_processes(process_name: str) -> int:
        wanted = os.path.basename(process_name).casefold()
        count = 0
        current_pid = os.getpid()
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info.get("pid") == current_pid:
                    continue
                if (proc.info.get("name") or "").casefold() != wanted:
                    continue
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except psutil.TimeoutExpired:
                    proc.kill()
                count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return count

    def cancel_active_task(self) -> None:
        if not self._require_unlock():
            return
        self._cancel_event.set()
        try:
            autoshutdown.run_command(autoshutdown.command_for("cancel"), False)
        except Exception:
            pass
        self._finish_task("Task stopped.")

    def hide_to_tray(self) -> None:
        if self.desktop.available:
            self.withdraw()
            self._set_status("Running in system tray.")
            self.desktop.notify("AutoShutdown", "AutoShutdown is still running in the system tray.")
        else:
            self.iconify()
            self._set_status("Tray support is unavailable; window minimized.")

    def show_window(self) -> None:
        self.deiconify()
        self.lift()
        try:
            self.focus_force()
        except tk.TclError:
            pass

    def tray_stop_task(self) -> None:
        self.show_window()
        if self._task_active:
            self.cancel_active_task()
        else:
            self._set_status("No active task.")

    def exit_application(self, force: bool = False) -> None:
        self.show_window()
        if self._task_active and not force:
            if not messagebox.askyesno("Exit AutoShutdown?", "Exit will stop the active AutoShutdown task. Continue?"):
                return
        self._cancel_event.set()
        if self._task_active:
            try:
                autoshutdown.run_command(autoshutdown.command_for("cancel"), False)
            except Exception:
                pass
        self.desktop.stop()
        self.destroy()

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _on_close(self) -> None:
        if self.desktop.available:
            self.hide_to_tray()
        else:
            self.exit_application()


def main() -> None:
    AutoShutdownGUI().mainloop()


if __name__ == "__main__":
    main()
