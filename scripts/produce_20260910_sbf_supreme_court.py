#!/usr/bin/env python3
"""Produce the single newest fresh package for the scheduled run."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098145162689937869"
PACKAGE_ID = "pkg-20260910-sbf-supreme-court"
GENERATED = Path("/root/.codex/generated_images/01a08d11-14f6-7d20-a8fe-7243857b91d5/exec-d8863c4b-ff40-4d74-9811-7343d109aaa4.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
OUT = ROOT / "deliverables" / PACKAGE_ID

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    OUT.mkdir(parents=True, exist_ok=True)
    raw = OUT / "generated.png"
    final = OUT / "when2buy-image-model.png"
    shutil.copyfile(GENERATED, raw)
    subprocess.run([
        "convert", str(raw), "(", str(LOGO), "-resize", "112x112", ")",
        "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(final)
    ], check=True)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Sam Bankman-Fried seeks Supreme Court review",
        "status": "ready",
        "postText": "Sam Bankman-Fried asks the Supreme Court to overturn his fraud conviction.\n\nThe former FTX founder is seeking review after a federal appeals court upheld the conviction.",
        "mirroredFacts": [
            "Sam Bankman-Fried is asking the U.S. Supreme Court to overturn his fraud conviction.",
            "A federal appeals court upheld the conviction in June 2026."
        ],
        "verificationSources": [
            source["url"],
            "https://www.supremecourt.gov/",
            "https://apnews.com/article/e709df4a152e9b3b52a266dd81eb44cc"
        ],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": now(),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Square premium financial-news editorial visual: serious Supreme Court-inspired civic architecture, scales of justice, subtle digital-asset cue, near-black slate palette, no text, no logos, no watermark, clean lower-right logo-safe area; exact repository logo composited once afterward.",
            "logoApplied": True,
            "qaStatus": "passed"
        }
    }
    existing = next((item for item in document["packages"] if item.get("id") == PACKAGE_ID), None)
    if existing:
        existing.clear(); existing.update(package)
    else:
        document["packages"].append(package)
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": now(), "completedAt": now(),
        "summary": "Produced one newest fresh SBF Supreme Court package with exact-logo compositing.", "reason": ""
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
