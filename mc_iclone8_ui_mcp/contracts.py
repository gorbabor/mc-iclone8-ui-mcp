from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Status = Literal["ok", "failed", "blocked"]


@dataclass
class ToolResult:
    status: Status
    action: str
    target: str
    screenshots: list[str] = field(default_factory=list)
    observed_state_before: dict[str, Any] = field(default_factory=dict)
    observed_state_after: dict[str, Any] = field(default_factory=dict)
    verification: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    next_step: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "action": self.action,
            "target": self.target,
            "screenshots": self.screenshots,
            "observed_state_before": self.observed_state_before,
            "observed_state_after": self.observed_state_after,
            "verification": self.verification,
            "warnings": self.warnings,
            "next_step": self.next_step,
        }
