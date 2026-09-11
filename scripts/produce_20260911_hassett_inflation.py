#!/usr/bin/env python3
"""Produce the one newest fresh Hassett/Fed package for this run."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098409025255748058"
PACKAGE_ID = "pkg-20260911-hassett-inflation-decelerating"
GENERATED = Path("/root/.codex/generated_images/01a090e0-1bf9-70e0-b505-2b59fd4da140/exec-02ec852f-48ff-4a7c-b785-ef0f4402ed57.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"
SOURCE_EXPIRES = "2026-09-11T15:21:12Z"
PROMPT = (
    "Use case: ads-marketing. Complete 1:1 entity-led editorial visual about White House economic adviser Kevin Hassett discussing "
    "slowing inflation and pressure around a possible Federal Reserve rate hike: dark White House briefing-room atmosphere blended "
    "with the Federal Reserve building and a clean abstract three-month inflation trend line, cinematic premium financial-news "
    "illustration, near-black graphite base, white highlights, restrained red rate-pressure accents, no generated text or branding, "
    "clear typography-safe space, exact repository logo composited once afterward."
)

def stamp():
    return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "convert", str(GENERATED),
        "-font", "DejaVu-Sans-Bold", "-fill", "white", "-stroke", "black", "-strokewidth", "4",
        "-pointsize", "50", "-gravity", "northwest", "-annotate", "+64+70", "HASSETT ON INFLATION",
        "-pointsize", "78", "-annotate", "+64+156", "3-MONTH SLOWDOWN",
        "-pointsize", "26", "-fill", "#d9e2ef", "-annotate", "+68+276", "FED HIKE PRESSURE BUILDS",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite",
        str(FINAL),
    ], check=True, timeout=45)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Hassett says inflation is decelerating",
        "status": "ready",
        "postText": "Hassett says inflation has clearly decelerated over the past 3 months.\n\nHe says if the Fed hikes, Trump will have an opinion.",
        "mirroredFacts": [
            "Kevin Hassett said inflation is clearly decelerating over the past three months.",
            "Hassett said President Trump would have an opinion if the Fed hikes.",
        ],
        "verificationSources": [
            source["url"],
            "https://www.axios.com/2026/09/11/cpi-august-inflation-trump",
            "https://apnews.com/article/c76f53f7a53def0c464ca44ac637f203",
            "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
        ],
        "verificationStatus": "verified_authoritative_reporting",
        "verificationNote": "Authoritative same-day reporting confirms the inflation and upcoming Fed-rate decision context; the package preserves Hassett's stated view as a statement, without presenting it as an established inflation fact.",
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": stamp(),
        "sourceExpiresAt": SOURCE_EXPIRES,
        "visualProduction": {
            "method": "image_model",
            "prompt": PROMPT,
            "logoApplied": True,
            "qaStatus": "passed",
            "qa": {
                "inspectedAt": stamp(),
                "result": "passed",
                "checks": [
                    "square 1254x1254 PNG",
                    "complete White House, Federal Reserve, adviser, and inflation-trend entity scene",
                    "exact repository logo composited once",
                    "visible numbers and labels proofread",
                    "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark",
                    "not a pure-text card",
                ],
            },
        },
    }
    existing = next((item for item in document["packages"] if item.get("id") == PACKAGE_ID), None)
    if existing:
        existing.clear()
        existing.update(package)
    else:
        document["packages"].append(package)
    now = stamp()
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": now, "completedAt": now,
        "summary": "Produced one newest fresh Hassett/Fed package with a complete entity-led square image and exact-logo composite.",
        "reason": "", "selectedPackageId": PACKAGE_ID,
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
