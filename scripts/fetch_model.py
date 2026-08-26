"""Download a HuggingFace model into a local directory (hf-mirror.com friendly for CN).

Usage:
    python scripts/fetch_model.py [repo_id] [dest_dir]

Defaults to BAAI/bge-base-zh-v1.5 into data/models/bge-base-zh-v1.5. Downloads resume
after interrupted connections (HTTP Range) and retry with backoff, so they survive flaky
links.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import httpx

REPO = sys.argv[1] if len(sys.argv) > 1 else "BAAI/bge-base-zh-v1.5"
DEST = sys.argv[2] if len(sys.argv) > 2 else f"data/models/{REPO.split('/')[-1]}"
BASE = "https://hf-mirror.com"
MAX_ATTEMPTS = 10


def download(client: httpx.Client, url: str, dest: Path, size: int) -> None:
    attempts = 0
    while True:
        current = dest.stat().st_size if dest.exists() else 0
        if current >= size > 0:
            return
        headers = {"Range": f"bytes={current}-"} if current > 0 else {}
        try:
            with client.stream("GET", url, headers=headers) as response:
                if response.status_code not in (200, 206):
                    response.raise_for_status()
                mode = "ab" if (current > 0 and response.status_code == 206) else "wb"
                with dest.open(mode) as handle:
                    for chunk in response.iter_bytes(chunk_size=1 << 20):
                        handle.write(chunk)
            if dest.stat().st_size >= size:
                return
            attempts += 1
        except httpx.HTTPError as exc:
            attempts += 1
            print(f"  [retry {attempts}/{MAX_ATTEMPTS}] {dest.name}: {type(exc).__name__}",
                  flush=True)
        if attempts >= MAX_ATTEMPTS:
            raise RuntimeError(f"gave up on {dest.name} after {MAX_ATTEMPTS} attempts")
        time.sleep(min(2**attempts, 30))


def main() -> None:
    with httpx.Client(timeout=120, follow_redirects=True) as client:
        tree = client.get(f"{BASE}/api/models/{REPO}/tree/main?recursive=true").json()
        files = [f for f in tree if f.get("type") == "file"]
        expected = {f["path"]: (f.get("size") or 0) for f in files}
        print(f"{len(files)} files -> {DEST}", flush=True)

        for path, size in expected.items():
            dest = Path(DEST) / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and dest.stat().st_size == size and size > 0:
                print(f"  [skip] {path}", flush=True)
                continue
            download(client, f"{BASE}/{REPO}/resolve/main/{path}", dest, size)
            print(f"  [done] {path} ({dest.stat().st_size / 1e6:.1f} MB)", flush=True)

    print("done", flush=True)


if __name__ == "__main__":
    main()
