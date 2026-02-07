"""
Dedalus SDK - Official Dedalus Labs SDK with MCP integration
https://docs.dedaluslabs.ai/dmcp/server/overview
"""

import asyncio
import os
from typing import Optional

from dotenv import load_dotenv

from dedalus_labs import AsyncDedalus, DedalusRunner

# Load environment variables from .env file
load_dotenv()


class DedalusClient:
    """
    Wrapper around Dedalus Labs SDK for easy interaction with LLMs and MCP servers

    This client provides a simple interface to:
    - Run AI completions with various models (Claude, GPT, etc.)
    - Connect to local or hosted MCP servers
    - Execute tools through MCP integration
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Dedalus Client

        Args:
            api_key: Dedalus Labs API key. If not provided, will use DEDALUS_API_KEY env var
        """
        self.api_key = api_key or os.getenv("DEDALUS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Dedalus API key is required. Set DEDALUS_API_KEY env var or pass api_key"
            )

        self.client = AsyncDedalus(api_key=self.api_key)
        self.runner = DedalusRunner(self.client)

        # Default model (Claude Sonnet 4)
        self.default_model = "anthropic/claude-sonnet-4-20250514"

        print("✓ Dedalus Client initialized")

    async def run(
        self,
        input_text: str,
        model: Optional[str] = None,
        mcp_servers: Optional[list[str]] = None,
    ) -> str:
        """
        Run an AI completion with optional MCP server integration

        Args:
            input_text: The input/prompt for the AI
            model: Model to use (defaults to Claude Sonnet 4)
            mcp_servers: List of MCP servers to connect to (local URLs or marketplace slugs)

        Returns:
            AI response text

        Examples:
            # Simple chat
            response = await client.run("Hello, how are you?")

            # With local MCP server
            response = await client.run(
                "Use the log_hello tool",
                mcp_servers=["http://localhost:8000/mcp"]
            )

            # With hosted MCP server (marketplace)
            response = await client.run(
                "Search for docs",
                mcp_servers=["your-org/your-server"]
            )
        """
        model = model or self.default_model

        # Build request parameters
        kwargs = {
            "input": input_text,
            "model": model,
        }

        if mcp_servers:
            kwargs["mcp_servers"] = mcp_servers

        # Run the completion
        try:
            response = await self.runner.run(**kwargs)
            # Extract text from response
            if hasattr(response, "final_output"):
                return response.final_output
            elif hasattr(response, "text"):
                return response.text
            else:
                return str(response)
        except Exception as e:
            return f"Error: {str(e)}"

    async def run_with_local_mcp(
        self,
        input_text: str,
        mcp_url: str = "http://localhost:8000/mcp",
        model: Optional[str] = None,
    ) -> str:
        """
        Convenience method to run with a local MCP server

        Args:
            input_text: The input/prompt for the AI
            mcp_url: Local MCP server URL (default: http://localhost:8000/mcp)
            model: Model to use

        Returns:
            AI response text
        """
        return await self.run(
            input_text=input_text,
            model=model,
            mcp_servers=[mcp_url],
        )

    async def chat(self, message: str, model: Optional[str] = None) -> str:
        """
        Simple chat method without MCP tools

        Args:
            message: User message
            model: Model to use

        Returns:
            AI response
        """
        return await self.run(input_text=message, model=model)


# ============================================
# Example Usage
# ============================================


async def main():
    """Demo the Dedalus Client"""
    print("\n" + "=" * 60)
    print("Dedalus Client Demo")
    print("=" * 60 + "\n")

    # Check for API key
    api_key = os.getenv("DEDALUS_API_KEY")
    if not api_key:
        print("⚠️  DEDALUS_API_KEY not set in environment")
        print("   Please set it in your .env file or environment variables")
        print("   Example: export DEDALUS_API_KEY='your-api-key'\n")
        return

    try:
        # Initialize client
        client = DedalusClient(api_key=api_key)

        # Simple chat
        print("📝 Test 1: Simple chat")
        print("-" * 60)
        response = await client.chat(
            "Hello! Introduce yourself in one sentence.",
            system_prompt="You are Dedalus, an AI assistant with MCP capabilities.",
        )
        print(f"🤖 Response: {response}\n")

        # With local MCP server (requires server running)
        print("📝 Test 2: Chat with local MCP server")
        print("-" * 60)
        print("   (This requires the MCP server to be running on localhost:8000)")
        print("   To start: python mcp_server.py")
        print("   Skipping for now...\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("  1. DEDALUS_API_KEY is set correctly")
        print("  2. You have internet connection")
        print("  3. The dedalus-labs package is installed")


if __name__ == "__main__":
    asyncio.run(main())
