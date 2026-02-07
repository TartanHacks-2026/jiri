"""
Dedalus Integration Demo - Complete example using Dedalus Labs SDK and MCP server
https://docs.dedaluslabs.ai/dmcp/server/overview
"""

import asyncio
import os

from dotenv import load_dotenv

from dedalus import DedalusClient
from mcp_server import create_dedalus_mcp_server

# Load environment variables from .env file
load_dotenv()


async def run_mcp_server_demo():
    """Demo the MCP server standalone"""
    print("\n" + "=" * 70)
    print("📡 Dedalus MCP Server Standalone Demo")
    print("=" * 70 + "\n")

    # Create the MCP server
    server = create_dedalus_mcp_server()

    print("\n📋 Testing MCP Server Tools:")
    print("-" * 70)

    # Note: In production, these tools would be called by the SDK through the server
    # For demo purposes, we're showing what the server provides
    print("\n✓ Server initialized with tools:")
    print("  - log_hello: Logs 'hello' to the console")
    print("  - log_message: Logs a custom message")
    print("  - get_server_info: Get server information")
    print("  - add_numbers: Add two numbers together")

    print("\n💡 To run the server, use: python mcp_server.py")
    print("   The server will listen for MCP requests on the configured port")


async def run_sdk_demo():
    """Demo the Dedalus SDK"""
    print("\n" + "=" * 70)
    print("🤖 Dedalus SDK Demo")
    print("=" * 70 + "\n")

    # Check for API key
    api_key = os.getenv("DEDALUS_API_KEY")
    if not api_key:
        print("⚠️  DEDALUS_API_KEY not set in environment")
        print("\n   To use the Dedalus SDK:")
        print("   1. Sign up at https://dedaluslabs.ai")
        print("   2. Get your API key")
        print("   3. Add to .env: DEDALUS_API_KEY=your-key")
        print("   4. Run this demo again\n")
        return

    try:
        # Initialize client
        client = DedalusClient(api_key=api_key)

        # Test 1: Simple chat
        print("📝 Test 1: Simple chat (no MCP)")
        print("-" * 70)
        response = await client.chat(
            "Hello! Introduce yourself in one sentence as Dedalus, an AI assistant.",
        )
        print(f"🤖 Dedalus: {response}\n")

        # Test 2: Explain MCP integration
        print("\n📝 Test 2: MCP capabilities")
        print("-" * 70)
        response = await client.chat(
            "Explain what MCP (Model Context Protocol) is in one sentence.",
        )
        print(f"🤖 Dedalus: {response}\n")

        # Test 3: With local MCP server (if running)
        print("\n📝 Test 3: Integration with local MCP server")
        print("-" * 70)
        print("   To use this, you need to:")
        print("   1. Run 'python mcp_server.py' in another terminal")
        print("   2. Ensure it's serving on http://localhost:8000/mcp")
        print("   3. Then the SDK can connect and use the tools\n")

        # Example of how it would work (commented out - requires running server)
        print("   Example code:")
        print("   ```python")
        print("   response = await client.run_with_local_mcp(")
        print('       "Please log hello using the log_hello tool",')
        print('       mcp_url="http://localhost:8000/mcp"')
        print("   )")
        print("   ```\n")

    except Exception as e:
        print(f"❌ Error: {e}\n")
        print("   Make sure DEDALUS_API_KEY is set correctly")


async def run_full_integration_demo():
    """Demo showing how SDK and MCP server work together"""
    print("\n" + "=" * 70)
    print("🔗 Full Integration: SDK + MCP Server")
    print("=" * 70 + "\n")

    print("How the integration works:")
    print("-" * 70)
    print()
    print("1. MCP Server:")
    print("   - Registers tools using @tool decorator")
    print("   - Serves tools via HTTP endpoint")
    print("   - Handles tool execution")
    print()
    print("2. Dedalus SDK:")
    print("   - Connects to MCP server (local or hosted)")
    print("   - Discovers available tools")
    print("   - Passes tools to LLM context")
    print()
    print("3. LLM (Claude, GPT, etc.):")
    print("   - Sees available tools in context")
    print("   - Decides when to use tools")
    print("   - SDK executes tools via MCP server")
    print()
    print("4. Result:")
    print("   - AI can use tools dynamically")
    print("   - Tools run in sandboxed environment")
    print("   - Responses include tool outputs")
    print()
    print("-" * 70)
    print()
    print("📚 Learn more at: https://docs.dedaluslabs.ai/dmcp/server/overview")


async def main():
    """Main demo entry point"""
    print("\n" + "=" * 80)
    print(" 🚀 Dedalus Labs Integration Demo")
    print(" Using official Dedalus SDK and MCP framework")
    print("=" * 80)

    # Run MCP server demo
    await run_mcp_server_demo()

    # Run SDK demo
    await run_sdk_demo()

    # Explain full integration
    await run_full_integration_demo()

    # Summary
    print("\n" + "=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
    print("\n📦 Next Steps:")
    print("  1. Install dependencies: uv sync")
    print("  2. Set DEDALUS_API_KEY in .env")
    print("  3. Start MCP server: python mcp_server.py")
    print("  4. Use SDK to connect: python dedalus.py")
    print()
    print("📚 Resources:")
    print("  - Dedalus Labs: https://dedaluslabs.ai")
    print("  - Documentation: https://docs.dedaluslabs.ai")
    print("  - MCP Quickstart: https://docs.dedaluslabs.ai/dmcp/quickstart")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
