"""Tests for the store backup helper."""

from __future__ import annotations

from pathlib import Path

from ragkb.core.backup import backup_store


def test_backup_store_to_file(tmp_path) -> None:
    source = tmp_path / "store.sqlite"
    source.write_bytes(b"data")
    dest = tmp_path / "backup.sqlite"
    target = backup_store(str(source), str(dest))
    assert target == str(dest)
    assert dest.read_bytes() == b"data"


def test_backup_store_to_directory(tmp_path) -> None:
    source = tmp_path / "store.sqlite"
    source.write_bytes(b"data")
    dest_dir = tmp_path / "backups"
    dest_dir.mkdir()
    target = backup_store(str(source), str(dest_dir))
    assert Path(target).name == "store.sqlite.backup"
    assert Path(target).read_bytes() == b"data"
