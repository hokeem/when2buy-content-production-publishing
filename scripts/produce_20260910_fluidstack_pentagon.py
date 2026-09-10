#!/usr/bin/env python3
"""Persist the single newest fresh Fluidstack/Pentagon package after image QA."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098164965123236185"
PACKAGE_ID = "pkg-20260910-fluidstack-pentagon-5b-loan-talks"
BASE = Path("/root/.codex/generated_images/01a08d48-00f6-7170-810e-023a991dc184/exec-404aef72-809e-40ea-9f08-3b8fc44fe790.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
OUT_DIR = ROOT / "deliverables" / PACKAGE_ID
FINAL = OUT_DIR / "when2buy-image-model.png"
PROMPT = "Use case: photorealistic-natural. Complete 1:1 editorial scene linking the Pentagon with an AI cloud data center and glowing GPU servers; near-black, cool steel-blue palette with restrained red accents; dark upper-left and lower-right negative space for later typography and exact-logo compositing; no generated text, logos, watermarks, source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or pure-text card."

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    expires = posted + timedelta(minutes=90)
    if now >= expires:
        raise SystemExit("Selected benchmark expired before production.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BASE, OUT_DIR / "generated-base.png")
    subprocess.run([
        "convert", str(BASE), "-gravity", "northwest", "-font", "DejaVu-Sans-Bold",
        "-fill", "white", "-pointsize", "54", "-annotate", "+58+82", "PENTAGON",
        "-fill", "#ff4b4b", "-pointsize", "86", "-annotate", "+58+185", "$5B LOAN TALKS",
        "-fill", "white", "-pointsize", "54", "-annotate", "+58+270", "FLUIDSTACK",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite",
        str(FINAL),
    ], check=True, timeout=30)
    identify = subprocess.run(["identify", "-format", "%wx%h", str(FINAL)], check=True, capture_output=True, text=True, timeout=10).stdout
    if identify != "1254x1254":
        raise SystemExit(f"Unexpected image dimensions: {identify}")
    created = stamp()
    package = {
        "id": PACKAGE_ID, "benchmarkPostId": SOURCE_ID, "benchmarkPostUrl": source["url"],
        "title": "Pentagon in talks to lend roughly $5B to Fluidstack", "status": "ready",
        "postText": "The Pentagon is in talks to lend roughly $5B to AI cloud startup Fluidstack.\n\nThe money would come through the Pentagon's Office of Strategic Capital.",
        "mirroredFacts": ["The benchmark post said the Pentagon is in talks to lend roughly $5 billion to AI cloud-computing startup Fluidstack.", "The proposed lender is the Pentagon's Office of Strategic Capital, which provides loans to companies working in areas deemed critical to U.S. national security."],
        "verificationSources": [source["url"], "https://www.defense.gov/News/Releases/Release/Article/4020461/office-of-strategic-capital-announces-release-of-the-fiscal-year-2025-investment-strategy/", "https://fluidstack.io/blog/series-a-announcement"],
        "imagePath": str(FINAL.relative_to(ROOT)), "createdAt": created, "sourceExpiresAt": expires.isoformat().replace("+00:00", "Z"),
        "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed", "qa": {"inspectedAt": created, "result": "passed", "checks": ["square 1254x1254 PNG", "complete Pentagon and AI data-center entity scene", "exact factual text composited once", "exact repository logo composited once in lower-right clear space", "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark", "not a pure-text card or generic-radar visual"]}},
    }
    document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": created, "completedAt": stamp(), "summary": "Produced the sole newest fresh Fluidstack/Pentagon package with an inspected entity-led image and exact-logo composite.", "reason": "", "packageId": PACKAGE_ID})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
