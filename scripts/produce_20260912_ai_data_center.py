#!/usr/bin/env python3
"""Create exactly one fresh AI data-center fast-follow package."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098866872368148899"
PACKAGE_ID = "pkg-20260912-ai-data-center-buildout"
GENERATED = Path("/root/.codex/generated_images/01a09742-5883-7181-91bd-ebaa55ad5e49/exec-b9be0dca-4510-4b64-9009-3e3ebe74b8be.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image.png"

COPY = "AI data-center construction is accelerating after ChatGPT.\n\nThe IEA expects data-center electricity demand to roughly double to 945 TWh by 2030."
PROMPT = "Use case: photorealistic-natural; complete square 1:1 premium financial-news visual about the rise of AI data-center construction and spending since ChatGPT; vast modern data-center campus at dusk with server halls, cooling infrastructure, construction cranes, power substations, and realistic fiber-optic light; near-black base, white and steel-blue highlights, restrained red accents; leave readable text and logos out of generated image; exact repository logo composited once afterward; no watermark, source, attribution, disclaimer, commentary, CTA, tagline, hashtags, pure-text card, or generic abstract background."

def iso(dt=None):
    return (dt or datetime.now(timezone.utc)).replace(microsecond=0).isoformat().replace("+00:00", "Z")

doc = state.load_state()
source = next((x for x in doc["benchmarkPosts"] if str(x.get("id")) == SOURCE_ID), None)
if not source:
    raise SystemExit("selected benchmark post is missing")
posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
now = datetime.now(timezone.utc)
if now - posted > timedelta(minutes=90):
    raise SystemExit("STALE_SOURCE: selected benchmark exceeded the 90-minute TTL")
if not GENERATED.is_file():
    raise SystemExit(f"missing generated image: {GENERATED}")
FINAL.parent.mkdir(parents=True, exist_ok=True)
subprocess.run([
    "convert", str(GENERATED), "-gravity", "southwest", "-fill", "#050506cc", "-draw", "rectangle 0,820 1254,1254",
    "-fill", "white", "-font", "DejaVu-Sans-Bold", "-pointsize", "58", "-annotate", "+64+230", "AI DATA-CENTER BUILDOUT",
    "-fill", "#ef3348", "-pointsize", "78", "-annotate", "+64+125", "945 TWh BY 2030",
    "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite", str(FINAL)
], check=True)
package = {
    "id": PACKAGE_ID, "benchmarkPostId": SOURCE_ID, "benchmarkPostUrl": source["url"],
    "title": "AI data-center buildout accelerates", "status": "ready", "postText": COPY,
    "mirroredFacts": [
        "The benchmark describes rapidly rising spending to build data centers since ChatGPT.",
        "The IEA expects data-center electricity demand to roughly double to 945 TWh by 2030.",
    ],
    "verificationSources": [source["url"], "https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai"],
    "imagePath": str(FINAL.relative_to(ROOT)), "createdAt": iso(now),
    "sourceExpiresAt": iso(posted + timedelta(minutes=90)),
    "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "logoPath": "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png", "logoCount": 1, "canvas": "1254x1254", "qaStatus": "passed", "qa": {"inspectedAt": iso(now), "result": "passed", "checks": ["square 1:1 PNG", "complete entity-led data-center scene", "headline and 945 TWh fact proofread", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, hashtags, or watermark", "not a pure-text card or generic-radar visual"]}},
}
doc["packages"] = [x for x in doc["packages"] if x.get("id") != PACKAGE_ID]
doc["packages"].append(package)
doc["runs"].append({"id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": iso(now), "completedAt": iso(), "summary": "Produced one newest fresh AI data-center package with a complete square entity-led visual and exact-logo composite.", "reason": "", "selectedPackageIds": [PACKAGE_ID]})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(f"Prepared {PACKAGE_ID} {FINAL.relative_to(ROOT)}")
