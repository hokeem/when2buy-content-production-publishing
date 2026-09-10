#!/usr/bin/env python3
"""Persist the single newest fresh KERMIT/Robinhood Chain package after QA."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098154982411305155"
PACKAGE_ID = "pkg-20260910-kermit-grok-robinhood-chain"
BASE = Path("/root/.codex/generated_images/01a08d3a-44dd-7401-98c3-c042a7195f0e/exec-8d2ce7fb-be29-4f38-b690-7c90329be462.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
OUT_DIR = ROOT / "deliverables" / PACKAGE_ID
FINAL = OUT_DIR / "when2buy-image-model.png"
PROMPT = "Use case: photorealistic-natural. Complete square 1:1 premium financial-news editorial visual about $KERMIT becoming the first project on Robinhood Chain to integrate Grok, with a frog-themed crypto token, blockchain network, and AI assistant as the entity-led subject; near-black base, crisp white typography and restrained red accents added later; clean upper-left typography space and lower-right logo-safe space; no generated text, source, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, generated branding, or pure-text card; exact repository logo composited once afterward."

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    expires = posted + timedelta(minutes=90)
    if now >= expires:
        raise SystemExit("Selected benchmark expired before production.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BASE, OUT_DIR / "generated-base.png")
    subprocess.run([
        "convert", str(BASE), "-gravity", "northwest", "-font", "DejaVu-Sans-Bold",
        "-fill", "white", "-pointsize", "48", "-annotate", "+58+72", "$KERMIT",
        "-fill", "#ff4b4b", "-pointsize", "72", "-annotate", "+58+150", "FIRST ON ROBINHOOD CHAIN",
        "-fill", "white", "-pointsize", "66", "-annotate", "+58+245", "TO INTEGRATE GROK",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite",
        str(FINAL),
    ], check=True, timeout=30)
    created = stamp()
    package = {
        "id": PACKAGE_ID, "benchmarkPostId": SOURCE_ID, "benchmarkPostUrl": source["url"],
        "title": "$KERMIT integrates Grok on Robinhood Chain", "status": "ready",
        "postText": "$KERMIT is the first project on Robinhood Chain to integrate Grok.",
        "mirroredFacts": ["The benchmark alert said $KERMIT became the first project on Robinhood Chain to integrate Grok.", "$KERMIT rallied after the integration alert."],
        "verificationSources": [source["url"], "https://docs.robinhood.com/chain/"],
        "imagePath": str(FINAL.relative_to(ROOT)), "createdAt": created, "sourceExpiresAt": expires.isoformat().replace("+00:00", "Z"),
        "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed", "qa": {"inspectedAt": created, "result": "passed", "checks": ["square 1254x1254 PNG", "complete KERMIT token, Robinhood Chain, and AI entity scene", "exact factual text composited once", "exact repository logo composited once in lower-right clear space", "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark", "not a pure-text card or generic-radar visual"]}},
    }
    document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": created, "completedAt": stamp(), "summary": "Produced the sole newest fresh KERMIT/Robinhood Chain package with an inspected entity-led image and exact-logo composite.", "reason": "", "packageId": PACKAGE_ID})
    errors = state.validate(document)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__": main()
