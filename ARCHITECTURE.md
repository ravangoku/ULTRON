# Architecture

The frontend is a Vite React/TypeScript console. The FastAPI API owns policy enforcement and publishes REST plus `/ws/chat` token events. `services/llm.py` is the provider seam: `mock` is usable offline and `openai`/`openai_compatible` use an OpenAI-compatible chat-completions endpoint. No provider logic leaks into routes.

The development `RuntimeStore` is deliberately ephemeral. PostgreSQL + pgvector schema in `infra/postgres/init.sql` is the persistent target for conversations, memories, projects, tasks, knowledge provenance, embeddings, audit logs, automation jobs, and system events. Redis is reserved for caching, queues, sessions, and temporary event state; a worker is an explicit next production deployment component.

Research ingestion design: discovery → policy/robots validation → fetch → parse → clean → chunk → hash/metadata → embed → vector store → retrieve/rerank → answer with citations. Untrusted content is data only, never executable instructions.
