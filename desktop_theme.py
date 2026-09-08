"""Desktop-theme detection and palette helpers for AutoShutdown."""

from __future__ import annotations

import platform
import subprocess


def _linux_prefers_dark() -> bool | None:
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            check=False,
            capture_output=True,
            text=True,
            timeout=1.5,
        )
        value = (result.stdout or "").strip().lower()
        if "prefer-dark" in value:
            return True
        if "default" in value or "prefer-light" in value:
            return False
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            check=False,
            capture_output=True,
            text=True,
            timeout=1.5,
        )
        value = (result.stdout or "").strip().lower()
        if value:
            return "dark" in value
    except Exception:
        pass
    return None


def _windows_prefers_dark() -> bool | None:
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return int(value) == 0
    except Exception:
        return None


def prefers_dark() -> bool:
    system = platform.system().lower()
    if system == "linux":
        detected = _linux_prefers_dark()
    elif system == "windows":
        detected = _windows_prefers_dark()
    else:
        detected = None
    return bool(detected) if detected is not None else False


def palette() -> dict[str, str]:
    if prefers_dark():
        return {
            "mode": "dark",
            "bg": "#242424",
            "panel": "#1e1e1e",
            "surface": "#2b2b2b",
            "surface_alt": "#333333",
            "fg": "#f2f2f2",
            "muted": "#b7b7b7",
            "border": "#454545",
            "select": "#3b5f85",
            "select_fg": "#ffffff",
            "cat_bg": "#1e1e1e",
            "cat_fg": "#ededed",
            "cat_muted": "#a7a7a7",
        }
    return {
        "mode": "light",
        "bg": "#f6f6f6",
        "panel": "#eeeeee",
        "surface": "#ffffff",
        "surface_alt": "#e7e7e7",
        "fg": "#202020",
        "muted": "#606060",
        "border": "#c9c9c9",
        "select": "#d8e7f7",
        "select_fg": "#202020",
        "cat_bg": "#ededed",
        "cat_fg": "#202020",
        "cat_muted": "#666666",
    }
