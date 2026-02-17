# Jiri — LangChain / LangGraph Implementation 🤖

Self-improving AI agent powered by [LangGraph](https://langchain-ai.github.io/langgraph/), [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters), and OpenAI models.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [OpenAI API key](https://platform.openai.com/account/api-keys)

### Setup

```bash
cd LangChain
cp .env.example .env
# Add your OPENAI_API_KEY to .env
# Optionally add NEWS_API_KEY for the NewsAPI MCP server
uv sync
```

### Run

**Web UI:**

```bash
cd MCP
uv run python web_server.py
# Open http://localhost:8080
```

---

## 🏗️ Architecture

This implementation replaces the Dedalus Labs SDK with **LangGraph + langchain-mcp-adapters** for a fully open, provider-agnostic architecture:

- **Agent Runtime**: LangGraph `create_react_agent` with `ChatOpenAI` (GPT-4.1-mini)
- **Embeddings**: OpenAI `text-embedding-3-small` via `langchain-openai`
- **MCP Transport**: Direct connections via `MultiServerMCPClient` — supports **HTTP**, **SSE**, and **stdio** transports
- **Custom MCP Servers**: Build your own MCP tools (see `servers/news_server.py` for an example)
- **Tool Discovery**: `discover_tools` LangChain tool backed by local semantic search

### Key Differences from the Dedalus Implementation

| Area | Dedalus | LangChain |
|---|---|---|
| Agent execution | `DedalusRunner` + Dedalus API | LangGraph ReAct agent |
| MCP connections | Dedalus marketplace URLs | Direct HTTP/SSE/stdio via `MultiServerMCPClient` |
| Tool source | Dedalus marketplace only | Any MCP server (remote or local) |
| Custom servers | Not supported | ✅ Build your own (see `servers/`) |
| Error handling | Basic retry | Automatic server-level fault isolation and retry |

### Flow

```
User Query
    ↓
SmartRouter.handle_turn()
    ↓
Build ReAct agent with cached MCP tools + discover_tools
    ↓
Agent decides: use cached tool OR call discover_tools()
    ↓
If discover_tools called:
    → Semantic search (OpenAI embeddings)
    → Add server to LRU cache
    → Re-run with expanded tool set via MultiServerMCPClient
    ↓
Execute tool via MCP (HTTP/SSE/stdio)
    ↓
Post-run: LRU touch, metrics, health tracking
    ↓
Return response to user
```

---

## 📁 Project Structure

```
LangChain/
├── MCP/
│   ├── web_server.py           # FastAPI web UI with WebSocket
│   ├── static/
│   │   └── index.html          # Chat interface
│   ├── servers/
│   │   └── news_server.py      # Custom MCP server (stdio transport)
│   └── router/
│       ├── core.py             # SmartRouter (LangGraph ReAct agent)
│       ├── registry.py         # Tool registry (OpenAI embeddings)
│       ├── tool_cache.py       # LRU cache for active servers
│       ├── health.py           # Server health tracking
│       ├── metrics.py          # Usage analytics
│       ├── history.py          # Conversation history
│       └── config.py           # Configuration
├── src/                        # FastAPI backend (API, models, voice)
├── ios/                        # iOS client app
├── pyproject.toml
└── docker-compose.yml
```

---

## 📡 Registered MCP Servers

| Server | Category | Transport | Description |
|---|---|---|---|
| CoinGecko MCP | Crypto | SSE | Cryptocurrency prices, market data, coin info |
| DeepWiki | GitHub | HTTP | GitHub repository analysis and code search |
| Web Fetch MCP | Web | HTTP | Fetch and scrape web pages |
| NewsAPI | News | stdio | Latest news headlines (custom local server) |

Edit `MCP_REGISTRY` in `web_server.py` to add/remove servers.

### Adding a Custom MCP Server

1. Create a new Python file in `MCP/servers/`:

```python
# servers/my_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-tool")

@mcp.tool()
def my_tool(query: str) -> str:
    """Do something useful."""
    return f"Result for {query}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

2. Register it in `MCP_REGISTRY`:

```python
{
    "url": "my-server-stdio",
    "name": "My Custom Tool",
    "category": "custom",
    "transport": "stdio",
    "command": "uv",
    "args": ["run", "python", str(Path(__file__).resolve().parent / "servers" / "my_server.py")],
    "description": "Description of what this tool does",
    "keywords": ["keyword1", "keyword2"],
}
```

---

## ⚙️ Configuration

Located in `MCP/router/config.py`:

```python
@dataclass
class RouterConfig:
    execution_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    similarity_threshold: float = 0.35      # Semantic search strictness
    relative_score_cutoff: float = 0.7      # Filter low-score results
    max_cache_size: int = 10                # Max cached MCP servers
    preload_count: int = 5                  # Preload top N tools on startup
    max_history_turns: int = 20             # Conversation memory
    max_steps: int = 20                     # Max agent execution steps
    health_cooldown_seconds: int = 300      # 5-min cooldown for failures
    debug: bool = False
```

---

## 🎮 Usage Examples

```
You: What's the price of Bitcoin?
You: Explain the TensorFlow GitHub repository
You: Fetch the contents of https://example.com
You: What's the latest news about AI?
You: Get the price of Bitcoin and then search for news about crypto
```

---

## 🐛 Debugging

Debug mode is enabled by default in the web UI. Logs are streamed to the live log panel.

**Common issues:**

| Problem | Fix |
|---|---|
| `401 AuthenticationError` | Set `OPENAI_API_KEY` in `.env` |
| NewsAPI server fails | Set `NEWS_API_KEY` in `.env` |
| Tool not discovered | Lower `similarity_threshold` in `config.py` |
| Server connection failing | Server auto-removed; check logs for details |
| Stale usage cache | Delete `MCP/data/usage_metrics.jsonl` and restart |

---

## 🔗 Dependencies

- `langchain-openai` — ChatOpenAI + OpenAIEmbeddings
- `langchain-mcp-adapters` — MultiServerMCPClient for MCP connections
- `langgraph` — ReAct agent framework
- `mcp` — MCP server SDK (for custom servers)
- `fastapi` + `uvicorn` — Web server
- `python-dotenv` — Environment variables

---

## 📄 License

MIT
