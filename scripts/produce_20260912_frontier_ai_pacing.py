#!/usr/bin/env python3
"""Persist the single newest fresh frontier-AI pacing package after visual QA."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098818125097583056"
PACKAGE_ID = "pkg-20260912-frontier-ai-pacing"
BASE = Path("/root/.codex/generated_images/01a0968f-d1af-7b01-8ba2-878773d5d031/exec-94904047-a62f-4cd2-8efb-5c664c3fddcb.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
OUT_DIR = ROOT / "deliverables" / PACKAGE_ID
BASE_COPY = OUT_DIR / "generated-base.png"
FINAL = OUT_DIR / "when2buy-image.png"

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

document = state.load_state()
source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
if source.get("isPinned") or source.get("account") != "WhaleInsider":
    raise SystemExit("selected source no longer eligible")
OUT_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(BASE, BASE_COPY)
subprocess.run([
    "convert", str(BASE_COPY), "(", str(LOGO), "-resize", "112x112", ")",
    "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(FINAL),
], check=True, timeout=30)
created = stamp()
package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": source["url"],
    "title": "Sam Altman backs pacing frontier AI development",
    "status": "ready",
    "postText": "Sam Altman agrees with Dario Amodei's proposal to pace frontier AI development.",
    "mirroredFacts": [
        "Sam Altman agreed with Dario Amodei's proposal to pace frontier AI development.",
        "Current reporting describes Amodei's proposal as an immediate slowdown in the pace of AI development.",
    ],
    "verificationSources": [
        source["url"],
        "https://www.axios.com/2026/09/12/anthropic-ai-amodei-pacing",
        "https://apnews.com/article/d59552edcb27892d8ee4d98a48397706",
    ],
    "imagePath": str(FINAL.relative_to(ROOT)),
    "createdAt": created,
    "sourceExpiresAt": "2026-09-12T18:26:49Z",
    "visualProduction": {
        "method": "image_model",
        "prompt": "Complete square entity-led frontier-AI compute facility and secure research campus at night, with a physical AI accelerator server rack and a controlled gate motif; premium near-black financial-news photography, cool blue-white highlights, restrained red accent, clean lower-right logo-safe area; no readable text, letters, numbers, logos, source, attribution, disclaimer, commentary, CTA, tagline, watermark, or generic radar background.",
        "logoApplied": True,
        "logoPath": str(LOGO.relative_to(ROOT)),
        "logoCount": 1,
        "canvas": "1254x1254",
        "qaStatus": "passed",
        "qa": {
            "inspectedAt": created,
            "result": "passed",
            "checks": [
                "square 1:1 1254x1254 PNG",
                "complete frontier-AI compute entity-led scene",
                "exact repository logo composited once in lower-right clear space",
                "no generated readable text, source, attribution, disclaimer, commentary, CTA, tagline, or watermark",
                "not a pure-text card or generic radar visual",
            ],
        },
    },
}
document["packages"] = [item for item in document["packages"] if item.get("id") != PACKAGE_ID]
document["packages"].append(package)
document["runs"].append({
    "id": "run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-produce",
    "mode": "produce", "status": "succeeded", "startedAt": created, "completedAt": stamp(),
    "summary": "Produced one newest fresh frontier-AI pacing package with a complete entity-led square visual and exact-logo composite.",
    "reason": "", "selectedPackageId": PACKAGE_ID,
})
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(PACKAGE_ID)
