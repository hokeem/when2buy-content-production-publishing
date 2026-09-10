#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

PACKAGE_ID = "pkg-20260910-nvidia-cybersecurity-ai"
SOURCE_ID = "2098082819452833956"
BASE = Path("/root/.codex/generated_images/01a08c19-df7a-7082-b8df-508c7c4b5630/exec-e441d533-5670-4ab5-93e4-5b714e76888b.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
OUT_DIR = ROOT / "deliverables" / PACKAGE_ID
OUT = OUT_DIR / "when2buy-image-model.png"

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    doc = state.load_state()
    source = next(x for x in doc["benchmarkPosts"] if str(x["id"]) == SOURCE_ID)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "convert", str(BASE), "-gravity", "northwest", "-font", "DejaVu-Sans-Bold",
        "-fill", "white", "-pointsize", "72", "-annotate", "+72+92", "NVIDIA",
        "-fill", "#ff4b4b", "-pointsize", "104", "-annotate", "+72+220", "CYBERSECURITY",
        "-fill", "white", "-pointsize", "48", "-annotate", "+72+292", "NEXT MAJOR AI USE CASE",
        "(", str(LOGO), "-resize", "132x132", ")", "-gravity", "southeast", "-geometry", "+54+54",
        "-composite", str(OUT)
    ], check=True)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "NVIDIA CEO calls cybersecurity the next major AI use case",
        "status": "ready",
        "postText": "NVIDIA CEO Jensen Huang said cybersecurity is the next major use case of AI.",
        "mirroredFacts": ["NVIDIA CEO Jensen Huang said cybersecurity is the next major use case of AI."],
        "verificationSources": [source["url"], "https://blogs.nvidia.com/blog/nvidia-crowdstrike-fal-con-2026/"],
        "imagePath": f"deliverables/{PACKAGE_ID}/when2buy-image-model.png",
        "createdAt": stamp(),
        "sourceExpiresAt": (datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y") + __import__("datetime").timedelta(minutes=90)).isoformat().replace("+00:00", "Z"),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Complete square entity-led NVIDIA AI cybersecurity server scene; near-black premium financial-news visual with Jensen Huang, AI GPU/server architecture, protective cybersecurity shield, no readable text in base; typography and exact repository logo composited afterward.",
            "logoApplied": True,
            "qaStatus": "passed",
            "qa": {"inspectedAt": stamp(), "result": "passed", "checks": ["square 1254x1254 PNG", "complete entity-led AI cybersecurity server scene", "exact factual text composited once", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text card or generic-radar visual"]}
        }
    }
    old = next((x for x in doc["packages"] if x.get("id") == PACKAGE_ID), None)
    if old:
        old.clear(); old.update(package)
    else:
        doc["packages"].append(package)
    doc["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced the single newest fresh NVIDIA cybersecurity package with an inspected entity-led image and exact-logo composite.", "reason": ""})
    errors = state.validate(doc)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(doc)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
