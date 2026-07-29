from __future__ import annotations

from typing import Any

from .windows import WindowsUIDriver


class AccessibilityUnavailable(RuntimeError):
    pass


class WindowsAccessibilityReader:
    """Optional UI Automation reader; it never performs UI actions."""

    def __init__(self, driver: WindowsUIDriver) -> None:
        self.driver = driver

    def read_tree(self, max_elements: int = 80) -> dict[str, Any]:
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
        # iClone exposes a large/custom-drawn UI tree. A recursive descendants()
        # walk can block for a long time, so the safe first pass is shallow.
        for control in root.children()[:max_elements]:
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
            "depth": 1,
            "window": windows[0].title,
            "element_count": len(elements),
            "elements": elements,
            "read_only": True,
        }

    def read_named_control(self, name: str, max_elements: int = 80) -> dict[str, Any]:
        """Read one named direct child and its immediate children, without actions."""
        tree = self.read_tree(max_elements=max_elements)
        windows = self.driver.enumerate_windows()
        from pywinauto import Desktop
        root = Desktop(backend="uia").window(handle=windows[0].handle)

        def find_named(parent: Any, wanted: str, depth: int = 3) -> Any | None:
            if depth <= 0:
                return None
            for child in parent.children()[:max_elements]:
                if child.element_info.name == wanted:
                    return child
                found = find_named(child, wanted, depth - 1)
                if found is not None:
                    return found
            return None

        control = find_named(root, name)
        if control is None:
            raise AccessibilityUnavailable(f"Contrôle UIA introuvable: {name}")
        info = control.element_info
        match = {
            "control_type": info.control_type,
            "name": info.name,
            "automation_id": info.automation_id,
            "class_name": info.class_name,
            "enabled": bool(info.enabled),
            "visible": bool(info.visible),
        }
        children: list[dict[str, Any]] = []
        for child in control.children()[:max_elements]:
            try:
                info = child.element_info
                children.append({
                    "control_type": info.control_type,
                    "name": info.name,
                    "automation_id": info.automation_id,
                    "class_name": info.class_name,
                    "enabled": bool(info.enabled),
                    "visible": bool(info.visible),
                })
            except Exception:
                continue
        return {"backend": "uia", "control": match, "children": children, "read_only": True}

    def read_automation_control(self, automation_id: str, max_elements: int = 80) -> dict[str, Any]:
        windows = self.driver.enumerate_windows()
        if not windows:
            raise AccessibilityUnavailable("Fenêtre iClone 8 non détectée")
        from pywinauto import Desktop
        root = Desktop(backend="uia").window(handle=windows[0].handle)

        def find_id(parent: Any, wanted: str, depth: int = 4) -> Any | None:
            if depth <= 0:
                return None
            for child in parent.children()[:max_elements]:
                actual_id = child.element_info.automation_id
                if actual_id == wanted or (wanted.startswith(":/") and actual_id.endswith(wanted)):
                    return child
                found = find_id(child, wanted, depth - 1)
                if found is not None:
                    return found
            return None

        control = find_id(root, automation_id)
        if control is None:
            raise AccessibilityUnavailable(f"Contrôle UIA introuvable: {automation_id}")
        info = control.element_info
        children: list[dict[str, Any]] = []
        for child in control.children()[:max_elements]:
            try:
                child_info = child.element_info
                children.append({
                    "control_type": child_info.control_type,
                    "name": child_info.name,
                    "automation_id": child_info.automation_id,
                    "class_name": child_info.class_name,
                    "enabled": bool(child_info.enabled),
                    "visible": bool(child_info.visible),
                })
            except Exception:
                continue
        return {
            "backend": "uia",
            "control": {"control_type": info.control_type, "name": info.name, "automation_id": info.automation_id, "class_name": info.class_name, "enabled": bool(info.enabled), "visible": bool(info.visible)},
            "children": children,
            "read_only": True,
        }

    def read_bounded_descendants(self, automation_id: str, max_elements: int = 200, max_depth: int = 4) -> dict[str, Any]:
        """Read a bounded UIA subtree using children(), avoiding unbounded descendants()."""
        windows = self.driver.enumerate_windows()
        if not windows:
            raise AccessibilityUnavailable("Fenêtre iClone 8 non détectée")
        from pywinauto import Desktop
        root = Desktop(backend="uia").window(handle=windows[0].handle)

        def find_id(parent: Any, wanted: str, depth: int) -> Any | None:
            if depth < 0:
                return None
            for child in parent.children()[:max_elements]:
                actual_id = child.element_info.automation_id
                if actual_id == wanted or (wanted.startswith(":/") and actual_id.endswith(wanted)):
                    return child
                found = find_id(child, wanted, depth - 1)
                if found is not None:
                    return found
            return None

        control = find_id(root, automation_id, max_depth)
        if control is None:
            raise AccessibilityUnavailable(f"Contrôle UIA introuvable: {automation_id}")
        queue: list[tuple[Any, int]] = [(control, 0)]
        elements: list[dict[str, Any]] = []
        while queue and len(elements) < max_elements:
            current, depth = queue.pop(0)
            if depth > 0:
                info = current.element_info
                elements.append({"depth": depth, "control_type": info.control_type, "name": info.name, "automation_id": info.automation_id, "class_name": info.class_name, "enabled": bool(info.enabled), "visible": bool(info.visible)})
            if depth < max_depth:
                queue.extend((child, depth + 1) for child in current.children()[:max_elements - len(elements)])
        return {"backend": "uia", "root_automation_id": automation_id, "max_depth": max_depth, "element_count": len(elements), "elements": elements, "read_only": True}
