# 🌐 Web UI for Jiri MCP Router

A beautiful web interface for interacting with the MCP Router with real-time logging.

## Features

- 💬 **Chat Interface**: Send queries just like the console
- 📊 **Live Logging**: See real-time logs of tool discovery and execution
- 🗄️ **Cache Visualization**: View currently cached MCP servers
- 🎨 **Beautiful UI**: Clean, modern interface with Tailwind CSS

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/deepanshsaxena/Documents/Jiri/jiri
uv pip install websockets
```

### 2. Start the Web Server

```bash
cd /Users/deepanshsaxena/Documents/Jiri/jiri/MCP
uv run python web_server.py
```

### 3. Open in Browser

Navigate to: **http://localhost:8080**

## Usage

1. Type your query in the text box (e.g., "How is MSFT stock doing?")
2. Press Enter or click "Send"
3. Watch the **Live Logs** panel on the right to see:
   - 🔍 Tool discovery
   - ✅ Successful operations
   - ❌ Errors
   - 📊 Server connections
4. Check the **Cached Servers** panel to see which MCP servers are currently loaded

## Features Explained

### Chat Area (Left)
- Send natural language queries
- View assistant responses
- Clean, conversation-style interface

### Cached Servers (Top Right)
- Shows which MCP servers are currently in the cache
- Updates in real-time as servers are discovered and used
- Helps you understand which tools are available

### Live Logs (Bottom Right)
- Real-time stream of all router operations
- Color-coded by type:
  - 🟣 Purple: Discovery operations
  - 🟢 Green: Success
  - 🔴 Red: Errors
  - 🟡 Yellow: Warnings
  - 🔵 Blue: User actions
- Clear button to reset logs
- Auto-scrolls to latest log

## Example Queries

Try these:

- **"How is MSFT stock doing?"** - Discovers and uses Yahoo Finance
- **"What's the weather in Seattle?"** - Discovers Weather MCP (will fail as expected)
- **"What are Elon Musk's recent tweets?"** - Discovers X API MCP
- **"Tell me about restaurants near me"** - Discovers Foursquare Places

## Debugging

The web UI always runs in debug mode, so you'll see all internal logs in the Live Logs panel.

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.
