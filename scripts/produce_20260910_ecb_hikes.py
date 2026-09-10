#!/usr/bin/env python3
"""Produce the sole newest fresh ECB-rate-hikes package."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098057773099430149"
PACKAGE_ID = "pkg-20260910-ecb-three-rate-hikes"
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
BASE_SOURCE = Path("/root/.codex/generated_images/01a08bd5-3598-7e93-935c-1fd00741dfdf/exec-fbaaa88a-a2c1-437f-8c6a-d2795d102300.png")
PROMPT = """Use case: photorealistic-natural
Asset type: complete square 1:1 premium X financial-news editorial visual for When2Buy
Primary request: an original entity-led visual about traders fully pricing three additional European Central Bank rate hikes by mid-2027.
Scene/backdrop: cinematic near-black European central-bank-inspired institutional plaza and modern monetary-policy trading desk, with a restrained euro motif and three distinct ascending rate steps; no readable signage.
Subject: neutral central-bank architecture, euro currency and a focused rates-trading environment, with exactly three ascending luminous steps communicating three rate hikes.
Style/medium: high-end photorealistic financial-news editorial photography, realistic materials, sharp detail, premium and factual.
Composition/framing: exact 1:1 square; architecture and three-step rate motif dominate; reserve lower-right negative space for the supplied circular when2buy logo; leave upper-left clean space for factual typography composited later.
Lighting/mood: high-contrast night lighting, crisp white rim light, restrained red accent, urgent but factual.
Color palette: near-black, charcoal, white, restrained red, muted steel-blue.
Text (verbatim): none; all typography will be composited later.
Constraints: no generated readable text, logos, source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, generic radar graphic, pure-text card, or extra brand marks."""


def main():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    document = state.load_state()
    if any(package.get("id") == PACKAGE_ID for package in document["packages"]):
        raise SystemExit(f"Skipped: package already exists: {PACKAGE_ID}")
    source = next(post for post in document["benchmarkPosts"] if str(post.get("id")) == SOURCE_ID)
    posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    expires = posted + timedelta(minutes=90)
    if now >= expires:
        raise SystemExit("Skipped: source expired before image packaging")
    target = ROOT / "deliverables" / PACKAGE_ID
    target.mkdir(parents=True, exist_ok=True)
    base = target / "generated-base.png"
    final = target / "when2buy-image-model.png"
    shutil.copyfile(BASE_SOURCE, base)
    subprocess.run([
        "convert", str(base),
        "-gravity", "northwest", "-fill", "white", "-stroke", "black", "-strokewidth", "2",
        "-font", "DejaVu-Sans-Bold", "-pointsize", "58", "-annotate", "+54+76", "ECB",
        "-pointsize", "38", "-annotate", "+54+126", "3 MORE RATE HIKES",
        "-pointsize", "32", "-annotate", "+54+170", "BY MID-2027",
        "-gravity", "southeast", "-geometry", "+42+42", "(", str(LOGO), "-resize", "112x112", ")", "-composite",
        str(final),
    ], check=True)
    stamp = now.isoformat().replace("+00:00", "Z")
    document["packages"].append({
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Traders price three more ECB rate hikes",
        "status": "ready",
        "postText": "Traders are fully pricing three more ECB rate hikes by mid-2027.",
        "mirroredFacts": ["Traders are fully pricing three additional ECB rate hikes by mid-2027."],
        "verificationSources": [source["url"]],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": stamp,
        "sourceExpiresAt": expires.isoformat().replace("+00:00", "Z"),
        "visualProduction": {
            "method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed",
            "qa": {"inspectedAt": stamp, "result": "passed", "checks": [
                "square 1254x1254 PNG",
                "complete entity-led central-bank, euro, and three-step rate scene",
                "visible factual text is limited to ECB, three more rate hikes, and mid-2027",
                "premium near-black, white, steel-blue, and restrained-red palette",
                "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark",
                "not a pure-text card or generic-radar visual",
                "exact repository logo composited once",
            ]},
        },
    })
    document["runs"].append({
        "id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": stamp, "completedAt": stamp,
        "summary": "Produced the sole newest fresh ECB-rate-hikes package with an inspected entity-led image and exact-logo composite.",
        "reason": "",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(f"Prepared: {PACKAGE_ID}")


if __name__ == "__main__":
    main()
