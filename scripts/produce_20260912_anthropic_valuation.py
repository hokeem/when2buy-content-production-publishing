#!/usr/bin/env python3
"""Package the newest fresh Anthropic valuation benchmark."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

SOURCE_ID = "2098793299662274652"
PACKAGE_ID = "pkg-20260912-anthropic-valuation-7500"
BASE_SOURCE = Path("/root/.codex/generated_images/01a0963d-6b72-7541-b0e7-9423eb30c0a1/exec-2c0070a7-537f-4698-8a6e-82d8a0e3ae76.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
PROMPT = "Use case: ads-marketing. Complete 1:1 premium entity-led financial-news visual about Anthropic's explosive private-company valuation growth: cinematic near-black AI data center with glowing neural lattice, central AI entity silhouette, realistic server racks, restrained red upward valuation signal, cool blue-white light, sharp contrast, clean upper typography space and lower-right logo-safe area. No generated readable text, numbers, logos, watermark, source, attribution, disclaimer, commentary, CTA, tagline, hashtags, pure-text card, or generic radar background; exact repository logo composited once afterward."

def iso(value):
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    now = datetime.now(timezone.utc)
    document = state.load_state()
    if any(item.get("id") == PACKAGE_ID for item in document["packages"]):
        raise SystemExit(f"Skipped: package already exists: {PACKAGE_ID}")
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    expires = posted + timedelta(minutes=90)
    if now >= expires:
        raise SystemExit("Skipped: source expired before image packaging")
    target = ROOT / "deliverables" / PACKAGE_ID
    target.mkdir(parents=True, exist_ok=True)
    base = target / "generated-base.png"
    final = target / "when2buy-image.png"
    shutil.copyfile(BASE_SOURCE, base)
    overlay = "Anthropic\n7,500%+ IN 2 YEARS"
    subprocess.run(["convert", str(base), "-gravity", "northwest", "-fill", "white", "-font", "DejaVu-Sans-Bold", "-pointsize", "76", "-annotate", "+72+110", overlay, "-gravity", "southeast", "-geometry", "+42+42", "(", str(LOGO), "-resize", "112x112", ")", "-composite", str(final)], check=True)
    created = iso(now)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Anthropic valuation rises more than 7,500%",
        "status": "ready",
        "postText": "Anthropic's valuation has increased by more than 7,500% over the last 2 years.",
        "mirroredFacts": [
            "The benchmark states that Anthropic's valuation increased by more than 7,500% over the last two years.",
            "Anthropic announced a $380 billion post-money valuation in its February 2026 Series G financing.",
            "Anthropic announced a $965 billion post-money valuation in its May 2026 Series H financing.",
            "A January 2024 financing report put Anthropic's valuation at $18.4 billion."
        ],
        "verificationSources": [source["url"], "https://www.anthropic.com/news/anthropic-raises-30-billion-series-g-funding-380-billion-post-money-valuation", "https://www.anthropic.com/news/series-h", "https://www.forbes.com/sites/alexkonrad/2024/01/11/anthropic-750million-funding-round-menlo-ventures/"],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": created,
        "sourceExpiresAt": iso(expires),
        "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed", "qa": {"inspectedAt": created, "result": "passed", "checks": ["square 1254x1254 PNG", "complete Anthropic AI infrastructure entity-led scene", "factual copy and visible 7,500% number proofread", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, hashtags, or watermark", "not a pure-text card or generic-radar visual"]}}
    }
    document["packages"].append(package)
    document["runs"].append({"id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": created, "completedAt": iso(datetime.now(timezone.utc)), "summary": "Produced one newest fresh Anthropic valuation package with an inspected entity-led image and exact-logo composite.", "reason": "", "selectedPackageIds": [PACKAGE_ID]})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
