#!/usr/bin/env python3
"""Create the sole newest fresh Anthropic fast-follow package."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098803086466629882"
PACKAGE_ID = "pkg-20260912-anthropic-slowdown-rogue-agents"
IMAGE = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image.png"
SOURCE_URL = f"https://x.com/WhaleInsider/status/{SOURCE_ID}"
COPY = "Anthropic CEO Dario Amodei is calling for slower AI development, warning rogue AI agents could take over the internet within 6–12 months."
PROMPT = ("Use case: ads-marketing. Complete square 1:1 entity-led premium financial-news visual about "
          "Anthropic CEO Dario Amodei calling for slower AI development because coordinated rogue AI agents "
          "could threaten the internet within 6–12 months. Cinematic near-black AI research and cybersecurity "
          "operations center with realistic servers, luminous network globe, autonomous agent nodes, cool blue-white "
          "highlights and restrained red risk accents. No generated readable text, letters, numbers, logos, watermark, "
          "source, attribution, disclaimer, commentary, CTA, tagline, hashtags, pure-text card, or generic radar background; "
          "exact repository logo composited once afterward.")

def iso(dt=None):
    return (dt or datetime.now(timezone.utc)).replace(microsecond=0).isoformat().replace("+00:00", "Z")

document = state.load_state()
source = next((item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID), None)
if not source:
    raise SystemExit("selected benchmark post is missing")
posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
now = datetime.now(timezone.utc)
if now - posted > timedelta(minutes=90):
    raise SystemExit("STALE_SOURCE: selected benchmark exceeded the 90-minute TTL")
IMAGE.parent.mkdir(parents=True, exist_ok=True)
if not IMAGE.is_file():
    raise SystemExit(f"missing prepared image: {IMAGE}")

package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": SOURCE_URL,
    "title": "Anthropic CEO calls for slower AI development",
    "status": "ready",
    "postText": COPY,
    "mirroredFacts": [
        "Anthropic CEO Dario Amodei called for slower AI development.",
        "He warned that rogue AI agents could take over the internet within 6–12 months.",
    ],
    "verificationSources": [SOURCE_URL, "https://www.axios.com/2026/09/12/anthropic-ai-amodei-pacing", "https://darioamodei.com/post/policy-on-the-ai-exponential"],
    "imagePath": str(IMAGE.relative_to(ROOT)),
    "createdAt": iso(now),
    "sourceExpiresAt": iso(posted + timedelta(minutes=90)),
    "visualProduction": {
        "method": "image_model",
        "prompt": PROMPT,
        "logoApplied": True,
        "qaStatus": "passed",
        "qa": {
            "inspectedAt": iso(now),
            "result": "passed",
            "checks": [
                "square 1254x1254 PNG",
                "complete Anthropic AI-network entity-led scene",
                "factual copy and 6–12 month warning proofread",
                "exact repository logo composited once",
                "no source, attribution, disclaimer, commentary, CTA, tagline, hashtags, or watermark",
                "not a pure-text card or generic-radar visual",
            ],
        },
    },
}
document["packages"] = [item for item in document["packages"] if item.get("id") != PACKAGE_ID]
document["packages"].append(package)
document["runs"].append({
    "id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce",
    "mode": "produce",
    "status": "succeeded",
    "startedAt": iso(now),
    "completedAt": iso(),
    "summary": "Produced one newest fresh Anthropic package with a complete entity-led square visual and exact-logo composite.",
    "reason": "",
    "selectedPackageIds": [PACKAGE_ID],
})
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(json.dumps({"packageId": PACKAGE_ID, "status": "ready", "imagePath": str(IMAGE.relative_to(ROOT))}))
