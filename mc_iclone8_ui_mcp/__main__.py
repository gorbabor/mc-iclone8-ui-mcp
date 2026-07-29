from .mcp_server.server import MCPServer


def main() -> None:
    MCPServer().run_stdio()


if __name__ == "__main__":
    main()
