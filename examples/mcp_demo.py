"""MCP security gateway demo: one benign call allowed, one malicious call blocked."""

import asyncio

from fastmcp import Client

from app.mcp.server import mcp


async def main():
    async with Client(mcp) as client:
        print("Benign call: read_file('notes.txt')")
        benign = await client.call_tool_mcp("read_file", {"path": "notes.txt"})
        print(f"  blocked={benign.isError}  result={benign.content}\n")

        print("Malicious call: read_file('../../etc/passwd')")
        malicious = await client.call_tool_mcp("read_file", {"path": "../../etc/passwd"})
        print(f"  blocked={malicious.isError}  result={malicious.content}")


asyncio.run(main())
