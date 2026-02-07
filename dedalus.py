import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    result = await runner.run(
        input="I want to know the stats of MSFT stock",
        model="openai/gpt-5-nano",
        # Any public MCP URL!
        mcp_servers=["tsion/yahoo-finance-mcp"]
    )
    
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())