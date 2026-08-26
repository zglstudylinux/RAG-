"""Base loader interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ragkb.core.models import Document


class Loader(ABC):
    """Extracts Documents from a single file."""

    @abstractmethod
    def load(self, path: Path) -> list[Document]:
        """Parse the file at ``path`` into one or more Documents."""
