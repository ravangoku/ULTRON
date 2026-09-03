# ULTRON — safety-first personal AI OS

ULTRON is an original, modular personal AI system—not a replica of a fictional character. This Phase 1 release provides a working FastAPI chat API, pluggable LLM adapters, WebSocket token streaming, explicit memory consent, a permission-aware tool registry, initial PostgreSQL/pgvector schema, and a React/TypeScript operations console.

## Quick start
1. `cp .env.example .env`; leave `ULTRON_LLM_PROVIDER=mock` for a no-key demo, or configure an approved OpenAI-compatible endpoint and key.
2. Backend: `cd backend && python -m venv .venv && .venv/bin/pip install -e '.[dev]' && .venv/bin/uvicorn app.main:app --reload`.
3. Frontend: `cd frontend && npm install && npm run dev`.
4. Visit `http://localhost:5173`; API docs are at `http://localhost:8000/docs`.

Use `docker compose up --build` after copying `.env`. Production requires real authentication, persistent repository implementations, a worker deployment, HTTPS, and secret management before exposing this system publicly.

## Implemented safety boundaries
- No fabricated external results: mock mode states its limitation; research is unavailable until an approved provider is configured.
- Memory requires explicit `authorized: true` on every store request.
- Only allowlisted tools execute; the emergency-stop configuration blocks all tools.
- Automations require confirmation; external computer control is intentionally not enabled.
- The voice endpoint is adapter-gated. ULTRON must use an original licensed/consented expressive voice, never a cloned actor or movie audio.

See [Architecture](ARCHITECTURE.md), [setup](SETUP.md), [API](API.md), and [security](SECURITY.md).
