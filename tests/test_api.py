from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import classifier, llm_router


client = TestClient(app)


async def fake_classify(query: str):
    if "python" in query.lower():
        return "coding", 0.95

    return "writing", 0.90


async def fake_generate(query: str):
    return f"Mock response for: {query}"


def test_chat_coding(monkeypatch):

    monkeypatch.setattr(
        classifier,
        "classify",
        fake_classify
    )

    monkeypatch.setattr(
        llm_router.providers["provider_a"],
        "generate",
        fake_generate
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "query": "Write Python code"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "coding"
    assert data["provider"] == "provider_a"
    assert data["fallback_used"] is False
    assert "Mock response" in data["response"]


def test_chat_writing(monkeypatch):

    monkeypatch.setattr(
        classifier,
        "classify",
        fake_classify
    )

    monkeypatch.setattr(
        llm_router.providers["provider_b"],
        "generate",
        fake_generate
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "query": "Write a professional email"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"] == "writing"
    assert data["provider"] == "provider_b"
    assert data["fallback_used"] is False
    assert "Mock response" in data["response"]


def test_empty_query():

    response = client.post(
        "/api/v1/chat",
        json={
            "query": ""
        }
    )

    assert response.status_code == 400


def test_missing_query():

    response = client.post(
        "/api/v1/chat",
        json={}
    )

    assert response.status_code == 422


def test_chat_manual_override(monkeypatch):

    monkeypatch.setattr(
        classifier,
        "classify",
        fake_classify
    )

    monkeypatch.setattr(
        llm_router.providers["provider_b"],
        "generate",
        fake_generate
    )

    # Force provider_b despite "python" in query
    response = client.post(
        "/api/v1/chat",
        json={
            "query": "Write Python code",
            "provider": "provider_b"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["provider"] == "provider_b"
    assert "metrics" in data
    assert "classification_latency" in data["metrics"]
    assert "generation_latency" in data["metrics"]
    assert "total_latency" in data["metrics"]
    assert "model" in data