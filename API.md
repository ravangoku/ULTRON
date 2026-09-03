# API

Implemented: `POST /chat`, `GET /system/status`, `POST /memory/store`, `GET /memory`, `POST /memory/search`, `DELETE /memory/{id}`, `POST/GET /tasks`, `POST /tools/execute`, `POST /research`, `POST /automation`, stubbed adapter endpoints for voice and vision, and `GET/POST /projects`. `POST /chat` accepts `{message, conversation_id?, mode}`. `ws://host/ws/chat` accepts the same payload and emits `status`, `token`, and `complete` events. Full schemas are versioned in OpenAPI at `/docs`.
