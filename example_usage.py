"""
Simple example showing how to use Dedalus SDK with MCP Server

This example demonstrates:
1. Creating a simple MCP server with tools
2. Using the Dedalus SDK to interact with the tools
3. Running everything together
"""

import asyncio
import os

from dotenv import load_dotenv

from dedalus import DedalusClient

# Load environment variables from .env file
load_dotenv()


async def example_simple_chat():
    """Example 1: Simple chat without MCP tools"""
    print("\n" + "=" * 60)
    print("Example 1: Simple Chat")
    print("=" * 60 + "\n")

    # Check if API key is set
    if not os.getenv("DEDALUS_API_KEY"):
        print("⚠️  Set DEDALUS_API_KEY in .env first")
        return

    client = DedalusClient()

    response = await client.chat(
        "What is 2+2? Answer in one sentence.",
    )

    print(f"User: What is 2+2?")
    print(f"AI: {response}")


async def example_with_local_mcp():
    """Example 2: Using local MCP server tools"""
    print("\n" + "=" * 60)
    print("Example 2: Using Local MCP Server")
    print("=" * 60 + "\n")

    if not os.getenv("DEDALUS_API_KEY"):
        print("⚠️  Set DEDALUS_API_KEY in .env first")
        return

    print("Note: This requires the MCP server to be running")
    print("      Start it with: python mcp_server.py")
    print()

    client = DedalusClient()

    # Example prompt that would use MCP tools
    prompt = """
    Please do the following:
    1. Use the log_hello tool to greet me
    2. Use the add_numbers tool to calculate 5 + 3
    3. Use the log_message tool to log the result
    """

    print(f"User prompt: {prompt}")
    print("\nNote: The AI will automatically discover and use the available tools")
    print("      Tools: log_hello, log_message, get_server_info, add_numbers")
    print()

    # Uncomment this when MCP server is running:
    # response = await client.run_with_local_mcp(
    #     prompt,
    #     mcp_url="http://localhost:8000/mcp"
    # )
    # print(f"AI: {response}")


async def example_custom_model():
    """Example 3: Using different AI models"""
    print("\n" + "=" * 60)
    print("Example 3: Using Different Models")
    print("=" * 60 + "\n")

    if not os.getenv("DEDALUS_API_KEY"):
        print("⚠️  Set DEDALUS_API_KEY in .env first")
        return

    client = DedalusClient()

    # You can specify different models
    models = [
        "anthropic/claude-sonnet-4-20250514",  # Claude Sonnet 4 (default)
        "openai/gpt-4o",  # GPT-4 Optimized
        "google/gemini-2.0-flash-exp",  # Gemini 2.0 Flash
    ]

    prompt = "Say hello in a creative way (one sentence)"

    for model in models:
        print(f"\nUsing model: {model}")
        try:
            response = await client.chat(prompt, model=model)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("  Dedalus SDK Usage Examples")
    print("=" * 70)

    # Example 1: Simple chat
    await example_simple_chat()

    # Example 2: With MCP tools (requires server running)
    await example_with_local_mcp()

    # Example 3: Different models
    # Uncomment to test different models:
    # await example_custom_model()

    print("\n" + "=" * 70)
    print("  Examples Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  - Modify these examples for your use case")
    print("  - Create custom MCP tools in mcp_server.py")
    print("  - Explore more at: https://docs.dedaluslabs.ai")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
