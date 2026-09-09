#!/usr/bin/env python3
"""Store the current timestamp-first image-model batch in durable state."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

ITEMS = [
    {"source": "2096867616916689269", "id": "pkg-20260907-fed-rate-path", "title": "UBS sees two 25 bp Fed hikes in 2026", "copy": "UBS Global Wealth Management sees 25 bp Fed rate hikes in September and December 2026, replacing its prior no-change call.", "facts": ["UBS Global Wealth Management expects 25-basis-point U.S. Fed rate hikes in September and December 2026.", "The prior UBS forecast was for no policy change."], "image": "deliverables/pkg-20260907-fed-rate-path/when2buy-final.png", "prompt": "Use case: ads-marketing. Square 1:1 premium entity-led U.S. financial-news visual: Federal Reserve building at night with a restrained red two-step rate path, near-black base, white editorial type reading '25 BP HIKES' and 'SEPT + DEC 2026', and a clean lower-right logo-safe area. No source references, disclaimers, CTA, watermark, or generic typography card."},
    {"source": "2095946340010168608", "id": "pkg-20260905-president-trump-just-said-that-he-speaks-with-fe-68608", "title": "Trump says he speaks with Fed Chair Kevin Warsh", "copy": "President Trump says he speaks with Fed Chair Kevin Warsh.", "facts": ["President Trump said that he speaks with Federal Reserve Chair Kevin Warsh."], "image": "deliverables/pkg-20260905-president-trump-just-said-that-he-speaks-with-fe-68608/when2buy-final.png", "prompt": "Use case: ads-marketing. Square 1:1 premium entity-led political-economic visual: editorial presidential silhouette and Federal Reserve building linked by a restrained communications line, near-black base, white type 'TRUMP + WARSH' and 'FED TALKS', controlled red accent, lower-right logo-safe area. No source references, disclaimer, CTA, watermark, or pure typography card."},
    {"source": "2095944730768978307", "id": "pkg-20260905-president-trump-just-said-growth-does-not-cause--78307", "title": "Trump links inflation to policy failures, not growth", "copy": "President Trump says he views growth as separate from inflation, blaming policy failures for price pressure.", "facts": ["President Trump said growth does not cause inflation.", "He blamed stupidity for inflation."], "image": "deliverables/pkg-20260905-president-trump-just-said-growth-does-not-cause--78307/when2buy-final.png", "prompt": "Use case: ads-marketing. Square 1:1 premium entity-led macroeconomic visual: editorial presidential podium silhouette with inflation chart and policy documents, black and near-black base, white type 'GROWTH ≠ INFLATION' and 'PRICE PRESSURE', controlled red accent, lower-right logo-safe area. No source references, disclaimer, CTA, watermark, or pure typography card."},
    {"source": "2095936496867934708", "id": "pkg-20260905-what-s-the-1-worst-performing-stock-in-your-port-34708", "title": "Portfolio's biggest loser today", "copy": "Which holding is your portfolio's biggest loser today?", "facts": ["The source asks which stock is the worst performer in the reader's portfolio so far today."], "image": "deliverables/pkg-20260905-what-s-the-1-worst-performing-stock-in-your-port-34708/when2buy-final.png", "prompt": "Use case: ads-marketing. Square 1:1 premium entity-led market-performance visual: tactile smartphone portfolio and a single sharply falling red chart on a dark trading desk, white type 'BIGGEST LOSER?' and 'TODAY', lower-right logo-safe area. No ticker, source references, disclaimer, CTA, watermark, or pure typography card."},
    {"source": "2095934683288678906", "id": "pkg-20260905-what-s-the-1-best-performing-stock-in-your-portf-78906", "title": "Portfolio's biggest winner today", "copy": "Which holding is your portfolio's biggest winner today?", "facts": ["The source asks which stock is the best performer in the reader's portfolio so far today."], "image": "deliverables/pkg-20260905-what-s-the-1-best-performing-stock-in-your-portf-78906/when2buy-final.png", "prompt": "Use case: ads-marketing. Square 1:1 premium entity-led market-performance visual: tactile smartphone portfolio and a single sharply rising green chart on a dark trading desk, white type 'BIGGEST WINNER?' and 'TODAY', lower-right logo-safe area. No ticker, source references, disclaimer, CTA, watermark, or pure typography card."},
]

def stamp(): return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
def main():
    document = state.load_state(); sources = {str(x["id"]): x for x in document["benchmarkPosts"]}
    for item in ITEMS:
        package = {"id": item["id"], "benchmarkPostId": item["source"], "benchmarkPostUrl": sources[item["source"]]["url"], "title": item["title"], "status": "ready", "postText": item["copy"], "mirroredFacts": item["facts"], "verificationSources": [sources[item["source"]]["url"]], "imagePath": item["image"], "createdAt": stamp(), "visualProduction": {"method": "image_model", "prompt": item["prompt"], "logoApplied": True, "qaStatus": "passed"}}
        prior = next((x for x in document["packages"] if str(x.get("benchmarkPostId")) == item["source"]), None)
        if prior: prior.clear(); prior.update(package)
        else: document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced the first five timestamp-first packages with image-model visuals and exact-logo compositing.", "reason": ""})
    errors = state.validate(document)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(document)
if __name__ == "__main__": main()
