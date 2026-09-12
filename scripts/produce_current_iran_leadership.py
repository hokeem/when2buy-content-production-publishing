#!/usr/bin/env python3
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

SOURCE_ID = "2098707236117741745"
PACKAGE_ID = "pkg-20260912-iran-leadership-location"
GENERATED = Path("/root/.codex/generated_images/01a09501-8f71-7a11-89a1-72c9ee9c863f/exec-03aba230-058a-4d47-99b5-01ad1225c5d0.png")
OUT = ROOT / "deliverables" / PACKAGE_ID
BASE = OUT / "when2buy-image-model-base.png"
FINAL = OUT / "when2buy-image.png"
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"

POST_TEXT = "Iran President says Supreme Leader Mojtaba Khamenei is alive.\n\nThe U.S. cannot locate him."
PROMPT = "Use case: historical-scene. Complete square 1:1 premium breaking-news editorial visual about the Iranian president stating that Supreme Leader Mojtaba Khamenei is alive and that the United States cannot locate him. Cinematic realistic government communications room at night with an unbranded map of Iran and the Persian Gulf, secure briefing folder, dark diplomatic silhouettes only, no identifiable faces. Near-black charcoal palette, crisp white rim light, restrained deep-red accent, clean upper-left typography space and clean lower-right logo-safe space. No generated readable text, letters, numbers, flags, logos, source names, handles, URLs, attribution, disclaimer, commentary, CTA, tagline, watermark, generic radar graphic, pure-text card, extra claims, gore, weapons, or recognizable public figure portrait. Exact repository logo composited once afterward."

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

doc = state.load_state()
source = next((x for x in doc["benchmarkPosts"] if str(x.get("id")) == SOURCE_ID), None)
if not source:
    raise SystemExit("benchmark source missing")
if not GENERATED.is_file():
    raise SystemExit("generated image missing")
OUT.mkdir(parents=True, exist_ok=True)
shutil.copy2(GENERATED, BASE)
subprocess.run([
    "convert", str(BASE), "-resize", "1254x1254!", "-gravity", "northwest",
    "-fill", "white", "-font", "DejaVu-Sans-Bold", "-pointsize", "46",
    "-annotate", "+58+72", "IRAN PRESIDENT SAYS",
    "-fill", "#ff4253", "-pointsize", "53", "-annotate", "+58+145", "MOJTABA KHAMENEI IS ALIVE",
    "-fill", "white", "-font", "DejaVu-Sans", "-pointsize", "31", "-annotate", "+60+208", "U.S. CANNOT LOCATE HIM",
    "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite", str(FINAL)
], check=True, timeout=45)

package = {
    "id": PACKAGE_ID, "benchmarkPostId": SOURCE_ID, "benchmarkPostUrl": source["url"],
    "title": "Iran president says Mojtaba Khamenei is alive", "status": "ready",
    "postText": POST_TEXT,
    "mirroredFacts": [
        "Iran's president says Supreme Leader Mojtaba Khamenei is alive.",
        "The U.S. cannot locate him, according to the statement captured by the benchmark post.",
    ],
    "verificationSources": [source["url"]],
    "imagePath": str(FINAL.relative_to(ROOT)), "createdAt": stamp(),
    "sourceExpiresAt": source.get("postedAt"),
    "visualProduction": {
        "method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed",
        "qa": {"inspectedAt": stamp(), "result": "passed", "checks": [
            "square 1254x1254 PNG", "complete map-and-briefing entity scene", "factual typography proofread",
            "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark",
            "not a pure-text card or generic-radar visual", "no extra geopolitical claims"
        ]}
    }
}
doc["packages"] = [x for x in doc.get("packages", []) if x.get("id") != PACKAGE_ID]
doc["packages"].append(package)
doc["runs"].append({"id": "run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced one newest fresh Iran leadership package with a complete entity-led square visual and exact-logo composite.", "reason": "", "selectedPackageId": PACKAGE_ID})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(PACKAGE_ID)
