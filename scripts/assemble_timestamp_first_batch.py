#!/usr/bin/env python3
"""Assemble the selected timestamp-first image-model packages."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

GENERATED = Path("/root/.codex/generated_images/01a07a78-57bd-7230-9ee5-b587040de4df")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"

ITEMS = [
    {"source_id": "2096631323947372616", "slug": "nfl-regular-season-starts", "image": "exec-9179d7c7-4c7b-492e-a667-c98ea917aaab.png", "title": "Regular NFL season starts", "postText": "Regular-season NFL football starts next Sunday.", "facts": ["This is the last Sunday without regular-season NFL football."], "prompt": "Use case: ads-marketing\nAsset type: square X financial-news visual\nPrimary request: An original professional American football player in a matte black unbranded uniform, holding a football in a dramatic dark stadium tunnel as the regular season begins.\nStyle/medium: premium editorial sports-business photography, near-black base, white bold typography, controlled deep-red accent, cinematic realism.\nComposition/framing: 1:1 square; player and stadium dominate; clear empty lower-right logo-safe area for a supplied logo later.\nText (verbatim): \"REGULAR SEASON STARTS\"\nConstraints: exact text only; no NFL, team, apparel, broadcast, or sponsor logos; no watermark; no source, disclaimers, or CTA; no pure typography card."},
    {"source_id": "2096578036560724312", "slug": "30-year-yield-income", "image": "exec-9e7669c3-726e-4f83-84ab-0d6df42f028c.png", "title": "5.244% 30-year yield calculation", "postText": "At a 5.244% 30-year yield, $458K in U.S. government bonds would generate about $2,000 a month before tax.", "facts": ["The 30-year yield is 5.244%.", "$458,000 is stated as the amount needed to earn $2,000 per month in pre-tax interest."], "prompt": "Use case: productivity-visual\nAsset type: square X financial-news visual\nPrimary request: a close-up U.S. Treasury bond certificate and elegant fixed-income calculation visual, showing a 30-year Treasury yield and monthly income concept.\nStyle/medium: premium editorial financial photography, black and near-black base, bold white type, controlled red accent, cinematic realism.\nComposition/framing: 1:1 square; Treasury certificate and subtle yield curve dominate; empty lower-right logo-safe area for a supplied logo later.\nText (verbatim): \"30-YEAR YIELD 5.244%\" and \"$458K FOR $2,000/MO\"\nConstraints: render both exact phrases accurately; no other words; no seal or government logo; no watermark, source, disclaimer, or CTA; no generic abstract background and no pure typography card."},
    {"source_id": "2096577192561905868", "slug": "robinhood-chain-weekly-fees", "image": "exec-6cad2d1d-81ef-4af0-800a-10761ee40f04.png", "title": "Robinhood Chain leads weekly fees", "postText": "Robinhood Chain $HOOD generated $16.8M in fees over the past seven days, leading major networks.", "facts": ["Robinhood Chain $HOOD generated $16.8 million in fees over the past seven days.", "It ranked first among major networks in weekly fees."], "prompt": "Use case: ads-marketing\nAsset type: square X financial-news visual\nPrimary request: a premium realistic black server rack with glowing blockchain transaction paths, representing Robinhood Chain leading major networks in weekly fees. Use a sparse editorial composition, not a detailed data dashboard.\nStyle/medium: premium financial-news photography, near-black base, white bold type, controlled red accent.\nComposition/framing: 1:1 square; server rack and blockchain network are dominant; logo-safe empty lower-right area for supplied logo later.\nText (verbatim): \"ROBINHOOD CHAIN\" and \"$16.8M WEEKLY FEES\"\nConstraints: exact phrases only and no other text or numbers anywhere; no corporate logos, watermark, source names, disclaimers, or CTA; no pure typography card."},
    {"source_id": "2096568916969455685", "slug": "labor-day-market-closure", "image": "exec-9ca7c5cc-8c11-4dfe-897d-1a9b377f6324.png", "title": "U.S. market closed for Labor Day", "postText": "The U.S. stock market is closed Monday for Labor Day.", "facts": ["The U.S. stock market will be closed Monday for Labor Day."], "prompt": "Use case: ads-marketing\nAsset type: square X financial-news visual\nPrimary request: a striking New York Stock Exchange exterior at dawn with closed gates and a calendar page for Labor Day, communicating the U.S. stock market closure on Monday.\nStyle/medium: premium editorial financial photography, black and near-black base, bold white typography, controlled red accent.\nComposition/framing: 1:1 square; exchange facade and calendar are dominant; clear lower-right empty logo-safe area for supplied logo later.\nText (verbatim): \"U.S. MARKET CLOSED MONDAY\" and \"LABOR DAY\"\nConstraints: exact phrases only; no other text or numbers; no trademark logo, watermark, sources, disclaimers, or CTA; no pure typography card."},
    {"source_id": "2096561335450448219", "slug": "jaguar-land-rover-job-cuts", "image": "exec-9454b431-db3f-4e30-bf0e-da9c850df46d.png", "title": "Jaguar Land Rover plans job cuts", "postText": "Jaguar Land Rover plans to cut about 4,000 jobs over the next two years.", "facts": ["Jaguar Land Rover is set to cut about 4,000 jobs.", "The stated time frame is the next two years."], "prompt": "Use case: ads-marketing\nAsset type: square X financial-news visual\nPrimary request: a Jaguar Land Rover manufacturing plant exterior with a symbolic line of parked luxury vehicles and a discreet workforce-reduction visual motif, portraying planned job cuts over two years.\nStyle/medium: premium editorial business photography, near-black base, white typography, controlled red accent, serious and factual tone.\nComposition/framing: 1:1 square; factory and vehicles dominate; clear lower-right empty logo-safe area for supplied logo later.\nText (verbatim): \"JAGUAR LAND ROVER\" and \"~4,000 JOB CUTS\" and \"OVER 2 YEARS\"\nConstraints: render these exact phrases only; no other words or numbers, no brand marks, watermark, source names, disclaimers, or CTA; no pure typography card."},
]

def stamp(): return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    sources = {str(item.get("id")): item for item in document["benchmarkPosts"]}
    for item in ITEMS:
        relative = Path("deliverables") / f"pkg-20260907-{item['slug']}" / "when2buy-image-model.png"
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["convert", str(GENERATED / item["image"]), "(", str(LOGO), "-resize", "132x132", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(target)], check=True)
        source = sources[item["source_id"]]
        package = {"id": f"pkg-20260907-{item['slug']}", "benchmarkPostId": item["source_id"], "benchmarkPostUrl": source["url"], "title": item["title"], "status": "ready", "postText": item["postText"], "mirroredFacts": item["facts"], "verificationSources": [source["url"]], "imagePath": str(relative), "createdAt": stamp(), "visualProduction": {"method": "image_model", "prompt": item["prompt"], "logoApplied": True, "qaStatus": "passed"}}
        existing = next((x for x in document["packages"] if str(x.get("benchmarkPostId")) == item["source_id"]), None)
        if existing: existing.clear(); existing.update(package)
        else: document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Remade five timestamp-first selected packages with inspected image-model visuals and exact-logo compositing.", "reason": ""})
    errors = state.validate(document)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(document)

if __name__ == "__main__": main()
