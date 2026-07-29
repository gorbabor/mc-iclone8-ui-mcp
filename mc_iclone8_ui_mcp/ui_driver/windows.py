from __future__ import annotations

import ctypes
import ctypes.wintypes as wintypes
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class WindowInfo:
    handle: int
    process_id: int
    title: str
    visible: bool
    foreground: bool
    rect: tuple[int, int, int, int] | None


class WindowsUIDriver:
    """Read-only Win32 inspection with optional screenshot support."""

    def __init__(self, title_pattern: str = "iClone 8") -> None:
        self.title_pattern = title_pattern.casefold()
        self._stop_requested = False
        self.target_handle: int | None = None

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
            normalized = title.casefold()
            is_iclone_app = normalized.startswith("iclone 8 -") or normalized == "iclone 8"
            if self.title_pattern in normalized and is_iclone_app:
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                process_id = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
                found.append(WindowInfo(int(hwnd), int(process_id.value), title, True, int(hwnd) == foreground,
                                        (rect.left, rect.top, rect.right, rect.bottom)))
            return True

        user32.EnumWindows(callback, 0)
        found.sort(key=lambda item: (0 if item.title.casefold().startswith("iclone 8 -") else 1, 0 if item.foreground else 1))
        return found

    def inspect(self) -> dict:
        windows = [asdict(item) for item in self.enumerate_windows()]
        return {"application": "iClone 8", "windows": windows,
                "target_window": next((w for w in windows if w["handle"] == self.target_handle), None),
                "focused_window": next((w for w in windows if w["foreground"]), None),
                "read_only": True}

    def target_window(self) -> WindowInfo | None:
        windows = self.enumerate_windows()
        if self.target_handle is not None:
            return next((window for window in windows if window.handle == self.target_handle), None)
        return windows[0] if windows else None

    def set_target(self, handle: int) -> WindowInfo:
        window = next((item for item in self.enumerate_windows() if item.handle == handle), None)
        if window is None:
            raise RuntimeError(f"Instance iClone 8 introuvable: {handle}")
        self.target_handle = handle
        return window

    def activate(self, handle: int) -> dict:
        if not hasattr(ctypes, "windll"):
            raise RuntimeError("Activation de fenêtre disponible uniquement sous Windows")
        window = self.set_target(handle)
        user32 = ctypes.windll.user32
        user32.ShowWindow(window.handle, 9)
        user32.BringWindowToTop(window.handle)
        user32.SetForegroundWindow(window.handle)
        deadline = time.monotonic() + 2.0
        while int(user32.GetForegroundWindow()) != window.handle and time.monotonic() < deadline:
            time.sleep(0.05)
        refreshed = next((item for item in self.enumerate_windows() if item.handle == window.handle), window)
        return {"target": asdict(refreshed), "focus_acquired": refreshed.foreground, "restored": True}

    def can_interact(self) -> tuple[bool, str]:
        window = self.target_window()
        if window is None:
            return False, "Fenêtre iClone 8 non détectée"
        if not window.foreground:
            return False, "iClone 8 doit être au premier plan"
        if window.rect and (window.rect[2] <= window.rect[0] or window.rect[3] <= window.rect[1]):
            return False, "Fenêtre iClone 8 minimisée ou hors écran"
        return True, "ok"

    def capture_screen(self, output: Path, window_only: bool = False) -> str:
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            from PIL import ImageGrab
        except ImportError as exc:
            raise RuntimeError("Pillow est requis pour les captures: pip install -e .[screenshots]") from exc
        bbox = None
        if window_only:
            window = self.target_window()
            if window is None:
                raise RuntimeError("Fenêtre iClone 8 non détectée")
            bbox = window.rect
        ImageGrab.grab(bbox=bbox).save(output)
        return str(output)

    def request_stop(self) -> None:
        self._stop_requested = True

    def reset_stop(self) -> None:
        self._stop_requested = False

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested
