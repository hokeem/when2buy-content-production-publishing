#!/usr/bin/env python3
"""Record the three freshly generated, timestamp-first replacement packages."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

BRAND = ""
ITEMS = [
    {
        "source": "2095912220077006996", "id": "pkg-20260907-micron-mu-1000-per-share",
        "title": "Micron $MU returns above $1,000 per share",
        "copy": "Micron $MU stock is back above $1,000 per share.\n\n" + BRAND,
        "facts": ["Micron $MU stock is back above $1,000 per share."],
        "image": "deliverables/pkg-20260907-micron-mu-1000-per-share/when2buy-image-model.png",
        "prompt": "Use case: ads-marketing. Square 1:1 entity-led Micron DRAM chip and wafer scene with a rising price chart, premium near-black financial-news style, exact white headline 'MICRON $MU' and '$1,000+ PER SHARE', controlled red accent and lower-right logo-safe area. No source references, disclaimers, CTA, watermark or generic typography card.",
    },
    {
        "source": "2095901350622040118", "id": "pkg-20260907-us-stock-market-closed-labor-day",
        "title": "U.S. stock market closed Monday",
        "copy": "The U.S. stock market is closed Monday for Labor Day.\n\n" + BRAND,
        "facts": ["The U.S. stock market is closed Monday for Labor Day."],
        "image": "deliverables/pkg-20260907-us-stock-market-closed-monday/when2buy-image-model-v2.png",
        "prompt": "Use case: ads-marketing. Square 1:1 entity-led New York Stock Exchange exterior with a Monday calendar, premium near-black financial-news style, exact white headline 'U.S. MARKETS' and 'CLOSED MONDAY', controlled red accent and lower-right logo-safe area. No source references, disclaimers, CTA, watermark or generic typography card.",
    },
    {
        "source": "2095896468615790905", "id": "pkg-20260907-lululemon-short-talk",
        "title": "Lululemon $LULU short-selling talk",
        "copy": "Lululemon $LULU is drawing short-selling talk in a jab aimed at Michael Burry.\n\n" + BRAND,
        "facts": ["The source post says it wants to short Lululemon stock to show Michael Burry how it feels."],
        "image": "deliverables/pkg-20260907-lululemon-short-talk/when2buy-image-model.png",
        "prompt": "Use case: ads-marketing. Square 1:1 entity-led Lululemon retail storefront and downward market chart, premium near-black financial-news style, exact white headline 'LULULEMON $LULU' and 'SHORT TALK', controlled red accent and lower-right logo-safe area. No source references, disclaimers, CTA, watermark, named-person likeness or generic typography card.",
    },
]

def stamp(): return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    sources = {str(item.get("id")): item for item in document["benchmarkPosts"]}
    for item in ITEMS:
        source = sources[item["source"]]
        package = {
            "id": item["id"], "benchmarkPostId": item["source"], "benchmarkPostUrl": source["url"],
            "title": item["title"], "status": "ready", "postText": item["copy"],
            "mirroredFacts": item["facts"], "verificationSources": [source["url"]],
            "imagePath": item["image"], "createdAt": stamp(),
            "visualProduction": {"method": "image_model", "prompt": item["prompt"], "logoApplied": True, "qaStatus": "passed"},
        }
        old = next((x for x in document["packages"] if str(x.get("benchmarkPostId")) == item["source"]), None)
        if old: old.clear(); old.update(package)
        else: document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Remade three eligible timestamp-first packages with image-model visuals, exact-logo compositing, and visual QA.", "reason": ""})
    errors = state.validate(document)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print("Prepared " + ", ".join(item["id"] for item in ITEMS))

if __name__ == "__main__": main()
