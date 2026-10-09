"""Discover FlashData MCP tools without making a paid query."""

import asyncio
import os

from fastmcp.client.transports import StreamableHttpTransport
from langchain.mcp import MCPAdapter


async def main() -> None:
    transport = StreamableHttpTransport(
        "https://data.flashdata.dev/mcp",
        headers={"X-API-Key": os.environ["FLASHDATA_API_KEY"]},
    )
    async with MCPAdapter(transport) as adapter:
        tools = await adapter.list_tools()
        print(f"Discovered {len(tools)} tools:")
        for tool in tools:
            print(tool.name)
        # Pass selected tools to create_agent(model, tools=selected_tools).
        # The hosted catalog includes more capabilities than the four native tools.


if __name__ == "__main__":
    asyncio.run(main())
