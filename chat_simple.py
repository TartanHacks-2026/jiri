"""
Simple Interactive Dedalus Chat - Just chat, no MCP complexity
"""

import asyncio

from dotenv import load_dotenv

from dedalus import DedalusClient

# Load environment variables
load_dotenv()


async def interactive_chat():
    """Run an interactive chat session"""
    print("\n" + "=" * 70)
    print("  🤖 Dedalus Chat")
    print("=" * 70)
    print("\nChat with Claude Sonnet 4 powered by Dedalus Labs")
    print("Type 'quit' to exit, 'help' for commands\n")

    # Initialize
    try:
        client = DedalusClient()
        print("✓ Connected\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure DEDALUS_API_KEY is set in .env\n")
        return

    # Chat loop
    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!\n")
                break

            if user_input.lower() == "help":
                print("\nCommands:")
                print("  quit/exit/q - Exit chat")
                print("  clear - Clear screen")
                print("  help - Show this message\n")
                continue

            if user_input.lower() == "clear":
                print("\033[2J\033[H")
                continue

            # Get response
            print("AI: ", end="", flush=True)
            response = await client.chat(user_input)
            print(response + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(interactive_chat())
