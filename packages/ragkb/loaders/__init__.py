"""Document loaders (PDF/Word/Markdown; code & schematic loaders come later)."""

from ragkb.loaders.registry import load_directory, load_document

__all__ = ["load_directory", "load_document"]
