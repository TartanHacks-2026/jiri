"""FastAPI web server for the MCP router with WebSocket support."""
import os
import asyncio
from pathlib import Path
from typing import List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from dedalus_labs import AsyncDedalus, Dedalus, DedalusRunner

from router import SmartRouter, RouterConfig

load_dotenv()

app = FastAPI()

# Global router instance
router: SmartRouter = None
active_connections: List[WebSocket] = []

# MCP Registry
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
        "description": "Notion MCP server enables you to use Notion with Claude. You can access, search, and update Notion pages and databases.",
        "keywords": ["Notion", "Journal", "Database", "Pages"],
    },
    {
        "url": "windsor/open-meteo-mcp",
        "name": "Weather MCP",
        "category": "Weather",
        "description": "Retrieve weather conditions for any coordinates - Access multi-day forecasts with hourly detail - Analyze historical weather trends - Check air quality metrics and UV exposure",
        "keywords": ["weather", "forecast", "hourly", "historical", "air quality", "UV exposure"],
    },
]


async def broadcast_log(message: str, log_type: str = "info"):
    """Broadcast log message to all connected WebSocket clients."""
    for connection in active_connections:
        try:
            await connection.send_json({
                "type": "log",
                "log_type": log_type,
                "message": message
            })
        except:
            pass


class WebRouter(SmartRouter):
    """Extended router that broadcasts logs to WebSocket clients."""
    
    def _log(self, msg: str) -> None:
        """Override to broadcast logs."""
        super()._log(msg)
        # Extract log type from message
        if "🔍" in msg:
            log_type = "discovery"
        elif "✓" in msg or "completed" in msg.lower():
            log_type = "success"
        elif "❌" in msg or "error" in msg.lower():
            log_type = "error"
        elif "⚠️" in msg or "warning" in msg.lower():
            log_type = "warning"
        else:
            log_type = "info"
        
        # Broadcast async
        asyncio.create_task(broadcast_log(msg, log_type))


@app.on_event("startup")
async def startup():
    """Initialize the router on startup."""
    global router
    
    api_key = os.getenv("DEDALUS_API_KEY")
    if not api_key:
        raise ValueError("DEDALUS_API_KEY not set")
    
    dedalus = Dedalus(api_key=api_key)
    async_dedalus = AsyncDedalus(api_key=api_key)
    runner = DedalusRunner(async_dedalus)
    
    config = RouterConfig(registry=MCP_REGISTRY, debug=True)  # Always debug for web UI
    
    router = WebRouter(
        dedalus_client=dedalus,
        runner=runner,
        config=config
    )
    await router.initialize()
    print("✅ Router initialized")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial cache state
        await websocket.send_json({
            "type": "cache_update",
            "servers": router.cache_contents
        })
        
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "query":
                query = data["message"]
                
                # Broadcast user query
                await broadcast_log(f"You: {query}", "user")
                
                try:
                    # Process query
                    response = await router.handle_turn(query)
                    
                    # Send response
                    await websocket.send_json({
                        "type": "response",
                        "message": response
                    })
                    
                    # Send updated cache
                    await websocket.send_json({
                        "type": "cache_update",
                        "servers": router.cache_contents
                    })
                    
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                    
    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.get("/")
async def index():
    """Serve the main UI page."""
    return FileResponse("static/index.html")


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
