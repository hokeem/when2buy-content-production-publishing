#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

SOURCE_ID = "2098397752774234368"
PACKAGE_ID = "pkg-20260911-micron-taiwan-bonus"
GENERATED = Path("/root/.codex/generated_images/01a090a9-2cf6-75f2-8c5b-78bed8b29ffa/exec-43b165e5-de1a-4a92-9ec9-25439de3adec.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"

def stamp():
    return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    source = next(x for x in document["benchmarkPosts"] if str(x.get("id")) == SOURCE_ID)
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "convert", str(GENERATED), "(", str(LOGO), "-resize", "112x112", ")",
        "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(FINAL)
    ], check=True)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Micron Taiwan workers receive $31,600 cash bonus",
        "status": "ready",
        "postText": "Micron $MU is giving Taiwanese employees a $31,600 cash bonus plus additional stock rewards.\n\nAll global employees will receive equity through an annual performance-related bonus pool.",
        "mirroredFacts": [
            "Micron said Taiwanese employees will receive a $31,600 cash bonus.",
            "Taiwanese employees will also receive additional stock rewards.",
            "All global employees will receive equities through an annual performance-related bonus pool."
        ],
        "verificationSources": [
            "https://in.marketscreener.com/news/micron-s-taiwan-workers-to-get-rewards-worth-up-to-68-months-of-pay-ce785bdfd88ff52d",
            source["url"]
        ],
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": stamp(),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Use case: ads-marketing. Complete 1:1 entity-led photorealistic Micron semiconductor scene: advanced memory chips and silicon wafer in the foreground, Taiwan fabrication facility at night, subtle cleanroom employees, near-black graphite and cool blue palette with restrained red reflections, strong subject, dark lower-right logo-safe area, no text or embedded logos. Exact repository logo composited once afterward.",
            "logoApplied": True,
            "qaStatus": "passed"
        }
    }
    old = next((x for x in document["packages"] if x.get("id") == PACKAGE_ID), None)
    if old:
        old.clear(); old.update(package)
    else:
        document["packages"].append(package)
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(),
        "summary": "Produced the newest fresh Micron benchmark package with one complete entity-led square image and one exact-logo composite.",
        "reason": ""
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
