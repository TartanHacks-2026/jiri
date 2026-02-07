# Dedalus Quick Start Guide

Get up and running with Dedalus SDK and MCP Server in 5 minutes.

## 1. Setup (30 seconds)

```bash
# Run the setup script
./setup_dedalus.sh

# Or manually:
cp .env.example .env
# Edit .env and add your DEDALUS_API_KEY
uv sync
```

## 2. Get API Key (1 minute)

1. Go to [dedaluslabs.ai](https://dedaluslabs.ai)
2. Sign up / Log in
3. Copy your API key
4. Add to `.env`: `DEDALUS_API_KEY=your-key-here`

## 3. Run Examples (3 minutes)

### Option A: Full Demo

```bash
python dedalus_demo.py
```

Shows:
- MCP server capabilities
- SDK chat examples
- How they work together

### Option B: Quick Test

```bash
python example_usage.py
```

Simple examples you can modify.

### Option C: Individual Components

```bash
# Test SDK only
python dedalus.py

# Test MCP server only
python mcp_server.py
```

## 4. Your First Integration

### Step 1: Create a tool

Edit `mcp_server.py`:

```python
from dedalus_mcp import tool

@tool(description="Your custom tool")
def my_tool(param: str) -> str:
    return f"Processed: {param}"

# Add to server
server.collect(my_tool)
```

### Step 2: Start the server

```bash
python mcp_server.py
```

### Step 3: Use it with SDK

```python
from dedalus import DedalusClient

client = DedalusClient()
response = await client.run_with_local_mcp(
    "Use my_tool with parameter 'test'",
    mcp_url="http://localhost:8000/mcp"
)
print(response)
```

## Common Tasks

### Change AI Model

```python
# Default: Claude Sonnet 4
response = await client.chat("Hello")

# Use GPT-4
response = await client.chat("Hello", model="openai/gpt-4o")

# Use Gemini
response = await client.chat("Hello", model="google/gemini-2.0-flash-exp")
```

### Add More Tools

```python
@tool(description="Calculate factorial")
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)

@tool(description="Get current weather")
async def get_weather(city: str) -> dict:
    # Your API call here
    return {"city": city, "temp": 72, "condition": "sunny"}

server.collect(factorial)
server.collect(get_weather)
```

### Connect to Hosted MCP Server

```python
# Instead of local server
response = await client.run(
    "Search for docs",
    mcp_servers=["your-org/your-server"]  # Marketplace slug
)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key required" | Set `DEDALUS_API_KEY` in `.env` |
| "Connection refused" | Start MCP server: `python mcp_server.py` |
| "Tool not found" | Make sure `server.collect(tool)` is called |
| Tools not being used | Be explicit: "Use the X tool to do Y" |

## File Overview

```
jiri/
├── dedalus.py              # SDK wrapper (use this in your app)
├── mcp_server.py           # MCP server with tools
├── dedalus_demo.py         # Full demo
├── example_usage.py        # Simple examples
├── setup_dedalus.sh        # Setup script
├── DEDALUS_README.md       # Full documentation
└── DEDALUS_QUICKSTART.md   # This file
```

## Next Steps

1. ✅ Read full docs: `DEDALUS_README.md`
2. ✅ Check examples: `example_usage.py`
3. ✅ Build your tools: Edit `mcp_server.py`
4. ✅ Integrate: Use `DedalusClient` in your app
5. ✅ Deploy: Host on Dedalus marketplace

## Resources

- 📚 Documentation: https://docs.dedaluslabs.ai
- 🚀 Quickstart: https://docs.dedaluslabs.ai/dmcp/quickstart
- 🛠️ MCP Guide: https://docs.dedaluslabs.ai/dmcp/server/overview
- 💬 Examples: https://docs.dedaluslabs.ai/dmcp/examples

---

**Need help?** Check DEDALUS_README.md or visit docs.dedaluslabs.ai
