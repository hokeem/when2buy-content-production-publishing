#!/usr/bin/env python3
"""Replace the first five timestamp-first queue packages with image-model assets."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

IMAGE_DIR = Path("/root/.codex/generated_images/01a07aaf-46ff-7352-8626-9b9ba56b1fde")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"

ITEMS = [
    ("2096320375764258871", "btc-etf-weekly-inflow", "exec-cb07e4d4-6ca9-4fe3-9f0f-4db3ee679e4e.png", "U.S. Bitcoin ETFs see $986.8M weekly inflow", "U.S. $BTC ETFs saw $986.8M in inflows this week.\n\nWhen2Buy — your U.S. stock partner.", ["U.S. Bitcoin ETFs saw $986.8 million in inflows this week."], "Use case: productivity-visual\nAsset type: square X financial-news visual\nPrimary request: U.S. spot Bitcoin ETF inflows, represented by an elegant Bitcoin coin in front of a U.S. market-trading screen, with a clear rising capital-flow ribbon and stacks of institutional financial documents; entity-led, credible editorial scene.\nStyle/medium: premium financial-news photography and subtle data visualization, black and near-black base, white typography, controlled deep-red accent, cinematic realistic lighting.\nComposition/framing: exact 1:1 square, Bitcoin coin and institutional capital-flow scene dominate; reserve a clean empty lower-right corner for a logo to be composited later.\nText (verbatim): \"U.S. BITCOIN ETFs\" and \"$986.8M WEEKLY INFLOW\"\nConstraints: accurately render only these exact phrases; no other readable text or numbers, no company or exchange logos, no watermark, no source names, no disclaimers, no CTA, no generic abstract background, and not a pure typography card."),
    ("2096311155614498976", "sp500-decade-changes", "exec-0e3b000f-4073-4739-afff-cf4cc0727b7b.png", "S&P 500 membership changes over a decade", "S&P 500 membership has shifted across the past decade, with stocks added and removed from the index.\n\nWhen2Buy — your U.S. stock partner.", ["The source lists stocks added to and removed from the S&P 500 over the past decade."], "Use case: productivity-visual\nAsset type: square X financial-news visual\nPrimary request: an entity-led historical S&P 500 composition scene: an elegant heavyweight U.S. stock index binder and a large wall of company nameplates moving between inclusion and removal columns over a decade, conveying stocks added and removed from the S&P 500.\nStyle/medium: premium editorial financial newsroom photography, near-black background, white type, controlled deep-red accent, cinematic realism.\nComposition/framing: exact 1:1 square; index binder and company nameplate board dominate; leave an empty lower-right logo-safe area.\nText (verbatim): \"S&P 500\" and \"10-YEAR CHANGES\"\nConstraints: exact text only; no other readable words or numbers, no corporate logos, no watermark, no source names, no disclaimer, no CTA; do not make a pure typography card."),
    ("2096275001389281625", "nvidia-september-market-cap", "exec-0d886fda-8e9d-42d8-98fa-56425456a624.png", "NVIDIA's September market-cap history", "NVIDIA $NVDA's September market cap reached $5.6T in 2026, up from $1.5B in 1999.\n\nWhen2Buy — your U.S. stock partner.", ["NVIDIA's September 1999 market cap was $1.5 billion.", "NVIDIA's September 2026 market cap was $5.6 trillion."], "Use case: productivity-visual\nAsset type: square X financial-news visual\nPrimary request: NVIDIA's market-cap history across September since its IPO, represented by a photorealistic advanced AI data-center GPU chip on a black institutional market chart rising from a small 1999 marker to a towering 2026 peak. Entity-led chip and growth chart, not generic abstraction.\nStyle/medium: premium financial-news editorial photography with a clean graphic chart, near-black base, bold white type, controlled deep-red accent, cinematic light.\nComposition/framing: exact 1:1 square; GPU chip and upward history chart dominate; empty lower-right logo-safe area.\nText (verbatim): \"NVIDIA $NVDA\" and \"$5.6T MARKET CAP\"\nConstraints: render exact phrases only; no other readable text or numbers, no company logos, watermark, source names, disclaimer, CTA, generic background, or pure typography card."),
    ("2096273144906502203", "nvidia-fy29-profit", "exec-9b66346d-bf78-45ec-b5e6-43dd0c256707.png", "NVIDIA FY29 profit forecast", "NVIDIA $NVDA is expected to triple profit to nearly $595B by FY29.\n\nWhen2Buy — your U.S. stock partner.", ["NVIDIA is expected to triple profit to nearly $595 billion by fiscal 2029."], "Use case: productivity-visual\nAsset type: square X financial-news visual\nPrimary request: NVIDIA profit forecast to fiscal 2029, represented by a photorealistic advanced AI data-center GPU wafer on a dark earnings projection chart climbing sharply toward a large profit target. Entity-led semiconductor and financial forecast scene.\nStyle/medium: premium financial-news editorial photography, black and near-black base, bold white type, controlled deep-red accent, cinematic realism.\nComposition/framing: exact 1:1 square; chip and rising earnings projection dominate; reserve clean lower-right logo-safe area.\nText (verbatim): \"NVIDIA $NVDA\" and \"~$595B FY29 PROFIT\"\nConstraints: exact phrases only; no other readable text or numbers, no logo or trademark mark, no watermark, source name, disclaimer, CTA, generic abstract background, or pure typography card."),
    ("2096270144343294083", "apple-september-market-cap", "exec-5cfb80bd-ab0f-4e27-bdc7-be4aa975b2f5.png", "Apple's September market-cap history", "Apple $AAPL's September market cap reached $4.7T in 2026, up from $1.6B in 1984.\n\nWhen2Buy — your U.S. stock partner.", ["Apple's September 1984 market cap was $1.6 billion.", "Apple's September 2026 market cap was $4.7 trillion, with John Ternus taking over as CEO."], "Use case: productivity-visual\nAsset type: square X financial-news visual\nPrimary request: Apple market-cap history since 1984 and its 2026 leadership transition, shown with an elegant unbranded premium smartphone silhouette beside a long ascending market-cap timeline that reaches a 2026 peak, entity-led and factual.\nStyle/medium: premium financial-news editorial photography with minimalist chart detail, black and near-black base, bold white type, controlled deep-red accent, cinematic realism.\nComposition/framing: exact 1:1 square; smartphone and history timeline dominate; clean empty lower-right logo-safe area.\nText (verbatim): \"APPLE $AAPL\" and \"$4.7T MARKET CAP\"\nConstraints: render exact phrases only; no other readable text or numbers, no Apple logo, no watermark, source names, disclaimer, CTA, generic abstract background, or pure typography card."),
]

def now(): return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    sources = {str(x.get("id")): x for x in document["benchmarkPosts"]}
    for source_id, slug, filename, title, copy, facts, prompt in ITEMS:
        target_rel = Path("deliverables") / f"pkg-20260907-{slug}" / "when2buy-image-model.png"
        target = ROOT / target_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        base = target.with_name("generated-base.png")
        shutil.copy2(IMAGE_DIR / filename, base)
        subprocess.run(["convert", str(base), "(", str(LOGO), "-resize", "132x132", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(target)], check=True)
        base.unlink()
        package = {"id": f"pkg-20260907-{slug}", "benchmarkPostId": source_id, "benchmarkPostUrl": sources[source_id]["url"], "title": title, "status": "ready", "postText": copy, "mirroredFacts": facts, "verificationSources": [sources[source_id]["url"]], "imagePath": str(target_rel), "createdAt": now(), "visualProduction": {"method": "image_model", "prompt": prompt, "logoApplied": True, "qaStatus": "passed"}}
        existing = next((x for x in document["packages"] if str(x.get("benchmarkPostId")) == source_id), None)
        if existing: existing.clear(); existing.update(package)
        else: document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": now(), "completedAt": now(), "summary": "Remade the first five queue items with image-model visuals, exact-logo compositing, and visual QA.", "reason": ""})
    errors = state.validate(document)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(document)

if __name__ == "__main__": main()
