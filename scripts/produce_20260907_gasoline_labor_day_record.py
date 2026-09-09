#!/usr/bin/env python3
"""Assemble the newest Apify benchmark package after image-model QA."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2096991041987531044"
PACKAGE_ID = "pkg-20260907-us-gasoline-labor-day-record-415"
BASE = Path("/root/.codex/generated_images/01a07c9d-a69a-7021-a7f7-fc17e5641916/exec-7c45e17a-d534-486d-8231-5d7dd9609502.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
RELATIVE_IMAGE = Path("deliverables") / PACKAGE_ID / "when2buy-image-model.png"
PROMPT = "Use case: photorealistic-natural. Asset type: square 1:1 premium X financial-news visual for When2Buy. Primary request: original entity-led editorial image about a record U.S. Labor Day gasoline price. Scene/backdrop: sophisticated near-black premium night-time American gas station forecourt, subtle out-of-focus fuel canopy and unlabeled pump architecture with no trademarks. Subject: a single modern black regular gasoline nozzle in the foreground, entirely plain black metal and blank surfaces with absolutely no display, screen, gauge, symbols, letters, numbers, or labels. A restrained red upward price trajectory light behind it. Style: cinematic financial-news photography, realistic polished metal, premium and urgent. Composition: exact 1:1 square, nozzle dominant center-left, clean near-black lower-right 20 percent with no visual detail reserved for later circular logo placement. Lighting: white rim light and restrained deep-red accent. Text: none. Constraints: no readable or unreadable text anywhere, no numbers, no ticker, no logos, no brand marks, no watermark, no source handle, no URL, no disclaimer, no CTA, no generic radar graphics, no pure typography card, no damaged nozzle, no malformed objects."


def stamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main():
    if not BASE.is_file():
        raise SystemExit("Selected image-model render is unavailable.")
    target = ROOT / RELATIVE_IMAGE
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "convert", str(BASE), "(", str(LOGO), "-resize", "112x112", ")",
        "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(target),
    ], check=True)
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item["id"]) == SOURCE_ID)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "U.S. gasoline sets a $4.15 Labor Day record",
        "status": "ready",
        "postText": "U.S. regular gasoline averaged $4.15 a gallon on Labor Day, a holiday record.\n\nThe prior Labor Day high had never reached $4 a gallon.",
        "mirroredFacts": [
            "The national average price for regular unleaded gasoline was $4.15 a gallon on Labor Day.",
            "The $4.15 average was described as a record high for the holiday.",
            "Regular unleaded gasoline had not previously exceeded $4 a gallon on Labor Day.",
        ],
        "verificationSources": [source["url"]],
        "imagePath": str(RELATIVE_IMAGE),
        "createdAt": stamp(),
        "visualProduction": {
            "method": "image_model",
            "prompt": PROMPT,
            "logoApplied": True,
            "qaStatus": "passed",
            "qa": {
                "inspectedAt": stamp(),
                "checks": [
                    "first generated render rejected for display-like glyph",
                    "square 1254x1254",
                    "entity-led gasoline-nozzle scene",
                    "near-black premium palette with white and restrained-red accents",
                    "no readable generated text, source attribution, or branding",
                    "no generic radar imagery or pure typography",
                    "exact repository logo composited once in clear space",
                    "no visible damage or malformed subject",
                ],
            },
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
        "summary": "Produced the newest eligible U.S. gasoline Labor Day-record package with a regenerated image-model visual and exact-logo compositing.",
        "reason": "",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)


if __name__ == "__main__":
    main()
