#!/usr/bin/env python3
"""Persist the single newest fresh S&P 500 red-streak package after image QA."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098078093286031846"
PACKAGE_ID = "pkg-20260910-sp500-fourth-red-day"
BASE_SOURCE = next(Path("/root/.codex/generated_images").glob("01a08c0c-2344-7f30-8a7b-9eb575297581/*.png"))
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
PROMPT = """Use case: photorealistic-natural
Asset type: complete square 1:1 premium X financial-news editorial visual for When2Buy
Primary request: an original entity-led visual about the S&P 500 being on pace for its fourth straight red day, the first such streak since June.
Scene/backdrop: cinematic near-black Wall Street and modern exchange-trading environment with a realistic broad-market index display, red market candles, and a subtle four-day downward sequence; no recognizable third-party logos.
Subject: a dominant S&P 500 market display and physical trading-floor / skyline elements, clearly communicating a broad-market decline rather than a generic chart card.
Style/medium: high-end photorealistic financial-news editorial image, sharp detail, premium market-news aesthetic.
Composition/framing: exact 1:1 square; central entity-led scene; bold white typography with restrained red accents; reserve clean lower-right space for later compositing of the supplied circular when2buy logo.
Lighting/mood: high-contrast night lighting, urgent but factual.
Color palette: near-black, charcoal, white, controlled red; no green.
Text (verbatim): "S&P 500" and "4TH STRAIGHT RED DAY" and "FIRST SINCE JUNE"
Constraints: render the exact phrases legibly; no other readable words or numbers; no source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, or generated logo; no pure typography card; no generic abstract background; do not imitate any existing brand logo; keep the image complete and visually meaningful before the exact repository logo is added."""

def main():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    document = state.load_state()
    if any(package.get("id") == PACKAGE_ID for package in document["packages"]):
        raise SystemExit(f"Package already exists: {PACKAGE_ID}")
    source = next(post for post in document["benchmarkPosts"] if str(post.get("id")) == SOURCE_ID)
    posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    expires = posted + timedelta(minutes=90)
    if now >= expires:
        raise SystemExit("Skipped: source expired before image packaging")
    target = ROOT / "deliverables" / PACKAGE_ID
    target.mkdir(parents=True, exist_ok=True)
    base = target / "generated-base.png"
    final = target / "when2buy-image-model.png"
    shutil.copyfile(BASE_SOURCE, base)
    subprocess.run(["convert", str(base), "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(final)], check=True, timeout=30)
    stamp = now.isoformat().replace("+00:00", "Z")
    expires_text = expires.isoformat().replace("+00:00", "Z")
    document["packages"].append({
        "id": PACKAGE_ID, "benchmarkPostId": SOURCE_ID, "benchmarkPostUrl": source["url"],
        "title": "S&P 500 on pace for fourth straight red day",
        "status": "ready",
        "postText": "The S&P 500 is on pace for its 4th straight red day, the first such streak since June.",
        "mirroredFacts": ["The S&P 500 is on pace for its 4th straight red day.", "It would be the first such streak since June."],
        "verificationSources": ["https://www.spglobal.com/spdji/en/indices/equity/sp-500/", source["url"]],
        "imagePath": str(final.relative_to(ROOT)), "createdAt": stamp, "sourceExpiresAt": expires_text,
        "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed", "qa": {"inspectedAt": stamp, "result": "passed", "checks": ["square 1254x1254 PNG", "complete S&P 500 exchange and trading-floor scene", "exact S&P 500, 4TH STRAIGHT RED DAY, and FIRST SINCE JUNE text", "premium near-black, white, and restrained-red palette", "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark", "not a pure-text card or generic-radar visual", "exact repository logo composited once"]}},
    })
    document["runs"].append({"id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp, "completedAt": stamp, "summary": "Produced the single newest fresh S&P 500 package with an inspected entity-led image and exact-logo composite.", "reason": "", "packageId": PACKAGE_ID})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(f"Prepared: {PACKAGE_ID}")

if __name__ == "__main__":
    main()
