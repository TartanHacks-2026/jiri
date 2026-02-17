# Jiri 🤖

**Self-Improving AI Agent with Dynamic Tool Discovery**

An intelligent agent that **learns and evolves in real-time** by automatically discovering and adding new MCP (Model Context Protocol) tools as needed. Start with zero capabilities — Jiri builds its own toolkit on-demand by semantically searching for relevant servers, connecting them, and expanding its abilities with every query.

---

## 🌟 The Self-Improving Difference

Unlike traditional AI assistants with fixed capabilities, Jiri:

- **Starts with zero tools** — Lightweight and fast to initialize
- **Discovers tools at runtime** — Semantic search finds the right MCP server for any query
- **Chains tools automatically** — Seamlessly combines multiple tools for complex multi-step tasks
- **Builds its own toolkit** — Automatically connects to new capabilities as users ask questions
- **Remembers what works** — LRU cache keeps frequently-used tools loaded
- **Gets smarter over time** — Usage metrics learn which tools to preload on next startup
- **Handles failures gracefully** — Unhealthy servers get cooldowns, working servers persist

---

## 📁 Two Implementations

This repository contains **two separate implementations** of Jiri's MCP architecture, side-by-side:

| | [Dedalus](./Dedalus/) | [LangChain](./LangChain/) |
|---|---|---|
| **Agent Framework** | [Dedalus Labs SDK](https://dedaluslabs.ai) | [LangGraph](https://langchain-ai.github.io/langgraph/) + [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) |
| **LLM Provider** | Anthropic (Claude Haiku 4.5) via Dedalus | OpenAI (GPT-4.1-mini) via LangChain |
| **Embeddings** | Dedalus Embeddings API | OpenAI `text-embedding-3-small` |
| **MCP Transport** | Dedalus marketplace URLs | Direct HTTP/SSE/stdio connections |
| **Tool Discovery** | Dedalus marketplace semantic search | Local semantic search with OpenAI embeddings |
| **Custom MCP Servers** | — | ✅ (e.g. `servers/news_server.py` via stdio) |
| **API Key Required** | `DEDALUS_API_KEY` | `OPENAI_API_KEY` |

Both implementations share the **same core architecture**:

```
MCP/
├── web_server.py           # FastAPI web UI with WebSocket
├── static/index.html       # Chat interface
└── router/
    ├── core.py             # SmartRouter orchestrator
    ├── registry.py         # Tool registry with semantic search
    ├── tool_cache.py       # LRU cache for active servers
    ├── health.py           # Server health tracking
    ├── metrics.py          # Usage analytics
    ├── history.py          # Conversation history
    └── config.py           # Configuration
```

---

## 🚀 Quick Start

### Dedalus Implementation

```bash
cd Dedalus
cp .env.example .env
# Add DEDALUS_API_KEY to .env
uv sync
cd MCP && uv run python web_server.py
```

### LangChain Implementation

```bash
cd LangChain
cp .env.example .env
# Add OPENAI_API_KEY to .env
uv sync
cd MCP && uv run python web_server.py
```

Then open: **http://localhost:8080**

---

## 🎯 How It Works

### Runtime Tool Discovery

Jiri doesn't come pre-configured with tools. It **discovers capabilities dynamically** based on what you need:

```
You: How is MSFT stock doing?

1. Router checks cache → No stock server found
2. Semantic search discovers a finance MCP server
3. Connects and executes stock lookup
4. Returns real-time MSFT data ✅

Cache now contains: [finance-mcp]
```

### The Self-Improving Cycle

```
First Session (Cold Start):
  Query 1: "MSFT stock"      → Discovers finance tool → 3s
  Query 2: "AAPL stock"      → Uses cached tool       → 1s ⚡
  Query 3: "Send email"      → Discovers email tool   → 3s

Second Session (Learned Preferences):
  Startup: Preloads finance (most used) ← AUTOMATIC!
  Query 1: "TSLA stock"      → Uses preloaded tool    → 1s ⚡
```

### Automatic Tool Chaining

```
You: Explain the TensorFlow GitHub repo and email the summary to my team

1. Discovers Deep Wiki tool → Analyzes repository
2. Discovers Gmail tool → Sends summary email
✅ Multi-tool workflow from a single natural language request!
```

---

## ✨ Core Features

- 🧠 **Runtime Tool Discovery** — Zero configuration, discovers MCP servers on-demand
- 🔗 **Automatic Tool Chaining** — Chains multiple tools for complex multi-step tasks
- 🔄 **Continuous Learning** — Usage patterns shape which tools get preloaded
- 🗄️ **LRU Caching** — Keeps frequently-used tools loaded for instant reuse
- ❤️‍🩹 **Adaptive Health** — Failed servers get cooldowns, system self-heals
- 🎨 **Beautiful Web UI** — Real-time chat with live logging and cache visualization
- 📊 **Live Observability** — Watch tool discovery, cache updates, and execution in real-time

---

## 🏗️ Architecture

```
User Query
    ↓
SmartRouter.handle_turn()
    ↓
Check cache for matching tools
    ↓
If not found → discover_tools() → Semantic search → Add to cache
    ↓
Execute tool via MCP server
    ↓
Post-run: LRU touch, metrics, health tracking
    ↓
Return response to user
```

**Components:**

| Component | Description |
|---|---|
| **SmartRouter** | Main orchestrator — manages discovery, caching, and execution |
| **ToolRegistry** | Semantic search over MCP registry using embeddings |
| **ToolCache** | LRU cache for active MCP server connections |
| **HealthTracker** | Server failure tracking with automatic cooldowns |
| **UsageMetrics** | Persistent usage analytics for smart preloading |
| **ConversationHistory** | Multi-turn dialogue context with rollback support |

---

## 📖 More Details

- **[Dedalus README](./Dedalus/README.md)** — Setup, configuration, and usage for the Dedalus Labs implementation
- **[LangChain README](./LangChain/README.md)** — Setup, configuration, and usage for the LangChain/LangGraph implementation

---

## 🔒 Security

- API keys stored in `.env` (gitignored)
- No credentials in logs or agent context
- WebSocket connections are local only

---

## 📄 License

MIT

---

**Built with ❤️ for TartanHacks 2026**
