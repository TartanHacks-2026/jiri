# Dedalus Integration File Structure

Complete overview of all Dedalus-related files and their purposes.

## 📁 File Tree

```
jiri/
├── 🎯 Core Implementation
│   ├── dedalus.py                    # Dedalus SDK wrapper (use this in your app)
│   ├── mcp_server.py                 # MCP server with example tools
│   └── dedalus_demo.py               # Full integration demonstration
│
├── 📚 Documentation
│   ├── DEDALUS_SETUP_COMPLETE.md     # Setup completion summary (you are here!)
│   ├── DEDALUS_QUICKSTART.md         # 5-minute quick start guide ⭐
│   ├── DEDALUS_README.md             # Complete documentation
│   └── DEDALUS_FILE_STRUCTURE.md     # This file
│
├── 🔧 Utilities & Examples
│   ├── example_usage.py              # Simple code examples
│   ├── setup_dedalus.sh              # Automated setup script
│   └── .env.example                  # Environment template (updated)
│
├── 📦 Configuration
│   ├── pyproject.toml                # Dependencies (updated with dedalus packages)
│   └── README.md                     # Main project README (updated with Dedalus section)
│
└── 🌐 External Resources
    └── https://docs.dedaluslabs.ai   # Official Dedalus Labs documentation
```

## 📄 File Purposes

### Core Files

#### `dedalus.py` (177 lines)
**What**: SDK wrapper for Dedalus Labs
**Key Class**: `DedalusClient`
**Main Methods**:
- `chat()` - Simple AI chat
- `run()` - Chat with MCP servers
- `run_with_local_mcp()` - Convenience method for local servers

**Use in your app**:
```python
from dedalus import DedalusClient
client = DedalusClient()
```

#### `mcp_server.py` (85 lines)
**What**: MCP server implementation
**Framework**: `dedalus_mcp`
**Included Tools**:
1. `log_hello()` - Hello world tool
2. `log_message(message)` - Custom logging
3. `get_server_info()` - Server information
4. `add_numbers(a, b)` - Math calculator

**How to extend**:
```python
@tool(description="Your tool")
def my_tool(param: str) -> str:
    return f"Result: {param}"

server.collect(my_tool)
```

#### `dedalus_demo.py` (150 lines)
**What**: Complete integration demo
**Shows**:
- MCP server standalone usage
- SDK chat capabilities
- Integration explanation
- Full workflow

**Run**: `python dedalus_demo.py`

### Documentation Files

#### `DEDALUS_QUICKSTART.md` (⭐ Start here!)
**What**: Fast-track setup guide
**Sections**:
1. Setup (30 seconds)
2. Get API Key (1 minute)
3. Run Examples (3 minutes)
4. Your First Integration
5. Common Tasks
6. Troubleshooting

#### `DEDALUS_README.md`
**What**: Comprehensive documentation
**Sections**:
- Overview & Quick Start
- Usage Examples
- Available Tools
- Architecture
- Adding Custom Tools
- Environment Variables
- Troubleshooting
- Resources

#### `DEDALUS_SETUP_COMPLETE.md`
**What**: Setup completion summary
**Contents**:
- What was created
- How to get started
- Key concepts
- Next steps
- Common questions

#### `DEDALUS_FILE_STRUCTURE.md`
**What**: This file - complete file overview

### Examples & Utilities

#### `example_usage.py` (130 lines)
**What**: Simple, modifiable examples
**Examples**:
1. Simple chat without tools
2. Using local MCP server
3. Using different AI models

**Best for**: Learning and quick testing

#### `setup_dedalus.sh` (50 lines)
**What**: Automated setup script
**Does**:
1. Creates `.env` from template
2. Installs dependencies
3. Shows next steps

**Run**: `./setup_dedalus.sh`

## 🔄 File Relationships

```
User Application
      ↓
   dedalus.py (DedalusClient)
      ↓
   Dedalus Labs SDK (dedalus-labs package)
      ↓
   AI Model (Claude/GPT/etc.) ←→ mcp_server.py (Tools)
      ↓
   Response
```

## 🎯 Quick Reference

### I want to...

| Task | File to Use | Command |
|------|-------------|---------|
| Get started quickly | `DEDALUS_QUICKSTART.md` | Read the guide |
| See a demo | `dedalus_demo.py` | `python dedalus_demo.py` |
| Run examples | `example_usage.py` | `python example_usage.py` |
| Add a tool | `mcp_server.py` | Edit and add `@tool` function |
| Use in my app | `dedalus.py` | Import `DedalusClient` |
| Learn more | `DEDALUS_README.md` | Read full docs |
| Setup environment | `setup_dedalus.sh` | `./setup_dedalus.sh` |
| Troubleshoot | `DEDALUS_QUICKSTART.md` | Check troubleshooting section |

## 📊 File Statistics

| Category | Files | Total Lines |
|----------|-------|-------------|
| Core Code | 3 | ~400 |
| Documentation | 4 | ~600 |
| Examples | 1 | ~130 |
| Utilities | 1 | ~50 |
| **Total** | **9** | **~1,180** |

## 🚀 Recommended Reading Order

1. ✅ `DEDALUS_SETUP_COMPLETE.md` (if you haven't already)
2. ✅ `DEDALUS_QUICKSTART.md` (5-minute guide)
3. ✅ Run `python dedalus_demo.py` (see it in action)
4. ✅ Run `python example_usage.py` (try examples)
5. ✅ Read `DEDALUS_README.md` (when you need details)
6. ✅ Edit `mcp_server.py` (add your own tools)
7. ✅ Import `dedalus.py` in your app (integrate)

## 🔗 External Dependencies

Added to `pyproject.toml`:

```toml
dependencies = [
    # ... existing dependencies ...
    "dedalus-labs>=0.1.0",     # Dedalus Labs SDK
    "dedalus-mcp>=0.1.0",      # MCP server framework
]
```

## 🌟 Key Features

| Feature | File | Description |
|---------|------|-------------|
| Multi-model support | `dedalus.py` | Claude, GPT, Gemini, etc. |
| Easy tool creation | `mcp_server.py` | `@tool` decorator |
| Auto schema generation | `mcp_server.py` | Type hints → JSON Schema |
| Local & hosted MCP | `dedalus.py` | Both supported |
| Async support | All | Full async/await |

## 📞 Need Help?

1. Check `DEDALUS_QUICKSTART.md` troubleshooting section
2. Read `DEDALUS_README.md` for detailed docs
3. Visit https://docs.dedaluslabs.ai
4. Review `example_usage.py` for code samples

---

**Ready to start?** → `python dedalus_demo.py`
