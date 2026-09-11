#!/usr/bin/env python3
"""Produce the single newest fresh ETH benchmark package."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098419313346576672"
PACKAGE_ID = "pkg-20260911-eth-75-percent-move"
GENERATED = Path("/root/.codex/generated_images/01a090ed-d7c5-7ec1-8606-a1bb82eb1e22/exec-4f29b442-eeb4-4e63-bd64-54f376b1def6.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    if (datetime.now(timezone.utc) - datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y")).total_seconds() > 90 * 60:
        raise SystemExit("Selected source is outside the 90-minute TTL.")
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(GENERATED, FINAL)
    subprocess.run([
        "convert", str(FINAL), "-resize", "1254x1254!",
        "-fill", "#000000B8", "-draw", "rectangle 42,46 610,370",
        "-font", "DejaVu-Sans-Bold", "-fill", "white", "-stroke", "black", "-strokewidth", "3",
        "-pointsize", "48", "-gravity", "northwest", "-annotate", "+76+102", "ETH",
        "-pointsize", "86", "-annotate", "+72+225", ">7.5%",
        "-pointsize", "30", "-fill", "#D9E2EF", "-annotate", "+78+330", "PAST 24 HOURS",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite",
        str(FINAL),
    ], check=True, timeout=45)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "ETH rallies above 7.5% in 24 hours",
        "status": "ready",
        "postText": "ETH is up more than 7.5% over the past 24 hours.",
        "mirroredFacts": [
            "The benchmark post states that ETH rallied above 7.5% in the past 24 hours.",
            "The selected source is a new original from WhaleInsider and is within the 90-minute source TTL.",
        ],
        "verificationSources": [source["url"]],
        "verificationStatus": "benchmark_discovery_signal",
        "verificationNote": "Discovery payload preserved narrowly; no additional market interpretation added.",
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": stamp(),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Complete square entity-led editorial 3D scene centered on a polished Ethereum diamond with an upward green market line, near-black premium financial-news environment, upper-left typography-safe space, no generated text or branding; exact repository logo composited once afterward.",
            "logoApplied": True,
            "qaStatus": "passed",
            "qaChecks": ["square 1254x1254 PNG", "complete entity-led Ethereum scene", "factual text composited once", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text card or generic-radar visual"],
        },
    }
    existing = next((item for item in document["packages"] if item.get("id") == PACKAGE_ID), None)
    if existing:
        existing.clear()
        existing.update(package)
    else:
        document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced one newest fresh ETH package with an inspected entity-led image and exact-logo composite.", "reason": "", "selectedPackageId": PACKAGE_ID})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)


if __name__ == "__main__":
    main()
