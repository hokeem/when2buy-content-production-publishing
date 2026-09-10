"""Persist the newest fresh Oracle earnings package after image QA."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098142649915990353"
PACKAGE_ID = "pkg-20260910-oracle-earnings"
IMAGE_PATH = "deliverables/pkg-20260910-oracle-earnings/when2buy-image-model.png"
PROMPT = """Use case: ads-marketing
Asset type: square X financial-news visual for When2Buy
Primary request: one complete original entity-led editorial visual about Oracle reporting earnings.
Scene/backdrop: premium photorealistic Oracle corporate and cloud-infrastructure environment with illuminated data-center racks and a subtle financial-results display motif.
Subject: Oracle as the dominant subject through an enterprise cloud infrastructure scene; clearly an earnings-report moment, not a generic stock chart.
Style/medium: cinematic photorealistic financial-news editorial image, sharp detail, premium market-news aesthetic.
Composition/framing: exact 1:1 square; central entity-led scene; bold white typography with one controlled red accent; reserve clean lower-right space for later compositing of the supplied circular when2buy logo.
Lighting/mood: high-contrast studio lighting, urgent but factual.
Color palette: near-black, charcoal, white, controlled Oracle-red accent.
Text (verbatim): \"ORACLE JUST REPORTED EARNINGS\" and \"$ORCL\"
Constraints: no other readable words or numbers; no source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, or generated logo; no pure typography card; no generic abstract background; keep the image complete and meaningful before the logo is added."""

def stamp():
    return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    if any(item.get("id") == PACKAGE_ID for item in document["packages"]):
        raise SystemExit(f"Package already exists: {PACKAGE_ID}")
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    now = stamp()
    document["packages"].append({
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Oracle just reported earnings",
        "status": "ready",
        "postText": "$ORCL just reported earnings.",
        "mirroredFacts": ["Oracle reported earnings in a fresh market alert.", "The company trades under the ticker ORCL."],
        "verificationSources": ["https://investor.oracle.com/faq/default.aspx", source["url"]],
        "imagePath": IMAGE_PATH,
        "createdAt": now,
        "sourceExpiresAt": "2026-09-10T21:42:44Z",
        "visualProduction": {
            "method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed",
            "qa": {"inspectedAt": now, "result": "passed", "checks": [
                "square 1254x1254", "complete Oracle cloud-infrastructure entity scene",
                "exact ORACLE JUST REPORTED EARNINGS and $ORCL text",
                "near-black, white, and controlled-red palette",
                "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark",
                "not a pure-text card or generic-radar visual", "exact repository logo composited once",
            ]},
        },
    })
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded",
        "startedAt": now, "completedAt": stamp(),
        "summary": "Produced one newest fresh Oracle earnings package with an inspected entity-led image and exact-logo composite.", "reason": "",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(f"Prepared: {PACKAGE_ID}")

if __name__ == "__main__":
    main()
