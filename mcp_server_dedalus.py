# server.py
from dedalus_mcp import MCPServer, tool

@tool(description="Add two numbers")
def add(a: int, b: int) -> int:
    return a + b

@tool(description="Multiply two numbers")
def multiply(a: int, b: int) -> int:
    return a * b

server = MCPServer("calculator")
server.collect(add, multiply)

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.serve())