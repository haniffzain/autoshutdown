"""Cross-platform desktop tray integration for AutoShutdown."""

from __future__ import annotations

import threading

try:
    import pystray
    from PIL import Image, ImageDraw
except Exception:  # Optional fallback for environments without tray support.
    pystray = None
    Image = None
    ImageDraw = None


class DesktopIntegration:
    """Small wrapper around pystray so the main GUI stays toolkit-focused."""

    def __init__(self, app) -> None:
        self.app = app
        self.icon = None
        self._thread: threading.Thread | None = None
        self.available = pystray is not None and Image is not None and ImageDraw is not None

    @staticmethod
    def _image():
        image = Image.new("RGBA", (64, 64), (18, 20, 24, 255))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((8, 8, 56, 56), radius=12, outline=(235, 235, 235, 255), width=3)
        draw.arc((18, 18, 46, 46), 210, 510, fill=(235, 235, 235, 255), width=4)
        draw.line((32, 16, 32, 31), fill=(235, 235, 235, 255), width=4)
        return image

    def start(self) -> bool:
        if not self.available or self.icon is not None:
            return self.available

        menu = pystray.Menu(
            pystray.MenuItem("Open AutoShutdown", self._open, default=True),
            pystray.MenuItem("Hide Window", self._hide),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Stop Task", self._stop_task),
            pystray.MenuItem("Exit", self._exit),
        )
        self.icon = pystray.Icon("AutoShutdown", self._image(), "AutoShutdown - Ready", menu)
        self._thread = threading.Thread(target=self.icon.run, name="autoshutdown-tray", daemon=True)
        self._thread.start()
        return True

    def _open(self, _icon=None, _item=None) -> None:
        self.app.after(0, self.app.show_window)

    def _hide(self, _icon=None, _item=None) -> None:
        self.app.after(0, self.app.hide_to_tray)

    def _stop_task(self, _icon=None, _item=None) -> None:
        self.app.after(0, self.app.tray_stop_task)

    def _exit(self, _icon=None, _item=None) -> None:
        self.app.after(0, self.app.exit_application)

    def set_title(self, text: str) -> None:
        if self.icon is not None:
            self.icon.title = f"AutoShutdown - {text}"[:128]

    def notify(self, title: str, message: str) -> None:
        if self.icon is None:
            return
        try:
            self.icon.notify(message, title)
        except Exception:
            pass

    def stop(self) -> None:
        icon, self.icon = self.icon, None
        if icon is not None:
            try:
                icon.stop()
            except Exception:
                pass
