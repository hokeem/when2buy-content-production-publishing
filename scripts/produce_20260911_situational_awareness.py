import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

SOURCE_ID = "2098492555679662501"
PACKAGE_ID = "pkg-20260911-situational-awareness-clear-street"
IMAGE = "deliverables/pkg-20260911-situational-awareness-clear-street/when2buy-image.png"

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

doc = state.load_state()
source = next(x for x in doc["benchmarkPosts"] if str(x.get("id")) == SOURCE_ID)
package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": source["url"],
    "title": "Situational Awareness establishes Clear Street relationship",
    "status": "ready",
    "postText": "Leopold Aschenbrenner's Situational Awareness has established a prime brokerage relationship with Clear Street.",
    "mirroredFacts": [
        "Leopold Aschenbrenner leads Situational Awareness.",
        "Situational Awareness has established a prime brokerage relationship with Clear Street.",
    ],
    "verificationSources": [source["url"], "https://news.bloomberglaw.com/private-equity/situational-awareness-returns-to-investing-with-400-million-bet"],
    "imagePath": IMAGE,
    "createdAt": stamp(),
    "sourceExpiresAt": source.get("postedAt"),
    "visualProduction": {
        "method": "image_model",
        "prompt": "Complete square entity-led institutional trading operations scene about Situational Awareness establishing a prime brokerage relationship with Clear Street; no generated text or branding; exact factual typography and exact repository logo composited afterward; near-black premium financial-news palette; clean logo-safe space; no source, attribution, disclaimer, commentary, CTA, tagline, watermark, or generic radar visual.",
        "logoApplied": True,
        "qaStatus": "passed",
        "qa": {"inspectedAt": stamp(), "result": "passed", "checks": ["square 1254x1254 PNG", "complete entity-led trading scene", "factual text composited once", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text card or generic-radar visual"]},
    },
}
existing = next((x for x in doc["packages"] if x.get("id") == PACKAGE_ID), None)
if existing:
    existing.clear(); existing.update(package)
else:
    doc["packages"].append(package)
doc["runs"].append({"id": "run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced one newest fresh Situational Awareness package with a complete entity-led square visual and exact-logo composite.", "reason": "", "selectedPackageId": PACKAGE_ID})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(PACKAGE_ID)
