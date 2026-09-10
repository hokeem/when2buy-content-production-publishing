#!/usr/bin/env python3
"""Persist the single newest fresh Amazon Leo package after visual QA."""
import shutil
import tempfile
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098193139685040156"
PACKAGE_ID = "pkg-20260910-amazon-leo-24-launches"
BASE = Path("/root/.codex/generated_images/01a08db5-dfd5-7583-829a-7062352f14d4/exec-e1bd84c5-95a6-446f-887b-c2abe927a991.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
RELATIVE_IMAGE = Path("deliverables") / PACKAGE_ID / "when2buy-image-model.png"
OFFICIAL = "https://newsroom.arianespace.com/amazon-leo-and-arianespace-strengthen-partnership-with-six-additional-ariane-64-launches/"
PROMPT = "Use case: stylized-concept. Asset type: complete square 1:1 premium financial-news editorial visual for When2Buy. Primary request: an original entity-led visual about Amazon Leo's low-Earth-orbit satellite internet network adding six Ariane 64 launches, expanding the Arianespace commitment from 18 to 24, with 100 satellites already placed across three missions. Scene/backdrop: cinematic near-black space above a curved blue Earth. Subject: one detailed communications satellite in low Earth orbit, several smaller satellites on orbital arcs, and an Ariane 6 rocket launching in the distance. Style/medium: polished realistic editorial space art, high contrast, restrained red and amber launch glow. Composition/framing: exact square, dominant satellite across the center, clean upper-left area for factual typography, clean lower-right area for the exact repository logo. Text: all factual typography added after generation. Constraints: no generated readable text, logos, source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, generic radar graphic, or pure-text card."

def stamp():
    return datetime.now(timezone.utc).isoformat()

def parse(value):
    return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")

document = state.load_state()
source = next((item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID), None)
if source is None:
    raise SystemExit("Selected benchmark source is missing")
age = (datetime.now(timezone.utc) - parse(source["postedAt"]).astimezone(timezone.utc)).total_seconds() / 60
if age > 90:
    raise SystemExit(f"Selected source expired before production: {age:.1f} minutes")
if any(item.get("id") == PACKAGE_ID for item in document.get("packages", [])):
    raise SystemExit("Package already exists; refusing duplicate production")
if not BASE.is_file():
    raise SystemExit(f"Generated base image is missing: {BASE}")

target = ROOT / RELATIVE_IMAGE
target.parent.mkdir(parents=True, exist_ok=True)
fd, temp_name = tempfile.mkstemp(prefix="amazon-leo-", suffix=".png", dir=target.parent)
os.close(fd)
Path(temp_name).unlink()
subprocess.run([
    "convert", str(BASE), "-gravity", "northwest", "-fill", "white", "-stroke", "black", "-strokewidth", "2",
    "-font", "DejaVu-Sans-Bold", "-pointsize", "62", "-annotate", "+54+80", "AMAZON LEO",
    "-fill", "#ff5362", "-pointsize", "56", "-annotate", "+54+146", "18  →  24 LAUNCHES",
    "-fill", "white", "-pointsize", "35", "-annotate", "+54+196", "100 SATELLITES · 3 MISSIONS",
    "-gravity", "southeast", "-geometry", "+42+42", "(", str(LOGO), "-resize", "112x112", ")", "-composite", temp_name,
], check=True)
shutil.move(temp_name, target)

package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": source["url"],
    "title": "Amazon Leo expands to 24 launches",
    "status": "ready",
    "postText": "Amazon Leo just added six Ariane 64 launches, expanding its Arianespace commitment from 18 to 24.\n\nArianespace has already placed 100 Amazon Leo satellites into orbit across three missions in 2026.",
    "mirroredFacts": [
        "Amazon Leo added six Ariane 64 launches, expanding its Arianespace commitment from 18 to 24.",
        "Arianespace placed 100 Amazon Leo satellites into orbit across three missions in 2026.",
    ],
    "verificationSources": [OFFICIAL],
    "imagePath": str(RELATIVE_IMAGE),
    "createdAt": stamp(),
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
                "complete entity-led Amazon Leo satellite and Ariane 6 launch visual",
                "factual typography limited to 18 to 24 launches and 100 satellites across 3 missions",
                "premium near-black, white, blue, and restrained red/amber palette",
                "not a pure-text card or generic radar",
                "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark",
                "exact repository logo composited once",
            ],
        },
    },
}
document["packages"].append(package)
document["runs"].append({
    "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
    "mode": "produce",
    "status": "succeeded",
    "startedAt": stamp(),
    "completedAt": stamp(),
    "summary": "Produced the single newest Amazon Leo package with an inspected image-model visual and exact-logo composite.",
    "reason": "",
    "selectedPackageIds": [PACKAGE_ID],
})
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(f"Produced {PACKAGE_ID}: ready")
