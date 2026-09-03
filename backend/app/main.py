from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.models import AutomationCreate, ChatRequest, ChatResponse, MemoryCreate, MemorySearch, ResearchRequest, TaskCreate, ToolExecute
from app.services.llm import provider_for
from app.services.runtime import runtime
from app.services.tools import REGISTRY, execute_tool

settings = get_settings()

@asynccontextmanager
async def lifespan(_: FastAPI):
    yield

app = FastAPI(title="ULTRON API", version="0.1.0", description="Safety-first personal AI operating system API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=False, allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type", "Authorization"])

@app.get("/health")
async def health(): return {"status": "ok", "service": settings.app_name}

@app.get("/system/status")
async def system_status():
    return {"status": "ready", "environment": settings.environment, "llm_provider": settings.llm_provider, "memory_backend": "development-memory", "emergency_stop": settings.emergency_stop, "registered_tools": list(REGISTRY)}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    conversation_id = request.conversation_id or uuid4()
    history = runtime.histories[str(conversation_id)][-12:]
    try: response = await provider_for(settings).complete(request.message, history)
    except RuntimeError as exc: raise HTTPException(503, str(exc)) from exc
    runtime.histories[str(conversation_id)].extend([{"role": "user", "content": request.message}, {"role": "assistant", "content": response}])
    runtime.audit("chat", conversation_id=str(conversation_id), mode=request.mode)
    return ChatResponse(conversation_id=conversation_id, response=response, confidence=0.35 if settings.llm_provider == "mock" else 0.7, provider=settings.llm_provider, safety_note="No external action was taken.")

@app.websocket("/ws/chat")
async def chat_stream(socket: WebSocket):
    await socket.accept()
    try:
        while True:
            payload = await socket.receive_json(); request = ChatRequest.model_validate(payload)
            await socket.send_json({"type": "status", "status": "thinking"})
            try:
                async for token in provider_for(settings).stream(request.message, []): await socket.send_json({"type": "token", "value": token})
            except RuntimeError as exc: await socket.send_json({"type": "error", "message": str(exc)})
            await socket.send_json({"type": "complete"})
    except WebSocketDisconnect: return

@app.post("/memory/store")
async def store_memory(memory: MemoryCreate):
    try: return runtime.save_memory(memory)
    except PermissionError as exc: raise HTTPException(403, str(exc)) from exc
@app.get("/memory")
async def list_memory(): return runtime.memories
@app.post("/memory/search")
async def search_memory(request: MemorySearch): return runtime.search_memories(request.query, request.limit)
@app.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str):
    runtime.memories[:] = [item for item in runtime.memories if str(item.id) != memory_id]; return {"deleted": memory_id}
@app.post("/tasks")
async def create_task(task: TaskCreate): return runtime.create_task(task)
@app.get("/tasks")
async def list_tasks(): return runtime.tasks
@app.post("/tools/execute")
async def tools_execute(call: ToolExecute):
    result = execute_tool(call.name, call.arguments, call.confirmed, settings.emergency_stop); runtime.audit("tool_call", tool=call.name, result=result); return result
@app.post("/research")
async def research(request: ResearchRequest):
    if settings.web_search_provider == "disabled": raise HTTPException(503, "Research is disabled. Configure an approved web search provider; no web result was fabricated.")
    raise HTTPException(501, "Configured research provider adapter is not yet installed.")
@app.post("/automation")
async def automation(job: AutomationCreate):
    if not job.confirmed: raise HTTPException(409, "Automation requires explicit confirmation before it is scheduled.")
    return {"status": "accepted", "message": "Scheduler integration is configuration-gated in this Phase 1 build."}
@app.post("/voice/transcribe")
async def transcribe(): raise HTTPException(501, "Configure an STT adapter to enable transcription.")
@app.post("/voice/speak")
async def speak(): raise HTTPException(501, "Configure an expressive TTS adapter to enable synthesized speech.")
@app.post("/vision/analyze")
async def vision(): raise HTTPException(501, "Configure a vision adapter to enable image analysis.")
@app.get("/projects")
async def projects(): return []
@app.post("/projects")
async def create_project(): raise HTTPException(501, "Project persistence is pending PostgreSQL repository configuration.")
