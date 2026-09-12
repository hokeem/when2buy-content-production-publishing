#!/usr/bin/env python3
"""Persist the newest fresh OpenAI humanoid-robot demo package."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098829700558631099"
PACKAGE_ID = "pkg-20260912-openai-humanoid-robot-demo"
IMAGE = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image.png"

def iso(value=None):
    return (value or datetime.now(timezone.utc)).replace(microsecond=0).isoformat().replace("+00:00", "Z")

doc = state.load_state()
source = next((item for item in doc["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID), None)
if not source:
    raise SystemExit("selected benchmark post is missing")
posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
now = datetime.now(timezone.utc)
if now - posted > timedelta(minutes=90):
    raise SystemExit("STALE_SOURCE: selected benchmark exceeded the 90-minute TTL")
if not IMAGE.is_file():
    raise SystemExit(f"missing prepared image: {IMAGE}")

package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": source["url"],
    "title": "OpenAI humanoid robot demo set for 2027",
    "status": "ready",
    "postText": "OpenAI will have an impressive humanoid-robot demo in 2027, Sam Altman says.",
    "mirroredFacts": ["Sam Altman said OpenAI will have an impressive demo of a humanoid robot in 2027."],
    "verificationSources": [source["url"], "https://blog.samaltman.com/the-gentle-singularity"],
    "imagePath": str(IMAGE.relative_to(ROOT)),
    "createdAt": iso(now),
    "sourceExpiresAt": iso(posted + timedelta(minutes=90)),
    "visualProduction": {
        "method": "image_model",
        "prompt": "Complete square 1:1 entity-led cinematic realistic humanoid robot prototype in a near-black AI robotics laboratory at night, beside AI compute racks and a glass research campus; robot dominant center-right, clean upper-left negative space, cool blue-white light and one restrained red accent; no readable text, logos, watermark, attribution, disclaimer, commentary, CTA, tagline, hashtags, pure-text card, or generic radar background; exact repository logo composited once afterward.",
        "logoApplied": True,
        "logoPath": "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png",
        "logoCount": 1,
        "canvas": "1254x1254",
        "qaStatus": "passed",
        "qa": {"inspectedAt": iso(now), "result": "passed", "checks": ["square 1:1 1254x1254 PNG", "complete humanoid-robot entity-led scene", "exact repository logo composited once", "headline and 2027 fact proofread", "no source, attribution, disclaimer, commentary, CTA, tagline, hashtags, or watermark", "not a pure-text card or generic-radar visual"]},
    },
}
doc["packages"] = [item for item in doc["packages"] if item.get("id") != PACKAGE_ID]
doc["packages"].append(package)
doc["runs"].append({"id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": iso(now), "completedAt": iso(), "summary": "Produced newest fresh benchmark item with original factual copy and exact-logo square entity visual.", "reason": "", "selectedPackageIds": [PACKAGE_ID]})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(PACKAGE_ID)
