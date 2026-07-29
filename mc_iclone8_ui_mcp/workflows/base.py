from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..contracts import ToolResult
from ..ui_driver.windows import WindowsUIDriver


@dataclass
class WorkflowContext:
    driver: WindowsUIDriver
    confirm_destructive: bool = False


class Workflow:
    name = "workflow"

    def __init__(self, context: WorkflowContext) -> None:
        self.context = context

    def blocked(self, target: str, reason: str, next_step: str) -> dict[str, Any]:
        return ToolResult("blocked", self.name, target, warnings=[reason], next_step=next_step).as_dict()


def require_confirmation(confirmed: bool, action: str) -> None:
    if not confirmed:
        raise PermissionError(f"Confirmation explicite requise pour: {action}")
