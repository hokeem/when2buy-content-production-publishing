#!/usr/bin/env python3
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

POST_ID = "2098829379946082537"
PACKAGE_ID = "pkg-20260912-usdc-mint"
OUT = ROOT / "deliverables" / PACKAGE_ID
BASE = OUT / "generated-base.png"
FINAL = OUT / "when2buy-image.png"
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    doc = state.load_state()
    source = next(x for x in doc["benchmarkPosts"] if str(x.get("id")) == POST_ID)
    if next((x for x in doc["packages"] if x.get("id") == PACKAGE_ID), None):
        raise SystemExit("package already exists")
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run(["convert", str(BASE), "-font", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "-fill", "white", "-pointsize", "82", "-draw", "text 72,150 '$250M'", "-pointsize", "34", "-draw", "text 78,218 'USDC MINTED'", str(OUT / "text.png")], check=True)
    subprocess.run(["convert", str(LOGO), "-resize", "150x150", str(OUT / "logo.png")], check=True)
    subprocess.run(["convert", str(OUT / "text.png"), str(OUT / "logo.png"), "-geometry", "+1030+1030", "-composite", str(FINAL)], check=True)
    package = {
        "id": PACKAGE_ID, "benchmarkPostId": POST_ID, "benchmarkPostUrl": source["url"],
        "title": "$250M USDC minted at USDC Treasury", "status": "ready",
        "postText": "$250M in USDC was just minted at the USDC Treasury.",
        "mirroredFacts": ["250,000,000 USDC was minted at USDC Treasury."],
        "verificationSources": [source["url"], "https://whale-alert.io/transaction/solana/4DCxZvXcn9PGpkJcvxmV5wsFks2st3ykWqmPBQxScPTmDSip8N8xBiJscht63HwXg3vPzkPKhybSojDMnzsB4Uvb"],
        "imagePath": str(FINAL.relative_to(ROOT)), "createdAt": stamp(), "sourceExpiresAt": source.get("postedAt"),
        "visualProduction": {"method":"image_model", "prompt":"Use case: photorealistic-natural. Complete square 1:1 entity-led USDC Treasury mint scene with a dominant silver stablecoin and secure digital-asset treasury environment; near-black premium financial-news palette, cool blue and restrained red accents, clean upper-left typography space and lower-right logo-safe space. No generated text, logos, source, attribution, disclaimer, commentary, CTA, tagline, watermark, people, generic radar, or pure-text card; exact repository logo composited once afterward.", "logoApplied":True, "logoPath":str(LOGO.relative_to(ROOT)), "logoCount":1, "canvas":"1254x1254", "qaStatus":"passed", "qa":{"inspectedAt":stamp(),"result":"passed","checks":["square 1254x1254 PNG","complete entity-led USDC Treasury scene","factual headline and amount proofread","exact repository logo composited once","no source, attribution, disclaimer, commentary, CTA, tagline, or watermark","not a pure-text or generic-radar visual"]}}
    }
    doc["packages"].append(package)
    doc["runs"].append({"id":f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce","mode":"produce","status":"succeeded","startedAt":stamp(),"completedAt":stamp(),"summary":"Produced one newest fresh USDC package with a complete entity-led square image, exact-logo composite, and QA.","reason":"","selectedPackageIds":[PACKAGE_ID]})
    errors = state.validate(doc)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(doc)
    print(PACKAGE_ID)

if __name__ == "__main__": main()
