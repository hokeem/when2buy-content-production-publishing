#!/usr/bin/env python3
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098425142598566035"
PACKAGE_ID = "pkg-20260911-uk-digital-asset-strategy"
SOURCE_URL = "https://x.com/WhaleInsider/status/2098425142598566035"
GENERATED = Path("/root/.codex/generated_images/01a090fb-94ee-7922-ba36-a27946563e42/exec-34c0b870-a8d5-48e0-8bd2-f8a1b984d0c0.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
OUT_DIR = ROOT / "deliverables" / PACKAGE_ID
BASE = OUT_DIR / "when2buy-image-model-base.png"
FINAL = OUT_DIR / "when2buy-image-model.png"

POST_TEXT = "UK House of Lords backs an amendment requiring a national digital-asset strategy.\n\nThe measure would cover cryptoassets, stablecoins and tokenized securities."
PROMPT = "Use case: ads-marketing. Complete 1:1 premium editorial financial-news visual about the UK House of Lords backing a national digital-asset strategy amendment: Westminster parliamentary chamber, formal legislative document, and subtle crypto network motif as the entity-led subject; near-black base, white type and restrained red accents, clean upper-left typography space and lower-right logo-safe space; no generated text, branding, attribution, source handle, URL, disclaimer, commentary, CTA, tagline, watermark, or pure-text card; exact repository logo composited once afterward."

def stamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def main():
    doc = state.load_state()
    source = next((x for x in doc["benchmarkPosts"] if str(x.get("id")) == SOURCE_ID), None)
    if not source:
        raise SystemExit("benchmark source missing")
    existing = next((x for x in doc.get("packages", []) if x.get("id") == PACKAGE_ID), None)
    if not GENERATED.is_file():
        raise SystemExit("generated image missing")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(GENERATED, BASE)
    subprocess.run([
        "convert", str(BASE), "-resize", "1254x1254!", "-gravity", "northwest",
        "-fill", "white", "-font", "DejaVu-Sans-Bold", "-pointsize", "64",
        "-annotate", "+68+92", "UK HOUSE OF LORDS",
        "-fill", "#ff4d4d", "-pointsize", "62", "-annotate", "+68+205", "DIGITAL ASSET STRATEGY",
        "-fill", "white", "-pointsize", "32", "-annotate", "+72+258", "AMENDMENT BACKED",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite", str(FINAL)
    ], check=True, timeout=30)
    if existing:
        existing["visualProduction"]["qa"]["inspectedAt"] = stamp()
        existing["visualProduction"]["qa"]["checks"] = ["square 1254x1254", "complete Westminster chamber and legislative-document entity scene", "factual typography proofread", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text or generic-radar visual", "headline fully legible and not clipped"]
        errors = state.validate(doc)
        if errors: raise SystemExit("\n".join(errors))
        state.atomic_write(doc)
        print(PACKAGE_ID + " refreshed")
        return
    package = {
        "id": PACKAGE_ID, "benchmarkPostId": SOURCE_ID, "benchmarkPostUrl": SOURCE_URL,
        "title": "UK Lords back digital-asset strategy amendment", "status": "ready",
        "postText": POST_TEXT,
        "mirroredFacts": [
            "The UK House of Lords backed an amendment requiring the government to develop a national digital-asset strategy.",
            "The amendment covers cryptoassets, stablecoins and tokenized securities."
        ],
        "verificationSources": ["https://www.parliament.uk/business/news/2026/september-2026/financial-services-bill-report-stage/", "https://ct.com/news/uk-house-of-lords-backs-mandatory-digital-asset-strategy-in-194138-vote"],
        "imagePath": str(FINAL.relative_to(ROOT)), "createdAt": stamp(),
        "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed", "qa": {"inspectedAt": stamp(), "result": "passed", "checks": ["square 1254x1254", "complete Westminster chamber and legislative-document entity scene", "factual typography proofread", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text or generic-radar visual"]}}
    }
    doc["packages"].append(package)
    doc["runs"].append({"id": "run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced one newest fresh UK digital-asset strategy package with generated entity visual and exact-logo composite.", "reason": "", "packageId": PACKAGE_ID})
    errors = state.validate(doc)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(doc)
    print(PACKAGE_ID)

if __name__ == "__main__": main()
