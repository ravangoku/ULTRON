from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
def test_health_and_status():
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/system/status").json()["emergency_stop"] is False
def test_chat_uses_explicit_mock_disclosure():
    response = client.post("/chat", json={"message":"Hello"})
    assert response.status_code == 200
    assert "demonstration mode" in response.json()["response"]
def test_memory_requires_authorization():
    assert client.post("/memory/store",json={"content":"private preference"}).status_code == 403
    assert client.post("/memory/store",json={"content":"use metric units","authorized":True}).status_code == 200
def test_calculator_and_unknown_tool_safety():
    assert client.post("/tools/execute",json={"name":"calculator","arguments":{"expression":"8 * (3 + 2)"}}).json()["result"] == 40
    assert client.post("/tools/execute",json={"name":"shell","arguments":{}}).status_code == 200
    assert client.post("/tools/execute",json={"name":"shell","arguments":{}}).json()["ok"] is False
