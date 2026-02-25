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

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    GoogleGenerativeAIEmbeddings = None

from router import SmartRouter, RouterConfig
from router.db import load_registry

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

app = FastAPI()

# Global router instance
router: SmartRouter = None
active_connections: List[WebSocket] = []


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
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Neither OPENROUTER_API_KEY nor OPENAI_API_KEY set")

    # Load MCP server registry from Postgres
    try:
        registry = await load_registry()
        print(f"Loaded {len(registry)} MCP server(s) from database")
    except Exception as e:
        raise RuntimeError(
            f"Failed to load MCP registry from Postgres: {e}\n"
            "Have you run: uv run python scripts/init_db.py ?"
        ) from e

    # Initialize LangChain models
    # If using OpenRouter, point base_url there
    is_openrouter = "OPENROUTER" in os.environ or api_key.startswith("sk-or-")
    
    chat_kwargs = {
        "model": "meta-llama/llama-3.1-8b-instruct" if is_openrouter else "gpt-4.1-mini",
        "api_key": api_key,
    }
    if is_openrouter:
        chat_kwargs["base_url"] = "https://openrouter.ai/api/v1"

    chat_model = ChatOpenAI(**chat_kwargs)
    
    # Embeddings (OpenRouter doesn't do embeddings easily)
    # 1. Try OpenAI directly if key is explicitly set
    # 2. Try Gemini if GEMINI_API_KEY is available
    # 3. Fallback to OpenRouter key (usually fails for embeddings)
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if openai_key:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=openai_key,
        )
    elif gemini_key and GoogleGenerativeAIEmbeddings is not None:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=gemini_key,
        )
    else:
        # Fallback to whatever key we have (likely OpenRouter, which may fail)
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=api_key,
        )

    config = RouterConfig(registry=registry, debug=True)

    router = WebRouter(
        chat_model=chat_model,
        embeddings=embeddings,
        config=config,
    )
    await router.initialize()
    router.set_loop(asyncio.get_running_loop())
    print("\u2705 Router initialized")


@app.on_event("shutdown")
async def shutdown():
    """Gracefully close DB and Redis connections."""
    if router:
        await router.shutdown()
    print("\u2705 Router shut down cleanly")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial cache state
        await websocket.send_json({
            "type": "cache_update",
            "servers": await router.cache_contents
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
                    # Always send updated cache (discover_tools may have cached servers even if execution failed)
                    await websocket.send_json({
                        "type": "cache_update",
                        "servers": await router.cache_contents
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
