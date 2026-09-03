from collections import defaultdict
from datetime import datetime
from app.core.models import MemoryCreate, MemoryRecord, Task, TaskCreate


class RuntimeStore:
    """Development store; swap with Postgres repositories in deployed environments."""
    def __init__(self) -> None:
        self.memories: list[MemoryRecord] = []
        self.tasks: list[Task] = []
        self.histories: dict[str, list[dict[str, str]]] = defaultdict(list)
        self.audit_log: list[dict] = []

    def save_memory(self, memory: MemoryCreate) -> MemoryRecord:
        if not memory.authorized:
            raise PermissionError("Explicit authorization is required before ULTRON stores memory.")
        record = MemoryRecord(**memory.model_dump())
        self.memories.append(record)
        return record

    def search_memories(self, query: str, limit: int) -> list[MemoryRecord]:
        terms = set(query.lower().split())
        ranked = sorted(self.memories, key=lambda item: (len(terms & set(item.content.lower().split())), item.importance, item.created_at), reverse=True)
        return [item for item in ranked if terms & set(item.content.lower().split())][:limit]

    def create_task(self, task: TaskCreate) -> Task:
        record = Task(**task.model_dump())
        self.tasks.append(record)
        return record

    def audit(self, event: str, **data: object) -> None:
        self.audit_log.append({"event": event, "at": datetime.utcnow().isoformat(), **data})


runtime = RuntimeStore()
