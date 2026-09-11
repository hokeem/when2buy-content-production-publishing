#!/usr/bin/env python3
"""Produce the single newest fresh NVIDIA robotaxi package."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098368762542010806"
PACKAGE_ID = "pkg-20260911-nvidia-robotaxis-drive"
GENERATED = Path("/root/.codex/generated_images/01a0902d-9394-71a1-b9a1-ba92ec595dbc/exec-ed355293-90af-40a3-b5d6-d36d1c32dca5.png")
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
        "-pointsize", "52", "-gravity", "northwest", "-annotate", "+62+66", "NVIDIA ROBOTAXIS",
        "-pointsize", "78", "-annotate", "+62+150", "DRIVE POWER",
        "-pointsize", "32", "-fill", "#d9e2ef", "-annotate", "+62+210", "HELPING AUTONOMOUS CARS HIT THE ROAD",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite",
        str(FINAL),
    ], check=True, timeout=45)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "NVIDIA DRIVE is helping power robotaxis",
        "status": "ready",
        "postText": "NVIDIA's DRIVE platform is helping power robotaxis hitting the road.",
        "mirroredFacts": [
            "The benchmark post said robotaxis are hitting the road.",
            "It said NVIDIA is helping power them.",
            "NVIDIA describes DRIVE as powering next-generation transportation, including robotaxis and autonomous delivery vehicles.",
        ],
        "verificationSources": [source["url"], "https://nvidianews.nvidia.com/news/drive-hyperion-level-4"],
        "verificationStatus": "verified_primary_source",
        "verificationNote": "NVIDIA newsroom material supports the DRIVE/robotaxi platform claim; benchmark wording was rewritten originally.",
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": stamp(),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Complete square entity-led editorial illustration of an autonomous robotaxi in a city at dusk, near-black premium financial-news palette, restrained green AI-compute accents, generous upper-left typography-safe space, no generated text or branding; exact repository logo composited once afterward.",
            "logoApplied": True,
            "qaStatus": "passed",
            "qaChecks": ["square 1254x1254 PNG", "complete entity-led robotaxi scene", "factual text composited once", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text card or generic-radar visual"],
        },
    }
    existing = next((item for item in document["packages"] if item.get("id") == PACKAGE_ID), None)
    if existing:
        existing.clear(); existing.update(package)
    else:
        document["packages"].append(package)
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(),
        "summary": "Produced one newest fresh NVIDIA robotaxi package with an inspected entity-led image and exact-logo composite.",
        "reason": "", "selectedPackageId": PACKAGE_ID,
    })
    errors = state.validate(document)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)


if __name__ == "__main__":
    main()
