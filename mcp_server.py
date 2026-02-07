"""
Dedalus MCP Server - Model Context Protocol server with basic tools
Built using the official Dedalus Labs MCP framework
https://docs.dedaluslabs.ai/dmcp/server/overview
"""

import asyncio
from datetime import datetime

from dedalus_mcp import MCPServer, tool


# ============================================
# Tool Implementations
# ============================================


@tool(description="Logs 'hello' to the console")
def log_hello() -> str:
    """Basic tool that logs 'hello' to the console"""
    message = "Hello from Dedalus MCP Server! 👋"
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
    print(f"{'='*50}\n")
    return message


@tool(description="Logs a custom message to the console")
def log_message(message: str) -> str:
    """Tool that logs a custom message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(f"\n📝 MCP Log: {log_msg}")
    return log_msg


@tool(description="Get information about the MCP server status and version")
def get_server_info() -> dict[str, str]:
    """Get information about the MCP server"""
    return {
        "server": "Dedalus MCP Server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "status": "running",
    }


@tool(description="Add two numbers together")
def add_numbers(a: int, b: int) -> int:
    """Add two numbers and return the result"""
    result = a + b
    print(f"\n🔢 Adding {a} + {b} = {result}")
    return result


# ============================================
# Server Initialization
# ============================================


def create_dedalus_mcp_server() -> MCPServer:
    """
    Create and initialize the Dedalus MCP server with all tools

    NOTE: Server name must match your deployment slug if deploying to Dedalus Labs
    """
    server = MCPServer("dedalus-demo")

    # Collect all tools decorated with @tool
    server.collect(log_hello)
    server.collect(log_message)
    server.collect(get_server_info)
    server.collect(add_numbers)

    print("✓ Dedalus MCP Server initialized")
    print(f"  - Registered tools: log_hello, log_message, get_server_info, add_numbers")

    return server


# ============================================
# Server Entry Point
# ============================================


async def main():
    """Run the MCP server"""
    server = create_dedalus_mcp_server()

    print("\n" + "=" * 60)
    print("Starting Dedalus MCP Server...")
    print("=" * 60)
    print("\n🌐 MCP Server will be available for connections")
    print("💡 To chat with tools, run in another terminal:")
    print("   python chat.py")
    print("\n" + "=" * 60 + "\n")

    # Serve the MCP server
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
