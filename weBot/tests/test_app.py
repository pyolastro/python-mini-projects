import pytest
from fastapi.testclient import TestClient
from app import app, conversations

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_memory():
    """Clear in-memory conversations between tests."""
    conversations.clear()

def test_rest_chat_rules_brain():
    """Simple REST test using the fallback RulesBrain."""
    body = {"user_id": "tester", "message": "hello"}
    response = client.post("/chat", json=body)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["user_id"] == "tester"
    assert isinstance(data["reply"], str)

def test_history_endpoint():
    """Check that chat history persists."""
    client.post("/chat", json={"user_id": "x", "message": "hi"})
    res = client.get("/history/x")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert any(m["role"] == "user" for m in items)

def test_websocket_basic():
    """Test WebSocket roundtrip."""
    with client.websocket_connect("/ws/testuser") as ws:
        ws.send_text("hello")
        reply = ws.receive_text()
        assert isinstance(reply, str)
