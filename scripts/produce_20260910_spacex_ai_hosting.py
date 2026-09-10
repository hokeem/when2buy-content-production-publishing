"""Record the single newest SpaceX AI-hosting package after image QA."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098174494493773975"
PACKAGE_ID = "pkg-20260910-spacex-ai-hosting-111b-month"
RELATIVE_IMAGE = Path("deliverables") / PACKAGE_ID / "when2buy-image-model.png"
PROMPT = ("Complete square 1:1 premium financial-news editorial visual: SpaceX-style heavy-lift rocket "
          "at a night launch complex connected to high-density AI data-center servers, recurring monthly "
          "hosting agreement visual cues, near-black charcoal palette, white highlights, restrained red, "
          "clean upper-left typography space and lower-right logo space; no generated text, logos, handles, "
          "URLs, attribution, disclaimer, CTA, tagline, watermark, generic radar card, or extra brand marks.")

def stamp():
    return datetime.now(timezone.utc).isoformat()

document = state.load_state()
source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": source["url"],
    "title": "SpaceX signs $1.11B-a-month AI hosting agreement",
    "status": "ready",
    "postText": "SpaceX signed an AI hosting agreement worth about $1.11B a month.\n\nThe contract is scheduled to begin December 1.",
    "mirroredFacts": [
        "SpaceX signed an AI hosting agreement worth about $1.11 billion a month.",
        "The contract is scheduled to begin December 1."
    ],
    "verificationSources": [source["url"], "https://ir.spacex.com/updates/"],
    "imagePath": str(RELATIVE_IMAGE),
    "createdAt": stamp(),
    "sourceExpiresAt": "2026-09-10T23:49:16Z",
    "visualProduction": {
        "method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed",
        "qa": {"inspectedAt": stamp(), "result": "passed", "checks": [
            "square 1254x1254 PNG", "complete rocket and AI data-center entity-led scene",
            "visible text matches the factual payload: SpaceX AI hosting, $1.11B/month, December 1",
            "near-black, white, steel-blue, and restrained-red palette",
            "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark",
            "not a pure-text card or generic-radar visual", "exact repository logo composited once"
        ]}
    }
}
existing = next((item for item in document["packages"] if item.get("id") == PACKAGE_ID), None)
if existing:
    existing.clear(); existing.update(package)
else:
    document["packages"].append(package)
document["runs"].append({
    "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
    "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(),
    "summary": "Produced the single newest fresh SpaceX AI-hosting package with inspected entity visual and exact-logo composite.",
    "reason": "", "selectedPackageIds": [PACKAGE_ID]
})
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(PACKAGE_ID)
