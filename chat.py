"""
Interactive Dedalus Chat - Chat with AI in your terminal with MCP tools
"""

import asyncio
import sys

from dotenv import load_dotenv

from dedalus import DedalusClient

# Load environment variables
load_dotenv()


async def check_mcp_server():
    """Check if MCP server is running"""
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=2.0)
            return response.status_code == 200
    except Exception:
        return False


async def interactive_chat(use_mcp: bool = True):
    """Run an interactive chat session in the terminal"""
    print("\n" + "=" * 70)
    print("  🤖 Dedalus Interactive Chat")
    print("=" * 70)

    # Initialize client
    try:
        client = DedalusClient()
        print("✓ Connected to Dedalus AI")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure DEDALUS_API_KEY is set in your .env file")
        return

    # Check for MCP server
    mcp_available = False
    if use_mcp:
        print("🔍 Checking for MCP server...", end="", flush=True)
        mcp_available = await check_mcp_server()
        if mcp_available:
            print(" ✓ MCP server detected!")
            print("   Available tools: log_hello, log_message, get_server_info, add_numbers")
        else:
            print(" ⚠️  No MCP server found")
            print("   To enable tools, run in another terminal: python mcp_server.py")
            print("   Continuing with chat only...\n")

    print("\nType your questions and press Enter. Type 'quit', 'exit', or 'q' to stop.")
    print("Type 'help' for available commands.\n")

    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            # Check for exit commands
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!\n")
                break

            # Check for help
            if user_input.lower() == "help":
                print("\n📚 Available commands:")
                print("  - Type any question to chat with the AI")
                print("  - 'help' - Show this help message")
                print("  - 'tools' - List available tools")
                print("  - 'clear' - Clear the screen")
                print("  - 'quit', 'exit', 'q' - Exit the chat")
                print()
                continue

            # Show tools
            if user_input.lower() == "tools":
                if mcp_available:
                    print("\n🛠️  Available MCP Tools:")
                    print("  - log_hello: Logs 'hello' to the console")
                    print("  - log_message: Logs a custom message")
                    print("  - get_server_info: Get server information")
                    print("  - add_numbers: Add two numbers together")
                    print("\nExample: 'Use the add_numbers tool to calculate 5 + 3'\n")
                else:
                    print("\n⚠️  No tools available. Start MCP server with: python mcp_server.py\n")
                continue

            # Clear screen
            if user_input.lower() == "clear":
                print("\033[2J\033[H")  # ANSI escape codes to clear screen
                continue

            # Skip empty input
            if not user_input:
                continue

            # Get AI response (with or without MCP)
            print("🤖 Dedalus: ", end="", flush=True)
            if mcp_available:
                response = await client.run_with_local_mcp(
                    user_input, mcp_url="http://localhost:8000/mcp"
                )
            else:
                response = await client.chat(user_input)
            print(response + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


async def main():
    # Check command line arguments
    use_mcp = True
    if len(sys.argv) > 1 and sys.argv[1] == "--no-mcp":
        use_mcp = False

    await interactive_chat(use_mcp=use_mcp)


if __name__ == "__main__":
    asyncio.run(main())
