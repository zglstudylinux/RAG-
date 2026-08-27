"""Pytest configuration: isolate cached settings and ambient env between tests."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

from ragkb.config import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _isolate_ragkb_env(monkeypatch) -> Iterator[None]:
    """Drop any ambient RAGKB_* env vars so tests don't depend on the shell config.

    A developer may have run ``$env:RAGKB_LLM_PROVIDER="fake"`` (as our offline
    testing docs suggest); without this, ``test_settings_defaults`` would read that
    value and fail. ``monkeypatch.delenv`` restores each original value afterwards.
    """
    for key in list(os.environ):
        if key.startswith("RAGKB_"):
            monkeypatch.delenv(key, raising=False)
    yield
