# Jiri — Dedalus Labs Implementation 🤖

Self-improving AI agent powered by the [Dedalus Labs SDK](https://dedaluslabs.ai) and MCP marketplace.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [Dedalus Labs API key](https://dedaluslabs.ai)

### Setup

```bash
cd Dedalus
cp .env.example .env
# Add your DEDALUS_API_KEY to .env
uv sync
```

### Run

**Web UI (recommended):**

```bash
cd MCP
uv run python web_server.py
# Open http://localhost:8080
```

**Console:**

```bash
cd MCP
uv run python dedalus.py
```

**Console with debug logging:**

```bash
cd MCP
uv run python dedalus.py --debug
```

---

## 🏗️ Architecture

This implementation uses the **Dedalus Labs SDK** for both agent execution and MCP tool management:

- **Agent Runtime**: `DedalusRunner` with `AsyncDedalus` — handles agent execution with Anthropic Claude Haiku 4.5
- **Embeddings**: Dedalus Embeddings API — semantic search over tool registry
- **MCP Transport**: Dedalus marketplace URLs (e.g. `tsion/yahoo-finance-mcp`) — tools are hosted on the Dedalus marketplace
- **Tool Discovery**: `discover_tools` function integrated as an agent tool, backed by semantic registry search

### Flow

```
User Query
    ↓
SmartRouter.handle_turn()
    ↓
DedalusRunner.run() with discover_tools + cached server URLs
    ↓
Agent decides: use cached tool OR call discover_tools()
    ↓
If discover_tools called:
    → Semantic search in registry (Dedalus embeddings)
    → Add server URL to LRU cache
    → Re-run with new server
    ↓
Execute tool via Dedalus MCP marketplace
    ↓
Return response to user
```

---

## 📁 Project Structure

```
Dedalus/
├── MCP/
│   ├── dedalus.py              # Console entry point
│   ├── web_server.py           # FastAPI web UI with WebSocket
│   ├── static/
│   │   └── index.html          # Chat interface
│   └── router/
│       ├── core.py             # SmartRouter (uses DedalusRunner)
│       ├── registry.py         # Tool registry (Dedalus embeddings)
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

These servers are available via the Dedalus Labs marketplace:

| Server | Category | Description |
|---|---|---|
| `tsion/yahoo-finance-mcp` | Finance | Stock quotes, market data, financial stats |
| `issac/fetch-mcp` | Web | Webpage scraping, URL fetching |
| `windsor/foursquare-places-mcp` | Travel | Location search, restaurant recommendations |
| `windsor/x-api-mcp` | Social | Twitter/X API for tweets and timelines |
| `michaelwaves/notion-mcp` | Productivity | Notion pages and databases |
| `windsor/open-meteo-mcp` | Weather | Forecasts, historical weather, air quality |

Edit `MCP_REGISTRY` in `web_server.py` or `dedalus.py` to add/remove servers.

---

## ⚙️ Configuration

Located in `MCP/router/config.py`:

```python
@dataclass
class RouterConfig:
    execution_model: str = "anthropic/claude-haiku-4-5"
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
You: How is MSFT stock doing?
You: Explain the PyTorch GitHub repository
You: What's the weather in San Francisco?
You: Find restaurants near me
You: What are Elon Musk's recent tweets?
You: Analyze the LangChain GitHub repo and email the summary to my team
```

---

## 🐛 Debugging

**Enable debug mode:**

```bash
uv run python dedalus.py --debug
```

**Common issues:**

| Problem | Fix |
|---|---|
| Tools not discovered | Lower `similarity_threshold` in `config.py` (try 0.25) |
| Server 500 errors | Server may be down on Dedalus marketplace — auto-marked unhealthy |
| Stale usage cache | Delete `MCP/data/usage_metrics.jsonl` and restart |

---

## 🔗 Dependencies

- `dedalus-labs` — SDK for agent execution and MCP marketplace
- `fastapi` + `uvicorn` — Web server
- `python-dotenv` — Environment variables

---

## 📄 License

MIT
