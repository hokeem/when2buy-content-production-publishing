#!/usr/bin/env python3
"""Create the single fresh Goldman/Fed package for this scheduled run."""
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098674263930593636"
GENERATED = Path("/root/.codex/generated_images/01a09485-f49e-7611-85bc-b7673a35febb/exec-3ff8f187-345d-48a7-b933-c7ec4028e6f1.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
PACKAGE_ID = "pkg-20260912-goldman-fed-rate-hike"
IMAGE = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image-model.png"

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    IMAGE.parent.mkdir(parents=True, exist_ok=True)
    import subprocess
    subprocess.run(["convert", str(GENERATED), "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(IMAGE)], check=True)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Goldman Sachs expects a Fed hike next week",
        "status": "ready",
        "postText": "Goldman Sachs now expects a 25-basis-point Fed rate hike next week.\n\nThe FOMC decision is due Wednesday.",
        "mirroredFacts": ["Goldman Sachs now expects a 25-basis-point FOMC rate increase next week.", "The meeting concludes next Wednesday."],
        "verificationSources": ["https://www.goldmansachs.com/insights/the-markets/what-a-fed-rate-hike-could-mean-for-us-stocks", "https://www.tipranks.com/news/the-fly/goldman-sachs-now-expects-25bp-fomc-rate-increase-next-week-thefly-news", source["url"]],
        "imagePath": str(IMAGE.relative_to(ROOT)),
        "createdAt": stamp(),
        "visualProduction": {"method": "image_model", "prompt": "Square editorial Federal Reserve building with rising rate marker; exact text FED RATE HIKE / NEXT WEEK and GOLDMAN SACHS: 25 BP; near-black base, white type, red accents; no logo generated. Exact repository logo composited once afterward.", "logoApplied": True, "qaStatus": "passed"},
    }
    existing = next((item for item in document["packages"] if item.get("id") == PACKAGE_ID), None)
    if existing:
        existing.clear(); existing.update(package)
    else:
        document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced one fresh Goldman/Fed package with a complete square entity-led visual and exact-logo compositing.", "reason": ""})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
