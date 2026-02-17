"""FastAPI web server for the MCP router with WebSocket support."""
import os
import asyncio
from pathlib import Path
from typing import List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from router import SmartRouter, RouterConfig

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

app = FastAPI()

# Global router instance
router: SmartRouter = None
active_connections: List[WebSocket] = []

# MCP Registry
MCP_REGISTRY = [
    {
        "url":"https://mcp.api.coingecko.com/sse",
        "name": "CoinGecko MCP",
        "category": "Crypto",
        "transport": "sse",
        "description": "Get cryptocurrency prices, market data, coin info, and trading volumes for Bitcoin, Ethereum, and other tokens",
        "keywords": ["crypto", "cryptocurrency", "bitcoin", "ethereum", "coin", "token", "price", "market cap", "trading", "coingecko"],
    },
    {
        "url": "https://mcp.deepwiki.com/mcp",
        "name": "Github Repo Search MCP (DeepWiki)",
        "category": "Github",
        "transport": "http",
        "description": "Search Github repositories for code, documentation, and other resources",
        "keywords": ["github", "repo", "search", "code", "documentation", "resources"],
    },
    {
        "url": "https://remote.mcpservers.org/fetch/mcp",
        "name": "Web Fetch MCP",
        "category": "Web",
        "transport": "http",
        "description": "Fetch web pages for code, documentation, and other resources",
        "keywords": ["web", "fetch", "scraping", "documentation", "resources"],
    },
    {
        "url": "news-server-stdio",
        "name": "NewsAPI",
        "category": "News",
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "python", str(Path(__file__).resolve().parent / "servers" / "news_server.py")],
        "description": "Get the latest news articles and headlines about any topic using NewsAPI",
        "keywords": ["news", "headlines", "articles", "current events", "breaking news", "journalism"],
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = None  # Will be set during startup
    
    def set_loop(self, loop):
        self._loop = loop
    
    def _log(self, msg: str) -> None:
        """Override to broadcast logs (thread-safe)."""
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
        
        # Broadcast — thread-safe
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(
                asyncio.ensure_future, broadcast_log(msg, log_type)
            )


@app.on_event("startup")
async def startup():
    """Initialize the router on startup."""
    global router
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    
    # Initialize LangChain models
    chat_model = ChatOpenAI(
        model="gpt-4.1-mini",
        api_key=api_key,
    )
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key,
    )
    
    config = RouterConfig(registry=MCP_REGISTRY, debug=True)  # Always debug for web UI
    
    router = WebRouter(
        chat_model=chat_model,
        embeddings=embeddings,
        config=config,
    )
    await router.initialize()
    router.set_loop(asyncio.get_running_loop())
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
                    
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                finally:
                    # Always send updated cache (discover_tools may have cached servers even if execution failed)
                    await websocket.send_json({
                        "type": "cache_update",
                        "servers": router.cache_contents
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
