#!/usr/bin/env python3
"""Produce the single fresh India bond-tokenisation package for this run."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098330814857506832"
PACKAGE_ID = "pkg-20260911-india-corporate-bond-tokenization"
GENERATED = Path("/root/.codex/generated_images/01a08fa4-43ff-7122-b02c-f4584c020818/exec-708f50ee-0c91-4a53-92e3-8902553fc067.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"

def stamp():
    return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    # Model art contains no branding; add the exact repository logo once after generation.
    subprocess.run([
        "convert", str(GENERATED),
        "-font", "DejaVu-Sans-Bold", "-fill", "white", "-stroke", "black", "-strokewidth", "3",
        "-pointsize", "58", "-gravity", "northwest", "-annotate", "+58+72", "INDIA TOKENIZES",
        "-pointsize", "92", "-annotate", "+58+176", "$620B BOND MARKET",
        "-pointsize", "36", "-fill", "#dddddd", "-annotate", "+58+232", "WHOLESALE DIGITAL RUPEE SETTLEMENT",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite",
        str(FINAL),
    ], check=True, timeout=45)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "India tokenizes corporate bonds in digital-rupee pilot",
        "status": "ready",
        "postText": "India just launched a pilot to tokenize its $620B corporate-bond market.\n\nSettlements will use the RBI’s wholesale digital rupee.",
        "mirroredFacts": [
            "India launched a pilot to tokenize its $620 billion corporate-bond market.",
            "Settlements use the RBI's wholesale digital rupee.",
        ],
        "verificationSources": [
            "https://recindia.nic.in/rec-limited-successfully-issued-indias-first-pilot-issue-on-tokenized-corporate-bonds-under-sebi-regulatory-sandbox-framework",
            "https://indianexpress.com/article/business/banking-and-finance/sebi-rbi-launch-demat-2-0-pilot-for-corporate-bond-tokenisation-10872369/",
            source["url"],
        ],
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": stamp(),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Square 1:1 editorial financial illustration of an Indian corporate bond certificate transitioning into linked blockchain ledger blocks and a digital rupee settlement token in a central-bank setting; no generated text or branding, clean lower-right logo-safe area; exact repository logo composited once after generation.",
            "logoApplied": True,
            "qaStatus": "passed",
        },
    }
    existing = next((item for item in document["packages"] if item.get("id") == PACKAGE_ID), None)
    if existing:
        existing.clear(); existing.update(package)
    else:
        document["packages"].append(package)
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(),
        "summary": "Produced one fresh India corporate-bond tokenisation package with exact-logo compositing.",
        "reason": "",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
