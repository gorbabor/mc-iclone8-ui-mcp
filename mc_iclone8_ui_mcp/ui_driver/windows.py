from __future__ import annotations

import ctypes
import ctypes.wintypes as wintypes
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class WindowInfo:
    handle: int
    title: str
    visible: bool
    foreground: bool
    rect: tuple[int, int, int, int] | None


class WindowsUIDriver:
    """Read-only Win32 inspection with optional screenshot support."""

    def __init__(self, title_pattern: str = "iClone 8") -> None:
        self.title_pattern = title_pattern.casefold()
        self._stop_requested = False

    def enumerate_windows(self) -> list[WindowInfo]:
        if not hasattr(ctypes, "windll"):
            return []
        user32 = ctypes.windll.user32
        foreground = int(user32.GetForegroundWindow())
        found: list[WindowInfo] = []

        @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        def callback(hwnd: int, _: int) -> bool:
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            if self.title_pattern in title.casefold():
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                found.append(WindowInfo(int(hwnd), title, True, int(hwnd) == foreground,
                                        (rect.left, rect.top, rect.right, rect.bottom)))
            return True

        user32.EnumWindows(callback, 0)
        return found

    def inspect(self) -> dict:
        windows = [asdict(item) for item in self.enumerate_windows()]
        return {"application": "iClone 8", "windows": windows,
                "focused_window": next((w for w in windows if w["foreground"]), None),
                "read_only": True}

    def capture_screen(self, output: Path, window_only: bool = False) -> str:
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            from PIL import ImageGrab
        except ImportError as exc:
            raise RuntimeError("Pillow est requis pour les captures: pip install -e .[screenshots]") from exc
        bbox = None
        if window_only:
            windows = self.enumerate_windows()
            if not windows:
                raise RuntimeError("Fenêtre iClone 8 non détectée")
            bbox = windows[0].rect
        ImageGrab.grab(bbox=bbox).save(output)
        return str(output)

    def request_stop(self) -> None:
        self._stop_requested = True

    def reset_stop(self) -> None:
        self._stop_requested = False

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested
