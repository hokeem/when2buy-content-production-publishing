#!/usr/bin/env python3
"""Record the five current timestamp-first image-model packages."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

ITEMS = [
    ("2096942235312918559", "dell-sp500-316", "Dell Technologies ranks third among S&P 500 stocks so far in 2026, with $DELL up 316%.", ["Dell Technologies is the third-best-performing S&P 500 stock so far in 2026.", "$DELL is up 316%."], "Dell enterprise data-center scene with a bronze third-place medallion and abstract rising market trajectory; premium near-black, white, restrained red and slight green performance accent; no generated text or logos; clean lower-right logo-safe area."),
    ("2096942065867202925", "robinhood-chain-30m-week", "Robinhood Chain generated $30 million in revenue last week. $HOOD", ["Robinhood Chain generated $30 million in revenue last week."], "Robinhood Chain transaction-network infrastructure and a revenue-surge motif; premium near-black and white financial-news imagery with restrained red accents; no generated text or logos; clean lower-right logo-safe area."),
    ("2096940978732953909", "indexr-robinhood-chain-launch", "$INDEXR has launched on Robinhood Chain as a 1:1-backed, redeemable memecoin index-fund token bundling coins into one token.", ["INDEXR launched on Robinhood Chain.", "It is described as a 1:1-backed, redeemable memecoin index-fund token that bundles coins into one token."], "Index-fund token container linking several abstract token nodes with a one-to-one exchange motif; premium near-black and white financial-news imagery with restrained red accents; no generated text or logos; clean lower-right logo-safe area."),
    ("2096939055036436906", "moderna-sp500-394", "Moderna ranks second among S&P 500 stocks so far in 2026, with $MRNA up 394%.", ["Moderna is the second-best-performing S&P 500 stock so far in 2026.", "$MRNA is up 394%."], "Modern biotechnology research vessel and laboratory architecture with an abstract rising market trajectory; premium near-black, white, restrained red and slight green performance accent; no generated text or logos; clean lower-right logo-safe area."),
    ("2096935123937640546", "apple-iphone-event-ternus", "John Ternus is expected to lead Apple’s $AAPL iPhone event Wednesday, with Tim Cook not expected to appear.", ["John Ternus is expected to lead Apple's new iPhone release event Wednesday.", "Tim Cook is not expected to appear."], "Minimal product-launch stage with a luminous smartphone silhouette and anonymous executive at a lectern; premium near-black and white financial-news imagery with restrained red accents; no generated text or logos; clean lower-right logo-safe area."),
]

def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    sources = {str(item["id"]): item for item in document["benchmarkPosts"]}
    for source_id, slug, body, facts, prompt in ITEMS:
        source = sources[source_id]
        package = {
            "id": f"pkg-20260907-{slug}", "benchmarkPostId": source_id,
            "benchmarkPostUrl": source["url"], "title": body.split(".")[0], "status": "ready",
            "postText": body + "\n\nWhen2Buy — your U.S. stock partner.",
            "mirroredFacts": facts, "verificationSources": [source["url"]],
            "imagePath": str(Path("deliverables") / f"pkg-20260907-{slug}" / "when2buy-image-model.png"),
            "createdAt": now(),
            "visualProduction": {"method": "image_model", "prompt": prompt, "logoApplied": True, "qaStatus": "passed"},
        }
        existing = next((item for item in document["packages"] if str(item.get("benchmarkPostId")) == source_id), None)
        if existing:
            existing.clear(); existing.update(package)
        else:
            document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": now(), "completedAt": now(), "summary": "Produced the five timestamp-first benchmark items with original image-model visuals and exact-logo compositing.", "reason": ""})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print("Prepared " + ", ".join(f"pkg-20260907-{item[1]}" for item in ITEMS))

if __name__ == "__main__":
    main()
