"""User-level startup integration for Linux and Windows."""

from __future__ import annotations

import os
import platform
import shlex
import sys
from pathlib import Path

APP_DIR = Path.home() / ".autoshutdown"
LINUX_AUTOSTART = Path.home() / ".config" / "autostart" / "autoshutdown.desktop"


def _launch_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable)}"'
    gui = Path(__file__).resolve().parents[1] / "gui.py"
    return f'"{Path(sys.executable)}" "{gui}"'


def is_enabled() -> bool:
    system = platform.system().lower()
    if system == "windows":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                winreg.QueryValueEx(key, "AutoShutdown")
            return True
        except Exception:
            return False
    if system == "linux":
        return LINUX_AUTOSTART.exists()
    return False


def enable() -> None:
    system = platform.system().lower()
    command = _launch_command()
    if system == "windows":
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
            winreg.SetValueEx(key, "AutoShutdown", 0, winreg.REG_SZ, command)
        return
    if system == "linux":
        LINUX_AUTOSTART.parent.mkdir(parents=True, exist_ok=True)
        LINUX_AUTOSTART.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=AutoShutdown\n"
            "Comment=Start AutoShutdown with the desktop session\n"
            f"Exec={command}\n"
            "Terminal=false\n"
            "X-GNOME-Autostart-enabled=true\n",
            encoding="utf-8",
        )
        return
    raise RuntimeError(f"Startup integration is not supported on {platform.system()}.")


def disable() -> None:
    system = platform.system().lower()
    if system == "windows":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, "AutoShutdown")
        except FileNotFoundError:
            pass
        return
    if system == "linux":
        try:
            LINUX_AUTOSTART.unlink()
        except FileNotFoundError:
            pass
        return
    raise RuntimeError(f"Startup integration is not supported on {platform.system()}.")
