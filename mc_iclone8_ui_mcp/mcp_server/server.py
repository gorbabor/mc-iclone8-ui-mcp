from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

from ..contracts import ToolResult
from ..scene_state.reader import VisibleSceneStateReader
from ..ui_driver.accessibility import AccessibilityUnavailable, WindowsAccessibilityReader
from ..ui_driver.windows import WindowsUIDriver
from ..workflows.catalog import planned_workflows
from ..workflows.scene import SceneManagerReadWorkflow
from ..workflows.base import WorkflowContext

log = logging.getLogger("mc-iclone8-ui-mcp")


class MCPServer:
    def __init__(self, driver: WindowsUIDriver | None = None) -> None:
        self.driver = driver or WindowsUIDriver()
        self.state_reader = VisibleSceneStateReader(self.driver)
        self.accessibility_reader = WindowsAccessibilityReader(self.driver)
        self.scene_workflow = SceneManagerReadWorkflow(WorkflowContext(self.driver))
        self.planned = planned_workflows(self.driver)
        self.started_at = time.time()
        self.interaction_mode = "observe"

    def tools(self) -> list[dict[str, Any]]:
        return [
            {"name": "ui.inspect_application", "description": "Inspecte les fenêtres visibles iClone 8 en lecture seule.", "inputSchema": {"type": "object", "properties": {}}},
            {"name": "ui.list_instances", "description": "Liste les instances iClone 8 détectées avec handle, PID, projet et focus.", "inputSchema": {"type": "object", "properties": {}}},
            {"name": "ui.get_active_instance", "description": "Retourne l’instance iClone 8 ciblée et l’état du focus.", "inputSchema": {"type": "object", "properties": {}}},
            {"name": "ui.activate_instance", "description": "Restaure et place une instance iClone 8 au premier plan.", "inputSchema": {"type": "object", "properties": {"handle": {"type": "integer"}}, "required": ["handle"]}},
            {"name": "ui.set_interaction_mode", "description": "Configure observe, interact ou session.", "inputSchema": {"type": "object", "properties": {"mode": {"type": "string", "enum": ["observe", "interact", "session"]}}, "required": ["mode"]}},
            {"name": "ui.inspect_accessibility_tree", "description": "Lit les contrôles directs Windows UI Automation sans effectuer d'action.", "inputSchema": {"type": "object", "properties": {"max_elements": {"type": "integer", "minimum": 1, "maximum": 250, "default": 80}}}},
            {"name": "ui.inspect_named_control", "description": "Inspecte un contrôle UIA nommé et ses enfants directs, sans action.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "max_elements": {"type": "integer", "minimum": 1, "maximum": 250, "default": 80}}, "required": ["name"]}},
            {"name": "ui.inspect_automation_control", "description": "Inspecte un contrôle UIA par automation_id et ses enfants directs, sans action.", "inputSchema": {"type": "object", "properties": {"automation_id": {"type": "string"}, "max_elements": {"type": "integer", "minimum": 1, "maximum": 250, "default": 80}}, "required": ["automation_id"]}},
            {"name": "scene.read_manager", "description": "Lit un sous-arbre borné du Scene Manager en lecture seule.", "inputSchema": {"type": "object", "properties": {"max_elements": {"type": "integer", "minimum": 1, "maximum": 500, "default": 200}, "max_depth": {"type": "integer", "minimum": 1, "maximum": 6, "default": 4}}}},
            {"name": "scene.list_items", "description": "Extrait les TreeItem visibles du Scene Manager en lecture seule.", "inputSchema": {"type": "object", "properties": {"max_elements": {"type": "integer", "minimum": 1, "maximum": 500, "default": 200}, "max_depth": {"type": "integer", "minimum": 1, "maximum": 6, "default": 6}}}},
            {"name": "scene.select_item", "description": "Sélectionne un TreeItem par son nom accessible après confirmation et vérification du focus.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "confirm": {"type": "boolean"}, "max_depth": {"type": "integer", "minimum": 1, "maximum": 6, "default": 6}}, "required": ["name", "confirm"]}},
            {"name": "workflow.catalog", "description": "Retourne l'état des huit familles de workflows, sans action UI.", "inputSchema": {"type": "object", "properties": {}}},
            {"name": "ui.capture_screen", "description": "Capture l'écran ou la fenêtre iClone 8 sans modifier la scène.", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "window_only": {"type": "boolean", "default": True}}, "required": ["path"]}},
            {"name": "scene.read_visible_state", "description": "Lit l'état visible connu de l'interface iClone 8.", "inputSchema": {"type": "object", "properties": {}}},
            {"name": "workflow.stop_all", "description": "Demande l'arrêt propre du workflow UI courant.", "inputSchema": {"type": "object", "properties": {}}},
        ]

    def call(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        before = self.state_reader.read()
        if name == "ui.inspect_application":
            after = self.driver.inspect()
            detected = bool(after.get("windows"))
            result = ToolResult("ok" if detected else "blocked", "inspect_application", "iClone 8", observed_state_before=before, observed_state_after=after, verification={"visual_verification": False, "window_detected": detected, "reason": "inspection only"}, warnings=[] if detected else ["Fenêtre iClone 8 non détectée"], next_step="Si une fenêtre iClone 8 est détectée, lancer uniquement un workflow explicitement confirmé.")
        elif name == "ui.list_instances":
            instances = [window.__dict__ for window in self.driver.enumerate_windows()]
            result = ToolResult("ok" if instances else "blocked", "list_instances", "iClone 8 instances", observed_state_before=before, observed_state_after={"instances": instances, "count": len(instances)}, verification={"read_only": True, "instance_count": len(instances)}, warnings=[] if instances else ["Aucune instance iClone 8 détectée"], next_step="Choisir un handle puis appeler ui.activate_instance.")
        elif name == "ui.get_active_instance":
            target = self.driver.target_window()
            focused = next((window for window in self.driver.enumerate_windows() if window.foreground), None)
            state = {"target": target.__dict__ if target else None, "focused": focused.__dict__ if focused else None, "mode": self.interaction_mode}
            result = ToolResult("ok" if target else "blocked", "get_active_instance", "iClone 8 active instance", observed_state_before=before, observed_state_after=state, verification={"read_only": True, "focus_matches_target": bool(target and focused and target.handle == focused.handle)}, warnings=[] if target else ["Aucune instance iClone 8 détectée"], next_step="Appeler ui.activate_instance si la cible n’est pas au premier plan.")
        elif name == "ui.activate_instance":
            try:
                state = self.driver.activate(int(args["handle"]))
                self.interaction_mode = "interact"
                result = ToolResult("ok" if state["focus_acquired"] else "blocked", "activate_instance", str(args["handle"]), observed_state_before=before, observed_state_after=state, verification={"focus_acquired": state["focus_acquired"], "restored": state["restored"]}, warnings=[] if state["focus_acquired"] else ["Windows n’a pas accordé le focus"], next_step="Vérifier get_active_instance avant une action UI.")
            except (RuntimeError, KeyError) as exc:
                result = ToolResult("blocked", "activate_instance", str(args.get("handle", "")), observed_state_before=before, warnings=[str(exc)], next_step="Relire ui.list_instances et vérifier le handle.")
        elif name == "ui.set_interaction_mode":
            mode = str(args.get("mode", ""))
            if mode not in {"observe", "interact", "session"}:
                result = ToolResult("blocked", "set_interaction_mode", mode, observed_state_before=before, warnings=["Mode invalide"], next_step="Utiliser observe, interact ou session.")
            else:
                self.interaction_mode = mode
                result = ToolResult("ok", "set_interaction_mode", mode, observed_state_before=before, observed_state_after={"mode": mode}, verification={"local_state_updated": True}, next_step="Les actions UI doivent encore vérifier le focus cible.")
        elif name == "ui.inspect_accessibility_tree":
            try:
                tree = self.accessibility_reader.read_tree(int(args.get("max_elements", 250)))
                result = ToolResult("ok", "inspect_accessibility_tree", "iClone 8 UIA tree", observed_state_before=before, observed_state_after=tree, verification={"read_only": True, "backend": "uia", "element_count": tree["element_count"]}, next_step="Utiliser les noms accessibles et rôles retournés pour préparer des sélecteurs sémantiques.")
            except AccessibilityUnavailable as exc:
                result = ToolResult("blocked", "inspect_accessibility_tree", "iClone 8 UIA tree", observed_state_before=before, warnings=[str(exc)], next_step="Installer l'extra windows-ui puis relancer l'inspection.")
        elif name == "ui.inspect_named_control":
            try:
                control_name = str(args["name"])
                state = self.accessibility_reader.read_named_control(control_name, int(args.get("max_elements", 80)))
                result = ToolResult("ok", "inspect_named_control", control_name, observed_state_before=before, observed_state_after=state, verification={"read_only": True, "children_count": len(state["children"])}, next_step="Utiliser les noms retournés pour définir un sélecteur sémantique avant toute action.")
            except (AccessibilityUnavailable, KeyError) as exc:
                result = ToolResult("blocked", "inspect_named_control", str(args.get("name", "")), observed_state_before=before, warnings=[str(exc)], next_step="Vérifier le nom accessible et la disponibilité de UI Automation.")
        elif name == "ui.inspect_automation_control":
            try:
                automation_id = str(args["automation_id"])
                state = self.accessibility_reader.read_automation_control(automation_id, int(args.get("max_elements", 80)))
                result = ToolResult("ok", "inspect_automation_control", automation_id, observed_state_before=before, observed_state_after=state, verification={"read_only": True, "children_count": len(state["children"])}, next_step="Utiliser les enfants retournés pour cartographier le Scene Manager avant toute action.")
            except (AccessibilityUnavailable, KeyError) as exc:
                result = ToolResult("blocked", "inspect_automation_control", str(args.get("automation_id", "")), observed_state_before=before, warnings=[str(exc)], next_step="Vérifier l'automation_id et la disponibilité de UI Automation.")
        elif name == "scene.read_manager":
            result = self.scene_workflow.run(int(args.get("max_elements", 200)), int(args.get("max_depth", 4)))
        elif name == "scene.list_items":
            raw = self.scene_workflow.run(int(args.get("max_elements", 200)), int(args.get("max_depth", 6)))
            if raw["status"] != "ok":
                result = raw
            else:
                elements = raw["observed_state_after"].get("elements", [])
                items = [{"name": item["name"], "depth": item["depth"], "enabled": item["enabled"], "visible": item["visible"]} for item in elements if item["control_type"] == "TreeItem" and item["name"]]
                result = ToolResult("ok", "scene.list_items", "Scene Manager TreeItems", observed_state_before=raw["observed_state_before"], observed_state_after={"items": items, "count": len(items)}, verification={"read_only": True, "item_count": len(items), "visual_verification": False}, next_step="Choisir un nom exact pour le prochain test de sélection UI vérifiée.").as_dict()
        elif name == "scene.select_item":
            target = str(args.get("name", ""))
            if not bool(args.get("confirm", False)):
                result = ToolResult("blocked", "scene.select_item", target, observed_state_before=before, warnings=["Confirmation explicite requise pour modifier la sélection UI."], next_step="Relancer avec confirm=true après avoir vérifié le nom exact.")
            else:
                can_interact, reason = self.driver.can_interact()
                if not can_interact:
                    result = ToolResult("blocked", "scene.select_item", target, observed_state_before=before, warnings=[reason], next_step="Restaurer iClone 8 et le placer au premier plan, puis relancer.")
                else:
                    try:
                        state = self.accessibility_reader.select_tree_item(target, max_depth=int(args.get("max_depth", 6)))
                        verified = state["selected_after"] is True
                        result = ToolResult("ok" if verified else "blocked", "scene.select_item", target, observed_state_before=before, observed_state_after=state, verification={"visual_verification": False, "selected_after": state["selected_after"], "ui_action": "semantic_tree_item_select", "selection_confirmed": verified}, warnings=[] if verified else ["Le contrôle Qt n’expose pas l’état SelectionItem; preuve visuelle requise."], next_step="Capturer l'écran et lire le panneau Modify pour confirmer l'objet sélectionné.")
                    except (AccessibilityUnavailable, RuntimeError, ValueError) as exc:
                        result = ToolResult("blocked", "scene.select_item", target, observed_state_before=before, warnings=[str(exc)], next_step="Vérifier que le TreeItem est visible et que UI Automation est disponible.")
        elif name == "workflow.catalog":
            catalog = {key: {"category": workflow.category, "status": "planned"} for key, workflow in self.planned.items()}
            result = ToolResult("ok", "workflow.catalog", "eight workflow families", observed_state_before=before, observed_state_after=catalog, verification={"read_only": True}, next_step="Activer chaque workflow après validation sur une scène de test iClone 8.")
        elif name in self.planned:
            result = self.planned[name].run(str(args.get("target", name)))
        elif name == "scene.read_visible_state":
            after = self.state_reader.read()
            result = ToolResult("ok", "read_visible_state", "visible iClone 8 state", observed_state_before=before, observed_state_after=after, verification={"read_only": True}, next_step="La lecture d'objets détaillée nécessite un backend d'accessibilité UI.")
        elif name == "ui.capture_screen":
            try:
                path = self.driver.capture_screen(Path(args["path"]), bool(args.get("window_only", True)))
                result = ToolResult("ok", "capture_screen", path, screenshots=[path], observed_state_before=before, observed_state_after=self.driver.inspect(), verification={"file_exists": Path(path).exists(), "visual_verification": True}, next_step="Utiliser la capture pour confirmer visuellement l'état avant toute action.")
            except Exception as exc:
                result = ToolResult("failed", "capture_screen", str(args.get("path", "")), observed_state_before=before, warnings=[str(exc)], next_step="Installer le support capture ou vérifier la fenêtre iClone 8.")
        elif name == "workflow.stop_all":
            self.driver.request_stop()
            result = ToolResult("ok", "stop_all", "local workflow", observed_state_before=before, observed_state_after={"stop_requested": True}, verification={"stop_requested": self.driver.stop_requested}, next_step="Le workflow doit tester ce drapeau entre chaque action UI.")
        else:
            result = ToolResult("blocked", name, "unknown tool", observed_state_before=before, warnings=["Outil inconnu"], next_step="Utiliser tools/list pour obtenir les outils disponibles.")
        return result if isinstance(result, dict) else result.as_dict()

    def handle(self, message: dict[str, Any]) -> dict[str, Any]:
        method = message.get("method")
        request_id = message.get("id")
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "mc-iclone8-ui-mcp", "version": "0.1.0"}}}
        if method == "notifications/initialized":
            return {}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": self.tools()}}
        if method == "tools/call":
            params = message.get("params", {})
            content = self.call(params.get("name", ""), params.get("arguments", {}))
            return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": json.dumps(content, ensure_ascii=False)}], "structuredContent": content}}
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

    def run_stdio(self) -> None:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                response = self.handle(json.loads(line))
                if response:
                    sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                    sys.stdout.flush()
            except Exception as exc:
                log.exception("MCP request failed")
                sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(exc)}}) + "\n")
                sys.stdout.flush()
