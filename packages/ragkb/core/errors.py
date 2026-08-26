"""Domain exceptions."""

from __future__ import annotations


class RagkbError(Exception):
    """Base class for ragkb errors."""


class ConfigurationError(RagkbError):
    """Raised when required configuration (e.g. API keys) is missing."""
