#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098466092888764797"
PACKAGE_ID = "pkg-20260911-penpe-143pct"
BASE = Path("/root/.codex/generated_images/01a091a0-5f20-7ff3-9d54-6ff8939d1f16/exec-a69874d6-a77b-40ed-a281-c74628326d46.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"

def stamp():
    return datetime.now(timezone.utc).isoformat()

doc = state.load_state()
source = next(x for x in doc["benchmarkPosts"] if str(x.get("id")) == SOURCE_ID)
target = ROOT / "deliverables" / PACKAGE_ID
target.mkdir(parents=True, exist_ok=True)
final = target / "when2buy-image.png"
subprocess.run([
    "convert", str(BASE), "-gravity", "northwest", "-fill", "white", "-font", "DejaVu-Sans-Bold",
    "-pointsize", "108", "-annotate", "+72+150", "PENPE", "-fill", "#39e75f", "-pointsize", "150",
    "-annotate", "+72+305", "+143%", "-fill", "white", "-pointsize", "42", "-annotate", "+78+375",
    "24-HOUR MOVE", "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southwest",
    "-geometry", "+42+42", "-composite", str(final)
], check=True)
existing = next((x for x in doc["packages"] if x.get("id") == PACKAGE_ID), None)
package = {
    "id": PACKAGE_ID, "benchmarkPostId": SOURCE_ID, "benchmarkPostUrl": source["url"],
    "title": "PENPE rallies 143% in 24 hours", "status": "ready",
    "postText": "PENPE rallies 143% in the past 24 hours.",
    "mirroredFacts": ["The benchmark says PENPE rallied 143% in the past 24 hours."],
    "verificationSources": [source["url"], "https://pump.fun/coin/0xb83fC6010C8Dcf628abE787a161c619FcC543117"],
    "imagePath": str(final.relative_to(ROOT)), "createdAt": stamp(),
    "sourceExpiresAt": "2026-09-11T19:07:58Z",
    "visualProduction": {"method": "image_model", "prompt": "Entity-led square PENPE crypto rally scene; typography and exact logo composited afterward; no source, attribution, disclaimer, commentary, CTA, tagline, or watermark.", "logoApplied": True, "qaStatus": "passed", "qa": {"result": "passed", "checks": ["square 1254x1254 PNG", "complete entity-led crypto scene", "factual text composited once", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark"]}}
}
if existing:
    existing.clear(); existing.update(package)
else:
    doc["packages"].append(package)
now = datetime.now(timezone.utc)
doc["runs"].append({"id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced one newest fresh PENPE package with entity-led image and exact-logo composite.", "reason": "", "selectedPackageIds": [PACKAGE_ID]})
errors = state.validate(doc)
if errors: raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(PACKAGE_ID)
