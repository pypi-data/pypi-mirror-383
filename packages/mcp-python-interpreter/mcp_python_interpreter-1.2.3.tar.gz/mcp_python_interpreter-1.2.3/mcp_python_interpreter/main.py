"""Main module for mcp-python-interpreter."""

from mcp_python_interpreter.server import mcp


def main():
    """Run the MCP Python Interpreter server."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()