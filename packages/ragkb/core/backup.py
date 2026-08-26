"""Store file backup helper."""

from __future__ import annotations

import shutil
from pathlib import Path


def backup_store(src: str, dest: str) -> str:
    """Copy the store file to a destination file or directory; return the target path."""
    source = Path(src)
    if not source.is_file():
        raise FileNotFoundError(f"Store file not found: {source}")
    target = Path(dest)
    if target.is_dir() or dest.endswith(("/", "\\")):
        target.mkdir(parents=True, exist_ok=True)
        target = target / (source.name + ".backup")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return str(target)
