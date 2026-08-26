"""Tests for the VLM provider factory."""

from __future__ import annotations

import pytest

from ragkb.config import Settings
from ragkb.core.errors import ConfigurationError
from ragkb.providers.registry import build_vlm


def test_build_vlm_none_when_disabled() -> None:
    assert build_vlm(Settings(vlm_provider="none")) is None


def test_build_vlm_fake() -> None:
    assert build_vlm(Settings(vlm_provider="fake")) is not None


def test_build_vlm_missing_key_raises() -> None:
    with pytest.raises(ConfigurationError):
        build_vlm(Settings(vlm_provider="openai-compatible", vlm_api_key=""))
