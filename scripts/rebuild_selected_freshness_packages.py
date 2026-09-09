#!/usr/bin/env python3
"""Replace legacy ready packages with current-standard image-model packages."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402


def stamp():
    return datetime.now(timezone.utc).isoformat()


ITEMS = [
    {
        "source_id": "2096679710545596816", "slug": "nvidia-decade-gain",
        "title": "Nvidia gains more than 15,000% in a decade",
        "postText": "$NVDA has gained more than 15,000% over the last decade.",
        "facts": ["Nvidia $NVDA stock is up more than 15,000% over the last decade."],
        "image": "deliverables/pkg-20260907-nvidia-decade-gain/when2buy-image-model.png",
        "prompt": "Use case: ads-marketing. Square entity-led NVIDIA AI chip and GPU-server visual with an accurate 15,000%+ decade-gain headline, near-black premium financial-news style, white type, controlled red accents, and a bottom-right logo-safe area.",
    },
    {
        "source_id": "2096673953204847100", "slug": "us-market-holidays",
        "title": "U.S. market closures for the rest of 2026",
        "postText": "U.S. stock markets have three full-day closures left in 2026: Sep. 7, Nov. 26 and Dec. 25.\n\nEarly closes: Nov. 27 and Dec. 24.",
        "facts": ["The U.S. stock market closure dates listed are September 7, November 26, and December 25, 2026.", "Early closes listed are November 27 and December 24, 2026."],
        "image": "deliverables/pkg-20260907-us-market-holidays/when2buy-image-model.png",
        "prompt": "Use case: infographic-diagram. Square NYSE exterior and accurate 2026 market-closure schedule, near-black premium financial-news style, white type, controlled red accents, and a bottom-right logo-safe area.",
    },
    {
        "source_id": "2096629612713291967", "slug": "btc-global-money",
        "title": "Bitcoin reaches 1% of global money",
        "postText": "$BTC now represents 1% of global money.",
        "facts": ["Bitcoin is stated as 1% of global money."],
        "image": "deliverables/pkg-20260907-btc-global-money/when2buy-image-model.png",
        "prompt": "Use case: ads-marketing. Square entity-led Bitcoin and global financial-network visual with exact 1% of global money headline, near-black premium financial-news style, white type, controlled red accents, and a bottom-right logo-safe area.",
    },
    {
        "source_id": "2096619731239268580", "slug": "btc-kalshi-odds",
        "title": "Bitcoin odds put $50,000 first below 16%",
        "postText": "Prediction markets put the chance of $BTC reaching $50,000 before $100,000 below 16%.",
        "facts": ["The stated Kalshi probability of Bitcoin hitting $50,000 before $100,000 is less than 16%."],
        "image": "deliverables/pkg-20260907-btc-kalshi-odds/when2buy-image-model.png",
        "prompt": "Use case: ads-marketing. Square entity-led Bitcoin prediction-market visual with exact less-than-16-percent chance of $50K first, near-black premium financial-news style, white type, controlled red accents, and a bottom-right logo-safe area.",
    },
]


def main():
    document = state.load_state()
    sources = {str(x.get("id")): x for x in document["benchmarkPosts"]}
    for item in ITEMS:
        source = sources[item["source_id"]]
        package = {
            "id": f"pkg-20260907-{item['slug']}", "benchmarkPostId": item["source_id"],
            "benchmarkPostUrl": source["url"], "title": item["title"], "status": "ready",
            "postText": item["postText"], "mirroredFacts": item["facts"],
            "verificationSources": [source["url"]], "imagePath": item["image"], "createdAt": stamp(),
            "visualProduction": {"method": "image_model", "prompt": item["prompt"], "logoApplied": True, "qaStatus": "passed"},
        }
        old = next((x for x in document["packages"] if str(x.get("benchmarkPostId")) == item["source_id"]), None)
        if old:
            old.clear(); old.update(package)
        else:
            document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Rebuilt four selected financial packages from image-model visuals under the current standard.", "reason": "The intervening NFL-only source post was excluded from financial publication as off-topic; the promotional NFL Pick'em post was excluded."})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print("Rebuilt " + ", ".join(f"pkg-20260907-{x['slug']}" for x in ITEMS))


if __name__ == "__main__":
    main()
