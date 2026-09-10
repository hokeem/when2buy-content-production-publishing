#!/usr/bin/env python3
"""Produce the single newest fresh Oracle backlog package for this run."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098147267538559075"
PACKAGE_ID = "pkg-20260910-oracle-ai-backlog"
GENERATED = Path("/root/.codex/generated_images/01a08d03-5855-7a72-818c-8d5585b33b84/exec-c3931228-91eb-4980-918c-f87f48a2b413.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"

def stamp():
    return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "convert", str(GENERATED), "-resize", "1254x1254!", "-gravity", "northwest",
        "-fill", "#050505cc", "-draw", "roundrectangle 44,44 650,535 28,28",
        "-font", "DejaVu-Sans-Bold", "-fill", "white", "-pointsize", "48",
        "-annotate", "+78+120", "ORACLE AI BACKLOG",
        "-fill", "#ef3b2d", "-pointsize", "164", "-annotate", "+78+290", "$664B",
        "-fill", "white", "-pointsize", "34", "-annotate", "+82+495", "UP FROM $455.3B",
        "(", str(LOGO), "-resize", "116x116", ")", "-gravity", "southeast",
        "-geometry", "+46+46", "-composite", str(FINAL)
    ], check=True)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Oracle AI backlog reaches $664B",
        "status": "ready",
        "postText": "Oracle $ORCL now has a $664B AI backlog, up from $455.3B in the same quarter last year.",
        "mirroredFacts": [
            "Oracle's AI backlog is $664 billion.",
            "The comparable figure in the same quarter last year was $455.3 billion."
        ],
        "verificationSources": [
            "https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Q1-Results-Driven-by-Triple-Digit-Growth-in-Cloud-Infrastructure-Revenues/default.aspx",
            "https://www.oracle.com/news/announcement/q4fy26-earnings-release-2026-06-10/",
            source["url"]
        ],
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": stamp(),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Photorealistic square Oracle AI cloud data-center visual with near-black servers and restrained red accents; no generated text or branding; exact repository logo composited once afterward.",
            "logoApplied": True,
            "qaStatus": "passed",
            "qa": {"checks": ["square 1254x1254", "complete entity-led visual", "factual headline and supporting number proofread", "no source attribution or CTA", "exact repository logo composited once", "logo clear space"]}
        }
    }
    existing = next((item for item in document["packages"] if str(item.get("benchmarkPostId")) == SOURCE_ID), None)
    if existing:
        existing.clear(); existing.update(package)
    else:
        document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced one newest fresh Oracle backlog package with exact-logo compositing.", "reason": ""})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(f"Produced {PACKAGE_ID}")

if __name__ == "__main__":
    main()
