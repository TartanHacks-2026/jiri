# Jiri - Voice-First Agentic Bridge

> Talk to Siri, it calls our backend agent, gets a reply, speaks it back, and keeps context across turns using a session_id.

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/TartanHacks-2026/jiri.git
cd jiri

# 2. Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 3. Run with Docker (recommended for team)
./run.sh
```

## API Endpoint

**POST /turn** - Main conversation endpoint

```bash
curl -X POST http://localhost:8000/turn \
  -H "Content-Type: application/json" \
  -d '{"session_id":"","user_text":"hello","client":"shortcut","meta":{"voice":true}}'
```

Response:
```json
{
  "session_id": "uuid",
  "reply_text": "Hey! I'm Jiri. How can I help?",
  "end_conversation": false
}
```

## Project Structure

```
jiri/
├── src/
│   ├── api/           # FastAPI app & /turn endpoint
│   ├── session/       # Redis-backed session store
│   └── orchestrator/  # LLM agent & fallback logic
├── docs/              # API contract & Shortcut guide
├── tests/             # Unit tests
├── docker-compose.yml # Container orchestration
└── run.sh             # One-command startup
```

## For Team (4 Laptops)

Docker ensures consistent environments:

```bash
# Everyone runs the same command
docker-compose up --build

# API available at http://localhost:8000
# Redis at localhost:6379
```

## Siri Shortcut Setup

See [docs/shortcut_contract.md](docs/shortcut_contract.md) for complete build guide.

## Tech Stack

- **Python 3.13** + **FastAPI**
- **Redis** (containerized session store)
- **OpenAI GPT-4o** (conversation)
- **Docker Compose** (deployment)
