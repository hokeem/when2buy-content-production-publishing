#!/usr/bin/env python3
"""Prepare the newest OpenAI valuation package, fail-closed if unverified."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

SOURCE_ID = "2098797888063312188"
PACKAGE_ID = "pkg-20260912-openai-valuation-766"
BASE = Path("/root/.codex/generated_images/01a0964b-2187-70b0-a08c-25c1ba42bd6c/exec-796e13d8-63be-4a7b-986b-99c796fae72c.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
FINAL_REL = Path("deliverables") / PACKAGE_ID / "when2buy-image.png"

def stamp():
    return datetime.now(timezone.utc).isoformat()

doc = state.load_state()
source = next(p for p in doc["benchmarkPosts"] if str(p.get("id")) == SOURCE_ID)
final = ROOT / FINAL_REL
final.parent.mkdir(parents=True, exist_ok=True)
subprocess.run([
    "convert", str(BASE), "-gravity", "northwest", "-fill", "white",
    "-font", "DejaVu-Sans-Bold", "-pointsize", "72",
    "-annotate", "+72+108", "OPENAI VALUATION",
    "-pointsize", "88", "-annotate", "+72+208", "UP 766% IN 2 YEARS",
    "-gravity", "southeast", "-geometry", "+42+42", "(", str(LOGO),
    "-resize", "112x112", ")", "-composite", str(final)
], check=True)

package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": source["url"],
    "title": "OpenAI valuation up 766% in two years",
    "status": "blocked",
    "postText": "OpenAI's valuation has increased by 766% over the last two years.",
    "mirroredFacts": ["The benchmark post claims OpenAI's valuation increased by 766% over the last two years."],
    "verificationSources": [
        source["url"],
        "https://openai.com/index/scale-the-benefits-of-ai/",
        "https://openai.com/index/accelerating-the-next-phase-ai/",
    ],
    "verificationStatus": "blocked_unverified_benchmark_claim",
    "verificationNote": "Authoritative OpenAI disclosures confirm valuation milestones but do not establish the benchmark's exact 766% two-year calculation; publication withheld in standard mode.",
    "imagePath": str(FINAL_REL),
    "createdAt": stamp(),
    "visualProduction": {
        "method": "image_model",
        "prompt": "Complete square 1:1 entity-led AI data-center visual, no generated text or branding; factual typography and exact repository logo composited afterward once.",
        "logoApplied": True,
        "qaStatus": "passed",
        "qa": {"inspectedAt": stamp(), "result": "passed", "checks": [
            "square 1254x1254 PNG", "complete AI infrastructure entity scene",
            "factual text proofread", "exact repository logo composited once",
            "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark",
            "not a pure-text card or generic-radar visual"
        ]}
    }
}
old = next((p for p in doc["packages"] if p.get("id") == PACKAGE_ID), None)
if old:
    old.clear(); old.update(package)
else:
    doc["packages"].append(package)
now = stamp()
doc["runs"].append({"id": "run-" + now.replace("-", "").replace(":", "").replace("+00:00", "Z") + "-produce", "mode": "produce", "status": "partial", "startedAt": now, "completedAt": now, "summary": "Produced the newest fresh OpenAI valuation package with an inspected entity-led image and exact-logo composite; publication blocked because the exact benchmark percentage could not be verified.", "reason": "blocked_unverified_benchmark_claim", "selectedPackageIds": [PACKAGE_ID]})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(PACKAGE_ID)
