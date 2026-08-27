"""One-time migration: strip stale ``[n]`` citation markers from existing FAQ answers.

FAQ answers promoted before the strip fix contained ``[n]`` markers from their original
generation, which corrupted citations when the FAQ was later re-served. Idempotent.
"""
from ragkb.core.rag import strip_citation_markers
from ragkb.indexing.faq_store import FaqStore


def main() -> None:
    store = FaqStore("data/ragkb.sqlite")
    rows = store._conn.execute("SELECT id, answer FROM faqs").fetchall()
    updated = 0
    for faq_id, answer in rows:
        cleaned = strip_citation_markers(answer)
        if cleaned != answer:
            store._conn.execute("UPDATE faqs SET answer = ? WHERE id = ?", (cleaned, faq_id))
            updated += 1
    store._conn.commit()
    print(f"cleaned {updated} of {len(rows)} FAQ answers")
    store.close()


if __name__ == "__main__":
    main()
