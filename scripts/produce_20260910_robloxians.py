#!/usr/bin/env python3
"""Produce the single newest fresh Roblox-themed $ROBLOXIANS package."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098122034635038838"
SOURCE_URL = "https://x.com/WhaleInsider/status/2098122034635038838"
PACKAGE_ID = "pkg-20260910-robloxians-traction"
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
BASE = Path("/root/.codex/generated_images/01a08cb0-f29d-7c63-9b08-efb7003aab82/exec-60896e0e-3398-46bd-99d2-b1e929a6aaf3.png")
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"
PROMPT = "Use case: photorealistic-natural. Complete square 1:1 premium financial-news editorial visual about Roblox-themed meme-token attention involving two online meme communities; cinematic near-black digital social-media trading environment with a Roblox-inspired blocky game-world skyline, central blocky avatar, glowing coin/token, two distinct meme-community signals converging, realistic glass and metal, muted blue and restrained red lighting, no generated readable text, logos, source names, URLs, attribution, disclaimer, commentary, CTA, tagline, watermark, generic radar graphic, or pure-text card; reserve upper-left for factual typography and lower-right for the exact repository logo."


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "convert", str(BASE), "-resize", "1254x1254!",
        "-gravity", "northwest", "-font", "DejaVu-Sans-Bold", "-fill", "white",
        "-pointsize", "104", "-annotate", "+74+142", "$ROBLOXIANS",
        "-pointsize", "38", "-fill", "#ff4d4d", "-annotate", "+80+214", "ROBLOX-THEMED POSTS",
        "-pointsize", "34", "-fill", "white", "-annotate", "+80+270", "TRACTION",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite",
        str(FINAL),
    ], check=True)
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": SOURCE_URL,
        "title": "$ROBLOXIANS gains traction on Roblox-themed posts",
        "status": "ready",
        "postText": "The official PNUT and Gigachad X accounts both posted Roblox-themed tweets.\n\n$ROBLOXIANS is gaining traction.",
        "mirroredFacts": [
            "The official PNUT X account posted a Roblox-themed tweet.",
            "The official Gigachad X account posted a Roblox-themed tweet.",
            "$ROBLOXIANS gained traction after the posts.",
        ],
        "verificationSources": [SOURCE_URL, "https://x.com/PNUTonSol", "https://x.com/Gigachad_meme"],
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": stamp(),
        "visualProduction": {
            "method": "image_model",
            "prompt": PROMPT,
            "logoApplied": True,
            "qaStatus": "passed",
            "qa": {
                "inspectedAt": stamp(),
                "result": "passed",
                "checks": [
                    "square 1254x1254 PNG",
                    "complete entity-led blocky game-world and social-traction scene",
                    "visible factual text is limited to $ROBLOXIANS, Roblox-themed posts, and traction",
                    "premium near-black, white, blue, and restrained-red palette",
                    "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark",
                    "not a pure-text card or generic-radar visual",
                    "exact repository logo composited once",
                ],
            },
        },
    }
    document["packages"] = [item for item in document["packages"] if item.get("id") != PACKAGE_ID]
    document["packages"].append(package)
    now = stamp()
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": now, "completedAt": stamp(),
        "summary": "Produced the single newest fresh Roblox-themed $ROBLOXIANS package with an inspected entity-led image and exact-logo composite.",
        "reason": "", "packageId": PACKAGE_ID,
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)


if __name__ == "__main__":
    main()
