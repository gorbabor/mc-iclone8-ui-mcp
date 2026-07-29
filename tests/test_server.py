import json

from mc_iclone8_ui_mcp.mcp_server.server import MCPServer


def test_initialize_and_tools_list():
    server = MCPServer()
    initialized = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert initialized["result"]["serverInfo"]["name"] == "mc-iclone8-ui-mcp"
    listed = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert {tool["name"] for tool in listed["result"]["tools"]} == {
        "ui.inspect_application", "ui.capture_screen", "scene.read_visible_state", "workflow.stop_all"
    }


def test_result_contract_and_stop():
    server = MCPServer()
    response = server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "workflow.stop_all", "arguments": {}}})
    payload = json.loads(response["result"]["content"][0]["text"])
    assert set(payload) == {"status", "action", "target", "screenshots", "observed_state_before", "observed_state_after", "verification", "warnings", "next_step"}
    assert payload["status"] == "ok"
    assert payload["verification"]["stop_requested"] is True
