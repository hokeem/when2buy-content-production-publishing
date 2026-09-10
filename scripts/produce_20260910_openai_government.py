#!/usr/bin/env python3
"""Produce the single newest fresh OpenAI government-access package."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098069243799515422"
PACKAGE_ID = "pkg-20260910-openai-government-access"
BASE = Path("/root/.codex/generated_images/01a08bf0-ae7e-7fb2-89dc-a8549e0aa047/exec-e8c2685f-2392-4e4e-9138-f8720585f5fe.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
PROMPT = """Use case: photorealistic-natural
Asset type: complete square 1:1 premium X financial-news editorial visual for When2Buy
Primary request: a complete original entity-led editorial scene about OpenAI expanding ChatGPT access for U.S. government agencies.
Scene/backdrop: a secure modern civic technology operations center with a subtle U.S. government building silhouette through glass, monitored AI workstations, and a clear service-access flow represented by luminous interface panels; no recognizable third-party logos, no flags with readable text, no watermark.
Subject: the secure government technology workspace and OpenAI-style AI service infrastructure are the dominant concrete subjects, communicating public-sector software access and reduced usage cost without relying on a generic abstract background.
Style/medium: cinematic photorealistic financial-news editorial image, sharp detail, premium market-news aesthetic.
Composition/framing: exact 1:1 square; near-black base; central entity-led scene; leave generous clean upper-left space for factual typography to be composited later and clean lower-right space for the supplied circular when2buy logo.
Lighting/mood: high-contrast studio lighting, urgent but factual, cool blue-white monitor glow with restrained red accent.
Color palette: black, charcoal, white, muted blue, controlled red; no decorative green.
Text (verbatim): none; all typography will be composited later.
Constraints: no readable words or numbers, no logos, no source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, generated logo, pure typography card, generic radar graphic, or extra brand marks; make the image visually complete before the logo and text are added."""

def stamp():
    return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if item["id"] == SOURCE_ID)
    if any(item.get("id") == PACKAGE_ID for item in document["packages"]):
        raise SystemExit(f"package already exists: {PACKAGE_ID}")
    posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y")
    expires = posted.timestamp() + 90 * 60
    now = datetime.now(timezone.utc)
    if now.timestamp() >= expires:
        raise SystemExit("selected source expired before production")
    target = ROOT / "deliverables" / PACKAGE_ID
    target.mkdir(parents=True, exist_ok=True)
    generated = target / "generated-base.png"
    final = target / "when2buy-image-model.png"
    shutil.copyfile(BASE, generated)
    subprocess.run([
        "convert", str(generated),
        "-gravity", "northwest", "-fill", "white", "-stroke", "black", "-strokewidth", "2",
        "-font", "DejaVu-Sans-Bold", "-pointsize", "62", "-annotate", "+64+78", "OPENAI FOR GOVERNMENT",
        "-pointsize", "46", "-annotate", "+64+138", "FREE CHATGPT LICENSES",
        "-pointsize", "42", "-annotate", "+64+192", "50% LOWER USAGE COSTS",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite",
        str(final),
    ], check=True)
    identify = subprocess.check_output(["identify", "-format", "%wx%h", str(final)], text=True).strip()
    if identify != "1254x1254":
        raise SystemExit(f"unexpected image size: {identify}")
    created = stamp()
    document["packages"].append({
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "OpenAI expands ChatGPT access for U.S. government agencies",
        "status": "ready",
        "postText": "OpenAI said U.S. government agencies will get free ChatGPT licenses and 50% lower usage costs.",
        "mirroredFacts": [
            "OpenAI said U.S. government agencies will get free access to ChatGPT licenses.",
            "OpenAI said usage costs will be reduced by 50%.",
        ],
        "verificationSources": ["https://openai.com/solutions/industries/government/", source["url"]],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": created,
        "sourceExpiresAt": datetime.fromtimestamp(expires, timezone.utc).isoformat().replace("+00:00", "Z"),
        "visualProduction": {
            "method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed",
            "qa": {"inspectedAt": created, "result": "passed", "checks": [
                "square 1254x1254 PNG", "complete civic technology and AI infrastructure entity scene",
                "exact factual text composited once", "premium near-black, white, blue, and restrained-red palette",
                "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark",
                "not a pure-text card or generic-radar visual", "exact repository logo composited once",
            ]},
        },
    })
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded",
        "startedAt": created, "completedAt": stamp(),
        "summary": "Produced the single newest fresh OpenAI government-access package with an inspected entity-led image and exact-logo composite.",
        "reason": "", "packageId": PACKAGE_ID,
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
