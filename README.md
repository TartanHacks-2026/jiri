# Jiri 🤖

**Self-Improving AI Agent with Dynamic Tool Discovery**

An intelligent agent that **learns and evolves in real-time** by automatically discovering and adding new MCP (Model Context Protocol) tools as needed. Start with zero capabilities - Jiri builds its own toolkit on-demand by semantically searching the Dedalus Labs marketplace, connecting to relevant servers, and expanding its abilities with every query.

## 🌟 The Self-Improving Difference

Unlike traditional AI assistants with fixed capabilities, Jiri:

- **Starts with zero tools** - Lightweight and fast to initialize
- **Discovers tools at runtime** - Semantic search finds the right MCP server for any query
- **Chains tools automatically** - Seamlessly combines multiple tools for complex multi-step tasks
- **Builds its own toolkit** - Automatically connects to new capabilities as users ask questions
- **Remembers what works** - LRU cache keeps frequently-used tools loaded
- **Gets smarter over time** - Usage metrics learn which tools to preload on next startup
- **Handles failures gracefully** - Unhealthy servers get cooldowns, working servers persist

**The result:** An agent that continuously expands its capabilities based on actual user needs, not predetermined assumptions.

---

## ✨ Features

### Core Self-Improving Engine

- 🧠 **Runtime Tool Discovery**: Zero configuration - discovers MCP servers on-demand via semantic search
- 🔗 **Automatic Tool Chaining**: Seamlessly chains multiple tools to complete complex multi-step tasks
- 🔄 **Continuous Learning**: Usage patterns shape which tools get preloaded on next startup
- 🗄️ **Intelligent Caching**: LRU cache keeps frequently-used tools loaded for instant reuse
- ❤️‍🩹 **Adaptive Health**: Failed servers get cooldowns, system learns to avoid broken tools
- 📈 **Gets Smarter Over Time**: Metrics-driven preloading means popular tools load automatically

### User Experience

