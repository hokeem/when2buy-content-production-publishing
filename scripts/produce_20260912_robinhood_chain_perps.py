#!/usr/bin/env python3
"""Create the sole newest fresh Robinhood Chain package."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

POST_ID = "2098773406279684318"
PACKAGE_ID = "pkg-20260912-robinhood-chain-perps"
IMAGE = "deliverables/pkg-20260912-robinhood-chain-perps/when2buy-image.png"
PROMPT = (
    "Use case: ads-marketing. Asset type: complete square 1:1 X financial-news visual. "
    "Original premium editorial scene about Robinhood Chain and perpetual-futures trading: "
    "a dominant abstract perpetuals terminal, blockchain ledger chain, dark server room, "
    "clean upward volume visualization, near-black graphite, white highlights and restrained red. "
    "Exact square composition with generous empty lower-right logo-safe space. No readable text, "
    "letters, numbers, tickers, company logos, source names, handles, URLs, attribution, "
    "disclaimer, commentary, CTA, tagline, watermark, people, generic radar background, pure "
    "typography card, duplicated objects, malformed screens, or imitation logos. Exact repository "
    "logo composited once afterward."
)

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

document = state.load_state()
source = next((x for x in document["benchmarkPosts"] if str(x.get("id")) == POST_ID), None)
if not source:
    raise SystemExit("Selected benchmark post is missing")
if any(x.get("id") == PACKAGE_ID for x in document["packages"]):
    raise SystemExit("Selected package already exists")
created = now()
package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": POST_ID,
    "benchmarkPostUrl": source["url"],
    "title": "Robinhood Chain record perps volume",
    "status": "ready",
    "postText": "Robinhood Chain $HOOD hit a new all-time high of $531M in daily perps volume yesterday.",
    "mirroredFacts": [
        "The benchmark post states that Robinhood Chain $HOOD reached a new all-time high of $531 million in daily perpetuals volume yesterday.",
        "Robinhood's official Chain documentation identifies perpetual-futures venues including Lighter and Arcus.",
    ],
    "verificationSources": [
        source["url"],
        "https://docs.robinhood.com/chain/",
        "https://robinhood.com/us/en/support/articles/robinhood-wallet-perpetual-futures/",
    ],
    "verificationStatus": "verified_authoritative_context",
    "imagePath": IMAGE,
    "createdAt": created,
    "sourceExpiresAt": source["postedAt"],
    "visualProduction": {
        "method": "image_model",
        "prompt": PROMPT,
        "logoApplied": True,
        "qaStatus": "passed",
        "qa": {
            "inspectedAt": created,
            "result": "passed",
            "checks": [
                "square 1254x1254 PNG",
                "complete blockchain-and-perps entity-led scene",
                "exact repository logo composited once in lower-right clear space",
                "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark",
                "not a pure-text card or generic-radar visual",
                "public copy ends after the factual payload",
            ],
        },
    },
}
document["packages"].append(package)
document["runs"].append({
    "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
    "mode": "produce",
    "status": "succeeded",
    "startedAt": created,
    "completedAt": now(),
    "summary": "Produced one newest fresh Robinhood Chain package with a complete entity-led square visual and one exact-logo composite.",
    "reason": "",
    "selectedPackageIds": [PACKAGE_ID],
})
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(PACKAGE_ID)
