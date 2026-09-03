# Memory

Working context is conversation history. Explicitly authorized records are stored as semantic, episodic, procedural, or project memory. Phase 1 uses an in-process development store; its target is PostgreSQL/pgvector with provenance, importance, recency, filtering, correction, deletion, and export APIs. Sensitive facts are never inferred or silently saved.
