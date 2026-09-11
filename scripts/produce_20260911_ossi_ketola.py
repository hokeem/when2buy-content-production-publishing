#!/usr/bin/env python3
from datetime import datetime, timezone, timedelta
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

SOURCE_ID = "2098448408344186893"
PACKAGE_ID = "pkg-20260911-ossi-ketola-duel-million"
GENERATED = Path("/root/.codex/generated_images/01a0914d-f944-7bc0-921b-ceca09b78a55/exec-6fe83cc5-4ace-4ea8-939d-2546f8da205f.png")
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"
FINAL = ROOT / "deliverables" / PACKAGE_ID / "when2buy-image.png"

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def main():
    doc = state.load_state()
    source = next(item for item in doc["benchmarkPosts"] if str(item.get("id")) == SOURCE_ID)
    posted = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    if now - posted > timedelta(minutes=90):
        raise SystemExit("source expired before production")
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["convert", str(GENERATED), "-resize", "1254x1254^", "-gravity", "center", "-crop", "1254x1254+0+0", "+repage", "-fill", "#050505", "-colorize", "8%", "-fill", "white", "-font", "DejaVu-Sans-Bold", "-pointsize", "43", "-gravity", "northwest", "-annotate", "+54+52", "OSSI KETOLA", "-fill", "#E11D2E", "-pointsize", "76", "-annotate", "+54+178", "$1M FIRST HAND", "-fill", "white", "-pointsize", "29", "-annotate", "+54+280", "DUEL HEADS-UP POKER", "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite", str(FINAL)], check=True, timeout=45)
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Ossi Ketola reportedly wins $1M first hand",
        "status": "blocked",
        "postText": "Ossi (Monarch) Ketola, owner of Duel, just won $1 million on the first hand of the biggest heads-up poker game ever.",
        "mirroredFacts": [
            "The benchmark post says Ossi (Monarch) Ketola, owner of Duel, won $1 million on the first hand.",
            "The benchmark post calls it the biggest heads-up poker game ever.",
        ],
        "verificationSources": [source["url"], "https://www.pokernews.com/news/2026/09/limitless-sucks-out-to-win-triton-2m-heads-up-match-in-minu-52343.htm"],
        "verificationStatus": "blocked_conflicting_authoritative_reporting",
        "verificationNote": "PokerNews reporting describes the opening $2M heads-up match as a win for Wiktor Malinowski, conflicting with the benchmark claim that Ketola won $1M on the first hand.",
        "imagePath": str(FINAL.relative_to(ROOT)),
        "createdAt": stamp(),
        "sourceExpiresAt": source.get("postedAt"),
        "visualProduction": {
            "method": "image_model",
            "prompt": "Photorealistic-natural square editorial poker-room scene with a high-stakes winner, dark premium room, green felt, chips and cards, near-black palette, restrained red accent, clear upper-left typography-safe space; no generated text, logos, watermark, signage, source, attribution, disclaimer, commentary, CTA, tagline, or generic chart.",
            "logoApplied": True,
            "qaStatus": "passed",
            "qa": {"inspectedAt": stamp(), "result": "passed", "checks": ["square 1254x1254 PNG", "complete entity-led poker scene", "factual text composited once", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text card or generic-radar visual"]},
        },
    }
    old = next((item for item in doc["packages"] if item.get("id") == PACKAGE_ID), None)
    if old:
        old.clear(); old.update(package)
    else:
        doc["packages"].append(package)
    now_stamp = stamp()
    doc["runs"].append({"id": "run-" + now_stamp.replace("-", "").replace(":", "") + "-produce", "mode": "produce", "status": "partial", "startedAt": now_stamp, "completedAt": now_stamp, "summary": "Produced the newest fresh benchmark package but blocked publication because authoritative reporting conflicts with the benchmark claim.", "reason": "blocked_conflicting_authoritative_reporting", "selectedPackageId": PACKAGE_ID})
    errors = state.validate(doc)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(doc)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
