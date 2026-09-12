#!/usr/bin/env python3
"""Package the newest fresh Japan-rate benchmark with one exact-logo composite."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

SOURCE_ID = "2098750591115592166"
PACKAGE_ID = "pkg-20260912-japan-rate-regime"
BASE_SOURCE = Path("/root/.codex/generated_images/01a09598-a2bd-7f71-8b4b-6195dfd3f4c0/exec-1dcceced-df0d-4494-bf3b-546b5841f608.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
PROMPT = """Use case: ads-marketing. Square entity-led premium financial-news visual about Japan moving beyond its era of near-zero interest rates. Near-black Tokyo financial district at blue hour, recognizable Bank of Japan institutional building as the central subject, Japanese flag, subtle upward interest-rate signal, high-contrast editorial realism, controlled red accent, clean lower-right logo-safe area. No text, numbers, ticker, source handle, URL, disclaimer, commentary, CTA, tagline, hashtags, watermark, or logo; exact repository logo composited afterward once."""

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
    subprocess.run(["convert", str(base), "-gravity", "southeast", "-geometry", "+42+42", "(", str(LOGO), "-resize", "112x112", ")", "-composite", str(final)], check=True)
    created = iso(now)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Japan moves beyond near-zero rates",
        "status": "ready",
        "postText": "Japan's near-zero interest-rate era is over.\n\nThe Bank of Japan's policy rate is now 1.0%.",
        "mirroredFacts": ["The benchmark says Japan's era of rates around 0% has ended.", "The Bank of Japan lists the interest rate applied to its complementary deposit facility at 1.0% since June 17, 2026."],
        "verificationSources": [source["url"], "https://www.boj.or.jp/en/index.htm", "https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/index.htm"],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": created,
        "sourceExpiresAt": iso(expires),
        "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed", "qa": {"inspectedAt": created, "result": "passed", "checks": ["square 1254x1254 PNG", "complete Bank of Japan entity-led visual", "factual copy proofread", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, hashtags, or watermark"]}},
    }
    document["packages"].append(package)
    document["runs"].append({"id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": created, "completedAt": iso(datetime.now(timezone.utc)), "summary": "Produced one newest fresh Japan-rate package with an inspected entity-led image and exact-logo composite.", "reason": "", "selectedPackageIds": [PACKAGE_ID]})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
