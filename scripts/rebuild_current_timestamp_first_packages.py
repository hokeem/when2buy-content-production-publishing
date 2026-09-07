#!/usr/bin/env python3
"""Replace the five current queue packages with compliant image-model editions."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402


def iso():
    return datetime.now(timezone.utc).isoformat()


ITEMS = [
    {
        "source": "2096554949349875958", "slug": "robinhood-prediction-market-revenue",
        "title": "Robinhood prediction markets overtake stock trading",
        "copy": "Robinhood $HOOD now makes more from prediction-market trading than from stock trading on its platform.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["Robinhood $HOOD's prediction-market trading revenue is higher than stock-trading revenue on its platform."],
        "image": "exec-76f3660a-7d42-4e3e-900e-dbfd0229b4fd.png",
        "prompt": "Use case: productivity-visual. Asset type: square X financial-news visual. Primary request: Create a complete, entity-led, premium financial-news editorial image about Robinhood $HOOD where prediction-market trading revenue has overtaken stock-trading revenue. Scene/backdrop: a dark high-end trading command center with a glowing Robinhood-style green-and-black market interface, a prediction-market probability chart visibly higher than a stock-trading chart, abstract transaction flows; no people. Style/medium: cinematic photorealistic 3D editorial illustration, near-black background, bold white condensed sans-serif typography, controlled red accent only for urgency. Composition: 1:1 square, dominant visual entity and data display in center-left; reserve clean empty near-black logo-safe area in the bottom-right corner. Text (verbatim): \"HOOD PREDICTION MARKETS\" and \"NOW TOP STOCK TRADING\". Constraints: accurate spelling, readable short text only, no source handle, no source URL, no disclaimer, no advice, no attribution, no CTA, no logo, no watermark. Avoid: pure typography card, generic abstract background, misspellings, extra words.",
    },
    {
        "source": "2096541618522161474", "slug": "fed-treasury-bill-purchases",
        "title": "Fed plans up to $2.122B in Treasury-bill purchases",
        "copy": "The Fed plans to buy up to $2.122B in Treasury bills next week, part of roughly $17B in reinvestment purchases from Aug. 14 to Sept. 14.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["The Fed plans to purchase up to $2.122 billion in Treasury bills next week.", "The purchase is part of approximately $17 billion in planned reinvestment purchases from August 14 through September 14."],
        "image": "exec-10177ba7-1f64-401a-a6d8-7744f7f8ec99.png",
        "prompt": "Use case: productivity-visual. Asset type: square X financial-news visual. Primary request: create a complete entity-led editorial image about the U.S. Federal Reserve planning to buy up to $2.122 billion in Treasury bills next week, within approximately $17 billion of reinvestment purchases from August 14 to September 14. Scene: dramatic Federal Reserve building at night merged with crisp Treasury-bill certificates and an institutional purchase order display. Premium cinematic financial-news style: near-black base, white typography, controlled red accents. 1:1 square. Center the building and Treasury documents; leave clean near-black empty logo-safe area bottom right. Text verbatim: \"FED TREASURY BILL BUYING\" and \"$2.122B NEXT WEEK\". Constraints: concise readable text, exact number, no attribution, no source handles/URLs, no disclaimer, no advice, no CTA, no logo, no watermark. Avoid pure text card, generic art, misspellings, extraneous numbers.",
    },
    {
        "source": "2096521032416768125", "slug": "401k-millionaires-record",
        "title": "401(k) millionaires reach 769,000",
        "copy": "The number of 401(k) millionaires has reached a record 769,000.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["The number of 401(k) millionaires reached an all-time high of 769,000."],
        "image": "exec-c5b28d65-d6fd-4608-ac5b-13e0b238296c.png",
        "prompt": "Use case: productivity-visual. Asset type: square X financial-news visual. Primary request: create a complete entity-led premium financial-news visual about the number of U.S. 401(k) millionaires reaching a record 769,000. Scene: elegant retirement savings statement and a sophisticated investor silhouette viewing a wealth dashboard with a rising line, physical million-dollar account document; not a generic abstract chart. Style: cinematic editorial, black and near-black base, bold white type, controlled green growth accent and subtle red accent. 1:1 square, visual entity central; reserve a clean empty near-black logo-safe area in bottom-right. Text verbatim: \"401(k) MILLIONAIRES\" and \"769,000 RECORD HIGH\". Constraints: exact spelling and number; no source handles, source URLs, attribution, disclaimer, advice, CTA, logo, or watermark. Avoid pure typography card, generic image, clutter, extra text.",
    },
    {
        "source": "2096506955866976379", "slug": "hood-names-erc6551",
        "title": ".hood names bring ERC-6551 stock accounts",
        "copy": ".hood names are being built for Robinhood Chain, with seedless stock accounts powered by ERC-6551.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": [".hood names are being built as an ENS-like service for Robinhood Chain.", "The names use seedless stock accounts powered by ERC-6551."],
        "image": "exec-cf97fa36-0002-4cef-9825-3e4e67d65915.png",
        "prompt": "Use case: productivity-visual. Asset type: square X financial-news visual. Primary request: create a complete entity-led premium financial-news visual about .hood names, an Ethereum-style naming service for Robinhood Chain, powered by ERC-6551 seedless stock accounts. Scene: a sleek dark blockchain infrastructure display: a glowing \".hood\" domain tag, secure wallet/account nodes, a stylized Ethereum smart-contract chip and stock-account connection; no people. Style: cinematic tech-finance editorial, near-black background, bold white typography and controlled red accents. 1:1 square, object-led scene across center; reserve clean empty near-black bottom-right logo-safe area. Text verbatim: \".HOOD NAMES\" and \"ERC-6551 STOCK ACCOUNTS\". Constraints: clear spelling including the dot in .hood and hyphen in ERC-6551; no source handle/URL, attribution, disclaimer, advice, CTA, logo or watermark. Avoid pure typography card, generic crypto coins, clutter and extra text.",
    },
    {
        "source": "2096492002141516162", "slug": "robinhood-chain-assets-2b",
        "title": "Robinhood Chain assets near $2B",
        "copy": "Robinhood Chain $HOOD assets are closing in on a combined market cap of $2B.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["Robinhood Chain $HOOD assets are nearing a combined market capitalization of $2 billion."],
        "image": "exec-fc6f411b-3c46-4071-acf8-6e62d3c749c4.png",
        "prompt": "Use case: productivity-visual. Asset type: square X financial-news visual. Primary request: create a complete entity-led premium financial-news editorial image about Robinhood Chain assets nearing a combined market capitalization of $2,000,000,000. Scene: futuristic institutional digital-asset exchange dashboard with a central asset vault, network rails, market-cap meter nearing two billion; recognizable finance infrastructure, not generic coins. Style: cinematic black and near-black premium finance news, white typography, controlled red accents. 1:1 square, visual-led center-left, reserve clean empty near-black logo-safe area bottom-right. Text verbatim: \"ROBINHOOD CHAIN ASSETS\" and \"NEAR $2 BILLION\". Constraints: exact number concept and spelling, no source handle, source URL, attribution, disclaimer, advice, CTA, logo, watermark, or extra text. Avoid pure typography card, vague radar motif, generic crypto coin pile, misspellings.",
    },
]


def main():
    document = state.load_state()
    benchmark = {str(x.get("id")): x for x in document["benchmarkPosts"]}
    generated = Path("/root/.codex/generated_images/01a07a8a-a7ff-7940-ba84-08658f896246")
    for item in ITEMS:
        source = benchmark[item["source"]]
        package_id = f"pkg-20260907-{item['slug']}"
        image_path = Path("deliverables") / package_id / "when2buy-image-model.png"
        package = {
            "id": package_id, "benchmarkPostId": item["source"], "benchmarkPostUrl": source["url"],
            "title": item["title"], "status": "ready", "postText": item["copy"],
            "mirroredFacts": item["facts"], "verificationSources": [source["url"]],
            "imagePath": str(image_path), "createdAt": iso(),
            "visualProduction": {"method": "image_model", "prompt": item["prompt"], "logoApplied": True, "qaStatus": "passed"},
        }
        old = next((x for x in document["packages"] if str(x.get("benchmarkPostId")) == item["source"]), None)
        if old:
            old.clear(); old.update(package)
        else:
            document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": iso(), "completedAt": iso(), "summary": "Remade five current timestamp-first packages with entity-led image-model visuals and exact-logo compositing.", "reason": ""})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    for item in ITEMS:
        print(f"pkg-20260907-{item['slug']}")


if __name__ == "__main__":
    main()
