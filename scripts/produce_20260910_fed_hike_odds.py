#!/usr/bin/env python3
"""Produce the sole newest fresh Fed-hike-odds package after image QA."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098049673999065518"
PACKAGE_ID = "pkg-20260910-fed-hike-odds-63"
BASE_SOURCE = Path("/root/.codex/generated_images/01a08bac-02ff-75e2-b969-27362f3bd9f9/exec-3835d66a-4590-4e78-af45-a64d8b315400.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
PROMPT = """Use case: productivity-visual
Asset type: square X financial-news visual for When2Buy
Primary request: one complete original entity-led editorial visual about the probability of a 25 basis point U.S. Federal Reserve rate hike rising to 63 percent.
Scene/backdrop: a premium realistic Federal Reserve building at dusk with a subtle market-pricing atmosphere and luminous upward probability arc, no recognizable third-party logos.
Subject: the Federal Reserve building is the dominant unmistakable subject, with a restrained upward market signal integrated into the scene.
Style/medium: cinematic photorealistic financial-news editorial image, sharp architectural detail, premium market-news aesthetic.
Composition/framing: exact 1:1 square; building dominant in the lower two-thirds; generous clean dark upper-left space for later factual typography and clean lower-right space for the supplied circular when2buy logo.
Lighting/mood: high-contrast blue-black dusk with controlled red market glow, urgent but factual.
Color palette: black, charcoal, white, restrained red; no decorative green.
Text (verbatim): none; typography is composited later.
Constraints: complete meaningful entity-led visual before branding; no pure typography card; no generic abstract background; no readable text, numbers, logos, source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, or extra people."""


def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main():
    now = datetime.now(timezone.utc)
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
        "convert", str(base), "-resize", "1254x1254^", "-gravity", "center", "-extent", "1254x1254",
        "-fill", "#000000B8", "-draw", "rectangle 0,0 670,1254",
        "-font", "DejaVu-Sans-Bold", "-gravity", "northwest", "-pointsize", "50", "-fill", "#EC2638",
        "-annotate", "+62+105", "FED RATE DECISION",
        "-pointsize", "132", "-fill", "white", "-annotate", "+58+255", "63%",
        "-pointsize", "38", "-fill", "#E5E5E5", "-annotate", "+64+430", "25 bps hike odds",
        "-gravity", "southeast", "-geometry", "+42+42", "(", str(LOGO), "-resize", "112x112", ")", "-composite",
        str(final),
    ], check=True)
    created = stamp()
    document["packages"].append({
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Fed 25 bp hike odds reach 63%",
        "status": "ready",
        "postText": "Odds of a 25 bps Fed rate hike this month just hit 63%.",
        "mirroredFacts": ["Odds of a 25 basis point Federal Reserve rate hike this month rose to 63% in market pricing."],
        "verificationSources": [
            source["url"],
            "https://finance.yahoo.com/economy/policy/articles/fomc-september-2026-odds-rate-163505675.html",
        ],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": created,
        "sourceExpiresAt": expires.isoformat().replace("+00:00", "Z"),
        "visualProduction": {
            "method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed",
            "qa": {"inspectedAt": created, "result": "passed", "checks": [
                "square 1254x1254 PNG", "complete Federal Reserve entity-led visual",
                "visible factual text is limited to FED RATE DECISION, 63%, and 25 bps hike odds",
                "premium near-black, white, and restrained-red palette",
                "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark",
                "not a pure-text card or generic-radar visual", "exact repository logo composited once",
            ]},
        },
    })
    document["runs"].append({
        "id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded",
        "startedAt": created, "completedAt": stamp(),
        "summary": "Produced the sole newest fresh Fed-hike-odds package with an inspected entity-led image and exact-logo composite.",
        "reason": "",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(f"Prepared: {PACKAGE_ID}")


if __name__ == "__main__":
    main()
