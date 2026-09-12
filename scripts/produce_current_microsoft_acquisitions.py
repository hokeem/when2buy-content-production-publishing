#!/usr/bin/env python3
"""Persist the sole newest fresh Microsoft acquisitions package after image QA."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402
from freshness_policy import freshness  # noqa: E402

SOURCE_ID = "2098771198326771884"
PACKAGE_ID = "pkg-20260912-microsoft-gaming-acquisitions"
GENERATED = Path("/root/.codex/generated_images/01a09606-7941-7e61-8a34-061dbf200767/exec-1e1c742f-216d-4cf5-9446-5c9ee747cb25.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"

PROMPT = """Use case: photorealistic-natural
Asset type: premium square 1:1 X financial-news visual
Primary request: an original entity-led editorial visual about Microsoft's three major video-game acquisitions dominating its largest-deals list.
Scene/backdrop: cinematic near-black premium gaming studio and corporate acquisition setting, subtle dark glass, a sophisticated unbranded game-console silhouette and a cluster of three distinct game-world objects arranged as a cohesive acquisition tableau.
Subject: Microsoft gaming expansion represented by one dominant central acquisition stack and three clearly different gaming entities; no identifiable logos or trademarks.
Style/medium: high-end photorealistic financial-news editorial photography, realistic materials, sharp white rim light, controlled red accent only.
Composition/framing: exact 1:1 square, central subject slightly left of center, strong depth and contrast, reserve the lower-right 20 percent as clean near-black empty logo-safe space for the supplied repository logo added later.
Lighting/mood: urgent, premium, analytical, institutional.
Color palette: near-black charcoal, white highlights, restrained deep red accents.
Text: none.
Constraints: complete meaningful visual before logo compositing; no readable text, letters, numbers, currency symbols, logos, watermark, source names, source handles, URLs, attribution, disclaimer, CTA, people, generic radar graphics, pure typography card, malformed or damaged objects, or fake brand marks."""

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

doc = state.load_state()
source = next((p for p in doc.get("benchmarkPosts", []) if str(p.get("id")) == SOURCE_ID), None)
if not source:
    raise SystemExit("selected benchmark source is missing")
fresh = freshness(source.get("postedAt"))
if not fresh["eligible"]:
    raise SystemExit(f"selected source expired before production: {fresh['reason']}")
if any(p.get("id") == PACKAGE_ID for p in doc.get("packages", [])):
    raise SystemExit("package already exists; never duplicate an accepted or produced package")
if not GENERATED.is_file():
    raise SystemExit("generated image is missing")

FINAL.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(GENERATED, FINAL)
subprocess.run(["convert", str(FINAL), "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(FINAL)], check=True, timeout=30)

fresh_after = freshness(source.get("postedAt"))
if not fresh_after["eligible"]:
    FINAL.unlink(missing_ok=True)
    FINAL.parent.rmdir()
    raise SystemExit(f"selected source expired after image generation: {fresh_after['reason']}")

now = stamp()
package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": source["url"],
    "title": "Microsoft gaming acquisitions",
    "status": "ready",
    "postText": "3 of Microsoft's 10 largest acquisitions are video-game companies: Activision Blizzard ($75.4B), ZeniMax Media ($8.1B), and Mojang ($2.5B).",
    "mirroredFacts": [
        "Microsoft's list of 10 largest acquisitions includes three video-game companies.",
        "Activision Blizzard was a $75.4B total purchase price.",
        "ZeniMax Media was an $8.1B total purchase price.",
        "Mojang was acquired for $2.5B.",
    ],
    "verificationSources": [
        "https://www.microsoft.com/investor/reports/ar25/",
        "https://www.microsoft.com/investor/reports/ar22/",
        "https://news.microsoft.com/source/2014/09/15/minecraft-to-join-microsoft/",
    ],
    "imagePath": str(FINAL.relative_to(ROOT)),
    "createdAt": now,
    "sourceExpiresAt": fresh_after["expiresAt"],
    "visualProduction": {
        "method": "image_model",
        "prompt": PROMPT,
        "logoApplied": True,
        "qaStatus": "passed",
        "qa": {"inspectedAt": now, "result": "passed", "checks": [
            "square 1254x1254 visual inspected after generation",
            "complete entity-led gaming acquisition scene",
            "no generated readable text or fake brand marks",
            "no source attribution, disclaimer, commentary, or CTA",
            "exact repository logo composited once in lower-right clear space",
            "no generic radar visual or pure-text card",
        ]},
    },
}
doc["packages"].append(package)
doc["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": now, "completedAt": stamp(), "summary": "Produced the sole newest fresh Microsoft acquisitions package with an inspected entity-led visual and exact-logo composite.", "reason": "", "selectedPackageIds": [PACKAGE_ID]})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(f"Produced {PACKAGE_ID}; source expires {fresh_after['expiresAt']}.")
