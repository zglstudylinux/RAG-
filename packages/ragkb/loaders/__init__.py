"""Document loaders: PDF/Word/Markdown, source code, and schematic (VLM)."""

from ragkb.loaders.registry import CODE_SUFFIXES, is_supported, load_directory, load_document
from ragkb.loaders.schematic import SchematicLoader, is_schematic_pdf

__all__ = [
    "CODE_SUFFIXES",
    "SchematicLoader",
    "is_schematic_pdf",
    "is_supported",
    "load_directory",
    "load_document",
]
