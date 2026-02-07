import os
import sys
import asyncio

from dotenv import load_dotenv
from dedalus_labs import AsyncDedalus, Dedalus, DedalusRunner

from router import SmartRouter, RouterConfig

load_dotenv()

MCP_REGISTRY = [
    {
        "url": "tsion/yahoo-finance-mcp",
        "name": "Yahoo Finance",
        "category": "finance",
        "description": "Stock market data, financial stats, quotes, and ticker information for stocks and equities",
        "keywords": ["stocks", "equities", "MSFT", "AAPL", "ticker", "price", "market cap", "dividends"],
    },
    {
        "url": "issac/fetch-mcp",
        "name": "Web Fetch",
        "category": "web",
        "description": "Fetch and read webpages, check robots.txt, ping URLs, and extract content from web pages",
        "keywords": ["http", "html", "scrape", "headlines", "URL", "website", "crawl"],
    },
    {
        "url": "windsor/foursquare-places-mcp",
        "name": "foursquare places mcp",
        "category": "travel",
        "description": "Enable your AI agents with real-time, global location intelligence and personalized place recommendations using the Foursquare Places MCP Server.",
        "keywords": ["travel", "tripadvisor", "location", "recommendations", "views", "restaurant", "hotel", "attraction"],
    },
    {
        "url": "windsor/x-api-mcp",
        "name": "x api mcp",
        "category": "tweet",
        "description": "Use X MCP to: - Look up users by username, ID, or authenticated account - Retrieve tweets and thread details by ID - Fetch user timelines and mentions - Search recent tweets from the last 7 days - Get follower and following lists - View likes and retweets on any tweet",
        "keywords": ["x", "twitter", "tweet", "user", "timeline", "mention", "search", "follower", "following", "like", "retweet"],
    },
    {
        "url": "michaelwaves/notion-mcp",
        "name": "Notion MCP",
        "category": "Journal",
        "description": "Core Notion integration enabling AI assistants to create, retrieve, and update pages within your Notion workspace. Manage page hierarchies, update properties, handle icons and covers, and archive/restore pages programmatically. Perfect for automating documentation workflows, building knowledge bases, syncing external data to Notion, or creating AI-powered note-taking systems. Supports both standalone pages and database entries with full property management capabilities. Ideal for teams using Notion as their central workspace who want to automate content creation and organization tasks",
        "keywords": ["notion", "journal", "documentation", "knowledge base", "note-taking", "automation", "property management", "page hierarchy", "database entries"],
    },
    {
        "url": "anny_personal/gcal-mcp",
        "name": "Google Calendar MCP",
        "category": "Calendar",
        "description": "Use Google Calendar MCP to: - View upcoming meetings and events - Create, update, and delete calendar entries - Check your availability and find free slots - Set reminders and recurring appointments",
        "keywords": ["calendar", "meeting", "event", "reminder", "recurring", "availability", "free slots", "create", "update", "delete"],
    },
    {
        "url": "danny/cat-facts",
        "name": "Cat Facts",
        "category": "Cat Facts",
        "description": "Get random cat facts and learn interesting tidbits about our feline friends",
        "keywords": ["cat", "facts", "interesting", "tidbits", "feline", "friends"],
    },
    {
        "url": "windsor/open-meteo-mcp",
        "name": "Weather MCP",
        "category": "Weather",
        "description": "Retrieve weather conditions for any coordinates - Access multi-day forecasts with hourly detail - Analyze historical weather trends - Check air quality metrics and UV exposure",
        "keywords": ["weather", "forecast", "hourly", "historical", "air quality", "UV exposure"],
    },
    {
        "url": "sintem/gmail-mcp",
        "name": "Gmail MCP",
        "category": "Email",
        "description": "Access and manage Gmail messages, threads, labels, and user information",
        "keywords": ["gmail", "email", "message", "thread", "label", "user", "inbox", "sent", "drafts", "trash"],
    },
    {
        "url": "https://mcp.deepwiki.com/mcp",
        "name": "Github MCP",
        "category": "Wiki",
        "description": "Access and manage github content, pages, and user information",
        "keywords": ["github","deepwiki", "wiki", "content", "page", "user", "edit", "create", "delete", "search"],
    },
    
]
async def main():
    api_key = os.getenv("DEDALUS_API_KEY")
    if not api_key:
        print("Error: DEDALUS_API_KEY not set in environment.")
        return

    dedalus = Dedalus(api_key=api_key)
    async_dedalus = AsyncDedalus(api_key=api_key)
    runner = DedalusRunner(async_dedalus)

    # Check for debug flag in command line args
    debug_mode = "--debug" in sys.argv or "-d" in sys.argv

    # Router config
    config = RouterConfig(registry=MCP_REGISTRY, debug=debug_mode)

    # Build router (pass clients directly)
    router = SmartRouter(
        dedalus_client=dedalus,
        runner=runner,
        config=config
    )
    await router.initialize()

    print("\nSemantic MCP Router (multi-turn)")
    if debug_mode:
        print("[Debug mode enabled]")
    print("Type 'quit' or 'exit' to stop.\n")

    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit"):
                print("Goodbye!")
                break

            try:
                response = await router.handle_turn(user_input)
                print(f"\nAssistant: {response}\n")
            except Exception as e:
                print(f"\nError: {e}\n")
                # Show cache state after error (only in debug mode)
                if debug_mode:
                    print(f"[Debug: Cache after error: {router.cache_contents}]")
    finally:
        router.shutdown()


if __name__ == "__main__":
    asyncio.run(main())