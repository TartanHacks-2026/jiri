# Agentuity Bridge Runbook (Jiri)

Use these commands exactly from the repo root:

```bash
cd /Users/nihal/Desktop/Repos/jiri
```

## 1) One-time fix: remove accidental gitlink/submodule

If `apps/agent-runtime` was committed as mode `160000`, run:

```bash
git switch -c feat/agentuity-bridge
git rm --cached apps/agent-runtime
rm -rf apps/agent-runtime/.git
git add apps/agent-runtime
git add .gitignore
```

Then verify:

```bash
git ls-files -s apps/agent-runtime
```

You should see regular file entries (not a single `160000` gitlink line).

## 2) Environment setup

### Frontend env

```bash
cp apps/web/.env.example apps/web/.env.local
```

Expected values:

- `NEXT_PUBLIC_AGENTUITY_API_URL=http://127.0.0.1:3500`
- `NEXT_PUBLIC_JIRI_WS_URL=ws://localhost:8000/ws`
- `NEXT_PUBLIC_JIRI_SSE_URL=http://localhost:8000/events`

### Agentuity runtime env

```bash
cp apps/agent-runtime/.env.example apps/agent-runtime/.env
```

Set:

- `JIRI_BACKEND_URL=http://127.0.0.1:8000`
- `AGENTUITY_SDK_KEY=...` (from `agentuity auth login`)

## 3) Install dependencies

```bash
cd /Users/nihal/Desktop/Repos/jiri/apps/web && npm install
cd /Users/nihal/Desktop/Repos/jiri/apps/agent-runtime && npm install
```

If `bun` is not found:

```bash
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```

## 4) Start all services (3 terminals)

### Terminal A: Python backend

```bash
cd /Users/nihal/Desktop/Repos/jiri
uv run uvicorn src.jiri.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal B: Agentuity runtime proxy

```bash
cd /Users/nihal/Desktop/Repos/jiri/apps/agent-runtime
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
agentuity dev
```

### Terminal C: Next frontend

```bash
cd /Users/nihal/Desktop/Repos/jiri/apps/web
npm run dev
```

Open `http://localhost:3000`.

## 5) Smoke tests

```bash
curl -sS http://127.0.0.1:8000/health
curl -sS http://127.0.0.1:3500/api/jiri/health
curl -sS -X POST http://127.0.0.1:3500/api/jiri/turn \
  -H "content-type: application/json" \
  -d '{"session_id":"","user_text":"hello","client":"web","meta":{"device":"web","voice":false,"timezone":"America/New_York"}}'
```

## 6) Common messages

- `[INFO] [Vite Asset] Port 5173 is in use, trying another one...`
  - Normal. Agentuity web assets move to another free port.
- `does not appear to be a valid Agentuity project`
  - You are in the wrong folder, or project scaffold files are missing.
  - Must contain `apps/agent-runtime/package.json`, `apps/agent-runtime/app.ts`, and `apps/agent-runtime/src/`.
- `fatal: couldn't find remote ref mian`
  - Typo. Use `main`.

## 7) Commit

```bash
cd /Users/nihal/Desktop/Repos/jiri
git add .
git commit -m "feat: bridge frontend to backend via Agentuity fallback proxy"
git push origin feat/agentuity-bridge
```
