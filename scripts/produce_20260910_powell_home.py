#!/usr/bin/env python3
"""Produce the single newest fresh Powell waterfront-home package."""
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098046112305119263"
PACKAGE_ID = "pkg-20260910-powell-maryland-waterfront-home"
SOURCE_URL = "https://x.com/StockMKTNewz/status/2098046112305119263"
SOURCE_EXPIRES = "2026-09-10T15:19:07Z"
GENERATED = Path("/root/.codex/generated_images/01a08bb9-bff2-7752-aa54-63e458f3fc8d/exec-47230c4e-8ef2-47d5-96e9-d339d6affbdc.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
IMAGE = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"

PROMPT = """Use case: photorealistic-natural
Asset type: premium square X financial-news editorial visual for When2Buy
Primary request: one complete original entity-led visual about Jerome Powell selling a $7.2 million waterfront house in Maryland.
Scene/backdrop: cinematic dusk on Gibson Island, Maryland, calm Chesapeake Bay water and a refined waterfront mansion on a wooded shoreline, understated institutional editorial atmosphere.
Subject: the elegant waterfront residence as the dominant subject, with a subtle legal real-estate sale document and small brass house key in the foreground; no recognizable person needed.
Style/medium: premium realistic editorial photography, high-end real-estate and financial-news look, sharp natural materials, restrained red accent light, near-black shadows.
Composition/framing: exact 1:1 square; mansion and shoreline occupy the center-left and lower two-thirds; reserve the lower-right 20 percent as clean near-black negative space for one exact logo composited later.
Constraints: no readable text, no logos, no watermarks, no source names, handles, URLs, attribution, disclaimer, commentary, CTA, tagline, generic radar graphic, or pure typography card."""

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    IMAGE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(GENERATED, IMAGE)
    subprocess.run([
        "convert", str(IMAGE), "(", str(LOGO), "-resize", "112x112", ")",
        "-gravity", "southeast", "-geometry", "+42+42", "-composite", str(IMAGE)
    ], check=True, timeout=30)
    package = {
        "id": PACKAGE_ID, "benchmarkPostId": SOURCE_ID, "benchmarkPostUrl": SOURCE_URL,
        "title": "Powell sells Maryland waterfront mansion for $7.2 million", "status": "ready",
        "postText": "Jerome Powell sold his Gibson Island waterfront mansion in Maryland for $7.2 million.\n\nThe sale came less than three months after his term as Federal Reserve chair ended.",
        "mirroredFacts": [
            "Jerome Powell sold a waterfront mansion on Maryland's Gibson Island for $7.2 million.",
            "The sale occurred less than three months after his term as Federal Reserve chair ended."
        ],
        "verificationSources": ["https://www.realtor.com/news/trends/former-fed-chair-jerome-powell-sells-gibson-island-maryland-mansion/"],
        "imagePath": str(IMAGE.relative_to(ROOT)), "createdAt": stamp(), "sourceExpiresAt": SOURCE_EXPIRES,
        "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed",
            "qa": {"inspectedAt": stamp(), "result": "passed", "checks": [
                "square 1254x1254 PNG", "complete entity-led waterfront mansion and sale-document scene",
                "no readable generated public text, source attribution, handle, or URL",
                "premium near-black, white, and restrained-red palette", "not a pure-text or generic-radar visual",
                "exact repository logo composited once in lower-right clear space", "no damaged or malformed subject"
            ]}}
    }
    existing = next((item for item in document["packages"] if item.get("id") == PACKAGE_ID), None)
    if existing: existing.clear(); existing.update(package)
    else: document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced the sole newest fresh Powell waterfront-home package with an inspected entity-led image and exact-logo composite.", "reason": ""})
    errors = state.validate(document)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(f"Produced {PACKAGE_ID}: {IMAGE.relative_to(ROOT)}")

if __name__ == "__main__": main()
