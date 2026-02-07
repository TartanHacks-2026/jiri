import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    result = await runner.run(
        input="Book an uber",
        model="openai/gpt-5-chat-latest",
        # External MCP URL!
        mcp_servers=["http://localhost:3333/mcp"],
    )
    
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())