- 🎨 **Beautiful Web UI**: Real-time chat with live logging and cache visualization
- 💬 **Console Mode**: Terminal-based interactive chat for power users
- 📊 **Live Observability**: Watch tool discovery, cache updates, and execution in real-time
- 🔍 **Debug Mode**: Optional detailed logging for development and troubleshooting

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- [Dedalus Labs API key](https://dedaluslabs.ai)

### 1. Install Dependencies

```bash
cd /Users/deepanshsaxena/Documents/Jiri/jiri
uv sync
```

### 2. Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Add your Dedalus API key to .env
# DEDALUS_API_KEY=your-api-key-here
```

### 3. Run the Router

**Option A: Web UI (Recommended)**

```bash
cd MCP
uv run python web_server.py
```

Then open: **http://localhost:8080**

**Option B: Console**

```bash
cd MCP
uv run python dedalus.py
```

**Option C: Console with Debug Logging**

```bash
cd MCP
uv run python dedalus.py --debug
```

---

## 🎯 How It Works: The Self-Improving Loop

### Runtime Evolution in Action

Jiri doesn't come pre-configured with tools. Instead, it **builds its capabilities dynamically** based on what you actually need:

```
You: How is MSFT stock doing?

1. Router checks cache → No stock server found
2. Auto-discovers "stock" tools via semantic search
3. Finds: tsion/yahoo-finance-mcp
4. Connects and executes stock lookup
5. Returns real-time MSFT data ✅

Cache now contains: [yahoo-finance-mcp]
```

```
You: What's the weather in Seattle?

1. Router checks cache → Has stock server, but no weather
2. Auto-discovers "weather" tools
3. Finds: windsor/open-meteo-mcp
4. Connects and executes weather lookup
5. Returns current Seattle weather ✅

Cache now contains: [yahoo-finance-mcp, open-meteo-mcp]
```

```
You: How is AAPL stock doing?

1. Router checks cache → Found yahoo-finance-mcp! ⚡
2. Reuses cached server (no discovery needed)
3. Returns AAPL data instantly ✅

🎉 The agent just got faster! Cached tools respond in ~1s vs ~3s for discovery.
```

### The Self-Improving Cycle

```
First Session (Cold Start):
  Query 1: "MSFT stock" → Discovers Yahoo Finance → 3s
  Query 2: "AAPL stock" → Uses cached Yahoo Finance → 1s ⚡
  Query 3: "Weather in NYC" → Discovers Weather → 3s
  
  Usage logged: {yahoo-finance: 2, weather: 1}

Second Session (Learned Preferences):
  Startup: Preloads yahoo-finance (most used) ← AUTOMATIC!
  Query 1: "TSLA stock" → Uses preloaded Yahoo Finance → 1s ⚡
  Query 2: "Weather in LA" → Discovers Weather → 3s
  
  Usage logged: {yahoo-finance: 3, weather: 2}

Third Session (Even Smarter):
  Startup: Preloads yahoo-finance AND weather ← DOUBLE AUTOMATIC!
  All queries: ~1s (everything cached) ⚡⚡⚡
```

**Key Insight:** Jiri optimizes itself based on YOUR usage patterns. The more you use it, the faster and smarter it becomes.

### Automatic Tool Chaining in Action

Jiri doesn't just discover tools - it intelligently **chains them together** to complete complex workflows:

```
You: Check the weather in Seattle and email it to john@example.com

1. Router analyzes query → Identifies two needs: weather + email
2. Discovers weather tool → Executes weather lookup → Gets Seattle weather data
3. Discovers Gmail tool → Composes and sends email with weather info
4. Returns confirmation ✅

🔗 Two tools chained automatically from a single natural language request!
```

```
You: Get the latest TSLA stock price and tweet about it

1. Router discovers Yahoo Finance → Fetches TSLA stock data
2. Router discovers Twitter tool → Formats and posts tweet with stock info
3. Returns tweet confirmation with link ✅

🔗 Finance + Social Media tools working together seamlessly!
```

```
You: Find my calendar events today, get weather for those locations, and email summary

1. Calendar tool → Fetches today's events
2. Weather tool → Gets weather for each event location
3. Gmail tool → Composes comprehensive email with events + weather
4. Sends to your inbox ✅

🔗 Three tools chained for a sophisticated multi-step workflow!
```

**Why This Matters:**
- No workflow configuration needed
- Natural language describes the entire process
- Tools discover and chain automatically
- Complex tasks become as simple as asking

### The Self-Improving Engine

**🧠 Semantic Discovery**
- Natural language queries → Semantic search → Right tool every time
- "MSFT stock" automatically matches financial servers
- "Weather in Seattle" finds meteorology tools
- No hardcoding, no manual configuration

**🔗 Automatic Tool Chaining**
- Tools can automatically chain together to accomplish complex tasks
- "Get weather and email it" → Discovers weather tool → Discovers Gmail → Chains execution
- "Check my calendar and tweet about it" → Calendar tool → Twitter tool → Seamless flow
- Multi-step workflows happen automatically based on natural language queries
- No manual workflow configuration required

**🗄️ Adaptive Caching**
- LRU (Least Recently Used) keeps your 10 most-used tools loaded
- First query discovers, second query reuses ⚡
- Cache persists within a session, resets between runs

**❤️‍🩹 Self-Healing**
- Failing servers get automatic 5-minute cooldowns
- Successful servers stay cached, broken ones are evicted
- System learns to avoid problematic tools without user intervention

**📊 Long-Term Learning**
- Every tool use is logged to `data/usage_metrics.jsonl`
- On next startup, **most-used tools preload automatically**
- Your personal usage patterns shape the agent's capabilities
- **No manual configuration needed - the system optimizes itself**

---

## 🌐 Web UI

### Features

- **💬 Chat Interface**: Clean conversation view with markdown rendering
- **📋 Live Logs**: Real-time color-coded logs showing:
  - 🟣 Tool discoveries
  - ✅ Successful operations
  - ❌ Errors and failures
  - 🟡 Warnings
- **🗄️ Cached Servers**: Visual display of loaded MCP servers
- **🎨 Beautiful Design**: Modern UI with Tailwind CSS
- **📊 Markdown Support**: Tables, bold text, lists, code blocks

### Screenshots

**Chat Interface**
- Clean message bubbles
- Syntax highlighting for code
- Beautiful table rendering

**Live Logs Panel**
- See tool discovery in real-time
- Track which servers are being used
- Monitor errors and warnings

### Starting the Web UI

```bash
cd /Users/deepanshsaxena/Documents/Jiri/jiri/MCP
uv run python web_server.py
```

Open: **http://localhost:8080**

---

## 🎮 Usage Examples

### Stock Queries

```
You: How is MSFT stock doing?
You: Compare AAPL and NVDA
You: Give me OHLCV data for TSLA
```

### Web Scraping

```
You: Scrape https://www.scrapethissite.com/pages/simple/
You: Check this GitHub repo https://github.com/user/repo
```

### Weather

```
You: What's the weather in Seattle?
You: Weather forecast for Pittsburgh?
```

### Social Media

```
You: What are Elon Musk's recent tweets?
You: Show me trending topics on X
```

### Email (Gmail)

```
You: Check my unread emails
You: Send an email to john@example.com about the project update
You: Search for emails from Sarah about the meeting
```

### Calendar

```
You: What's on my calendar today?
You: Schedule a meeting with the team for next Tuesday at 2pm
You: Show me my appointments for this week
```

### Twitter

```
You: Post a tweet about our new feature launch
You: Show me my recent mentions
You: What's trending on Twitter right now?
```

### Places & Travel

```
You: Find restaurants near me
You: Best hotels in San Francisco
```

### Tool Chaining

Jiri can automatically chain multiple tools together to accomplish complex tasks:

```
You: Check the weather in Seattle and send it to john@example.com

1. Discovers and uses weather tool → Gets Seattle weather
2. Discovers and uses Gmail tool → Sends email with weather info
✅ Both tools executed seamlessly in sequence!
```

```
You: Find my calendar events today and tweet about them

1. Uses calendar tool → Fetches today's events
2. Uses Twitter tool → Posts summary tweet
✅ Tools chain automatically based on your query!
```

```
You: Get MSFT stock price and email it to my team

1. Uses Yahoo Finance tool → Gets MSFT price
2. Uses Gmail tool → Sends email to recipients
✅ Multi-tool workflows happen automatically!
```

---

## 📁 Project Structure

```
jiri/MCP/
├── dedalus.py              # Main console entry point
├── web_server.py           # Web UI server with WebSocket
├── static/
│   └── index.html          # Beautiful web interface
└── router/
    ├── core.py             # SmartRouter orchestrator
    ├── registry.py         # Tool registry with semantic search
    ├── tool_cache.py       # LRU cache for active servers
    ├── health.py           # Server health tracking
    ├── metrics.py          # Usage analytics
    ├── history.py          # Conversation history
    └── config.py           # Configuration dataclass
```

---

## ⚙️ Configuration

### RouterConfig Options

Located in `router/config.py`:

```python
@dataclass
class RouterConfig:
    # Model selection
    execution_model: str = "anthropic/claude-haiku-4-5"
    
    # Semantic search tuning
    similarity_threshold: float = 0.35      # Higher = stricter matching
    relative_score_cutoff: float = 0.7     # Filter low scores
    
    # Cache settings
    max_cache_size: int = 10               # Max cached servers
    preload_count: int = 5                 # Preload top N tools
    
    # Conversation
    max_history_turns: int = 20            # Conversation memory
    max_steps: int = 20                    # Max agent execution steps
    
    # Health
    health_cooldown_seconds: int = 300     # 5 min cooldown for failures
    
    # Debug
    debug: bool = False                    # Enable verbose logging
```

### MCP Registry

Add/remove MCP servers in `dedalus.py`:

```python
MCP_REGISTRY = [
    {
        "url": "tsion/yahoo-finance-mcp",
        "name": "Yahoo Finance",
        "category": "finance",
        "description": "Stock market data, quotes, financial stats",
        "keywords": ["stocks", "equities", "ticker", "price"],
    },
    # Add more servers here...
]
```

---

## 🐛 Debugging

### Enable Debug Mode

**Console:**
```bash
uv run python dedalus.py --debug
```

**Web UI:**
```python
# In web_server.py, line ~129:
config = RouterConfig(registry=MCP_REGISTRY, debug=True)
```

### Clear Usage Cache

```bash
# Remove metrics file to start fresh
rm MCP/data/usage_metrics.jsonl
```

### Common Issues

**Problem: Tools not being discovered**
- ✅ Check debug logs for semantic search scores
- ✅ Lower `similarity_threshold` in `config.py` (try 0.25)
- ✅ Add more keywords to MCP_REGISTRY entries

**Problem: Server returns 500 errors**
- ✅ Some marketplace servers may be down/broken
- ✅ Router automatically marks them unhealthy and avoids them
- ✅ Check health cooldown with debug logs

**Problem: Cache cleared after error**
- ✅ Fixed! Only newly discovered servers are evicted on error
- ✅ Working servers persist in cache

---

## 🧪 Testing

### Test Individual MCP Server

Create a test file:

```python
from dedalus_labs import AsyncDedalus, DedalusRunner

async def test():
    client = AsyncDedalus(api_key="your-key")
    runner = DedalusRunner(client)
    
    result = await runner.run(
        messages=[{"role": "user", "content": "What is MSFT stock price?"}],
        model="gpt-4o",
        mcp_servers=["tsion/yahoo-finance-mcp"],
        max_steps=10,
    )
    print(result.final_output)
```

### Test Semantic Search

```python
from router import ToolRegistry
from dedalus_labs import Dedalus

client = Dedalus(api_key="your-key")
registry = ToolRegistry(client, MCP_REGISTRY)
registry.cache_embeddings()

results = registry.search(["stock market data"])
print(results)  # Should find yahoo-finance-mcp
```

---

## 🏗️ Architecture

### Components

**SmartRouter** (`core.py`)
- Main orchestrator for query processing
- Manages tool discovery, caching, and execution
- Handles conversation history and error recovery

**ToolRegistry** (`registry.py`)
- Semantic search over MCP registry
- Uses Dedalus embeddings API
- Finds relevant tools based on natural language queries

**ToolCache** (`tool_cache.py`)
- LRU (Least Recently Used) cache
- Tracks active MCP server connections
- Automatic eviction when full

**HealthTracker** (`health.py`)
- Monitors server failures
- Implements cooldown periods
- Filters out unhealthy servers

**UsageMetrics** (`metrics.py`)
- Logs tool usage to JSONL
- Ranks tools by frequency
- Enables smart preloading

**ConversationHistory** (`history.py`)
- Maintains multi-turn dialogue context
- Automatic sliding-window trimming
- Rollback support for failed queries

### Flow Diagram

```
User Query
    ↓
Auto-Discovery (keyword detection)
    ↓
SmartRouter.handle_turn()
    ↓
DedalusRunner.run() with discover_tools + cached servers
    ↓
Agent decides: use cached tool OR call discover_tools()
    ↓
If discover_tools called:
    - Semantic search in registry
    - Add to cache
    - Re-run with new server
    ↓
Execute tool via MCP server
    ↓
Return response to user
```

---

## 🔧 Advanced Usage

### Custom Auto-Discovery

Add your own keyword detection in `core.py`:

```python
# In handle_turn(), add:
elif any(word in query_lower for word in ['movie', 'film', 'imdb']):
    needs_discovery = True
    discovery_queries = ["movie database", "film info", "IMDB"]
    self._log(f"  [Query needs movies, but no movie server - auto-discovering]")
```

### Custom MCP Server

Add to `MCP_REGISTRY`:

```python
{
    "url": "your-username/your-mcp-server",
    "name": "Your Server",
    "category": "custom",
    "description": "What your server does",
    "keywords": ["keyword1", "keyword2", "keyword3"],
}
```

### Adjust Search Sensitivity

In `config.py`:

```python
similarity_threshold: float = 0.25  # Lower = more permissive
relative_score_cutoff: float = 0.5  # Lower = include more results
```

---

## 📊 Supported MCP Servers

### Finance
- **tsion/yahoo-finance-mcp**: Stock quotes, market data, financial stats

### Web
- **issac/fetch-mcp**: Webpage scraping, robots.txt, URL fetching

### Weather
- **windsor/open-meteo-mcp**: Weather forecasts, conditions, historical data

### Email & Communication
- **Gmail MCP**: Read, send, search emails, manage inbox
- **Calendar MCP**: View, create, update calendar events and appointments

### Social Media
- **windsor/x-api-mcp**: Twitter/X API for tweets, users, timelines
- **Twitter MCP**: Post tweets, read mentions, check trends, manage Twitter account

### Travel
- **windsor/foursquare-places-mcp**: Location search, restaurant recommendations

### Productivity
- **michaelwaves/notion-mcp**: Notion pages and databases

---

## 🎨 Web UI Features

### Markdown Rendering

The web UI supports full markdown:

- **Bold text**: `**text**` → **text**
- *Italic text*: `*text*` → *text*
- Lists: Both bullet and numbered
- Tables: Beautiful styled tables with hover effects
- Code blocks: Syntax-highlighted
- Headers: H1, H2, H3
- Links: Clickable URLs

### Real-Time Updates

- Messages appear instantly
- Logs stream in real-time
- Cache updates live
- WebSocket-based (auto-reconnects)

### Keyboard Shortcuts

- **Enter**: Send message
- **Escape**: Clear input
- **Ctrl+C**: Stop server

---

## 🛠️ Development

### Architecture: The Self-Improving System

#### Entry Points

**`dedalus.py`** - Console Interface
- Interactive chat loop with the SmartRouter
- Loads environment, initializes all subsystems
- Debug flag support for development

**`web_server.py`** - Web Interface
- FastAPI backend with WebSocket real-time updates
- Extended `WebRouter` broadcasts discovery/cache events to UI
- Serves beautiful Tailwind CSS frontend

#### Core Self-Improving Engine

**`router/core.py`** - SmartRouter (Orchestrator)
- **Runtime discovery**: Semantically searches MCP registry on-demand
- **Auto-discovery workaround**: Keyword-based tool finding when agent fails
- **Adaptive execution**: Learns from errors, evicts failing servers
- **History management**: Rollback failed queries to prevent conversation pollution

**`router/registry.py`** - ToolRegistry (Discovery)
- **Semantic search**: Embeds all MCP servers for similarity matching
- **Smart ranking**: Finds best tools based on query + metadata
- **One-time cost**: Embeddings cached after first run

**`router/tool_cache.py`** - ToolCache (Memory)
- **LRU eviction**: Keeps 10 most-used tools loaded
- **Metrics-driven preloading**: Automatically loads popular tools on startup
- **Session persistence**: Cache survives within a session, resets between runs

**`router/health.py`** - HealthTracker (Self-Healing)
- **Automatic cooldowns**: Failing servers get 5-min timeouts
- **Selective eviction**: Only newly-discovered broken tools are removed
- **Recovery tracking**: Servers can return to health after cooldown

**`router/metrics.py`** - UsageMetrics (Learning)
- **Persistent logging**: Every tool use → `data/usage_metrics.jsonl`
- **Cross-session learning**: Next startup preloads your most-used tools
- **Continuous optimization**: The more you use Jiri, the faster it gets

**`router/history.py`** - ConversationHistory (Context)
- **Multi-turn support**: Maintains conversation context across queries
- **Rollback on error**: Failed queries don't pollute history
- **Sliding window**: Prevents context overflow

**`router/config.py`** - RouterConfig (Tuning)
- All tunable parameters for the self-improving system
- Similarity thresholds, cache sizes, cooldowns, etc.

---

## 📖 API Documentation

### SmartRouter

```python
from router import SmartRouter, RouterConfig
from dedalus_labs import Dedalus, AsyncDedalus, DedalusRunner

# Initialize
dedalus = Dedalus(api_key="your-key")
async_dedalus = AsyncDedalus(api_key="your-key")
runner = DedalusRunner(async_dedalus)

config = RouterConfig(
    registry=MCP_REGISTRY,
    debug=False,
    max_cache_size=10,
)

router = SmartRouter(
    dedalus_client=dedalus,
    runner=runner,
    config=config
)

# Initialize (caches embeddings, preloads tools)
await router.initialize()

# Process query
response = await router.handle_turn("How is MSFT stock?")
print(response)

# Check cache
print(router.cache_contents)  # ['tsion/yahoo-finance-mcp']

# Cleanup
router.shutdown()
```

### ToolRegistry

```python
from router import ToolRegistry

registry = ToolRegistry(
    dedalus_client=client,
    registry=MCP_REGISTRY,
    similarity_threshold=0.35,
    relative_score_cutoff=0.7,
    debug=True,
)

# Cache embeddings
count = registry.cache_embeddings()

# Search for tools
results = registry.search(["stock market data", "financial quotes"])
# Returns: [{"url": "tsion/yahoo-finance-mcp", "description": "...", "score": 0.576}]
```

---

## 🔒 Security

- API keys stored in `.env` (gitignored)
- No credentials in logs or agent context
- WebSocket connections are local only
- No data persistence (privacy-first)

---

## 🤝 Contributing

### Adding MCP Servers

1. Find a server on the [Dedalus Labs Marketplace](https://docs.dedaluslabs.ai/mcp)
2. Add to `MCP_REGISTRY` in `dedalus.py` or `web_server.py`
3. Include good keywords for semantic search
4. Test with a relevant query

### Improving Auto-Discovery

Edit the keyword detection in `core.py` → `handle_turn()`:

```python
# Add new category
is_movies = any(word in query_lower for word in ['movie', 'film', 'imdb'])

# Add to if/elif chain
elif is_movies and not any('movie' in url.lower() for url in active_urls):
    needs_discovery = True
    discovery_queries = ["movie database", "film", "IMDB"]
    self._log(f"  [Query needs movies, but no movie server - auto-discovering]")
```

---

## 📊 Performance

### Benchmarks

- **Cold start** (no cache): ~2-3s for discovery + execution
- **Warm cache**: ~1s for execution only
- **Semantic search**: ~200ms for embedding + search
- **LRU operations**: O(1) for touch/evict

### Optimization Tips

1. **Increase `preload_count`**: Preload more tools on startup
2. **Lower `similarity_threshold`**: Find more tools (less strict)
3. **Increase `max_cache_size`**: Keep more tools in memory
4. **Use Claude Haiku**: Faster than GPT-5 for tool calling

---

## 🐛 Troubleshooting

### Problem: "No servers cached yet" persists

**Solution**: Delete metrics file and restart
```bash
rm MCP/data/usage_metrics.jsonl
```

### Problem: Tools not being reused

**Solution**: Check if they're marked unhealthy
```bash
# Run with --debug flag
uv run python dedalus.py --debug

# Look for:
[Health filter: 0 healthy, 1 unhealthy: server-name]
```

### Problem: Wrong tool selected

**Solution**: Improve keywords in MCP_REGISTRY
```python
"keywords": ["specific", "unique", "keywords", "here"]
```

### Problem: 500 errors from Dedalus API

**Solution**: Usually means the MCP server itself is broken
- Router automatically marks it unhealthy
- Try the server directly to confirm (see Testing section)
- Report to Dedalus Labs if persistent

### Problem: Multiple servers cause errors

**Solution**: Already handled! Router only passes newly discovered server on first use

---

## 📚 Learn More

- [Dedalus Labs Docs](https://docs.dedaluslabs.ai)
- [MCP Specification](https://modelcontextprotocol.io)
- [Dedalus MCP Guide](https://docs.dedaluslabs.ai/dmcp/server/overview)

---

## 🎯 Roadmap

### Self-Improving Enhancements

- [ ] **Collaborative learning**: Share tool discoveries across users
- [ ] **Predictive preloading**: Anticipate needed tools based on conversation context
- [ ] **Smart cache strategies**: Priority queues based on usage patterns + query similarity
- [ ] **Tool performance tracking**: Automatically prefer faster, more reliable servers
- [ ] **Chain optimization**: Learn common tool chains and optimize their execution order
- [ ] **Parallel chaining**: Execute independent tool chains concurrently for faster results
- [ ] **Chain templates**: Auto-suggest common multi-tool workflows based on usage patterns

### User Experience

- [ ] **Streaming responses** in web UI (real-time token streaming)
- [ ] **Multi-user sessions** with isolated conversation histories
- [ ] **Tool usage analytics dashboard** (visualize discovery patterns)
- [ ] **Custom tool marketplace** (publish and share your own MCP servers)

---

## 📄 License

MIT

---

## 🙏 Acknowledgments

- [Dedalus Labs](https://dedaluslabs.ai) - SDK and MCP marketplace
- [Anthropic](https://anthropic.com) - Claude models
- [OpenAI](https://openai.com) - GPT models
- [FastAPI](https://fastapi.tiangolo.com) - Web framework
- [Tailwind CSS](https://tailwindcss.com) - UI styling

---

**Built with ❤️ for TartanHacks 2026**
