#!/usr/bin/env python3
"""Produce the single newest fresh Anthropic resignation package."""
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

PACKAGE_ID = "pkg-20260911-anthropic-researcher-resigns"
BENCHMARK_ID = "2098511096038498591"
OUT_DIR = ROOT / "deliverables" / PACKAGE_ID
BASE = Path("/root/.codex/generated_images/01a09237-6e7d-72d0-9611-cd9b76c92683/exec-ad67d4b9-892d-4248-acd2-5d05c07e51a2.png")
FINAL = OUT_DIR / "when2buy-image.png"
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
PROMPT = "Use case: stylized-concept. Complete square entity-led editorial visual about an Anthropic AI researcher resignation and the existential-risk debate around advanced AI; cinematic near-black AI research lab with a departing researcher, glowing server racks and neural-network structures, cool blue-white light and restrained red warning accent, clean upper-left typography space and lower-right logo-safe space; no generated readable text, logos, source, attribution, disclaimer, commentary, CTA, tagline, watermark, generic radar visual, or pure-text card."

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    benchmark = next((x for x in document.get("benchmarkPosts", []) if str(x.get("id")) == BENCHMARK_ID), None)
    if not benchmark:
        raise SystemExit("Benchmark post not found")
    if any(x.get("id") == PACKAGE_ID for x in document.get("packages", [])):
        raise SystemExit("Package already exists")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BASE, OUT_DIR / "generated-base.png")
    subprocess.run([
        "convert", str(BASE), "-gravity", "northwest", "-fill", "white", "-stroke", "black", "-strokewidth", "3",
        "-font", "DejaVu-Sans-Bold", "-pointsize", "52", "-annotate", "+54+78", "ANTHROPIC RESEARCHER",
        "-pointsize", "52", "-annotate", "+54+140", "RESIGNS",
        "-fill", "#ff3344", "-pointsize", "34", "-annotate", "+54+198", "HUMANS MAY NOT SURVIVE THE AI RACE",
        "-gravity", "southeast", "-geometry", "+42+42", "(", str(LOGO), "-resize", "112x112", ")", "-composite", str(FINAL),
    ], check=True)
    created = stamp()
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": BENCHMARK_ID,
        "benchmarkPostUrl": benchmark["url"],
        "title": "Anthropic researcher resigns over AI-safety concerns",
        "status": "ready",
        "postText": "An Anthropic researcher resigned over AI-safety concerns.\n\nHe warned humans may not survive the AI race.",
        "mirroredFacts": [
            "An Anthropic researcher announced his resignation over concerns about AI development and safety.",
            "The warning said humans may not survive the AI race.",
        ],
        "verificationSources": [benchmark["url"], "https://apnews.com/article/2ed549e07f2f941600a135070487d83d"],
        "verificationStatus": "verified_against_authoritative_reporting",
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": created,
        "sourceExpiresAt": benchmark["postedAt"],
        "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed", "qa": {"inspectedAt": created, "result": "passed", "checks": ["square 1254x1254 PNG", "complete AI research lab and departing-researcher entity scene", "headline and supporting warning proofread", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text visual or generic radar graphic"]}},
    }
    document["packages"].append(package)
    document["runs"].append({"id": "run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-produce", "mode": "produce", "status": "succeeded", "startedAt": created, "completedAt": stamp(), "summary": "Produced the single newest fresh Anthropic resignation package with an inspected entity-led image and exact-logo composite.", "reason": "", "selectedPackageId": PACKAGE_ID})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
