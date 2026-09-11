#!/usr/bin/env python3
"""Produce the newest fresh Moonshot AI package and fail closed on verification."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098356117793354214"
PACKAGE_ID = "pkg-20260911-moonshot-ai-2b-sales-target"
GENERATED = Path("/root/.codex/generated_images/01a09004-6239-7e20-ad54-bb8a3bfb158b/exec-a87c053e-4724-48a7-b891-6a688ab3a002.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "convert", str(GENERATED),
        "-font", "DejaVu-Sans-Bold", "-fill", "white", "-stroke", "black", "-strokewidth", "4",
        "-pointsize", "54", "-gravity", "northwest", "-annotate", "+62+66", "MOONSHOT AI",
        "-pointsize", "88", "-annotate", "+62+158", "$2B SALES TARGET",
        "-pointsize", "34", "-fill", "#d9e2ef", "-annotate", "+62+216", "ANNUAL SALES BY END-2026",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite",
        str(FINAL),
    ], check=True, timeout=45)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Moonshot AI targets $2B in annual sales by end of 2026",
        "status": "blocked",
        "postText": "Moonshot AI is targeting $2B in annual sales by the end of 2026.",
        "mirroredFacts": ["Moonshot AI aims for $2 billion in annual sales by the end of 2026."],
        "verificationSources": [
            source["url"],
            "https://www.bloomberg.com/news/articles/2026-05-07/kimi-chatbot-maker-moonshot-ai-valued-at-20-billion-in-meituan-led-round?srnd=phx-ai",
        ],
        "verificationStatus": "blocked_unverified_forecast",
        "verificationNote": "Authoritative reporting located in this run supports Moonshot's funding and ARR figures, but not the benchmark's $2B year-end sales target.",
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": stamp(),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Square 1:1 cinematic editorial financial illustration of a Moonshot AI-inspired lunar crescent integrated with glowing data-center servers and an upward revenue trajectory, near-black base, white/cool-blue light, restrained red accents, no generated text or branding, clear typography-safe space, exact repository logo composited once after generation.",
            "logoApplied": True,
            "qaStatus": "passed",
        },
    }
    existing = next((item for item in document["packages"] if item.get("id") == PACKAGE_ID), None)
    if existing:
        existing.clear()
        existing.update(package)
    else:
        document["packages"].append(package)
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "partial", "startedAt": stamp(), "completedAt": stamp(),
        "summary": "Produced one newest fresh Moonshot AI package; publication blocked pending authoritative verification of the sales forecast.",
        "reason": "blocked_unverified_forecast",
        "selectedPackageId": PACKAGE_ID,
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)


if __name__ == "__main__":
    main()
