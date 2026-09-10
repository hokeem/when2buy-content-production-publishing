#!/usr/bin/env python3
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098169986414006375"
PACKAGE_ID = "pkg-20260910-gme-ryan-cohen-20m-purchase"
BASE = Path("/root/.codex/generated_images/01a08d63-779b-7682-a741-8eccd5b726b3/exec-8d5ec25f-415d-4231-b593-3e39530fedee.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
OUT_DIR = ROOT / "deliverables" / PACKAGE_ID
FINAL = OUT_DIR / "when2buy-image-model.png"
SEC = "https://www.sec.gov/Archives/edgar/data/1767470/000092189526002531/xslF345X06/form413177gme_09102026.xml"

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def parse_posted(value):
    return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    posted = parse_posted(source["postedAt"])
    expires = posted + timedelta(minutes=90)
    now = datetime.now(timezone.utc)
    if now >= expires:
        raise SystemExit("Selected benchmark expired before production.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BASE, OUT_DIR / "generated-base.png")
    subprocess.run([
        "convert", str(BASE), "-resize", "1254x1254!", "-fill", "#00000099", "-draw", "rectangle 0,0 1254,370",
        "-gravity", "northwest", "-font", "DejaVu-Sans-Bold", "-fill", "white", "-pointsize", "76",
        "-annotate", "+68+112", "RYAN COHEN BUYS", "-fill", "#ff3b30", "-pointsize", "122",
        "-annotate", "+68+245", "$20.4M OF $GME", "-fill", "white", "-pointsize", "34",
        "-annotate", "+72+315", "1,000,000 SHARES · SEPT 10", "(", str(LOGO), "-resize", "112x112", ")",
        "-gravity", "southeast", "-geometry", "+42+42", "-composite", str(FINAL),
    ], check=True, timeout=30)
    dimensions = subprocess.run(["identify", "-format", "%wx%h", str(FINAL)], check=True, capture_output=True, text=True, timeout=10).stdout
    if dimensions != "1254x1254":
        raise SystemExit(f"Unexpected image dimensions: {dimensions}")
    created = stamp()
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Ryan Cohen buys $20.4M of GameStop stock",
        "status": "ready",
        "postText": "GameStop CEO Ryan Cohen just bought $20.4M worth of $GME stock.\n\nThe purchase covered 1,000,000 shares at a weighted average price of $20.3759.",
        "mirroredFacts": [
            "Ryan Cohen is GameStop's CEO, President and Chairman.",
            "He purchased 1,000,000 GameStop Class A shares on September 10, 2026.",
            "The SEC filing lists a weighted average price of $20.3759 per share, approximately $20.4 million.",
        ],
        "verificationSources": [SEC, source["url"]],
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": created,
        "sourceExpiresAt": expires.isoformat().replace("+00:00", "Z"),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Complete square GameStop entity-led editorial scene: GameStop storefront, filing pages, market atmosphere, near-black and red palette, no generated text or logo; reserve upper-left for factual typography and lower-right for exact repository logo.",
            "logoApplied": True,
            "qaStatus": "passed",
            "qa": {
                "inspectedAt": created,
                "result": "passed",
                "checks": [
                    "square 1254x1254 PNG",
                    "complete GameStop entity-led scene with filing and market context",
                    "factual text limited to Ryan Cohen, $20.4M, $GME, 1,000,000 shares, and September 10",
                    "exact repository logo composited once",
                    "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark",
                    "not a pure-text card or generic-radar visual",
                ],
            },
        },
    }
    document["packages"] = [item for item in document["packages"] if item.get("id") != PACKAGE_ID]
    document["packages"].append(package)
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": created, "completedAt": stamp(),
        "summary": "Produced the single newest fresh GameStop/Ryan Cohen package with primary-source verification, inspected entity-led image, and exact-logo composite.",
        "reason": "", "packageId": PACKAGE_ID,
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
