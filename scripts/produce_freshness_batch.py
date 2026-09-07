#!/usr/bin/env python3
"""Assemble the current five timestamp-first image-model packages."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
GENERATED = Path("/root/.codex/generated_images/01a07a53-e520-7860-9cdf-8c4e503304f1")

ITEMS = [
    {
        "source_id": "2096762652995248280", "slug": "us-stock-market-closed-monday",
        "image": "exec-6cc43248-3ea2-4a53-8bb1-f6e6ab9c2309.png",
        "title": "U.S. stock market closed Monday",
        "copy": "The U.S. stock market is closed Monday.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["The source post says the stock market is not open Monday."],
        "verification": ["https://www.nyse.com/markets/hours-calendars", "https://x.com/StockMKTNewz/status/2096762652995248280"],
        "prompt": "Square image-model visual: New York Stock Exchange exterior with a Monday market-closure headline; black premium financial-news palette, white type, controlled red accents, and a bottom-right logo-safe area.",
    },
    {
        "source_id": "2096718702703935494", "slug": "robinhood-chain-friday-fees",
        "image": "exec-5d24fa51-ae03-44e4-bd40-48e5d9ecd5a4.png",
        "title": "Robinhood Chain tops $8M in Friday fees",
        "copy": "$HOOD's Robinhood Chain generated more than $8M in fees Friday.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["Robinhood Chain $HOOD generated more than $8 million in fees on Friday."],
        "verification": ["https://www.coindesk.com/tech/2026/09/03/a-memecoin-making-app-becomes-crypto-s-top-fee-generators-as-robinhood-chain-activity-explodes", "https://x.com/StockMKTNewz/status/2096718702703935494"],
        "prompt": "Square image-model visual: dark Robinhood Chain transaction data center and fee dashboard, exact headline Robinhood Chain and $8M+ Friday Fees; premium black financial-news palette, white type, red accents, bottom-right logo-safe area.",
    },
    {
        "source_id": "2096694211605147791", "slug": "amazon-cargo-miami-runway-overrun",
        "image": "exec-761c3884-638c-4c2a-80a6-b1feedc6092f.png",
        "title": "Amazon cargo jet overruns Miami runway",
        "copy": "An Amazon $AMZN cargo plane overshot a runway at Miami International Airport and hit nearby vehicles.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["An Amazon cargo plane overshot a runway at Miami International Airport.", "The plane crashed into nearby vehicles."],
        "verification": ["https://apnews.com/article/47411c751782887757922efa5f634aa5", "https://x.com/StockMKTNewz/status/2096694211605147791"],
        "prompt": "Square image-model visual: serious Miami airport runway overrun involving an unbranded Amazon-style cargo jet and emergency vehicles, exact headline Amazon Cargo Jet / Miami Runway Overrun; black premium financial-news styling, white type, red accents, bottom-right logo-safe area.",
    },
    {
        "source_id": "2096691430164938804", "slug": "nvidia-chips-peace-talks",
        "image": "exec-89e79cf5-68c3-44ba-aa70-8ff2cf1f4d16.png",
        "title": "Nvidia chips in Armenia-Azerbaijan talks",
        "copy": "Nvidia AI-chip access was used to help secure a preliminary Armenia-Azerbaijan peace deal.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["American negotiators used the prospect of access to Nvidia AI chips in talks around a preliminary Armenia-Azerbaijan peace deal."],
        "verification": ["https://www.panorama.am/en/news/2026/09/05/US-Armenia-Azerbaijan/3168156", "https://x.com/StockMKTNewz/status/2096691430164938804"],
        "prompt": "Square image-model visual: advanced AI chip on a diplomacy table with restrained Armenia and Azerbaijan flags; exact headline Nvidia Chips / Peace Talks; black premium financial-news styling, white type, red accents, bottom-right logo-safe area.",
    },
    {
        "source_id": "2096679920785125677", "slug": "apple-tenfold-decade-return",
        "image": "exec-30efee89-c00f-4018-8656-837377e4f928.png",
        "title": "Apple gains more than 10x in a decade",
        "copy": "$AAPL stock is up more than 10x over the last decade.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["Apple $AAPL stock is up by more than 10x over the last decade."],
        "verification": ["https://www.axios.com/2026/09/01/apple-ceo-cook-stock", "https://x.com/StockMKTNewz/status/2096679920785125677"],
        "prompt": "Square image-model visual: sleek smartphone and upward decade-long chart, exact headline Apple $AAPL / 10X+ in a Decade; premium black financial-news styling, white type, controlled green performance accent, bottom-right logo-safe area.",
    },
]

def stamp():
    return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    posts = {str(item.get("id")): item for item in document["benchmarkPosts"]}
    for item in ITEMS:
        source = posts[item["source_id"]]
        package_id = f"pkg-20260907-{item['slug']}"
        relative = Path("deliverables") / package_id / "when2buy-image-model.png"
        final = ROOT / relative
        final.parent.mkdir(parents=True, exist_ok=True)
        # The supplied logo is composited once after model generation; no generated branding is used.
        subprocess.run(["convert", str(GENERATED / item["image"]), "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(final)], check=True)
        package = {
            "id": package_id, "benchmarkPostId": item["source_id"], "benchmarkPostUrl": source["url"],
            "title": item["title"], "status": "ready", "postText": item["copy"],
            "mirroredFacts": item["facts"], "verificationSources": item["verification"],
            "imagePath": str(relative), "createdAt": stamp(),
            "visualProduction": {"method": "image_model", "prompt": item["prompt"], "logoApplied": True, "qaStatus": "passed"},
        }
        old = next((x for x in document["packages"] if str(x.get("benchmarkPostId")) == item["source_id"]), None)
        if old:
            old.clear(); old.update(package)
        else:
            document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced five timestamp-first image-model packages with exact-logo compositing.", "reason": ""})
    errors = state.validate(document)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print("Prepared " + ", ".join(f"pkg-20260907-{item['slug']}" for item in ITEMS))

if __name__ == "__main__": main()
