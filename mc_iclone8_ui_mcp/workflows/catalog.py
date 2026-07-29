from __future__ import annotations

from typing import Any

from ..contracts import ToolResult
from ..ui_driver.windows import WindowsUIDriver
from .base import Workflow, WorkflowContext


class PlannedWorkflow(Workflow):
    def __init__(self, context: WorkflowContext, name: str, category: str) -> None:
        super().__init__(context)
        self.name = name
        self.category = category

    def run(self, target: str) -> dict[str, Any]:
        return self.blocked(target, f"Workflow {self.category} non activé sans validation UI iClone 8.", "Commencer par une scène de test et une capture avant/après.")


def planned_workflows(driver: WindowsUIDriver) -> dict[str, PlannedWorkflow]:
    context = WorkflowContext(driver)
    return {key: PlannedWorkflow(context, key, category) for key, category in {
        "project": "gestion de projet", "scene": "scène et objets", "paths": "paths et contraintes",
        "animation": "animation", "characters": "personnages", "facial": "facial et parole",
        "camera": "caméra", "materials_lighting_physics_render": "matériaux, lumière, physique et rendu",
    }.items()}
