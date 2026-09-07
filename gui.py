#!/usr/bin/env python3
"""Desktop UI for AutoShutdown.

Features:
- Timed shutdown/restart/logout
- Timed close application
- Timed restrict application for a chosen duration

The UI intentionally keeps scheduling local and transparent. Restrict mode checks
for an exact process name and terminates matching processes while the restriction
window is active.
"""

from __future__ import annotations

import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import psutil

import autoshutdown


class AutoShutdownGUI(tk.Tk):
    POLL_SECONDS = 1.0

    def __init__(self) -> None:
        super().__init__()
        self.title("AutoShutdown")
        self.geometry("760x620")
        self.minsize(700, 560)

        self._cancel_event = threading.Event()
        self._worker: threading.Thread | None = None

        self._build_style()
        self._build_ui()
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
        outer = ttk.Frame(self, padding=20)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="AutoShutdown", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="Shutdown, logout, close app dan restrict app mengikut masa.",
        ).pack(anchor="w", pady=(2, 16))

        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill="both", expand=True)

        self._build_power_tab()
        self._build_close_tab()
        self._build_restrict_tab()

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(14, 0))

        self.status_var = tk.StringVar(value="Sedia.")
        ttk.Label(footer, textvariable=self.status_var, style="Status.TLabel").pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(footer, text="Cancel Active Task", command=self.cancel_active_task).pack(
            side="right"
        )

    @staticmethod
    def _duration_row(parent: ttk.Frame, label: str, default: str) -> tk.StringVar:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=8)
        ttk.Label(row, text=label, width=22).pack(side="left")
        value = tk.StringVar(value=default)
        ttk.Entry(row, textvariable=value, width=18).pack(side="left")
        ttk.Label(row, text="contoh: 30s, 15m, 2h").pack(side="left", padx=10)
        return value

    def _build_power_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=18)
        self.notebook.add(tab, text="Power / Logout")

        ttk.Label(tab, text="Timed Shutdown / Logout", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            tab,
            text="Pilih tindakan dan tempoh sebelum ia dijalankan.",
        ).pack(anchor="w", pady=(3, 12))

        action_row = ttk.Frame(tab)
        action_row.pack(fill="x", pady=8)
        ttk.Label(action_row, text="Tindakan", width=22).pack(side="left")
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

        ttk.Separator(tab).pack(fill="x", pady=12)
        ttk.Label(
            tab,
            text=(
                "Nota: shutdown/restart menggunakan arahan native OS. Logout dijalankan "
                "oleh AutoShutdown selepas countdown tamat."
            ),
            wraplength=620,
        ).pack(anchor="w")

    def _build_close_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=18)
        self.notebook.add(tab, text="Close App")

        ttk.Label(tab, text="Timed Close App", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            tab,
            text="Tutup aplikasi tertentu selepas tempoh yang ditetapkan.",
        ).pack(anchor="w", pady=(3, 12))

        self.close_process = self._process_picker(tab, "Process / executable")
        self.close_delay = self._duration_row(tab, "Tutup selepas", "15m")

        ttk.Button(tab, text="Schedule Close", command=self.schedule_close_app).pack(
            anchor="w", pady=16
        )

        ttk.Label(
            tab,
            text="Amaran: aplikasi yang ditutup mungkin mempunyai kerja yang belum disimpan.",
            wraplength=620,
        ).pack(anchor="w")

    def _build_restrict_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=18)
        self.notebook.add(tab, text="Restrict App")

        ttk.Label(tab, text="Timed Restrict App", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            tab,
            text=(
                "Selepas masa mula dicapai, AutoShutdown akan menutup proses sasaran "
                "setiap kali ia dikesan sepanjang tempoh sekatan."
            ),
            wraplength=620,
        ).pack(anchor="w", pady=(3, 12))

        self.restrict_process = self._process_picker(tab, "Process / executable")
        self.restrict_start = self._duration_row(tab, "Mulakan selepas", "0s")
        self.restrict_duration = self._duration_row(tab, "Sekat selama", "1h")

        ttk.Button(tab, text="Start Restriction", command=self.schedule_restrict_app).pack(
            anchor="w", pady=16
        )

        ttk.Label(
            tab,
            text=(
                "Sekatan ini hanya aktif selagi AutoShutdown berjalan. Ia tidak mengubah "
                "permissions, registry atau polisi keselamatan sistem."
            ),
            wraplength=620,
        ).pack(anchor="w")

    def _process_picker(self, parent: ttk.Frame, label: str) -> tk.StringVar:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=8)
        ttk.Label(row, text=label, width=22).pack(side="left")
        value = tk.StringVar()
        ttk.Entry(row, textvariable=value, width=32).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse…", command=lambda: self._browse_process(value)).pack(
            side="left", padx=(8, 0)
        )
        return value

    def _browse_process(self, variable: tk.StringVar) -> None:
        path = filedialog.askopenfilename(title="Pilih executable aplikasi")
        if path:
            variable.set(os.path.basename(path))

    def _parse_duration_field(self, raw: str, field_name: str) -> int | None:
        try:
            return autoshutdown.parse_duration(raw)
        except Exception as exc:
            messagebox.showerror("Format masa tidak sah", f"{field_name}: {exc}")
            return None

    def _start_worker(self, target, *args) -> None:
        if self._worker and self._worker.is_alive():
            messagebox.showwarning(
                "Task masih aktif",
                "Batalkan task aktif sebelum menjadualkan task baharu.",
            )
            return
        self._cancel_event.clear()
        self._worker = threading.Thread(target=target, args=args, daemon=True)
        self._worker.start()

    def _wait_cancelable(self, seconds: int) -> bool:
        return self._cancel_event.wait(timeout=max(0, seconds))

    def schedule_power(self) -> None:
        delay = self._parse_duration_field(self.power_delay.get(), "Jalankan selepas")
        if delay is None:
            return
        action = self.power_action.get()
        self._start_worker(self._power_worker, action, delay)

    def _power_worker(self, action: str, delay: int) -> None:
        self._set_status(f"{action.title()} dijadualkan dalam {autoshutdown.human_duration(delay)}.")

        if action in {"shutdown", "restart"}:
            command = autoshutdown.command_for(action, delay)
            code = autoshutdown.run_command(command, False)
            if code == 0:
                self._set_status(f"{action.title()} telah dijadualkan oleh sistem.")
            else:
                self._set_status(f"Gagal menjadualkan {action}.")
            return

        if self._wait_cancelable(delay):
            self._set_status("Logout dibatalkan.")
            return
        code = autoshutdown.run_command(autoshutdown.command_for("logout"), False)
        if code != 0:
            self._set_status("Logout gagal dijalankan.")

    def schedule_close_app(self) -> None:
        process_name = self.close_process.get().strip()
        if not process_name:
            messagebox.showerror("Aplikasi diperlukan", "Masukkan nama process atau pilih executable.")
            return
        delay = self._parse_duration_field(self.close_delay.get(), "Tutup selepas")
        if delay is None:
            return
        self._start_worker(self._close_worker, process_name, delay)

    def _close_worker(self, process_name: str, delay: int) -> None:
        self._set_status(
            f"{process_name} akan ditutup dalam {autoshutdown.human_duration(delay)}."
        )
        if self._wait_cancelable(delay):
            self._set_status("Timed Close App dibatalkan.")
            return
        count = self._terminate_processes(process_name)
        self._set_status(f"Timed Close selesai: {count} process {process_name} ditutup.")

    def schedule_restrict_app(self) -> None:
        process_name = self.restrict_process.get().strip()
        if not process_name:
            messagebox.showerror("Aplikasi diperlukan", "Masukkan nama process atau pilih executable.")
            return
        start_delay = self._parse_duration_field(self.restrict_start.get(), "Mulakan selepas")
        duration = self._parse_duration_field(self.restrict_duration.get(), "Sekat selama")
        if start_delay is None or duration is None:
            return
        if duration <= 0:
            messagebox.showerror("Tempoh tidak sah", "Tempoh sekatan mestilah lebih daripada 0 saat.")
            return

        confirmed = messagebox.askyesno(
            "Aktifkan sekatan aplikasi?",
            (
                f"Sepanjang tempoh sekatan, {process_name} akan ditutup secara automatik "
                "jika ia dikesan. Kerja yang belum disimpan boleh hilang. Teruskan?"
            ),
        )
        if not confirmed:
            return

        self._start_worker(self._restrict_worker, process_name, start_delay, duration)

    def _restrict_worker(self, process_name: str, start_delay: int, duration: int) -> None:
        self._set_status(
            f"Sekatan {process_name} bermula dalam {autoshutdown.human_duration(start_delay)}."
        )
        if self._wait_cancelable(start_delay):
            self._set_status("Timed Restrict App dibatalkan.")
            return

        deadline = time.monotonic() + duration
        self._set_status(
            f"Sekatan {process_name} aktif selama {autoshutdown.human_duration(duration)}."
        )

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
        count = 0
        current_pid = os.getpid()

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = (proc.info.get("name") or "").casefold()
                if proc.info.get("pid") == current_pid or name != wanted:
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
        self._cancel_event.set()
        # Also ask the OS to cancel any native shutdown/restart timer.
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
    app = AutoShutdownGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
