"""API integration tests using the fake providers."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import create_app


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("RAGKB_LLM_PROVIDER", "fake")
    monkeypatch.setenv("RAGKB_EMBEDDING_PROVIDER", "fake")
    monkeypatch.setenv("RAGKB_STORE_PATH", str(tmp_path / "store.sqlite"))
    return TestClient(create_app())


def test_ingest_then_ask(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    content = "# GPIO\n\nGPIO pins are used for input and output.\n".encode("utf-8")

    response = client.post("/ingest", files={"file": ("guide.md", content, "text/markdown")})
    assert response.status_code == 200
    assert response.json()["chunks"] > 0

    response = client.post("/ask", json={"question": "GPIO pins"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "This is a fake answer."
    assert body["citations"]
    assert "GPIO" in body["citations"][0]["snippet"]
