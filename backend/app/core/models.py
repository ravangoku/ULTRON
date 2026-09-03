from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Mode(StrEnum):
    conversation = "conversation"
    command = "command"
    research = "research"
    coding = "coding"
    vision = "vision"
    system = "system"
    automation = "automation"
    focus = "focus"
    silent = "silent"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    conversation_id: UUID | None = None
    mode: Mode = Mode.conversation


class Citation(BaseModel):
    title: str
    url: str
    retrieved_at: datetime
    trust_score: float = Field(ge=0, le=1)


class ChatResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID = Field(default_factory=uuid4)
    response: str
    confidence: float = Field(ge=0, le=1)
    citations: list[Citation] = []
    provider: str
    safety_note: str | None = None


class MemoryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    kind: str = Field(default="semantic", pattern="^(semantic|episodic|procedural|project)$")
    importance: int = Field(default=3, ge=1, le=5)
    authorized: bool = False


class MemoryRecord(MemoryCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MemorySearch(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(default="", max_length=5000)


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ToolExecute(BaseModel):
    name: str
    arguments: dict = {}
    confirmed: bool = False


class ResearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    deep: bool = False


class AutomationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    schedule: str = Field(min_length=1, max_length=200)
    action: str = Field(min_length=1, max_length=1000)
    confirmed: bool = False
