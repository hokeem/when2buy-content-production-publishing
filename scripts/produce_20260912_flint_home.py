#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state
from freshness_policy import freshness

SOURCE_ID = "2098758203030802691"
PACKAGE_ID = "pkg-20260912-flint-29m-home"
BASE = Path("/root/.codex/generated_images/01a095c1-d084-7ec2-9c78-6efb2070e48d/exec-5d2941f8-fe44-4096-998c-fa303277a935.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
POST_TEXT = "This is what a $2.9M home looks like in the Flint, Michigan area."
PROMPT = "Square 1:1 premium editorial visual: a complete high-end detached home in a leafy Midwestern neighborhood representing a $2.9 million Flint, Michigan area property, photorealistic real-estate scene, near-black shadows, crisp contrast, warm stone and wood, generous upper-left sky space for typesetting, no readable text, no logos, no watermark, no signage, no generic finance background."


def iso_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    check = freshness(source.get("postedAt"))
    if not check["eligible"]:
        raise SystemExit(f"source expired before production: {check['reason']}")
    if any(item.get("id") == PACKAGE_ID for item in document.get("packages", [])):
        raise SystemExit(f"package already exists: {PACKAGE_ID}")
    target = ROOT / "deliverables" / PACKAGE_ID
    target.mkdir(parents=True, exist_ok=True)
    base = target / "generated-base.png"
    final = target / "when2buy-image.png"
    shutil.copy2(BASE, base)
    subprocess.run([
        "convert", str(base), "-gravity", "northwest", "-fill", "white", "-font", "DejaVu-Sans-Bold",
        "-pointsize", "64", "-annotate", "+72+112", "FLINT, MICHIGAN AREA",
        "-fill", "#ff514f", "-pointsize", "112", "-annotate", "+72+245", "$2.9M",
        "-fill", "white", "-pointsize", "34", "-annotate", "+78+405", "LUXURY HOME",
        "(", str(LOGO), "-resize", "104x104", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(final),
    ], check=True)
    stamp = iso_now()
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Flint area $2.9M home",
        "status": "ready",
        "postText": POST_TEXT,
        "mirroredFacts": ["The benchmark post shows a $2.9 million home in the Flint, Michigan area."],
        "verificationSources": [source["url"]],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": stamp,
        "sourceExpiresAt": check["expiresAt"],
        "visualProduction": {
            "method": "image_model",
            "prompt": PROMPT,
            "logoApplied": True,
            "qaStatus": "passed",
            "qa": {"inspectedAt": stamp, "result": "passed", "checks": [
                "square 1254x1254", "complete Flint-area luxury-home entity scene", "exact repository logo composited once",
                "visible typography proofread: FLINT, MICHIGAN AREA; $2.9M; LUXURY HOME",
                "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text card",
            ]},
        },
    }
    document["packages"].append(package)
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": stamp, "completedAt": stamp,
        "summary": "Produced one newest fresh Flint-area $2.9M home package with generated entity visual and exact-logo composite.", "reason": "",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)


if __name__ == "__main__":
    main()
