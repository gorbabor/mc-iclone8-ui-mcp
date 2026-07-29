from __future__ import annotations

from typing import Any

from .windows import WindowsUIDriver


class AccessibilityUnavailable(RuntimeError):
    pass


class WindowsAccessibilityReader:
    """Optional UI Automation reader; it never performs UI actions."""

    def __init__(self, driver: WindowsUIDriver) -> None:
        self.driver = driver

    def read_tree(self, max_elements: int = 250) -> dict[str, Any]:
        try:
            from pywinauto import Desktop
        except ImportError as exc:
            raise AccessibilityUnavailable(
                "Le backend UI Automation nécessite pywinauto: pip install -e .[windows-ui]"
            ) from exc

        windows = self.driver.enumerate_windows()
        if not windows:
            raise AccessibilityUnavailable("Fenêtre iClone 8 non détectée")

        root = Desktop(backend="uia").window(handle=windows[0].handle)
        elements: list[dict[str, Any]] = []
        for control in root.descendants()[:max_elements]:
            try:
                info = control.element_info
                elements.append({
                    "control_type": info.control_type,
                    "name": info.name,
                    "automation_id": info.automation_id,
                    "class_name": info.class_name,
                    "enabled": bool(info.enabled),
                    "visible": bool(info.visible),
                })
            except Exception:
                continue
        return {
            "backend": "uia",
            "window": windows[0].title,
            "element_count": len(elements),
            "elements": elements,
            "read_only": True,
        }
