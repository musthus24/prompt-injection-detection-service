"""Builds the FastMCP server: registers the three tools, attaches the
on_call_tool policy middleware.

Runnable directly: `python -m app.mcp.server` (stdio transport).
"""

from fastmcp import FastMCP

from .middleware import _make_middleware, _registry

mcp = FastMCP("mcp-security-gateway")
mcp.add_middleware(_make_middleware())


@mcp.tool
def read_file(path: str) -> dict:
    """Read a file from the sandbox directory."""
    return _registry.execute("read_file", {"path": path})


@mcp.tool
def fetch_url(url: str) -> dict:
    """Fetch a URL (stubbed - no real network call)."""
    return _registry.execute("fetch_url", {"url": url})


@mcp.tool
def send_email(to: str, body: str) -> dict:
    """Send an email (stubbed - never actually sends)."""
    return _registry.execute("send_email", {"to": to, "body": body})


if __name__ == "__main__":
    mcp.run()
