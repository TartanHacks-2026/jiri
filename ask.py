#!/usr/bin/env python
"""
Ask - Simple CLI to ask Dedalus AI a question
Usage: python ask.py "your question here"
"""

import asyncio
import sys

from dotenv import load_dotenv

from dedalus import DedalusClient

# Load environment variables
load_dotenv()


async def ask(question: str, model: str | None = None) -> str:
    """Ask a question and get a response"""
    try:
        client = DedalusClient()
        response = await client.chat(question, model=model)
        return response
    except Exception as e:
        return f"Error: {e}"


def main():
    """Main CLI entry point"""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python ask.py 'your question here'")
        print("\nExamples:")
        print('  python ask.py "What is 2+2?"')
        print('  python ask.py "Explain Python decorators"')
        print('  python ask.py "Write a hello world in Rust"')
        print("\nOr for interactive mode:")
        print("  python chat_simple.py")
        sys.exit(1)

    # Get question from arguments (join all args after script name)
    question = " ".join(sys.argv[1:])

    # Check for model flag
    model = None
    if "--model=" in question:
        parts = question.split("--model=")
        model = parts[1].split()[0]
        question = parts[0].strip()

    # Print question
    print(f"\n❓ Question: {question}\n")

    # Get and print answer
    print("🤖 Answer:")
    print("-" * 70)
    answer = asyncio.run(ask(question, model))
    print(answer)
    print("-" * 70 + "\n")


if __name__ == "__main__":
    main()
