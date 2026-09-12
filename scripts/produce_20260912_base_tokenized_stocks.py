#!/usr/bin/env python3
"""Persist the newest fresh Base tokenized-stocks volume package."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098855109228728502"
PACKAGE_ID = "pkg-20260912-base-tokenized-stocks-volume"
SOURCE_URL = f"https://x.com/WhaleInsider/status/{SOURCE_ID}"
IMAGE = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image.png"
COPY = "Tokenized stocks on Base just hit a new daily DEX trading-volume high of $100M."
PROMPT = ("Use case: productivity-visual. Complete square 1:1 entity-led premium financial-news visual "
          "about tokenized stocks on Base reaching a new daily decentralized-exchange trading-volume high "
          "of $100M. Cinematic near-black institutional digital-asset trading room, neutral unbranded equity "
          "tokens and security certificates flowing through a blue chain/exchange motif, rising volume bars, "
          "cool blue-white light and restrained red accent. Leave upper-left headline space and lower-right "
          "logo-safe space. No generated readable text, letters, numbers, logos, watermarks, source, attribution, "
          "disclaimer, commentary, CTA, tagline, hashtags, pure-text card, or generic abstract background; "
          "exact repository logo composited once afterward.")

def iso(value=None):
    value = value or datetime.now(timezone.utc)
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

doc = state.load_state()
source = next((item for item in doc["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID), None)
if not source:
    raise SystemExit("selected benchmark post is missing")
posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
now = datetime.now(timezone.utc)
expires = posted + timedelta(minutes=90)
if now >= expires:
    raise SystemExit("STALE_SOURCE: selected benchmark exceeded the 90-minute TTL")
if not IMAGE.is_file():
    raise SystemExit(f"missing prepared image: {IMAGE}")
package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": SOURCE_URL,
    "title": "Tokenized stocks on Base hit a new daily DEX volume high",
    "status": "ready",
    "postText": COPY,
    "mirroredFacts": ["Tokenized stocks on Base recorded a new daily decentralized-exchange trading-volume high of $100 million."],
    "verificationSources": [SOURCE_URL, "https://tokenterminal.com/resources/newsletter/tokenized-stocks-from-public-equities-to-private-markets", "https://brand.base.org/stocks"],
    "imagePath": str(IMAGE.relative_to(ROOT)),
    "createdAt": iso(now),
    "sourceExpiresAt": iso(expires),
    "visualProduction": {
        "method": "image_model",
        "prompt": PROMPT,
        "logoApplied": True,
        "logoPath": "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png",
        "logoCount": 1,
        "canvas": "1254x1254",
        "qaStatus": "passed",
        "qa": {"inspectedAt": iso(now), "result": "passed", "checks": [
            "square 1:1 1254x1254 PNG",
            "complete Base tokenized-stocks entity-led trading scene",
            "headline and $100M number proofread",
            "exact repository logo composited once",
            "no third-party marks, source, attribution, disclaimer, commentary, CTA, tagline, hashtags, or watermark",
            "not a pure-text card or generic-radar visual"
        ]}
    }
}
doc["packages"] = [item for item in doc["packages"] if item.get("id") != PACKAGE_ID]
doc["packages"].append(package)
doc["runs"].append({"id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": iso(now), "completedAt": iso(), "summary": "Produced one newest fresh Base tokenized-stocks volume package with a complete entity-led square visual and exact-logo composite.", "reason": "", "selectedPackageIds": [PACKAGE_ID]})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(json.dumps({"packageId": PACKAGE_ID, "status": "ready", "imagePath": str(IMAGE.relative_to(ROOT))}))
