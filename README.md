# Jiri 🎙️

**Voice-first agentic bridge with MCP tool discovery**

A high-fidelity, low-latency voice assistant that connects to the Model Context Protocol ecosystem for dynamic tool execution.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (3.13 recommended)
- Docker & Docker Compose
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/TartanHacks-2026/jiri.git
cd jiri

# Copy environment config
cp .env.example .env

# Edit .env with your settings (optional for local dev)
```

### 2. Start Infrastructure

```bash
# Start TimescaleDB, Redis, ChromaDB
docker-compose up -d

# Wait for services to be healthy
docker-compose ps
```

### 3. Install Dependencies

```bash
# Using uv (recommended - fast!)
uv sync

# Or using pip
pip install -e ".[dev]"
```

### 4. Run the Backend

```bash
# Development mode with hot reload
uv run uvicorn jiri.main:app --reload --port 8000

# Or using Python directly
python -m jiri.main
```

### 5. Verify

```bash
# Health check
curl http://localhost:8000/health

# Readiness check (tests DB/Redis)
curl http://localhost:8000/health/ready

# API docs (development only)
open http://localhost:8000/docs
```

## 📱 Siri Shortcut Setup

See [docs/shortcut_contract.md](docs/shortcut_contract.md) for complete build guide.

## 📁 Project Structure

```
jiri/
├── src/
│   ├── jiri/               # Main Backend (Robust Architecture)
│   │   ├── main.py         # FastAPI entrypoint
│   │   ├── core/           # Core infrastructure
│   │   ├── models/         # SQLAlchemy models
│   │   └── routers/        # API endpoints
│   ├── api/                # Legacy/Alternative API (to be merged)
│   ├── session/            # Legacy Session store
│   └── orchestrator/       # Legacy Orchestrator logic
├── docker-compose.yml      # Infrastructure services
├── pyproject.toml          # Python dependencies
├── alembic/                # Database migrations
└── tests/                  # Test suite
```

## 🔧 Configuration

All configuration is via environment variables (`.env` file):

| Variable       | Description           | Default                    |
| -------------- | --------------------- | -------------------------- |
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://...` |
| `REDIS_URL`    | Redis connection      | `redis://localhost:6379/0` |
| `API_KEY`      | Service auth key      | `CHANGE_ME_IN_PRODUCTION`  |
| `DEBUG`        | Enable debug mode     | `true`                     |

## 🐳 Docker Services

| Service     | Port | Description          |
| ----------- | ---- | -------------------- |
| TimescaleDB | 5432 | Time-series database |
| Redis       | 6379 | Session state cache  |
| ChromaDB    | 8001 | Vector store for RAG |

## 🧪 Development

```bash
# Run linting
ruff check .

# Run type checking
mypy src/

# Run tests
pytest

# Format code
ruff format .
```

## 📚 Documentation

- [PLAN-backend-infra.md](plans/PLAN-backend-infra.md) - Backend infrastructure plan
- [PLAN-voice-mcp-pipeline.md](plans/PLAN-voice-mcp-pipeline.md) - Voice pipeline plan
- [agent_docs/](agent_docs/) - Architecture and patterns

## 🔒 Security

- API key authentication for all protected endpoints
- Zero-trust credential injection via Dedalus proxy
- No secrets in logs or LLM context

## 📄 License

MIT
