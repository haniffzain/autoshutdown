#!/usr/bin/env python3
"""Desktop UI for AutoShutdown.

Features:
- Timed shutdown/restart/logout
- Timed close application
- Timed restrict application
- Password-protected changes
- Quick time presets
- Animated ASCII cat panel
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

import psutil

import autoshutdown


APP_DIR = Path.home() / ".autoshutdown"
SECURITY_FILE = APP_DIR / "security.json"
PBKDF2_ITERATIONS = 250_000
TIME_PRESETS = (
    ("5 min", "5m"),
    ("15 min", "15m"),
    ("30 min", "30m"),
    ("1 hr", "1h"),
    ("2 hr", "2h"),
    ("3 hr", "3h"),
)

CAT_FRAMES = (
    """       /\\_/\\
      ( o.o )
       > ^ <
     __/   \\__
    /  Auto   \\
   / Shutdown  \\
""",
    """        /\\_/\\
       ( -.- )
        > ^ <
      __/   \\__
     /  Auto   \\
    / Shutdown  \\
""",
    """         /\\_/\\
        ( o.o )
         > ^ <
       __/   \\__
      /  Auto   \\
     / Shutdown  \\
""",
    """        /\\_/\\
       ( ^.^ )
        > ^ <
      __/   \\__
     /  Auto   \\
    / Shutdown  \\
