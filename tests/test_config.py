"""Tests for the configuration system."""

from __future__ import annotations

from ragkb.config import Settings


def test_settings_defaults() -> None:
    settings = Settings(_env_file=None)
    assert settings.llm_provider == "openai-compatible"
    assert settings.llm_model == "deepseek-chat"
    assert settings.embedding_model == "BAAI/bge-m3"


def test_settings_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("RAGKB_LLM_MODEL", "qwen-plus")
    monkeypatch.setenv("RAGKB_EMBEDDING_MODEL", "text-embedding-v3")
    settings = Settings(_env_file=None)
    assert settings.llm_model == "qwen-plus"
    assert settings.embedding_model == "text-embedding-v3"


def test_public_summary_hides_secrets() -> None:
    settings = Settings(
        _env_file=None,
        llm_api_key="secret-llm",
        embedding_api_key="secret-embedding",
    )
    summary = settings.public_summary
    assert "secret-llm" not in str(summary)
    assert "secret-embedding" not in str(summary)
    assert summary["llm_configured"] is True
    assert summary["embedding_configured"] is True
