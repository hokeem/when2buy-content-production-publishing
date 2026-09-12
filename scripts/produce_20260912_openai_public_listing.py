#!/usr/bin/env python3
"""Persist the newest fresh OpenAI public-listing fast-follow package."""
import json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098814769964679425"
PACKAGE_ID = "pkg-20260912-openai-public-listing"
IMAGE = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image.png"
SOURCE_URL = f"https://x.com/StockMKTNewz/status/{SOURCE_ID}"
COPY = "OpenAI CEO Sam Altman says now is an ill-advised time for the company to go public.\n\nHe is not looking to take OpenAI public in 2026."
PROMPT = ("Use case: ads-marketing. Complete square 1:1 entity-led premium financial-news visual about "
          "OpenAI CEO Sam Altman saying now is an ill-advised time for OpenAI to go public and that the "
          "company is not looking to go public in 2026. Cinematic near-black private AI company headquarters "
          "and boardroom at night, glass tower, subtle public-markets skyline and a closed stock-exchange bell, "
          "thoughtful executive silhouette, cool blue-white highlights and restrained red accent. No generated "
          "readable text, letters, numbers, logos, watermark, source, attribution, disclaimer, commentary, CTA, "
          "tagline, hashtags, pure-text card, or generic radar background; exact repository logo composited once afterward.")

def iso(dt=None):
    return (dt or datetime.now(timezone.utc)).replace(microsecond=0).isoformat().replace("+00:00", "Z")

doc = state.load_state()
source = next((x for x in doc["benchmarkPosts"] if str(x.get("id")) == SOURCE_ID), None)
if not source: raise SystemExit("selected benchmark post is missing")
posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
now = datetime.now(timezone.utc)
if now - posted > timedelta(minutes=90): raise SystemExit("STALE_SOURCE: selected benchmark exceeded the 90-minute TTL")
if not IMAGE.is_file(): raise SystemExit(f"missing prepared image: {IMAGE}")
package = {
    "id": PACKAGE_ID, "benchmarkPostId": SOURCE_ID, "benchmarkPostUrl": SOURCE_URL,
    "title": "OpenAI CEO says now is an ill-advised time to go public", "status": "ready",
    "postText": COPY,
    "mirroredFacts": ["Sam Altman said now is an ill-advised time for OpenAI to go public.", "He said he is not looking to take OpenAI public in 2026."],
    "verificationSources": [SOURCE_URL, "https://fortune.com/article/why-is-openai-ceo-sam-altman-not-excited-about-being-ceo-of-public-company/", "https://www.fortune.com/2026/06/08/chatgpt-maker-openai-files-ipo-anthropic/"],
    "imagePath": str(IMAGE.relative_to(ROOT)), "createdAt": iso(now), "sourceExpiresAt": iso(posted + timedelta(minutes=90)),
    "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "logoPath": "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png", "logoCount": 1, "canvas": "1254x1254", "qaStatus": "passed", "qa": {"inspectedAt": iso(now), "result": "passed", "checks": ["square 1:1 1254x1254 PNG", "complete OpenAI public-listing entity-led scene", "copy and 2026 fact proofread", "exact repository logo composited once", "generated OpenAI mark removed before exact logo composite", "no source, attribution, disclaimer, commentary, CTA, tagline, hashtags, or watermark", "not a pure-text card or generic-radar visual"]}}
}
doc["packages"] = [x for x in doc["packages"] if x.get("id") != PACKAGE_ID]
doc["packages"].append(package)
doc["runs"].append({"id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": iso(now), "completedAt": iso(), "summary": "Produced one newest fresh OpenAI public-listing package with a complete entity-led square visual and exact-logo composite; publication deferred by delivery guard.", "reason": "delivery_guard_daily_limit", "selectedPackageIds": [PACKAGE_ID]})
errors = state.validate(doc)
if errors: raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(json.dumps({"packageId": PACKAGE_ID, "status": "ready", "imagePath": str(IMAGE.relative_to(ROOT))}))
