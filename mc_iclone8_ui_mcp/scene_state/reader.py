from __future__ import annotations

from ..ui_driver.windows import WindowsUIDriver


class VisibleSceneStateReader:
    def __init__(self, driver: WindowsUIDriver) -> None:
        self.driver = driver

    def read(self) -> dict:
        ui = self.driver.inspect()
        return {"application": ui["application"], "window": ui["focused_window"],
                "scene_manager": "not_read_without_accessibility_backend",
                "timeline": "not_read_without_accessibility_backend",
                "camera": "not_read_without_accessibility_backend",
                "selection": "not_read_without_accessibility_backend",
                "read_only": True}
