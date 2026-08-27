"""One-time migration: derive the ``folder`` (top-level directory) for existing chunks.

Ingested 5766 sources live under ``D:\\Code\\AI\\RAG_Test\\5766\\<folder>\\...``.
Future ingests derive ``folder`` automatically in ``IngestionPipeline.ingest_path``;
this script only backfills chunks ingested before that change. Idempotent.
"""
from ragkb.indexing.sqlite_store import SQLiteVectorStore


def derive_folder(source: str) -> str:
    parts = source.replace("\\", "/").split("/")
    if "5766" in parts:
        idx = parts.index("5766")
        if idx + 1 < len(parts) - 1:
            return parts[idx + 1]
    return ""


def main() -> None:
    store = SQLiteVectorStore("data/ragkb.sqlite")
    rows = store._conn.execute("SELECT id, source FROM chunks").fetchall()
    print(f"total chunks: {len(rows)}")
    updates = [(derive_folder(source), chunk_id) for chunk_id, source in rows]
    store._conn.executemany("UPDATE chunks SET folder = ? WHERE id = ?", updates)
    store._conn.commit()
    for row in store._conn.execute(
        "SELECT folder, COUNT(*) FROM chunks GROUP BY folder ORDER BY folder"
    ):
        print(f"{row[1]:5d} chunks | {row[0]!r}")
    store.close()


if __name__ == "__main__":
    main()
