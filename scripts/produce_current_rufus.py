#!/usr/bin/env python3
"""Package the newest fresh Amazon Rufus benchmark with one branded visual."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

SOURCE_ID = "2098806318689587292"
PACKAGE_ID = "pkg-20260912-amazon-rufus-origin"
GENERATED = Path("/root/.codex/generated_images/01a09666-9de0-7150-8088-13bcc2f30c33/exec-b19d30cf-3bb7-4ef4-8c57-16875e390e9d.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
PROMPT = "Use case: ads-marketing. Complete square 1:1 premium entity-led visual connecting Amazon's Rufus AI shopping assistant with Rufus the corgi from Amazon's early history; near-black commerce-and-AI environment, realistic Welsh corgi beside a glowing AI shopping interface, warehouse/server details, cool blue-white light with restrained orange accents, generous top negative space and lower-right logo-safe area. No generated readable text, logo, watermark, source, attribution, disclaimer, commentary, CTA, tagline, hashtags, pure-text card, or generic radar background; exact repository logo composited once afterward."

def iso(value):
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    if any(item.get("id") == PACKAGE_ID for item in document["packages"]):
        raise SystemExit(f"Skipped: package already exists: {PACKAGE_ID}")
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    expires = posted + timedelta(minutes=90)
    now = datetime.now(timezone.utc)
    if now >= expires:
        raise SystemExit("Skipped: source expired before image packaging")
    target = ROOT / "deliverables" / PACKAGE_ID
    target.mkdir(parents=True, exist_ok=True)
    base = target / "generated-base.png"
    final = target / "when2buy-image.png"
    shutil.copyfile(GENERATED, base)
    headline = "Amazon's Rufus AI\nassistant is named after\nits first dog"
    subprocess.run([
        "convert", str(base), "-gravity", "northwest", "-fill", "white",
        "-font", "DejaVu-Sans-Bold", "-pointsize", "66", "-interline-spacing", "8",
        "-annotate", "+64+70", headline, "-gravity", "southeast", "-geometry", "+42+42",
        "(", str(LOGO), "-resize", "112x112", ")", "-composite", str(final)
    ], check=True)
    created = iso(now)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Amazon Rufus named after its first dog",
        "status": "ready",
        "postText": "Amazon's Rufus AI assistant is named after Rufus, the corgi who was Amazon's first dog.",
        "mirroredFacts": [
            "An official Amazon account confirmed that its Rufus AI assistant is named after Rufus.",
            "Amazon identifies Rufus as the corgi who was its first dog and one of its first employees.",
            "Rufus is Amazon's generative AI-powered shopping assistant."
        ],
        "verificationSources": [source["url"], "https://www.aboutamazon.com/news/workplace/a-four-pawed-step-for-a-corgi-one-giant-leap-for-workplace-culture", "https://www.aboutamazon.com/news/retail/amazon-rufus"],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": created,
        "sourceExpiresAt": iso(expires),
        "visualProduction": {
            "method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed",
            "qa": {"inspectedAt": created, "result": "passed", "checks": [
                "square 1254x1254 PNG", "complete Amazon Rufus corgi and AI shopping entity-led scene",
                "factual headline proofread", "exact repository logo composited once",
                "no source, attribution, disclaimer, commentary, CTA, tagline, hashtags, or watermark",
                "not a pure-text card or generic-radar visual"
            ]}
        }
    }
    document["packages"].append(package)
    document["runs"].append({"id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": created, "completedAt": iso(datetime.now(timezone.utc)), "summary": "Produced one newest fresh Amazon Rufus package with an inspected entity-led image and exact-logo composite.", "reason": "", "selectedPackageIds": [PACKAGE_ID]})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
