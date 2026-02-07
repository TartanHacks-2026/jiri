# PLAN: Jiri - Backend Infrastructure

> **Goal:** Establish a robust, scalable backend foundation that supports high-concurrency voice streams and persistent state.
> **Role:** "The Backbone" - Providing Database, Auth, and Deployment infrastructure for other roles.

## 1. Overview

- **Scope:** Docker orchestration, Database (Timescale/Chroma/Redis) setup, Authentication, and Cloud Deployment configuration.
- **Project Type:** BACKEND
- **Output:** A running `docker-compose` environment and a production-grade FastAPI scaffold.

## 2. Tech Stack

| Component         | Tech               | Rationale                                           |
| :---------------- | :----------------- | :-------------------------------------------------- |
| **Orchestration** | **Docker Compose** | Unified local dev environment for DBs + App.        |
| **Relational DB** | **TimescaleDB**    | Time-series optimized for event logging.            |
| **Vector DB**     | **ChromaDB**       | Local/Containerized vector store for RAG.           |
| **Cache**         | **Redis**          | Sub-millisecond state for voice session management. |
| **Migrations**    | **Alembic**        | Schema version control.                             |

## 3. File Structure

```
jiri/
├── docker-compose.yml          # Services config
├── .env                        # Secrets (Gitignored)
├── infra/
│   ├── timescale/              # Init scripts
│   └── chroma/                 # Config
├── src/
│   ├── core/
│   │   ├── database.py         # Async engine
│   │   ├── security.py         # Auth logic
│   │   └── config.py           # Settings
│   └── models/                 # SQLAlchemy models
└── alembic/                    # Migration scripts
```

## 4. Task Breakdown

### Phase 1: Container Orchestration

- [ ] **Docker Compose**: Create `docker-compose.yml` defining services: `timescakedb`, `chromadb`, `redis`, `app`. <!-- best_agent: devops-engineer -->
- [ ] **Env Config**: define `.env.example` with standard ports and default credentials. <!-- best_agent: backend-specialist -->
- [ ] **Health Checks**: Add `healthcheck` blocks to all services to ensure ready state. <!-- best_agent: devops-engineer -->

### Phase 2: Database Layer

- [ ] **Async Engine**: Implement `src/core/database.py` using `sqlalchemy[asyncio]`. <!-- best_agent: database-architect -->
- [ ] **Models**: Define `InteractionLog` model (User, Timestamp, Intent, Latency). <!-- best_agent: database-architect -->
- [ ] **Migrations**: Initialize Alembic and generate initial migration script. <!-- best_agent: database-architect -->
- [ ] **Redis Client**: Implement async Redis wrapper for `UserSession` state management. <!-- best_agent: backend-specialist -->

### Phase 3: Security & Core

- [ ] **API Security**: Implement `APIKeyHeader` dependency for internal service-to-service auth. <!-- best_agent: security-auditor -->
- [ ] **Logging**: Configure `structlog` or `loguru` for JSON formatted logs (essential for observability). <!-- best_agent: backend-specialist -->

## 5. Phase X: Verification

- [ ] **Containers Up**: `docker-compose up -d` starts all services Healthy.
- [ ] **DB Connect**: Backend can SELECT 1 from Timescale.
- [ ] **Redis Connect**: Backend can SET/GET a key.
- [ ] **Persistance**: Restarting containers does not lose data.
