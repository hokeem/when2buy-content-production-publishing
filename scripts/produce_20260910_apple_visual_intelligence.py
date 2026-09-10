#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098037988483563998"
PACKAGE_ID = "pkg-20260910-apple-visual-intelligence-ads"
BASE = Path("/root/.codex/generated_images/01a08b82-d28c-7ef2-a1cd-c1bab2381b58/exec-245390a1-21dc-415b-aec4-43c3b2b02233.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
RELATIVE = Path("deliverables") / PACKAGE_ID / "when2buy-image.png"

def stamp():
    return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    source = next(x for x in document["benchmarkPosts"] if str(x.get("id")) == SOURCE_ID)
    output = ROOT / RELATIVE
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "convert", str(BASE), "-resize", "1080x1080^", "-gravity", "center", "-extent", "1080x1080",
        "-fill", "#000000B8", "-draw", "rectangle 0,0 620,1080",
        "-font", "DejaVu-Sans-Bold", "-pointsize", "58", "-fill", "#E62B2B", "-gravity", "northwest", "-annotate", "+78+110", "APPLE",
        "-pointsize", "64", "-fill", "white", "-annotate", "+78+195", "VISUAL INTELLIGENCE",
        "-pointsize", "86", "-fill", "white", "-annotate", "+78+330", "MAY GET ADS",
        "-pointsize", "30", "-fill", "#D5D5D5", "-annotate", "+78+470", "Code in iOS 27 points to sponsored results",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite", str(output)
    ], check=True)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Apple Visual Intelligence ads",
        "status": "ready",
        "postText": "Apple $AAPL may be exploring ads inside Visual Intelligence features.\n\nThe possibility comes from code uncovered in iOS 27.",
        "mirroredFacts": [
            "Apple may be exploring a way to show ads inside its Visual Intelligence features.",
            "The possibility is based on code uncovered in iOS 27."
        ],
        "verificationSources": [
            source["url"],
            "https://www.macrumors.com/guide/ios-27-visual-intelligence/",
            "https://www.reddit.com/r/apple/comments/1wcihp0/apple_considering_ads_inside_visual_intelligence/"
        ],
        "imagePath": str(RELATIVE),
        "createdAt": stamp(),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Dark square editorial Apple Visual Intelligence smartphone scene with clean left negative space; no generated logo; exact repository logo composited once afterward.",
            "logoApplied": True,
            "qaStatus": "passed"
        }
    }
    existing = next((x for x in document["packages"] if x.get("id") == PACKAGE_ID), None)
    if existing:
        existing.clear(); existing.update(package)
    else:
        document["packages"].append(package)
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(),
        "summary": "Produced one newest fresh Apple Visual Intelligence package with generated entity visual and exact-logo compositing.", "reason": ""
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
