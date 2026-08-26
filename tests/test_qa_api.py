"""API integration tests for Q&A logging, feedback, and FAQ promotion."""

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


def _login(
    client: TestClient, username: str = "admin", password: str = "admin123"
) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}


def test_ask_logs_feedback_promote(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    headers = _login(client)
    client.post(
        "/ingest",
        files={"file": ("a.md", "# GPIO\ngpio init\n".encode("utf-8"), "text/markdown")},
        data={"customer": "acme"},
        headers=headers,
    )
    response = client.post("/ask", json={"question": "gpio init"}, headers=headers)
    assert response.status_code == 200

    response = client.get("/qa/recent", headers=headers)
    assert response.status_code == 200
    qa = response.json()["qa"]
    assert qa and qa[0]["question"] == "gpio init"
    qa_id = qa[0]["id"]

    feedback_response = client.post(
        f"/qa/{qa_id}/feedback", json={"feedback": 1}, headers=headers
    )
    assert feedback_response.status_code == 200
    promote_response = client.post(f"/qa/{qa_id}/promote", headers=headers)
    assert promote_response.status_code == 200

    documents = client.get("/documents", headers=headers).json()["documents"]
    assert any(document["source"].startswith("faq:") for document in documents)


def test_similar_questions(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    headers = _login(client)
    client.post("/ask", json={"question": "gpio init"}, headers=headers)
    response = client.get("/qa/similar", params={"question": "gpio"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["similar"]


def test_customer_cannot_list_qa(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    admin = _login(client)
    client.post(
        "/users",
        json={"username": "acme", "password": "pw", "role": "customer", "customers": ["acme"]},
        headers=admin,
    )
    customer = _login(client, "acme", "pw")
    assert client.get("/qa/recent", headers=customer).status_code == 403
