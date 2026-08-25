#!/usr/bin/env python3
"""Archive original benchmark images locally and retain a manifest in state."""
import json
from pathlib import Path
from urllib.request import Request, urlopen
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

OUT = ROOT / "output" / "benchmark-media"

def extension(content_type, url):
    if "png" in content_type or ".png" in url: return ".png"
    if "webp" in content_type or ".webp" in url: return ".webp"
    if "gif" in content_type or ".gif" in url: return ".gif"
    return ".jpg"

def main():
    current = state.load_state()
    saved = failed = 0
    OUT.mkdir(parents=True, exist_ok=True)
    for post in current.get("benchmarkPosts", []):
        urls = post.get("mediaUrls") or []
        archive = post.setdefault("mediaArchive", [])
        known = {item.get("sourceUrl") for item in archive if isinstance(item, dict)}
        for index, source_url in enumerate(urls, start=1):
            if source_url in known or not isinstance(source_url, str) or not source_url.startswith("https://"):
                continue
            try:
                request = Request(source_url, headers={"User-Agent": "when2buy-radar/1.0"})
                with urlopen(request, timeout=45) as response:
                    body = response.read(15 * 1024 * 1024 + 1)
                    if len(body) > 15 * 1024 * 1024:
                        raise RuntimeError("image exceeds 15 MiB archive limit")
                    suffix = extension(response.headers.get("Content-Type", ""), source_url)
                relative = Path("benchmark-media") / post["account"] / f"{post['id']}-{index}{suffix}"
                target = OUT.parent / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
                archive.append({"sourceUrl": source_url, "path": str(Path("output") / relative), "status": "archived"})
                saved += 1
            except Exception as exc:
                archive.append({"sourceUrl": source_url, "status": "failed", "reason": str(exc)[:180]})
                failed += 1
    state.atomic_write(current)
    print(f"Benchmark media archive: {saved} downloaded, {failed} failed.")

if __name__ == "__main__":
    main()
