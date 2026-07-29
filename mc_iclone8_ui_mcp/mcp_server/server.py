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

log = logging.getLogger("mc-iclone8-ui-mcp")


class MCPServer:
    def __init__(self, driver: WindowsUIDriver | None = None) -> None:
        self.driver = driver or WindowsUIDriver()
        self.state_reader = VisibleSceneStateReader(self.driver)
        self.accessibility_reader = WindowsAccessibilityReader(self.driver)
        self.started_at = time.time()

    def tools(self) -> list[dict[str, Any]]:
        return [
            {"name": "ui.inspect_application", "description": "Inspecte les fenêtres visibles iClone 8 en lecture seule.", "inputSchema": {"type": "object", "properties": {}}},
            {"name": "ui.inspect_accessibility_tree", "description": "Lit les contrôles directs Windows UI Automation sans effectuer d'action.", "inputSchema": {"type": "object", "properties": {"max_elements": {"type": "integer", "minimum": 1, "maximum": 250, "default": 80}}}},
            {"name": "ui.inspect_named_control", "description": "Inspecte un contrôle UIA nommé et ses enfants directs, sans action.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "max_elements": {"type": "integer", "minimum": 1, "maximum": 250, "default": 80}}, "required": ["name"]}},
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
        return result.as_dict()

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
