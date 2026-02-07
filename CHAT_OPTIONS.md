# Chat Options - How to Use Your Dedalus Setup

## Current Situation

You have two working chat options:

### Option 1: Simple Chat (Working Now ✅)

**File**: `chat_simple.py`

```bash
uv run python chat_simple.py
```

**What it does**:
- Direct chat with Claude Sonnet 4
- No tools/MCP integration
- Fast and simple
- Works immediately

**Use when**: You just want to ask questions and chat with AI

---

### Option 2: Chat with MCP Tools (Requires Setup 🔧)

**What you need**:

MCP tools require either:
1. **Hosted MCP Server** - Deploy your tools to Dedalus marketplace
2. **Local MCP Server** - Run a proper MCP server locally

**Current Challenge**: 
The `mcp_server.py` we created defines tools, but connecting them to the chat requires either deploying to Dedalus marketplace or setting up a local MCP server that the SDK can connect to.

---

## Recommended Next Steps

### Immediate: Use Simple Chat

```bash
# Start chatting now
uv run python chat_simple.py
```

This works perfectly for:
- General questions
- Code help
- Analysis
- Writing assistance
- Math problems

### Future: Add Tools

To add tool capabilities, you have these options:

#### Option A: Use Hosted MCP Servers (Easiest)

Use existing tools from Dedalus marketplace:

```python
from dedalus import DedalusClient

client = DedalusClient()
response = await client.run(
    "Search for Python documentation",
    mcp_servers=["dedalus/search"]  # Example marketplace server
)
```

#### Option B: Deploy Your Own Tools

1. Create tools (already done in `mcp_server.py`)
2. Deploy to Dedalus marketplace
3. Use your slug in chat

#### Option C: Local MCP Server (Advanced)

Set up a full MCP server locally that the SDK can connect to via HTTP.

---

## What You Can Do Right Now

### 1. Chat with AI (No tools needed)

```bash
uv run python chat_simple.py
```

Example conversation:
```
You: Hello! Can you help me with Python?
AI: Of course! I'd be happy to help with Python...

You: What's the difference between a list and a tuple?
AI: Great question! The main differences are...
```

### 2. Use Dedalus SDK in Your Code

```python
from dedalus import DedalusClient
import asyncio

async def main():
    client = DedalusClient()
    
    # Simple chat
    response = await client.chat("Explain async/await in Python")
    print(response)
    
    # With different model
    response = await client.chat(
        "Write a haiku about coding",
        model="openai/gpt-4o"
    )
    print(response)

asyncio.run(main())
```

### 3. Explore the Demo

```bash
uv run python dedalus_demo.py
```

Shows how everything connects together.

---

## Tool Integration - The Full Picture

### How MCP Tools Work

```
Your Chat → Dedalus SDK → AI Model (sees available tools)
                             ↓
                      Decides to use tool
                             ↓
                MCP Server executes tool
                             ↓
                      Returns result
                             ↓
              AI incorporates result in response
```

### Why Tools Aren't Working Yet

The `mcp_server.py` defines tools using the `@tool` decorator, but they need to be:
1. **Served** via HTTP/MCP protocol
2. **Connected** to the Dedalus SDK
3. **Discovered** by the AI model

This requires either:
- Deploying to Dedalus marketplace
- Setting up a local MCP protocol server
- Using existing marketplace servers

---

## Summary

✅ **Working Now**:
- `chat_simple.py` - Interactive chat
- `dedalus.py` - SDK for your code
- `example_usage.py` - Code examples

🔧 **Needs Setup**:
- MCP tool integration
- Requires deployment or marketplace servers

🚀 **Recommended**:
1. Start with `chat_simple.py` for immediate use
2. Use the SDK in your projects
3. Explore Dedalus marketplace for existing tools
4. Deploy your own tools later if needed

---

## Quick Start

```bash
# Chat now
uv run python chat_simple.py

# Or use in your code
from dedalus import DedalusClient
client = DedalusClient()
# ... your code ...
```

**Questions?** Check `DEDALUS_README.md` or visit https://docs.dedaluslabs.ai