""",
)


def _hash_password(password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    ).hex()


def password_is_configured() -> bool:
    return SECURITY_FILE.exists()


def set_password(password: str) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    salt = secrets.token_bytes(16)
    payload = {
        "version": 1,
        "iterations": PBKDF2_ITERATIONS,
        "salt": salt.hex(),
        "password_hash": _hash_password(password, salt),
    }
    SECURITY_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    try:
        os.chmod(SECURITY_FILE, 0o600)
    except OSError:
        pass


def verify_password(password: str) -> bool:
    if not password_is_configured():
        return False
    try:
        data = json.loads(SECURITY_FILE.read_text(encoding="utf-8"))
        salt = bytes.fromhex(data["salt"])
        iterations = int(data.get("iterations", PBKDF2_ITERATIONS))
        expected = data["password_hash"]
        actual = _hash_password(password, salt, iterations)
        return secrets.compare_digest(actual, expected)
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False


class AutoShutdownGUI(tk.Tk):
    POLL_SECONDS = 1.0
    CAT_INTERVAL_MS = 380

    def __init__(self) -> None:
        super().__init__()
        self.title("AutoShutdown")
        self.geometry("1040x700")
        self.minsize(920, 620)

        self._cancel_event = threading.Event()
        self._worker: threading.Thread | None = None
        self._unlocked = False
        self._cat_frame = 0

        self._build_style()
        self._build_ui()
        self.after(120, self._ensure_password)
        self.after(self.CAT_INTERVAL_MS, self._animate_cat)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("TkDefaultFont", 20, "bold"))
        style.configure("Section.TLabel", font=("TkDefaultFont", 12, "bold"))
        style.configure("Status.TLabel", font=("TkDefaultFont", 11))

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        body = ttk.Frame(root)
        body.pack(fill="both", expand=True)

        self._build_cat_panel(body)

        main = ttk.Frame(body, padding=(18, 0, 0, 0))
        main.pack(side="left", fill="both", expand=True)

        header = ttk.Frame(main)
        header.pack(fill="x")
        ttk.Label(header, text="AutoShutdown", style="Title.TLabel").pack(side="left")

        self.lock_button = ttk.Button(header, text="Unlock", command=self.unlock_app)
        self.lock_button.pack(side="right")
        ttk.Button(header, text="Change Password", command=self.change_password).pack(
            side="right", padx=(0, 8)
        )

        ttk.Label(
            main,
            text="Timed shutdown, logout, close app dan restrict app.",
        ).pack(anchor="w", pady=(2, 16))

        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill="both", expand=True)

        self._build_power_tab()
        self._build_close_tab()
        self._build_restrict_tab()

        footer = ttk.Frame(main)
        footer.pack(fill="x", pady=(14, 0))

        self.status_var = tk.StringVar(value="Sedia.")
        ttk.Label(footer, textvariable=self.status_var, style="Status.TLabel").pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(footer, text="Cancel Active Task", command=self.cancel_active_task).pack(
            side="right"
        )

    def _build_cat_panel(self, parent: ttk.Frame) -> None:
        panel = tk.Frame(parent, width=245, bg="#111317", bd=0)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)

        tk.Label(
            panel,
            text="AUTOSHUTDOWN",
            bg="#111317",
            fg="#f2f2f2",
            font=("TkFixedFont", 14, "bold"),
        ).pack(pady=(34, 12))

        self.cat_label = tk.Label(
            panel,
            text=CAT_FRAMES[0],
            justify="left",
            anchor="center",
            bg="#111317",
            fg="#f2f2f2",
            font=("TkFixedFont", 13),
        )
        self.cat_label.pack(fill="x", padx=12, pady=(38, 6))

        self.cat_message = tk.StringVar(value="guardian is awake")
        tk.Label(
            panel,
            textvariable=self.cat_message,
            bg="#111317",
            fg="#d0d0d0",
            font=("TkFixedFont", 10),
        ).pack(pady=8)

        tk.Label(
            panel,
            text="[ timer armed ]\n[ app guard ready ]\n[ password lock ]",
            justify="left",
            bg="#111317",
            fg="#b8b8b8",
            font=("TkFixedFont", 9),
        ).pack(side="bottom", anchor="w", padx=20, pady=24)

    def _animate_cat(self) -> None:
        self._cat_frame = (self._cat_frame + 1) % len(CAT_FRAMES)
        self.cat_label.configure(text=CAT_FRAMES[self._cat_frame])
        self.after(self.CAT_INTERVAL_MS, self._animate_cat)

    def _duration_row(self, parent: ttk.Frame, label: str, default: str) -> tk.StringVar:
        wrapper = ttk.Frame(parent)
        wrapper.pack(fill="x", pady=8)

        row = ttk.Frame(wrapper)
        row.pack(fill="x")
        ttk.Label(row, text=label, width=19).pack(side="left")
        value = tk.StringVar(value=default)
        ttk.Entry(row, textvariable=value, width=14).pack(side="left")

        presets = ttk.Frame(wrapper)
        presets.pack(anchor="w", padx=(132, 0), pady=(5, 0))
        for text, duration in TIME_PRESETS:
            ttk.Button(
                presets,
                text=text,
                width=7,
                command=lambda d=duration, var=value: var.set(d),
            ).pack(side="left", padx=(0, 4))

        return value

    def _build_power_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=18)
        self.notebook.add(tab, text="Power / Logout")

        ttk.Label(tab, text="Timed Shutdown / Logout", style="Section.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Pilih tindakan dan tempoh sebelum ia dijalankan.").pack(
            anchor="w", pady=(3, 12)
        )

        action_row = ttk.Frame(tab)
        action_row.pack(fill="x", pady=8)
        ttk.Label(action_row, text="Tindakan", width=19).pack(side="left")
        self.power_action = tk.StringVar(value="shutdown")
        ttk.Combobox(
            action_row,
            textvariable=self.power_action,
            values=("shutdown", "restart", "logout"),
            state="readonly",
            width=16,
        ).pack(side="left")

        self.power_delay = self._duration_row(tab, "Jalankan selepas", "30m")
        ttk.Button(tab, text="Schedule", command=self.schedule_power).pack(anchor="w", pady=16)

    def _build_close_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=18)
        self.notebook.add(tab, text="Close App")

        ttk.Label(tab, text="Timed Close App", style="Section.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Tutup aplikasi tertentu selepas tempoh yang ditetapkan.").pack(
            anchor="w", pady=(3, 12)
        )

        self.close_process = self._process_picker(tab, "Process / executable")
        self.close_delay = self._duration_row(tab, "Tutup selepas", "15m")
        ttk.Button(tab, text="Schedule Close", command=self.schedule_close_app).pack(
            anchor="w", pady=16
        )
        ttk.Label(
            tab,
            text="Amaran: aplikasi yang ditutup mungkin mempunyai kerja yang belum disimpan.",
            wraplength=610,
        ).pack(anchor="w")

    def _build_restrict_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=18)
        self.notebook.add(tab, text="Restrict App")

        ttk.Label(tab, text="Timed Restrict App", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            tab,
            text=(
                "Apabila sekatan aktif, proses sasaran akan ditutup setiap kali dikesan "
                "sehingga tempoh sekatan tamat."
            ),
            wraplength=610,
        ).pack(anchor="w", pady=(3, 12))

        self.restrict_process = self._process_picker(tab, "Process / executable")
        self.restrict_start = self._duration_row(tab, "Mulakan selepas", "5m")
        self.restrict_duration = self._duration_row(tab, "Sekat selama", "1h")
        ttk.Button(tab, text="Start Restriction", command=self.schedule_restrict_app).pack(
            anchor="w", pady=16
        )

    def _process_picker(self, parent: ttk.Frame, label: str) -> tk.StringVar:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=8)
        ttk.Label(row, text=label, width=19).pack(side="left")
        value = tk.StringVar()
        ttk.Entry(row, textvariable=value, width=30).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse…", command=lambda: self._browse_process(value)).pack(
            side="left", padx=(8, 0)
        )
        return value

    def _browse_process(self, variable: tk.StringVar) -> None:
        if not self._require_unlock():
            return
        path = filedialog.askopenfilename(title="Pilih executable aplikasi")
        if path:
            variable.set(os.path.basename(path))

    def _ensure_password(self) -> None:
        if password_is_configured():
            self._unlocked = False
            self._update_lock_ui()
            return

        messagebox.showinfo(
            "Tetapkan kata laluan",
            "Tetapkan kata laluan pentadbir AutoShutdown. Ia diperlukan untuk mengubah task atau sekatan.",
        )
        while not password_is_configured():
            first = simpledialog.askstring("Kata laluan baharu", "Masukkan kata laluan:", show="*")
            if first is None:
                self.destroy()
                return
            if len(first) < 6:
                messagebox.showerror("Terlalu pendek", "Gunakan sekurang-kurangnya 6 aksara.")
                continue
            second = simpledialog.askstring("Sahkan kata laluan", "Masukkan semula kata laluan:", show="*")
            if first != second:
                messagebox.showerror("Tidak sepadan", "Kata laluan tidak sepadan.")
                continue
            set_password(first)
            self._unlocked = True
            self._update_lock_ui()
            messagebox.showinfo("Berjaya", "App Lock telah diaktifkan.")

    def unlock_app(self) -> None:
        if self._unlocked:
            self._unlocked = False
            self._update_lock_ui()
            return
        password = simpledialog.askstring("Unlock AutoShutdown", "Kata laluan:", show="*")
        if password is None:
            return
        if verify_password(password):
            self._unlocked = True
            self._update_lock_ui()
            self._set_status("Tetapan dibuka untuk modifikasi.")
        else:
            messagebox.showerror("Akses ditolak", "Kata laluan tidak betul.")

    def _update_lock_ui(self) -> None:
        self.lock_button.configure(text="Lock" if self._unlocked else "Unlock")
        self.cat_message.set("settings unlocked" if self._unlocked else "guardian is awake")

    def _require_unlock(self) -> bool:
        if self._unlocked:
            return True
        messagebox.showwarning("App dikunci", "Unlock dengan kata laluan sebelum membuat perubahan.")
        return False

    def change_password(self) -> None:
        if not password_is_configured():
            self._ensure_password()
            return
        current = simpledialog.askstring("Change Password", "Kata laluan semasa:", show="*")
        if current is None:
            return
        if not verify_password(current):
            messagebox.showerror("Akses ditolak", "Kata laluan semasa tidak betul.")
            return
        new = simpledialog.askstring("Change Password", "Kata laluan baharu:", show="*")
        if new is None:
            return
        if len(new) < 6:
            messagebox.showerror("Terlalu pendek", "Gunakan sekurang-kurangnya 6 aksara.")
            return
        confirm = simpledialog.askstring("Change Password", "Masukkan semula kata laluan baharu:", show="*")
        if new != confirm:
            messagebox.showerror("Tidak sepadan", "Kata laluan baharu tidak sepadan.")
            return
        set_password(new)
        self._unlocked = True
        self._update_lock_ui()
        messagebox.showinfo("Berjaya", "Kata laluan telah ditukar.")

    def _parse_duration_field(self, raw: str, field_name: str) -> int | None:
        try:
            return autoshutdown.parse_duration(raw)
        except Exception as exc:
            messagebox.showerror("Format masa tidak sah", f"{field_name}: {exc}")
            return None

    def _start_worker(self, target, *args) -> None:
        if self._worker and self._worker.is_alive():
            messagebox.showwarning("Task masih aktif", "Batalkan task aktif sebelum menjadualkan task baharu.")
            return
        self._cancel_event.clear()
        self._worker = threading.Thread(target=target, args=args, daemon=True)
        self._worker.start()

    def _wait_cancelable(self, seconds: int) -> bool:
        return self._cancel_event.wait(timeout=max(0, seconds))

    def schedule_power(self) -> None:
        if not self._require_unlock():
            return
        delay = self._parse_duration_field(self.power_delay.get(), "Jalankan selepas")
        if delay is None:
            return
        self._start_worker(self._power_worker, self.power_action.get(), delay)

    def _power_worker(self, action: str, delay: int) -> None:
        self._set_status(f"{action.title()} dijadualkan dalam {autoshutdown.human_duration(delay)}.")
        if action in {"shutdown", "restart"}:
            code = autoshutdown.run_command(autoshutdown.command_for(action, delay), False)
            self._set_status(
                f"{action.title()} telah dijadualkan oleh sistem."
                if code == 0
                else f"Gagal menjadualkan {action}."
            )
            return
        if self._wait_cancelable(delay):
            self._set_status("Logout dibatalkan.")
            return
        autoshutdown.run_command(autoshutdown.command_for("logout"), False)

    def schedule_close_app(self) -> None:
        if not self._require_unlock():
            return
        process_name = self.close_process.get().strip()
        if not process_name:
            messagebox.showerror("Aplikasi diperlukan", "Masukkan nama process atau pilih executable.")
            return
        delay = self._parse_duration_field(self.close_delay.get(), "Tutup selepas")
        if delay is not None:
            self._start_worker(self._close_worker, process_name, delay)

    def _close_worker(self, process_name: str, delay: int) -> None:
        self._set_status(f"{process_name} akan ditutup dalam {autoshutdown.human_duration(delay)}.")
        if self._wait_cancelable(delay):
            self._set_status("Timed Close App dibatalkan.")
            return
        count = self._terminate_processes(process_name)
        self._set_status(f"Timed Close selesai: {count} process {process_name} ditutup.")

    def schedule_restrict_app(self) -> None:
        if not self._require_unlock():
            return
        process_name = self.restrict_process.get().strip()
        if not process_name:
            messagebox.showerror("Aplikasi diperlukan", "Masukkan nama process atau pilih executable.")
            return
        start_delay = self._parse_duration_field(self.restrict_start.get(), "Mulakan selepas")
        duration = self._parse_duration_field(self.restrict_duration.get(), "Sekat selama")
        if start_delay is None or duration is None or duration <= 0:
            return
        if not messagebox.askyesno(
            "Aktifkan sekatan?",
            f"{process_name} akan ditutup automatik sepanjang sekatan. Kerja belum disimpan boleh hilang. Teruskan?",
        ):
            return
        self._start_worker(self._restrict_worker, process_name, start_delay, duration)

    def _restrict_worker(self, process_name: str, start_delay: int, duration: int) -> None:
        self._set_status(f"Sekatan {process_name} bermula dalam {autoshutdown.human_duration(start_delay)}.")
        if self._wait_cancelable(start_delay):
            self._set_status("Timed Restrict App dibatalkan.")
            return
        deadline = time.monotonic() + duration
        self._set_status(f"Sekatan {process_name} aktif selama {autoshutdown.human_duration(duration)}.")
        while time.monotonic() < deadline:
            if self._cancel_event.is_set():
                self._set_status("Timed Restrict App dibatalkan.")
                return
            self._terminate_processes(process_name)
            time.sleep(self.POLL_SECONDS)
        self._set_status(f"Sekatan {process_name} tamat.")

    @staticmethod
    def _terminate_processes(process_name: str) -> int:
        wanted = os.path.basename(process_name).casefold()
        current_pid = os.getpid()
        count = 0
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
        self._set_status("Permintaan cancel dihantar.")

    def _set_status(self, text: str) -> None:
        self.after(0, self.status_var.set, text)

    def _on_close(self) -> None:
        self._cancel_event.set()
        self.destroy()


def main() -> None:
    AutoShutdownGUI().mainloop()


if __name__ == "__main__":
    main()
