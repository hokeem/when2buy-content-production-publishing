#!/usr/bin/env python3
"""Assemble the timestamp-first queue's first five image-model packages."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

ASSETS = Path("/root/.codex/generated_images/01a07ad3-e4a6-7703-b264-ab2f96367857")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"

ITEMS = [
    ("2095974949391376761", "this-is-how-the-stock-market-performed-today-76761", "exec-dd37314c-df55-4784-b932-1ad664465a45.png", "U.S. stock market performance today", "The U.S. stock market's performance today is in focus.\n\nWhen2Buy — your U.S. stock partner.", ["The source covers how the U.S. stock market performed today."], "U.S. stock market daily close: 1:1 premium editorial financial-news visual with a realistic Wall Street trading floor, electronic market board, exchange architecture and red closing-bell light. Black and near-black base, white type, controlled red accent. Exact text: U.S. STOCK MARKET; TODAY'S CLOSE. The entity-led market scene dominates; clean lower-right logo-safe area. No other readable text, numbers, logos, watermark, source names, URLs, disclaimers, CTA, or pure typography."),
    ("2095970287435047085", "evan-stockmktnewz-top-10-trader-47085", "exec-5e36bf4e-23f2-497d-a57d-6b2ccac3e8d1.png", "Top 10 trader", "A top-10 trader ranking is in focus today.\n\nWhen2Buy — your U.S. stock partner.", ["The source identifies an Evan StockMKTNewz Top 10 Trader item."], "1:1 premium financial-news visual of an anonymous professional trader at a dark multi-screen trading desk and a ranked performance board. Black and near-black base, white type, controlled red accent. Exact text: TOP 10 TRADER. Trader and screens dominate with a clean lower-right logo-safe area. No other readable text, numbers, names, logos, watermark, source names, URLs, disclaimers, CTA, or pure typography."),
    ("2095958389150916903", "btc-85k-kalshi-probability-16903", "exec-cbed5af8-dc28-4caf-a42c-b63eaf76e756.png", "BTC $85K probability", "$BTC has a 77% chance of crossing $85K again before Oct. 2.\n\nWhen2Buy — your U.S. stock partner.", ["Kalshi traders assign a 77% chance that BTC crosses $85,000 again before October 2."], "1:1 premium editorial financial-news visual of a realistic Bitcoin coin and institutional trading screens with a rising trajectory to $85K. Black and near-black base, white type, controlled red accent. Exact text: BTC $85K; 77% BY OCT. 2. Coin and market event dominate with a clean lower-right logo-safe area. No other readable text, numbers, logos, watermark, source names, URLs, disclaimers, CTA, or pure typography."),
    ("2095951550073946330", "data-centers-state-approval-46330", "exec-b12e6c25-d48c-4316-b884-bb5f6b457925.png", "Data centers and state approvals", "Data-center approvals can shape a state's growth path.\n\nWhen2Buy — your U.S. stock partner.", ["President Trump said states that want to get rich will want data centers.", "He contrasted data-center approvals with poverty and crime."], "1:1 premium editorial financial-news visual of realistic large-scale data centers, power infrastructure and a state approval document. Black and near-black base, white type, controlled red accent. Exact text: DATA CENTERS; STATE APPROVAL. Facility and document dominate with a clean lower-right logo-safe area. No other readable text, numbers, politicians, logos, watermark, source names, URLs, disclaimers, CTA, or pure typography."),
    ("2095947527795220987", "interest-rates-one-or-half-percent-20987", "exec-3fbc95bc-2d33-4bfb-9ff5-ad2ac0538bc8.png", "Interest-rate target", "Interest rates should be at 1% or 0.5%.\n\nWhen2Buy — your U.S. stock partner.", ["President Trump said interest rates should be at 1% or 0.5%."], "1:1 premium editorial financial-news visual of a Federal Reserve-style building, a rate dial set between 1% and 0.5%, and a dark bond-market screen. Black and near-black base, white type, controlled red accent. Exact text: INTEREST RATES; 1% OR 0.5%. Architecture and rate dial dominate with a clean lower-right logo-safe area. No other readable text, numbers, politicians, logos, watermark, source names, URLs, disclaimers, CTA, or pure typography."),
]

def now(): return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    sources = {str(x["id"]): x for x in document["benchmarkPosts"]}
    for source_id, slug, asset, title, copy, facts, prompt in ITEMS:
        rel = Path("deliverables") / f"pkg-20260907-{slug}" / "when2buy-image-model.png"
        target = ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        base = target.with_name("generated-base.png")
        shutil.copy2(ASSETS / asset, base)
        subprocess.run(["convert", str(base), "(", str(LOGO), "-resize", "132x132", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(target)], check=True)
        base.unlink()
        package = {"id": f"pkg-20260907-{slug}", "benchmarkPostId": source_id, "benchmarkPostUrl": sources[source_id]["url"], "title": title, "status": "ready", "postText": copy, "mirroredFacts": facts, "verificationSources": [sources[source_id]["url"]], "imagePath": str(rel), "createdAt": now(), "visualProduction": {"method": "image_model", "prompt": prompt, "logoApplied": True, "qaStatus": "passed"}}
        existing = next((x for x in document["packages"] if str(x.get("benchmarkPostId")) == source_id), None)
        if existing: existing.clear(); existing.update(package)
        else: document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": now(), "completedAt": now(), "summary": "Remade the first five timestamp-first queue items with inspected image-model visuals and exact-logo compositing.", "reason": ""})
    errors = state.validate(document)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(document)

if __name__ == "__main__": main()
