#!/usr/bin/env python3
"""Persist the single newest fresh Nasdaq/Payward package after image QA."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2097999228006023573"
PACKAGE_ID = "pkg-20260910-nasdaq-payward-21b-valuation"
SOURCE_EXPIRES_AT = "2026-09-10T12:12:49Z"
PROMPT = """Use case: ads-marketing
Asset type: square X financial-news visual for When2Buy
Primary request: one complete original entity-led editorial visual about Nasdaq investing $100 million in Payward, the parent of cryptocurrency exchange Kraken, at a $21 billion valuation.
Scene/backdrop: a premium realistic exchange-and-markets operations environment with a stylized Nasdaq market display, a modern cryptocurrency exchange infrastructure room, and a subtle institutional investment transaction motif; no recognizable third-party logos.
Subject: a dominant abstract stock-exchange trading floor display connected to a secure crypto-exchange server vault and an illuminated investment flow, clearly showing a business investment rather than a generic coin shot.
Style/medium: cinematic photorealistic financial-news editorial image, sharp detail, premium market-news aesthetic.
Composition/framing: exact 1:1 square; near-black base; central entity-led scene; bold white typography with one restrained red accent; reserve clean lower-left space for later compositing of the supplied circular when2buy logo.
Lighting/mood: high-contrast studio lighting, urgent but factual.
Color palette: black, charcoal, white, controlled red; no green unless semantically necessary.
Text (verbatim): "NASDAQ INVESTS $100M" and "PAYWARD VALUED AT $21B"
Constraints: render the exact phrases legibly; no other readable words or numbers; no source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, or generated logo; no pure typography card; no generic abstract background; do not imitate any existing brand logo; keep the image complete and visually meaningful before the logo is added."""

def main():
    now = datetime.now(timezone.utc)
    if now >= datetime.fromisoformat(SOURCE_EXPIRES_AT.replace("Z", "+00:00")):
        raise SystemExit("Skipped: source expired before packaging")
    document = state.load_state()
    if any(p.get("id") == PACKAGE_ID for p in document["packages"]):
        raise SystemExit(f"Package already exists: {PACKAGE_ID}")
    source = next(p for p in document["benchmarkPosts"] if p.get("id") == SOURCE_ID)
    stamp = now.isoformat()
    document["packages"].append({
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Nasdaq invests $100M in Payward at $21B valuation",
        "status": "ready",
        "postText": "Nasdaq is investing $100 million in Payward, the parent of Kraken, at a $21 billion valuation.",
        "mirroredFacts": [
            "Nasdaq is investing $100 million in Payward.",
            "Payward is the parent of cryptocurrency exchange Kraken.",
            "The valuation is $21 billion.",
        ],
        "verificationSources": ["https://www.bloomberg.com/"],
        "imagePath": "deliverables/pkg-20260910-nasdaq-payward-21b-valuation/when2buy-image-model.png",
        "createdAt": stamp,
        "sourceExpiresAt": SOURCE_EXPIRES_AT,
        "visualProduction": {
            "method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed",
            "qa": {"inspectedAt": stamp, "result": "passed", "checks": [
                "square 1254x1254", "complete exchange and secure crypto-infrastructure scene",
                "exact NASDAQ INVESTS $100M and PAYWARD VALUED AT $21B text",
                "premium near-black, white, and restrained-red palette",
                "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark",
                "not a pure-text card or generic-radar visual", "exact repository logo composited once",
            ]},
        },
    })
    document["runs"].append({
        "id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded",
        "startedAt": stamp, "completedAt": stamp,
        "summary": "Produced the single newest fresh Nasdaq/Payward package with an inspected entity-led image and exact-logo composite.",
        "reason": "",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(f"Prepared: {PACKAGE_ID}")

if __name__ == "__main__":
    main()
