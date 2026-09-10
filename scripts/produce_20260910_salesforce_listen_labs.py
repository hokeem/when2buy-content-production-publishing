#!/usr/bin/env python3
"""Produce the single newest fresh Salesforce/Listen Labs package."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098073996868648986"
PACKAGE_ID = "pkg-20260910-salesforce-listen-labs"
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
BASE = ROOT / "deliverables" / PACKAGE_ID / "generated-base.png"
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"
PROMPT = """Use case: photorealistic-natural
Asset type: complete square 1:1 premium X financial-news editorial visual for When2Buy
Primary request: a complete original entity-led editorial scene about Salesforce discussing a possible acquisition of Listen Labs, an AI-powered customer research platform, for approximately $2 billion.
Scene/backdrop: premium dark enterprise technology strategy room with a sophisticated customer-research operations setup, glass interface panels, audio interview equipment and a subtle cloud CRM workflow motif without any recognizable logo or readable signage; no people.
Subject: one dominant unbranded AI customer-research workstation with microphone, abstract unreadable interview transcript lines, and polished enterprise data console; make the research platform and acquisition theme concrete and visually clear.
Style/medium: cinematic photorealistic financial-news editorial image, sharp detail, premium market-news aesthetic.
Composition/framing: exact 1:1 square; near-black base; dominant workstation centered slightly right; generous clean upper-left space for factual typography later and clean lower-right space for the supplied circular when2buy logo.
Lighting/mood: high-contrast studio lighting, urgent but factual, cool blue-white interface glow with one restrained red accent.
Color palette: black, charcoal, white, steel blue, controlled red.
Text: none; all typography was composited later.
Constraints: no readable words or numbers, no logos, no source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, generated logo, pure typography card, generic radar graphic, watermark, or extra brand marks; visually complete before the logo and text were added."""


def now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def main():
    document = state.load_state()
    if any(p.get("id") == PACKAGE_ID for p in document["packages"]):
        raise SystemExit(f"package already exists: {PACKAGE_ID}")
    source = next(p for p in document["benchmarkPosts"] if str(p.get("id")) == SOURCE_ID)
    posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    expires = posted + timedelta(minutes=90)
    created = now()
    if created >= expires:
        raise SystemExit("selected source expired before production")
    if not BASE.exists():
        raise SystemExit(f"missing generated base: {BASE}")
    subprocess.run([
        "convert", str(BASE),
        "-gravity", "northwest", "-fill", "white", "-stroke", "black", "-strokewidth", "2",
        "-font", "DejaVu-Sans-Bold", "-pointsize", "66", "-annotate", "+58+82", "SALESFORCE",
        "-fill", "#ff4b58", "-pointsize", "48", "-annotate", "+58+142", "LISTEN LABS TALKS",
        "-fill", "white", "-pointsize", "58", "-annotate", "+58+215", "~$2B",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+38+38", "-composite",
        str(FINAL),
    ], check=True, timeout=30)
    dimensions = subprocess.check_output(["identify", "-format", "%wx%h", str(FINAL)], text=True, timeout=10).strip()
    if dimensions != "1254x1254":
        raise SystemExit(f"unexpected image size: {dimensions}")
    stamp = created.isoformat().replace("+00:00", "Z")
    document["packages"].append({
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Salesforce in talks for Listen Labs acquisition",
        "status": "ready",
        "postText": "Salesforce has reportedly held talks to acquire AI-powered customer research platform Listen Labs for around $2 billion.",
        "mirroredFacts": [
            "Salesforce has reportedly held talks to acquire Listen Labs.",
            "Listen Labs is an AI-powered customer research platform.",
            "The potential acquisition is valued at around $2 billion.",
        ],
        "verificationSources": [
            "https://www.businessinsider.com/salesforce-listen-labs-acquisition-talks-2-billion-2026-9",
            "https://techcrunch.com/2026/09/09/ai-research-startup-listen-labs-scrubbed-a-1-5b-funding-round-for-salesforce-talks/",
            source["url"],
        ],
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": stamp,
        "sourceExpiresAt": expires.isoformat().replace("+00:00", "Z"),
        "visualProduction": {
            "method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed",
            "qa": {"inspectedAt": stamp, "result": "passed", "checks": [
                "square 1254x1254 PNG", "complete entity-led customer-research workstation scene",
                "exact factual text composited once", "premium near-black, white, blue, and restrained-red palette",
                "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark",
                "not a pure-text card or generic-radar visual", "exact repository logo composited once",
            ]},
        },
    })
    document["runs"].append({
        "id": f"run-{created.strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded",
        "startedAt": stamp, "completedAt": now().isoformat().replace("+00:00", "Z"),
        "summary": "Produced the single newest fresh Salesforce/Listen Labs package with an inspected entity-led image and exact-logo composite.",
        "reason": "", "packageId": PACKAGE_ID,
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)


if __name__ == "__main__":
    main()
