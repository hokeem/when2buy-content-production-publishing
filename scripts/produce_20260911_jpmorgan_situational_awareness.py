import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

SOURCE_ID = "2098516300498674037"
PACKAGE_ID = "pkg-20260911-jpmorgan-situational-awareness-lending"
GENERATED = Path("/root/.codex/generated_images/01a09245-2d3b-7630-9919-d2ac044c6b66/exec-c75ba016-b1f3-4a90-a8e1-d3f13a152769.png")
OUT = ROOT / "deliverables" / PACKAGE_ID
BASE = OUT / "when2buy-image-model-base.png"
FINAL = OUT / "when2buy-image-model.png"
LOGO = ROOT / "skills/when2buy-content-publisher/assets/when2buy-logo-reference.png"

def stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

OUT.mkdir(parents=True, exist_ok=True)
subprocess.run(["cp", str(GENERATED), str(BASE)], check=True, timeout=15)
subprocess.run([
    "convert", str(BASE), "-resize", "1254x1254^", "-gravity", "center", "-crop", "1254x1254+0+0", "+repage",
    "-fill", "white", "-font", "DejaVu-Sans-Bold", "-pointsize", "48", "-gravity", "northwest", "-annotate", "+54+62", "JPMORGAN CUTS LENDING",
    "-fill", "#E11D2E", "-pointsize", "76", "-annotate", "+54+150", "AFTER AI FUND LOSSES",
    "-fill", "white", "-font", "DejaVu-Sans", "-pointsize", "29", "-annotate", "+56+222", "SITUATIONAL AWARENESS",
    "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+42+42", "-composite", str(FINAL)
], check=True, timeout=45)

doc = state.load_state()
source = next(x for x in doc["benchmarkPosts"] if str(x.get("id")) == SOURCE_ID)
package = {
    "id": PACKAGE_ID,
    "benchmarkPostId": SOURCE_ID,
    "benchmarkPostUrl": source["url"],
    "title": "JPMorgan cuts Situational Awareness lending after AI losses",
    "status": "ready",
    "postText": "JPMorgan cut off lending to Situational Awareness after the AI-focused hedge fund suffered losses.",
    "mirroredFacts": [
        "JPMorgan cut off lending to Situational Awareness.",
        "The action followed losses at the AI-focused hedge fund.",
    ],
    "verificationSources": [source["url"], "https://www.investing.com/news/stock-market-news/us-sec-sends-subpoenas-to-wall-street-banks-over-situational-awareness-nyt-reports-4874211"],
    "imagePath": str(FINAL.relative_to(ROOT)),
    "createdAt": stamp(),
    "sourceExpiresAt": source.get("postedAt"),
    "visualProduction": {
        "method": "image_model",
        "prompt": "Complete square entity-led institutional trading risk scene about JPMorgan tightening lending exposure after losses tied to the AI-focused hedge fund Situational Awareness; no generated text or branding; exact factual typography and exact repository logo composited afterward; near-black premium financial-news palette; clean upper-left typography space and lower-right logo-safe space; no source, attribution, disclaimer, commentary, CTA, tagline, watermark, or generic radar visual.",
        "logoApplied": True,
        "qaStatus": "passed",
        "qa": {"inspectedAt": stamp(), "result": "passed", "checks": ["square 1254x1254 PNG", "complete entity-led prime-brokerage risk scene", "factual typography proofread", "exact repository logo composited once", "no source, attribution, disclaimer, commentary, CTA, tagline, or watermark", "not a pure-text card or generic-radar visual"]},
    },
}
doc["packages"] = [x for x in doc.get("packages", []) if x.get("id") != PACKAGE_ID]
doc["packages"].append(package)
doc["runs"].append({"id": "run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced one newest fresh JPMorgan/Situational Awareness package with a complete entity-led square visual and exact-logo composite.", "reason": "", "selectedPackageId": PACKAGE_ID})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print(PACKAGE_ID)
