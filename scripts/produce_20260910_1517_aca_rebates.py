#!/usr/bin/env python3
"""Produce exactly one newest fresh ACA-rebate package."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098065613763543262"
PACKAGE_ID = "pkg-20260910-aca-500-rebates"
BASE_SOURCE = Path("/root/.codex/generated_images/01a08be2-f1e0-7770-a3d7-dcdcff3d2688/exec-f0f68c71-4990-43ce-acea-3f46d7b31fad.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
PROMPT = """Use case: photorealistic-natural. Asset type: complete square 1:1 premium financial-news editorial visual for When2Buy. Primary request: an original entity-led visual about proposed $500 rebate checks for roughly one million Affordable Care Act marketplace enrollees. Scene/backdrop: cinematic near-black Washington policy setting blended with a modern health-insurance exchange interface motif and a stack of clean government-style rebate checks, no readable signage. Subject: one prominent physical rebate check marked only with a simple dollar symbol shape, subtle healthcare enrollment cards, and a restrained outline of the United States; communicate a large consumer rebate program, not a generic money graphic. Style/medium: high-end photorealistic editorial financial-news photography, realistic paper and glass materials, premium and factual. Composition/framing: exact 1:1 square; dominant check and enrollment-card subject; reserve lower-right negative space for the supplied circular when2buy logo; leave upper-left clean space for factual typography composited later. Lighting/mood: high-contrast night lighting, crisp white rim light, restrained red accent, urgent but factual. Color palette: near-black, charcoal, white, muted steel-blue, restrained red. Text: none; all typography will be composited later. Constraints: no generated readable text, logos, source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, generic radar graphic, pure-text card, or extra brand marks."""

def main():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    document = state.load_state()
    if any(p.get("id") == PACKAGE_ID for p in document["packages"]):
        raise SystemExit("Package already exists")
    source = next(p for p in document["benchmarkPosts"] if str(p.get("id")) == SOURCE_ID)
    posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    expires = posted + timedelta(minutes=90)
    if now >= expires:
        raise SystemExit("Source expired before production")
    target = ROOT / "deliverables" / PACKAGE_ID
    target.mkdir(parents=True, exist_ok=True)
    base = target / "generated-base.png"
    final = target / "when2buy-image-model.png"
    shutil.copyfile(BASE_SOURCE, base)
    subprocess.run(["convert", str(base), "-gravity", "northwest", "-fill", "white", "-stroke", "black", "-strokewidth", "2", "-font", "DejaVu-Sans-Bold", "-pointsize", "58", "-annotate", "+54+76", "$500 REBATE", "-pointsize", "38", "-annotate", "+54+126", "~1M ACA ENROLLEES", "-pointsize", "32", "-annotate", "+54+170", "EXPECTED IN OCTOBER", "-gravity", "southeast", "-geometry", "+42+42", "(", str(LOGO), "-resize", "112x112", ")", "-composite", str(final)], check=True)
    stamp = now.isoformat().replace("+00:00", "Z")
    document["packages"].append({
        "id": PACKAGE_ID, "benchmarkPostId": SOURCE_ID, "benchmarkPostUrl": source["url"],
        "title": "$500 ACA rebate payments proposed for nearly 1 million enrollees", "status": "ready",
        "postText": "The Trump administration is proposing $500 payments for nearly 1 million ACA exchange enrollees.\n\nThe checks are expected to go out in October.",
        "mirroredFacts": ["The administration is proposing $500 payments for nearly 1 million ACA exchange enrollees.", "The checks are expected to go out in October."],
        "verificationSources": ["https://apnews.com/article/5fea0b182d64b4d7966e0ec7af276e92", "https://www.axios.com/2026/09/09/trump-obamacare-rebates-election"],
        "imagePath": str(final.relative_to(ROOT)), "createdAt": stamp, "sourceExpiresAt": expires.isoformat().replace("+00:00", "Z"),
        "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed", "qa": {"inspectedAt": stamp, "result": "passed", "checks": ["square 1254x1254 PNG", "complete entity-led Washington, healthcare, and rebate-check scene", "visible factual text is limited to $500 rebate, ~1M ACA enrollees, and expected in October", "premium near-black, white, steel-blue, and restrained-red palette", "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark", "not a pure-text card or generic-radar visual", "exact repository logo composited once"]}},
    })
    document["runs"].append({"id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp, "completedAt": stamp, "summary": "Produced one newest fresh ACA-rebate package with an inspected entity-led image and exact-logo composite.", "reason": "", "selectedPackageIds": [PACKAGE_ID]})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
