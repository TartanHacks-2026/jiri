# PLAN: Mosaic Aegis - Model Improvement

> **Goal:** Create the "Discovery Brain" - enabling the agent to autonomously find, verify, and use new tools when defaults fail.
> **Role:** "The Brain Upgrade" - Focusing on Aweseome-MCP integration, RAG personalization, and self-healing logic.

## 1. Overview

- **Scope:** Dynamic discovery via Awesome-MCP, Vector Memory integration, and Tool Registry management.
- **Project Type:** BACKEND / DATA
- **Output:** A functional `DiscoveryService` and `MemoryManager`.

## 2. Tech Stack

| Component         | Tech                             | Rationale                                           |
| :---------------- | :------------------------------- | :-------------------------------------------------- |
| **Tool Registry** | **Awesome-MCP API**              | Source of truth for discoverable tools.             |
| **Isolation**     | **uvx (uv)**                     | Ephemeral execution of untrusted tools.             |
| **Memory**        | **ChromaDB + OpenAI Embeddings** | Semantic search for user preferences.               |
| **Logic**         | **Dedalus Registry Client**      | Standardized interface for adding new tool schemas. |

## 3. File Structure

```
mosaic-aegis/
├── src/
│   ├── discovery/
│   │   ├── registry_client.py  # Awesome-MCP query logic
│   │   ├── installer.py        # uvx wrapper
│   │   └── validator.py        # Schema verification
│   └── memory/
│       ├── embeddings.py       # OpenAI Embedding wrapper
│       └── rag_manager.py      # ChromaDB CRUD
└── tests/
    └── test_discovery.py       # Mock Awesome-MCP tests
```

## 4. Task Breakdown

### Phase 1: Dynamic Discovery (The "Search" Skill)

- [ ] **Registry Client**: Implement async client to query Awesome-MCP API (or github raw) for available servers. <!-- best_agent: data-engineer -->
- [ ] **Tool Validator**: Logic to parse `mcp.json` manifests and validate they match required schema. <!-- best_agent: backend-specialist -->
- [ ] **Installation Logic**: Implement `uvx` wrapper to test-run a discovered tool in isolation. <!-- best_agent: security-auditor -->

### Phase 2: Memory & Context (The "Recall" Skill)

- [ ] **Embedding Service**: Async wrapper for OpenAI `text-embedding-3-small`. <!-- best_agent: backend-specialist -->
- [ ] **RAG Manager**: CRUD operations for ChromaDB (Store Preference, Retrieve Context). <!-- best_agent: database-architect -->
- [ ] **Context Injection**: Logic to inject retrieved memories into the System Prompt. <!-- best_agent: backend-specialist -->

### Phase 3: Self-Healing Loop

- [ ] **Fallback Strategy**: Implement logic: `IF tool_not_found THEN trigger_discovery(query)`. <!-- best_agent: backend-specialist -->
- [ ] **Feedback Loop**: Log success/fail of discovered tools to DB to improve future ranking. <!-- best_agent: data-engineer -->

## 5. Phase X: Verification

- [ ] **Discovery Test**: Searching for "Spotify" returns a valid MCP server manifest.
- [ ] **Installation Test**: `uvx` successfully runs a test tool.
- [ ] **RAG Test**: Query "My favorite food" retrieves previously stored preference.
- [ ] **Performance**: Discovery lookup takes < 2s (cached).
