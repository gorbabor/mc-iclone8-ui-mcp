"""Smoke test sans dépendance externe: python tests/smoke_test.py"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from mc_iclone8_ui_mcp.mcp_server.server import MCPServer


server = MCPServer()
assert server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})["result"]["serverInfo"]["name"] == "mc-iclone8-ui-mcp"
response = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "workflow.stop_all", "arguments": {}}})
payload = json.loads(response["result"]["content"][0]["text"])
assert payload["status"] == "ok"
assert payload["verification"]["stop_requested"] is True
uia = server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "ui.inspect_accessibility_tree", "arguments": {}}})
assert json.loads(uia["result"]["content"][0]["text"])["status"] in {"ok", "blocked"}
print("smoke test: ok")
