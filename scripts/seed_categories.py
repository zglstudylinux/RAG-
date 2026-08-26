"""Seed default categories and backfill existing 5766 chunks into AB5766C.

Idempotent: categories are only created when missing, and the backfill only touches
chunks that are still uncategorized (``category = ''``) whose source path contains
"5766". Re-running is safe.

Usage:
    .venv\\Scripts\\python scripts/seed_categories.py
"""

from __future__ import annotations

import sys

from ragkb.config import get_settings
from ragkb.indexing.category_store import CategoryStore

DOMAIN = "芯片SDK"
CHIPS = ["AB5766C", "AB573X", "BT897X", "BT895X"]


def main() -> int:
    settings = get_settings()
    categories = CategoryStore(settings.store_path)
    try:
        existing = {category["name"] for category in categories.list()}
        if DOMAIN not in existing:
            categories.create(DOMAIN, description="芯片 SDK 技术资料")
            print(f"created domain: {DOMAIN}")
        for chip in CHIPS:
            if chip not in existing:
                categories.create(chip, parent=DOMAIN)
                print(f"created category: {chip}")

        updated = categories.assign("5766", "AB5766C")
        print(f"backfilled {updated} chunks into AB5766C")
    finally:
        categories.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
