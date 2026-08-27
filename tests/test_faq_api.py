"""API integration tests for curated FAQ endpoints and FAQ-priority answers."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import create_app


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("RAGKB_LLM_PROVIDER", "fake")
    monkeypatch.setenv("RAGKB_EMBEDDING_PROVIDER", "fake")
    monkeypatch.setenv("RAGKB_RETRIEVAL_MODE", "vector")
    monkeypatch.setenv("RAGKB_STORE_PATH", str(tmp_path / "store.sqlite"))
    monkeypatch.setenv("RAGKB_JWT_SECRET", "test-secret-key-for-ragkb-0123456789")
    return TestClient(create_app())


def _login(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}


def test_faq_crud_flow(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    headers = _login(client)

    response = client.post(
        "/faqs",
        json={
            "question": "如何配置一个新的串口",
            "answer": "步骤一、步骤二",
            "category": "AB5766C",
        },
        headers=headers,
    )
    assert response.status_code == 200
    faq_id = response.json()["id"]

    faqs = client.get("/faqs", headers=headers).json()["faqs"]
    assert any(f["question"] == "如何配置一个新的串口" for f in faqs)

    response = client.patch(f"/faqs/{faq_id}", json={"answer": "新答案"}, headers=headers)
    assert response.status_code == 200
    assert client.get("/faqs", headers=headers).json()["faqs"][0]["answer"] == "新答案"

    response = client.delete(f"/faqs/{faq_id}", headers=headers)
    assert response.status_code == 200
    assert client.get("/faqs", headers=headers).json()["faqs"] == []


def test_faq_answer_priority(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    headers = _login(client)
    client.post(
        "/faqs",
        json={
            "question": "如何配置一个新的串口",
            "answer": "标准步骤：使能 UART1 并配置 IO 复用。",
            "category": "",
        },
        headers=headers,
    )

    response = client.post("/ask", json={"question": "如何配置一个新的串口"}, headers=headers)
    assert response.status_code == 200
    citations = response.json()["citations"]
    assert any(citation["source"] == "FAQ 沉淀" for citation in citations)
