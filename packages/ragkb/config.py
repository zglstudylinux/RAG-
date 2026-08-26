"""Application configuration via environment variables / .env file."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Values come from env vars prefixed with RAGKB_ or a .env file."""

    model_config = SettingsConfigDict(env_prefix="RAGKB_", env_file=".env", extra="ignore")

    env: str = "dev"
    log_level: str = "INFO"

    # LLM
    llm_provider: str = "openai-compatible"
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"
    llm_temperature: float = 0.2

    # Embedding
    embedding_provider: str = "openai-compatible"  # "openai-compatible" | "local" | "fake"
    embedding_base_url: str = "https://api.siliconflow.cn/v1"
    embedding_api_key: str = ""
    embedding_model: str = "BAAI/bge-m3"

    # Vision-language model (for schematic / image-heavy PDFs)
    vlm_provider: str = "none"
    vlm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    vlm_api_key: str = ""
    vlm_model: str = "qwen-vl-max"
    schematic_min_chars_per_page: int = 80

    # Storage & chunking
    store_path: str = "data/ragkb.sqlite"
    chunk_size: int = 800
    chunk_overlap: int = 100
    retrieval_top_k: int = 4

    # Retrieval strategy
    retrieval_mode: str = "hybrid"  # "hybrid" | "vector"
    hybrid_candidate_k: int = 10
    hybrid_rrf_k: int = 60
    rerank_provider: str = "none"  # reserved for API rerankers (e.g. bge-reranker)

    # Auth
    jwt_secret: str = "change-me-in-production-use-a-long-random-secret"
    jwt_expires_minutes: int = 720
    default_admin_username: str = "admin"
    default_admin_password: str = "admin123"

    @property
    def public_summary(self) -> dict[str, object]:
        """Sanitized view of the config (no secrets) for health endpoints."""
        return {
            "env": self.env,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_base_url": self.llm_base_url,
            "llm_configured": bool(self.llm_api_key),
            "embedding_provider": self.embedding_provider,
            "embedding_model": self.embedding_model,
            "embedding_base_url": self.embedding_base_url,
            "embedding_configured": bool(self.embedding_api_key),
            "vlm_provider": self.vlm_provider,
            "vlm_configured": bool(self.vlm_api_key),
            "store_path": self.store_path,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "retrieval_top_k": self.retrieval_top_k,
            "retrieval_mode": self.retrieval_mode,
        }


@lru_cache
def get_settings() -> Settings:
    """Return the cached process-wide settings instance."""
    return Settings()
