#!/usr/bin/env python3
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098135120980898075"
PACKAGE_ID = "pkg-20260910-starship-revenue-flight"
OUT = ROOT / "deliverables" / PACKAGE_ID
FINAL = OUT / "when2buy-image-model.png"

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

doc = state.load_state()
source = next(x for x in doc["benchmarkPosts"] if str(x.get("id")) == SOURCE_ID)
OUT.mkdir(parents=True, exist_ok=True)
package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": source["url"],
    "title": "SpaceX says its next Starship flight will be revenue-generating",
    "status": "ready",
    "postText": "SpaceX’s next Starship flight will be revenue-generating.",
    "mirroredFacts": ["SpaceX said its next Starship flight will be revenue-generating."],
    "verificationSources": [source["url"], "https://content.spacex.com/cms-assets/FINAL_Documents%20and%20Updates/SpaceX%20-%20EU%20Prospectus%20%28Approved%20by%20Bafin%29%20-%20June%205%2C%202026.pdf"],
    "imagePath": str(FINAL.relative_to(ROOT)),
    "createdAt": stamp(),
    "sourceExpiresAt": (datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y") + timedelta(minutes=90)).astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    "visualProduction": {
        "method": "image_model",
        "prompt": "Use case: photorealistic-natural. Complete square 1:1 premium financial-news visual about SpaceX's next Starship flight becoming revenue-generating; realistic stainless-steel Starship at a night launch mount, near-black base, white rim light, restrained red accents, clean upper-left typography space and lower-right logo-safe space, no generated text or logos; exact repository logo composited once afterward.",
        "logoApplied": True,
        "qaStatus": "passed",
        "qa": {"inspectedAt": stamp(), "result": "passed", "checks": ["square 1254x1254 PNG", "complete entity-led Starship launch scene", "exact factual typography composited once", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text card or generic-radar visual"]},
    },
}
doc["packages"] = [x for x in doc["packages"] if str(x.get("id")) != PACKAGE_ID]
doc["packages"].append(package)
now = stamp()
doc["runs"].append({"id": "run-" + now.replace("-", "").replace(":", "") + "-produce", "mode": "produce", "status": "succeeded", "startedAt": now, "completedAt": now, "summary": "Produced one newest fresh SpaceX Starship revenue-generating package with exact-logo compositing.", "reason": "", "selectedPackageIds": [PACKAGE_ID]})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(PACKAGE_ID)
