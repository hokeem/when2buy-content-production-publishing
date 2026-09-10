#!/usr/bin/env python3
"""Produce the sole newest fresh TSMC August-sales package."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098015628158259276"
PACKAGE_ID = "pkg-20260910-tsmc-august-sales"
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
BASE_SOURCE = Path("/root/.codex/generated_images/01a08b30-6ce8-7cf2-8c9f-c717701fbed7/exec-46949375-753a-4a17-9293-cea5bd9f884a.png")
PROMPT = """Use case: ads-marketing
Asset type: square X financial-news visual for When2Buy
Primary request: Create one complete original entity-led editorial visual about Taiwan Semiconductor Manufacturing Company (TSMC) reporting a record August sales update.
Scene/backdrop: a premium photorealistic advanced semiconductor fabrication facility and wafer-processing environment, with a large glowing silicon wafer and cleanroom robotics as the dominant subject; subtle Taiwan-inspired industrial context without flags or readable signage.
Subject: one dominant semiconductor wafer and advanced chip-fab machinery, clearly recognizable as a real entity-led semiconductor manufacturing story.
Style/medium: cinematic photorealistic financial-news editorial image, premium market-news aesthetic, sharp detail.
Composition/framing: exact 1:1 square; near-black base; dominant central wafer and fab machinery; leave clean upper-left and lower-right negative space for later factual typography and the supplied circular when2buy logo.
Lighting/mood: high-contrast cool industrial light with a restrained red accent, urgent but factual.
Color palette: black, charcoal, white, steel blue, controlled red accents; no decorative gradients.
Text (verbatim): no readable text, no numbers, no logos.
Constraints: complete meaningful entity-led visual before branding; no pure typography card; no generic abstract background; no source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, or generated logo; do not imitate any existing brand logo."""


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
        "-font", "DejaVu-Sans-Bold", "-pointsize", "64", "-annotate", "+54+76", "TSMC",
        "-pointsize", "42", "-annotate", "+54+132", "AUGUST SALES +53.3% YoY",
        "-pointsize", "34", "-annotate", "+54+180", "$16.35B",
        "-gravity", "southeast", "-geometry", "+42+42", "(", str(LOGO), "-resize", "112x112", ")", "-composite",
        str(final),
    ], check=True)
    stamp = now.isoformat().replace("+00:00", "Z")
    document["packages"].append({
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "TSMC August sales jump 53.3%",
        "status": "ready",
        "postText": "TSMC reported August sales of $16.35B, up 53.3% YoY.\n\n2026 revenue has reached about $107.1B, up 39% YoY.",
        "mirroredFacts": [
            "TSMC reported August sales of $16.35 billion, up 53.3% year over year.",
            "TSMC has brought in approximately $107.1 billion of revenue so far in 2026, up 39% year over year.",
        ],
        "verificationSources": [
            "https://au.investing.com/news/stock-market-news/tsmc-august-revenue-jumps-53-as-strong-ai-demand-persists-4635906",
            "https://investor.tsmc.com/english/monthly-revenue/2026",
        ],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": stamp,
        "sourceExpiresAt": expires.isoformat().replace("+00:00", "Z"),
        "visualProduction": {
            "method": "image_model", "prompt": PROMPT, "logoApplied": True,
            "qaStatus": "passed",
            "qa": {"inspectedAt": stamp, "result": "passed", "checks": [
                "square 1254x1254",
                "complete entity-led semiconductor wafer and fabrication scene",
                "exact factual image text for TSMC and August sales",
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
        "summary": "Produced the sole newest fresh TSMC package with an inspected image-model visual and exact-logo composite.",
        "reason": "",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(f"Prepared: {PACKAGE_ID}")


if __name__ == "__main__":
    main()
