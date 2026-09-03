# Setup

Copy `.env.example` to `.env`; do not commit it. Set `ULTRON_LLM_PROVIDER=openai` or `openai_compatible`, `ULTRON_LLM_API_KEY`, model, and optional base URL to enable a real LLM. Set an explicitly supported STT/TTS provider before enabling voice. For original cinematic delivery, select a licensed voice with consent and use a speech-performance layer (SSML/prosody/style); do not clone or imitate a real performer.

Run services with `docker compose up --build`, or use the commands in the README. Apply the initial schema through the PostgreSQL container's initialization mount. The API's OpenAPI contract is served at `/docs`.
