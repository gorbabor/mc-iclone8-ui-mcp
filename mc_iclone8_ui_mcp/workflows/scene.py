from __future__ import annotations

from typing import Any

from ..contracts import ToolResult
from ..ui_driver.accessibility import AccessibilityUnavailable, WindowsAccessibilityReader
from ..ui_driver.windows import WindowsUIDriver
from .base import Workflow, WorkflowContext


SCENE_MANAGER_ID = "iClone6 MainWindow.:/plugin/ICListManager/ICListManager.ui.ListManager"


class SceneManagerReadWorkflow(Workflow):
    name = "scene.read_manager"

    def __init__(self, context: WorkflowContext) -> None:
        super().__init__(context)
        self.reader = WindowsAccessibilityReader(context.driver)

    def run(self, max_elements: int = 200, max_depth: int = 4) -> dict[str, Any]:
        before = self.context.driver.inspect()
        try:
            state = self.reader.read_bounded_descendants(SCENE_MANAGER_ID, max_elements, max_depth)
            return ToolResult("ok", self.name, "Scene Manager", observed_state_before=before, observed_state_after=state, verification={"read_only": True, "element_count": state["element_count"], "visual_verification": False}, next_step="Comparer les noms accessibles avec une capture avant d'activer une sélection UI.").as_dict()
        except AccessibilityUnavailable as exc:
            return ToolResult("blocked", self.name, "Scene Manager", observed_state_before=before, warnings=[str(exc)], next_step="Vérifier iClone 8 et UI Automation.").as_dict()
