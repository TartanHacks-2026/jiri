from dedalus_mcp.client import open_connection

async def main():
    async with open_connection("http://localhost:3333/mcp") as client:
    # async with open_connection("https://mcp.deepwiki.com/mcp") as client:
        tools = await client.list_tools()

        print("Available tools in Uber MCP:")   
        for tool in tools.tools:
            print(f"{tool.name}: {tool.description}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())