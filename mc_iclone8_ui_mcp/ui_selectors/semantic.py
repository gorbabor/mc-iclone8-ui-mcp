from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticSelector:
    key: str
    names: tuple[str, ...] = ()
    automation_ids: tuple[str, ...] = ()
    control_types: tuple[str, ...] = ()


SELECTORS = {
    "scene_manager": SemanticSelector(
        "scene_manager", ("Scene", "Scène"),
        (":/plugin/ICListManager/ICListManager.ui.ListManager",),
        ("Window", "Group"),
    ),
    "modify": SemanticSelector("modify", ("Modify", "Modifier"), control_types=("Window", "Group")),
    "content": SemanticSelector("content", ("Content", "Contenu"), control_types=("Tab", "Window")),
    "timeline": SemanticSelector("timeline", ("Timeline", "Chronologie"), control_types=("Window", "Group")),
    "render": SemanticSelector("render", ("Render", "Rendu"), control_types=("MenuItem", "Button")),
}


def get_selector(key: str) -> SemanticSelector:
    try:
        return SELECTORS[key]
    except KeyError as exc:
        raise ValueError(f"Sélecteur inconnu: {key}") from exc
